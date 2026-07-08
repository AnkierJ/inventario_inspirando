import base64
from pathlib import Path

import streamlit as st
from PIL import Image

ASSETS_DIR = Path(__file__).parent / "assets"


@st.cache_data
def _data_uri(filename: str, mime: str) -> str:
    conteudo = (ASSETS_DIR / filename).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(conteudo).decode()}"


def render_sidebar_logos():
    gentil = _data_uri("logoGentil.png", "image/png")
    nex = _data_uri("logoNEX.svg", "image/svg+xml")
    je = _data_uri("logoJE.png", "image/png")

    st.sidebar.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; padding:4px 4px 16px 4px;">
            <img src="{gentil}" style="max-height:40px; max-width:32%; object-fit:contain;" />
            <img src="{nex}" style="max-height:40px; max-width:32%; object-fit:contain;" />
            <img src="{je}" style="max-height:40px; max-width:32%; object-fit:contain;" />
        </div>
        <hr style="margin-top:0; margin-bottom:16px;" />
        """,
        unsafe_allow_html=True,
    )


def favicon() -> Image.Image:
    return Image.open(ASSETS_DIR / "logoGentil.png")
