from datetime import date, datetime

import streamlit as st

from db import (
    listar_eventos, criar_evento, excluir_evento,
    listar_ativacoes, criar_ativacao, excluir_ativacao,
    listar_alocacoes, alocar_brinde, desalocar_brinde, reconciliar_brinde, listar_brindes,
    listar_alocacoes_estrutura, alocar_estrutura, desalocar_estrutura, reconciliar_estrutura, listar_estruturas,
)

st.title("📅 Eventos e Ativações")


def data_referencia(evento):
    return evento.get("data_fim") or evento["data_inicio"]


def parse_data(valor):
    return datetime.strptime(valor, "%Y-%m-%d").date()


with st.form("novo_evento", clear_on_submit=True):
    st.subheader("Novo evento")
    nome = st.text_input("Nome do evento*")
    periodo = st.checkbox("Evento com data de início e fim (período)")
    if periodo:
        c1, c2 = st.columns(2)
        data_inicio = c1.date_input("Data de início", value=date.today())
        data_fim = c2.date_input("Data de fim", value=date.today())
    else:
        data_inicio = st.date_input("Data do evento", value=date.today())
        data_fim = None
    enviado = st.form_submit_button("Cadastrar evento")
    if enviado:
        if not nome:
            st.error("O nome é obrigatório.")
        else:
            criar_evento(nome.strip(), data_inicio, data_fim)
            st.success(f"Evento '{nome}' criado!")
            st.rerun()

st.divider()

eventos = listar_eventos()
if not eventos:
    st.info("Nenhum evento cadastrado ainda.")
    st.stop()

opcoes = {
    f"{e['nome']} ({e['data_inicio']}{' a ' + e['data_fim'] if e.get('data_fim') else ''})": e
    for e in eventos
}
escolha = st.selectbox("Selecione um evento para gerenciar", list(opcoes.keys()))
evento = opcoes[escolha]
evento_passado = parse_data(data_referencia(evento)) < date.today()

if st.button("🗑️ Excluir evento"):
    excluir_evento(evento["id"])
    st.warning("Evento excluído.")
    st.rerun()

st.subheader(f"Ativações de: {evento['nome']}")

if evento_passado:
    st.info(
        "📌 Este evento já ocorreu. Para cada item alocado, informe quanto retornou "
        "ao estoque (Depois) — brindes têm padrão 0 (assume-se distribuído) e "
        "estrutura tem padrão igual ao que foi levado (assume-se que retorna)."
    )
else:
    st.success("🗓️ Este evento ainda vai acontecer. Planeje as ativações e aloque brindes/estrutura.")

    with st.form("nova_ativacao", clear_on_submit=True):
        nome_at = st.text_input("Nome da ativação (ex: Estande de boas-vindas)")
        desc_at = st.text_area("Descrição (opcional)")
        if st.form_submit_button("Adicionar ativação"):
            if nome_at:
                criar_ativacao(evento["id"], nome_at.strip(), desc_at)
                st.success("Ativação adicionada!")
                st.rerun()
            else:
                st.error("Informe o nome da ativação.")

ativacoes = listar_ativacoes(evento["id"])
brindes = listar_brindes()
brindes_map = {b["nome"]: b for b in brindes}
estruturas = listar_estruturas()
estruturas_map = {e["nome"]: e for e in estruturas}

if not ativacoes:
    st.info("Nenhuma ativação cadastrada para este evento.")

