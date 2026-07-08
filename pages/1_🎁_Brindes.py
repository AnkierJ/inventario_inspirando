import streamlit as st
from db import listar_brindes, criar_brinde, atualizar_brinde, excluir_brinde, upload_foto

st.title("🎁 Cadastro de Brindes")

with st.form("novo_brinde", clear_on_submit=True):
    st.subheader("Novo brinde")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome*")
        quantidade = st.number_input("Quantidade em estoque*", min_value=0, step=1)
        localizacao = st.text_input("Localização (ex: Armário 2, Sala X)")
    with c2:
        foto = st.file_uploader("Foto", type=["png", "jpg", "jpeg"])
        observacoes = st.text_area("Observações")
    enviado = st.form_submit_button("Cadastrar brinde")

    if enviado:
        if not nome:
            st.error("O nome é obrigatório.")
        else:
            foto_url = None
            if foto is not None:
                nome_arquivo = f"{nome.strip().replace(' ', '_')}_{foto.name}"
                foto_url = upload_foto(foto.getvalue(), nome_arquivo)
            criar_brinde(nome.strip(), observacoes, int(quantidade), localizacao, foto_url)
            st.success(f"Brinde '{nome}' cadastrado!")
            st.rerun()

st.divider()
st.subheader("Brindes cadastrados")

brindes = listar_brindes()
busca = st.text_input("🔎 Buscar por nome")
if busca:
    brindes = [b for b in brindes if busca.lower() in b["nome"].lower()]

if not brindes:
    st.info("Nenhum brinde encontrado.")
else:
    for b in brindes:
        with st.expander(f"{b['nome']} — {b['quantidade']} un."):
            c1, c2 = st.columns([1, 3])
            with c1:
                if b.get("foto_url"):
                    st.image(b["foto_url"], width=150)
            with c2:
                with st.form(f"edit_{b['id']}"):
                    novo_nome = st.text_input("Nome", value=b["nome"], key=f"nome_{b['id']}")
                    nova_qtd = st.number_input(
                        "Quantidade", min_value=0, step=1, value=b["quantidade"], key=f"qtd_{b['id']}"
                    )
                    nova_loc = st.text_input(
                        "Localização", value=b.get("localizacao") or "", key=f"loc_{b['id']}"
                    )
                    novas_obs = st.text_area(
                        "Observações", value=b.get("observacoes") or "", key=f"obs_{b['id']}"
                    )
                    col_a, col_b = st.columns(2)
                    salvar = col_a.form_submit_button("💾 Salvar alterações")
                    apagar = col_b.form_submit_button("🗑️ Excluir")

                    if salvar:
                        atualizar_brinde(b["id"], {
                            "nome": novo_nome,
                            "quantidade": int(nova_qtd),
                            "localizacao": nova_loc,
                            "observacoes": novas_obs,
                        })
                        st.success("Atualizado!")
                        st.rerun()
                    if apagar:
                        excluir_brinde(b["id"])
                        st.warning("Excluído.")
                        st.rerun()
