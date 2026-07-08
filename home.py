import streamlit as st
from db import listar_brindes, listar_eventos, listar_estruturas

st.title("🏠 Inventário — Inspirando Empreendedores")
st.caption("Controle de estoque de brindes e estrutura, e alocação em eventos/ativações")

brindes = listar_brindes()
estruturas = listar_estruturas()
eventos = listar_eventos()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Brindes cadastrados", len(brindes))
col2.metric("Unidades de brindes em estoque", sum(b["quantidade"] for b in brindes) if brindes else 0)
col3.metric("Itens de estrutura cadastrados", len(estruturas))
col4.metric("Eventos cadastrados", len(eventos))

st.divider()

st.subheader("⚠️ Estoque baixo (≤ 10 unidades)")
baixos_brindes = [{"Tipo": "Brinde", "Item": b["nome"], "Quantidade": b["quantidade"], "Localização": b.get("localizacao") or "-"} for b in brindes if b["quantidade"] <= 10]
baixos_estruturas = [{"Tipo": "Estrutura", "Item": e["nome"], "Quantidade": e["quantidade"], "Localização": e.get("localizacao") or "-"} for e in estruturas if e["quantidade"] <= 10]
baixos = baixos_brindes + baixos_estruturas
if baixos:
    st.dataframe(baixos, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum item com estoque baixo.")

st.divider()

aba_brindes, aba_estrutura = st.tabs(["🎁 Estoque de Brindes", "🛋️ Estoque de Estrutura"])

with aba_brindes:
    if brindes:
        for b in brindes:
            c1, c2 = st.columns([1, 5])
            with c1:
                if b.get("foto_url"):
                    st.image(b["foto_url"], width=80)
                else:
                    st.write("🎁")
            with c2:
                st.markdown(f"**{b['nome']}** — {b['quantidade']} un. — 📍 {b.get('localizacao') or 'sem localização'}")
                if b.get("observacoes"):
                    st.caption(b["observacoes"])
    else:
        st.info("Nenhum brinde cadastrado ainda. Vá em '🎁 Brindes' no menu lateral para começar.")

with aba_estrutura:
    if estruturas:
        for e in estruturas:
            c1, c2 = st.columns([1, 5])
            with c1:
                if e.get("foto_url"):
                    st.image(e["foto_url"], width=80)
                else:
                    st.write("🛋️")
            with c2:
                st.markdown(f"**{e['nome']}** — {e['quantidade']} un. — 📍 {e.get('localizacao') or 'sem localização'}")
                if e.get("observacoes"):
                    st.caption(e["observacoes"])
    else:
        st.info("Nenhum item de estrutura cadastrado ainda. Vá em '🛋️ Estrutura' no menu lateral para começar.")