for at in ativacoes:
    with st.expander(f"🎯 {at['nome']}"):
        if at.get("descricao"):
            st.caption(at["descricao"])

        if st.button("🗑️ Excluir ativação", key=f"del_at_{at['id']}"):
            excluir_ativacao(at["id"])
            st.rerun()

        alocacoes = listar_alocacoes(at["id"])
        alocacoes_est = listar_alocacoes_estrutura(at["id"])

        # ------------------------------------------------------------
        # Evento no passado: conferência Antes/Depois (retorno ao estoque)
        # ------------------------------------------------------------
        if evento_passado:
            if not alocacoes and not alocacoes_est:
                st.caption("Nenhum brinde ou item de estrutura foi alocado nesta ativação.")
                continue

            with st.form(f"reconciliar_{at['id']}"):
                valores_brinde = {}
                valores_estrutura = {}

                if alocacoes:
                    st.markdown("**🎁 Brindes** (padrão: 0 — assume-se distribuído)")
                    for al in alocacoes:
                        b_info = al.get("brindes") or {}
                        antes = al["quantidade"]
                        default = al["quantidade_retornada"] if al.get("quantidade_retornada") is not None else 0
                        c1, c2, c3 = st.columns([3, 1, 2])
                        c1.write(b_info.get("nome", "—"))
                        c2.write(f"Antes: {antes}")
                        valores_brinde[al["id"]] = c3.number_input(
                            "Depois", min_value=0, max_value=antes, value=default,
                            key=f"brinde_{al['id']}", label_visibility="collapsed",
                        )

                if alocacoes_est:
                    st.markdown("**🛋️ Estrutura** (padrão: igual ao levado — assume-se que retorna)")
                    for al in alocacoes_est:
                        e_info = al.get("estruturas") or {}
                        antes = al["quantidade"]
                        default = al["quantidade_retornada"] if al.get("quantidade_retornada") is not None else antes
                        c1, c2, c3 = st.columns([3, 1, 2])
                        c1.write(e_info.get("nome", "—"))
                        c2.write(f"Antes: {antes}")
                        valores_estrutura[al["id"]] = c3.number_input(
                            "Depois", min_value=0, max_value=antes, value=default,
                            key=f"estrutura_{al['id']}", label_visibility="collapsed",
                        )

                if st.form_submit_button("💾 Salvar conferência desta ativação"):
                    for al_id, valor in valores_brinde.items():
                        reconciliar_brinde(al_id, int(valor))
                    for al_id, valor in valores_estrutura.items():
                        reconciliar_estrutura(al_id, int(valor))
                    st.success("Conferência salva e estoque atualizado!")
                    st.rerun()

        # ------------------------------------------------------------
        # Evento futuro: planejamento (alocar brindes/estrutura)
        # ------------------------------------------------------------
        else:
            aba_brindes, aba_estrutura = st.tabs(["🎁 Brindes", "🛋️ Estrutura"])

            with aba_brindes:
                st.markdown("**Brindes alocados**")
                if alocacoes:
                    for al in alocacoes:
                        b_info = al.get("brindes") or {}
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(b_info.get("nome", "—"))
                        c2.write(f"{al['quantidade']} un.")
                        if c3.button("↩️ Devolver ao estoque", key=f"desaloc_{al['id']}"):
                            desalocar_brinde(al["id"])
                            st.rerun()
                else:
                    st.caption("Nenhum brinde alocado ainda.")

                st.markdown("**Alocar novo brinde**")
                with st.form(f"aloc_{at['id']}"):
                    nomes_disponiveis = [n for n, b in brindes_map.items() if b["quantidade"] > 0]
                    if nomes_disponiveis:
                        brinde_sel = st.selectbox("Brinde", nomes_disponiveis, key=f"sel_{at['id']}")
                        max_qtd = brindes_map[brinde_sel]["quantidade"]
                        qtd = st.number_input(
                            f"Quantidade (disponível: {max_qtd})",
                            min_value=1, max_value=max_qtd, step=1, key=f"qtd_al_{at['id']}",
                        )
                        if st.form_submit_button("Alocar (retirar do estoque)"):
                            try:
                                alocar_brinde(at["id"], brindes_map[brinde_sel]["id"], int(qtd))
                                st.success("Brinde alocado e estoque atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao alocar: {e}")
                    else:
                        st.warning("Nenhum brinde com estoque disponível.")
                        st.form_submit_button("Alocar (retirar do estoque)", disabled=True)

            with aba_estrutura:
                st.markdown("**Estrutura alocada**")
                if alocacoes_est:
                    for al in alocacoes_est:
                        e_info = al.get("estruturas") or {}
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.write(e_info.get("nome", "—"))
                        c2.write(f"{al['quantidade']} un.")
                        if c3.button("↩️ Devolver ao estoque", key=f"desaloc_est_{al['id']}"):
                            desalocar_estrutura(al["id"])
                            st.rerun()
                else:
                    st.caption("Nenhum item de estrutura alocado ainda.")

                st.markdown("**Alocar novo item de estrutura**")
                with st.form(f"aloc_est_{at['id']}"):
                    nomes_disponiveis_est = [n for n, e in estruturas_map.items() if e["quantidade"] > 0]
                    if nomes_disponiveis_est:
                        estrutura_sel = st.selectbox("Item de estrutura", nomes_disponiveis_est, key=f"sel_est_{at['id']}")
                        max_qtd_est = estruturas_map[estrutura_sel]["quantidade"]
                        qtd_est = st.number_input(
                            f"Quantidade (disponível: {max_qtd_est})",
                            min_value=1, max_value=max_qtd_est, step=1, key=f"qtd_al_est_{at['id']}",
                        )
                        if st.form_submit_button("Alocar (retirar do estoque)"):
                            try:
                                alocar_estrutura(at["id"], estruturas_map[estrutura_sel]["id"], int(qtd_est))
                                st.success("Item de estrutura alocado e estoque atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao alocar: {e}")
                    else:
                        st.warning("Nenhum item de estrutura com estoque disponível.")
                        st.form_submit_button("Alocar (retirar do estoque)", disabled=True)
