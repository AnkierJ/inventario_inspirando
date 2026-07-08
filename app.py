import streamlit as st
from branding import favicon, render_sidebar_logos

st.set_page_config(page_title="Inspirando Empreendedores - Inventário", page_icon=favicon(), layout="wide")
render_sidebar_logos()

home = st.Page("home.py", title="Home", icon="🏠", default=True)
brindes = st.Page("pages/1_🎁_Brindes.py", title="Brindes", icon="🎁")
eventos = st.Page("pages/2_📅_Eventos.py", title="Eventos", icon="📅")
estrutura = st.Page("pages/3_🛋️_Estrutura.py", title="Estrutura", icon="🛋️")

pg = st.navigation({
    "": [home],
    "Gestão": [brindes, eventos, estrutura],
})
pg.run()
