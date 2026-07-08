import streamlit as st
from db import (
    listar_estruturas, criar_estrutura, atualizar_estrutura, excluir_estrutura,
    upload_foto, BUCKET_ESTRUTURAS,
)

st.title("🛋️ Cadastro de Estrutura")
st.caption("Itens estruturantes de lounge: puffs, mesas, braçadeiras, dinâmicas, etc.")

with st.form("nova_estrutura", clear_on_submit=True):
    st.subheader("Novo item de estrutura")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome*")
        quantidade = st.number_input("Quantidade em estoque*", min_value=0, step=1)
        localizacao = st.text_input("Localização (ex: Depósito 1, Container A)")
    with c2:
        foto = st.file_uploader("Foto", type=["png", "jpg", "jpeg"])
        observacoes = st.text_area("Observações")
    enviado = st.form_submit_button("Cadastrar item")

    if enviado:
        if not nome:
            st.error("O nome é obrigatório.")
        else:
            foto_url = None
            if foto is not None:
                nome_arquivo = f"{nome.strip().replace(' ', '_')}_{foto.name}"
                foto_url = upload_foto(foto.getvalue(), nome_arquivo, bucket=BUCKET_ESTRUTURAS)
            criar_estrutura(nome.strip(), observacoes, int(quantidade), localizacao, foto_url)
            st.success(f"Item '{nome}' cadastrado!")
            st.rerun()

st.divider()
st.subheader("Itens de estrutura cadastrados")

estruturas = listar_estruturas()
busca = st.text_input("🔎 Buscar por nome")
if busca:
    estruturas = [e for e in estruturas if busca.lower() in e["nome"].lower()]

if not estruturas:
    st.info("Nenhum item de estrutura encontrado.")
else:
    for e in estruturas:
        with st.expander(f"{e['nome']} — {e['quantidade']} un."):
            c1, c2 = st.columns([1, 3])
            with c1:
                if e.get("foto_url"):
                    st.image(e["foto_url"], width=150)
            with c2:
                with st.form(f"edit_{e['id']}"):
                    novo_nome = st.text_input("Nome", value=e["nome"], key=f"nome_{e['id']}")
                    nova_qtd = st.number_input(
                        "Quantidade", min_value=0, step=1, value=e["quantidade"], key=f"qtd_{e['id']}"
                    )
                    nova_loc = st.text_input(
                        "Localização", value=e.get("localizacao") or "", key=f"loc_{e['id']}"
                    )
                    novas_obs = st.text_area(
                        "Observações", value=e.get("observacoes") or "", key=f"obs_{e['id']}"
                    )
                    col_a, col_b = st.columns(2)
                    salvar = col_a.form_submit_button("💾 Salvar alterações")
                    apagar = col_b.form_submit_button("🗑️ Excluir")

                    if salvar:
                        atualizar_estrutura(e["id"], {
                            "nome": novo_nome,
                            "quantidade": int(nova_qtd),
                            "localizacao": nova_loc,
                            "observacoes": novas_obs,
                        })
                        st.success("Atualizado!")
                        st.rerun()
                    if apagar:
                        excluir_estrutura(e["id"])
                        st.warning("Excluído.")
                        st.rerun()
