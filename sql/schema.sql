-- Inventário Inspirando Empreendedores
-- Execute este script no SQL Editor do Supabase (Project > SQL Editor > New query)

create extension if not exists pgcrypto;

-- ==========================================================
-- BRINDES: itens do estoque
-- ==========================================================
create table if not exists brindes (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    foto_url text,
    observacoes text,
    quantidade integer not null default 0 check (quantidade >= 0),
    localizacao text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ==========================================================
-- EVENTOS: nome + data (única) ou data_inicio/data_fim (período)
-- ==========================================================
create table if not exists eventos (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    data_inicio date not null,
    data_fim date,
    created_at timestamptz not null default now()
);

-- ==========================================================
-- ATIVACOES: cada evento pode ter várias ativações
-- ==========================================================
create table if not exists ativacoes (
    id uuid primary key default gen_random_uuid(),
    evento_id uuid not null references eventos(id) on delete cascade,
    nome text not null,
    descricao text,
    created_at timestamptz not null default now()
);

-- ==========================================================
-- ATIVACAO_BRINDES: associação N:M entre ativações e brindes,
-- com a quantidade retirada do estoque para aquela ativação
-- ==========================================================
create table if not exists ativacao_brindes (
    id uuid primary key default gen_random_uuid(),
    ativacao_id uuid not null references ativacoes(id) on delete cascade,
    brinde_id uuid not null references brindes(id) on delete restrict,
    quantidade integer not null check (quantidade > 0),
    quantidade_retornada integer,
    created_at timestamptz not null default now()
);

create index if not exists idx_ativacoes_evento on ativacoes(evento_id);
create index if not exists idx_ativacao_brindes_ativacao on ativacao_brindes(ativacao_id);
create index if not exists idx_ativacao_brindes_brinde on ativacao_brindes(brinde_id);

-- ==========================================================
-- ROW LEVEL SECURITY: habilitado sem políticas em todas as
-- tabelas. O app acessa com a chave service_role (que ignora
-- RLS); as chaves anon/authenticated ficam sem nenhum acesso.
-- ==========================================================
alter table brindes enable row level security;
alter table eventos enable row level security;
alter table ativacoes enable row level security;
alter table ativacao_brindes enable row level security;

-- ==========================================================
-- FUNÇÕES: garantem que alocar/desalocar brinde e atualizar
-- o estoque aconteçam de forma atômica (tudo ou nada)
-- ==========================================================
create or replace function alocar_brinde(p_ativacao_id uuid, p_brinde_id uuid, p_quantidade integer)
returns void as $$
declare
    estoque_atual integer;
begin
    select quantidade into estoque_atual from brindes where id = p_brinde_id for update;

    if estoque_atual is null then
        raise exception 'Brinde não encontrado';
    end if;

    if estoque_atual < p_quantidade then
        raise exception 'Estoque insuficiente: disponível %, solicitado %', estoque_atual, p_quantidade;
    end if;

    update brindes set quantidade = quantidade - p_quantidade, updated_at = now() where id = p_brinde_id;

    insert into ativacao_brindes (ativacao_id, brinde_id, quantidade)
    values (p_ativacao_id, p_brinde_id, p_quantidade);
end;
$$ language plpgsql;

create or replace function desalocar_brinde(p_ativacao_brinde_id uuid)
returns void as $$
declare
    v_brinde_id uuid;
    v_quantidade integer;
begin
    select brinde_id, quantidade into v_brinde_id, v_quantidade
    from ativacao_brindes where id = p_ativacao_brinde_id;

    if v_brinde_id is null then
        raise exception 'Registro de alocação não encontrado';
    end if;

    update brindes set quantidade = quantidade + v_quantidade, updated_at = now() where id = v_brinde_id;

    delete from ativacao_brindes where id = p_ativacao_brinde_id;
end;
$$ language plpgsql;

-- ==========================================================
-- ESTRUTURAS: itens estruturantes de lounge (puffs, mesas,
-- braçadeiras, dinâmicas, etc.) — mesmo padrão de brindes
-- ==========================================================
create table if not exists estruturas (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    foto_url text,
    observacoes text,
    quantidade integer not null default 0 check (quantidade >= 0),
    localizacao text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ==========================================================
-- ATIVACAO_ESTRUTURAS: associação N:M entre ativações e estruturas,
-- com a quantidade retirada do estoque para aquela ativação
-- ==========================================================
create table if not exists ativacao_estruturas (
    id uuid primary key default gen_random_uuid(),
    ativacao_id uuid not null references ativacoes(id) on delete cascade,
    estrutura_id uuid not null references estruturas(id) on delete restrict,
    quantidade integer not null check (quantidade > 0),
    quantidade_retornada integer,
    created_at timestamptz not null default now()
);

create index if not exists idx_ativacao_estruturas_ativacao on ativacao_estruturas(ativacao_id);
create index if not exists idx_ativacao_estruturas_estrutura on ativacao_estruturas(estrutura_id);

alter table estruturas enable row level security;
alter table ativacao_estruturas enable row level security;

create or replace function alocar_estrutura(p_ativacao_id uuid, p_estrutura_id uuid, p_quantidade integer)
returns void as $$
declare
    estoque_atual integer;
begin
    select quantidade into estoque_atual from estruturas where id = p_estrutura_id for update;

    if estoque_atual is null then
        raise exception 'Estrutura não encontrada';
    end if;

    if estoque_atual < p_quantidade then
        raise exception 'Estoque insuficiente: disponível %, solicitado %', estoque_atual, p_quantidade;
    end if;

    update estruturas set quantidade = quantidade - p_quantidade, updated_at = now() where id = p_estrutura_id;

    insert into ativacao_estruturas (ativacao_id, estrutura_id, quantidade)
    values (p_ativacao_id, p_estrutura_id, p_quantidade);
end;
$$ language plpgsql;

create or replace function desalocar_estrutura(p_ativacao_estrutura_id uuid)
returns void as $$
declare
    v_estrutura_id uuid;
    v_quantidade integer;
begin
    select estrutura_id, quantidade into v_estrutura_id, v_quantidade
    from ativacao_estruturas where id = p_ativacao_estrutura_id;

    if v_estrutura_id is null then
        raise exception 'Registro de alocação não encontrado';
    end if;

    update estruturas set quantidade = quantidade + v_quantidade, updated_at = now() where id = v_estrutura_id;

    delete from ativacao_estruturas where id = p_ativacao_estrutura_id;
end;
$$ language plpgsql;

-- ==========================================================
-- RECONCILIAÇÃO PÓS-EVENTO: conferência "Antes/Depois" de
-- quanto de cada brinde/estrutura realmente retornou ao estoque
-- ==========================================================
create or replace function reconciliar_brinde(p_ativacao_brinde_id uuid, p_quantidade_retornada integer)
returns void as $$
declare
    v_brinde_id uuid;
    v_quantidade integer;
    v_retornada_atual integer;
begin
    select brinde_id, quantidade, quantidade_retornada
    into v_brinde_id, v_quantidade, v_retornada_atual
    from ativacao_brindes where id = p_ativacao_brinde_id;

    if v_brinde_id is null then
        raise exception 'Registro de alocação não encontrado';
    end if;

    if p_quantidade_retornada < 0 or p_quantidade_retornada > v_quantidade then
        raise exception 'Quantidade devolvida deve estar entre 0 e %', v_quantidade;
    end if;

    if v_retornada_atual is not null then
        update brindes set quantidade = quantidade - v_retornada_atual where id = v_brinde_id;
    end if;

    update ativacao_brindes set quantidade_retornada = p_quantidade_retornada where id = p_ativacao_brinde_id;
    update brindes set quantidade = quantidade + p_quantidade_retornada, updated_at = now() where id = v_brinde_id;
end;
$$ language plpgsql;

create or replace function reconciliar_estrutura(p_ativacao_estrutura_id uuid, p_quantidade_retornada integer)
returns void as $$
declare
    v_estrutura_id uuid;
    v_quantidade integer;
    v_retornada_atual integer;
begin
    select estrutura_id, quantidade, quantidade_retornada
    into v_estrutura_id, v_quantidade, v_retornada_atual
    from ativacao_estruturas where id = p_ativacao_estrutura_id;

    if v_estrutura_id is null then
        raise exception 'Registro de alocação não encontrado';
    end if;

    if p_quantidade_retornada < 0 or p_quantidade_retornada > v_quantidade then
        raise exception 'Quantidade devolvida deve estar entre 0 e %', v_quantidade;
    end if;

    if v_retornada_atual is not null then
        update estruturas set quantidade = quantidade - v_retornada_atual where id = v_estrutura_id;
    end if;

    update ativacao_estruturas set quantidade_retornada = p_quantidade_retornada where id = p_ativacao_estrutura_id;
    update estruturas set quantidade = quantidade + p_quantidade_retornada, updated_at = now() where id = v_estrutura_id;
end;
$$ language plpgsql;
