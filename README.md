# Inventário de Brindes — Inspirando Empreendedores

App Streamlit para cadastrar brindes, controlar estoque e alocá-los em ativações de eventos, com banco de dados no Supabase.

## Passo a passo — configurar o Supabase

1. **Criar o projeto**
   - Acesse https://supabase.com e crie uma conta (ou faça login).
   - Clique em "New project", escolha uma organização, dê um nome (ex: `inspirando-empreendedores`), defina uma senha do banco (guarde-a) e a região mais próxima (ex: South America).
   - Aguarde alguns minutos até o projeto ficar pronto.

2. **Criar as tabelas**
   - No menu lateral do projeto, abra **SQL Editor** → **New query**.
   - Cole todo o conteúdo do arquivo `sql/schema.sql` deste projeto e clique em **Run**.
   - Esse script único cria as tabelas `brindes`, `eventos`, `ativacoes`, `ativacao_brindes`, `estruturas`, `ativacao_estruturas`, as funções `alocar_brinde`/`desalocar_brinde`/`alocar_estrutura`/`desalocar_estrutura`/`reconciliar_brinde`/`reconciliar_estrutura` (que garantem que a baixa/devolução no estoque e o registro da alocação aconteçam juntos, de forma atômica) e habilita **Row Level Security** em todas as tabelas.
   - O editor do Supabase vai mostrar dois avisos antes de rodar: "operações destrutivas" (é o aviso genérico padrão para qualquer `CREATE`/`ALTER` — seguro aqui, pois é a primeira execução) e "tabelas sem RLS" (resolvido pelo próprio script, que já habilita RLS — pode marcar como revisado e rodar).

3. **Criar os buckets de fotos**
   - No menu lateral, abra **Storage** → **New bucket**.
   - Crie o bucket `brindes-fotos` (marque **Public bucket**).
   - Crie também o bucket `estruturas-fotos` (marque **Public bucket**).

4. **Pegar as credenciais**
   - No menu lateral, abra **Project Settings** → **API**.
   - Copie a **Project URL** e a chave **service_role** (não a `anon`).
   - O script habilita RLS sem criar políticas, então a chave `anon` fica sem nenhum acesso às tabelas — é preciso usar a `service_role`, que ignora RLS. Isso é seguro aqui porque o Streamlit roda no servidor: o `secrets.toml` nunca é enviado ao navegador do usuário.

5. **Configurar o app**
   - Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`.
   - Preencha com os valores copiados no passo anterior:
     ```toml
     SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
     SUPABASE_KEY = "sua-service-role-key-aqui"
     ```
   - **Nunca** compartilhe esse arquivo, não faça commit dele (já está no `.gitignore`) e não a exponha em código que rode no navegador — a `service_role` dá acesso total ao banco, ignorando qualquer restrição.

6. **Instalar dependências e rodar**
   ```powershell
   cd inventario_inspirando
   pip install -r requirements.txt
   streamlit run app.py
   ```

7. **(Opcional) Publicar no Streamlit Community Cloud**
   - Suba o projeto para um repositório no GitHub (sem o `secrets.toml`).
   - Em https://share.streamlit.io, crie um novo app apontando para o repositório.
   - Em "Advanced settings" → "Secrets", cole o mesmo conteúdo do `secrets.toml`.

## Estrutura do projeto

```
app.py                     # Roteador (st.navigation): define título/ícone da aba e o menu lateral
home.py                    # Home — dashboard (estoque geral, alertas de estoque baixo)
branding.py                # Logos (Gentil/NEX/JE) na barra lateral e favicon do navegador
pages/1_🎁_Brindes.py      # Cadastro/edição/exclusão de brindes
pages/2_📅_Eventos.py      # Cadastro de eventos e ativações. Evento futuro: aloca brindes/estrutura.
                           # Evento passado: pede a conferência Antes/Depois de cada item alocado.
pages/3_🛋️_Estrutura.py   # Cadastro/edição/exclusão de itens de estrutura de lounge
assets/                    # Logos usados pelo branding.py
db.py                      # Funções de acesso ao Supabase
sql/schema.sql             # Script único com todas as tabelas e funções do Supabase
.streamlit/secrets.toml    # Credenciais do Supabase (não versionar)
```
