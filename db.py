import re
import unicodedata

import streamlit as st
from supabase import create_client, Client

BUCKET_BRINDES = "brindes-fotos"
BUCKET_ESTRUTURAS = "estruturas-fotos"


def _slugify_filename(nome_arquivo: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", nome_arquivo).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", sem_acentos)


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ---------------- Brindes ----------------
def listar_brindes():
    sb = get_client()
    return sb.table("brindes").select("*").order("nome").execute().data


def criar_brinde(nome, observacoes, quantidade, localizacao, foto_url=None):
    sb = get_client()
    sb.table("brindes").insert({
        "nome": nome,
        "observacoes": observacoes,
        "quantidade": quantidade,
        "localizacao": localizacao,
        "foto_url": foto_url,
    }).execute()


def atualizar_brinde(brinde_id, dados: dict):
    sb = get_client()
    sb.table("brindes").update(dados).eq("id", brinde_id).execute()


def excluir_brinde(brinde_id):
    sb = get_client()
    sb.table("brindes").delete().eq("id", brinde_id).execute()


def upload_foto(conteudo: bytes, nome_arquivo: str, bucket: str = BUCKET_BRINDES) -> str:
    sb = get_client()
    nome_seguro = _slugify_filename(nome_arquivo)
    sb.storage.from_(bucket).upload(
        nome_seguro, conteudo, {"content-type": "image/jpeg", "upsert": "true"}
    )
    return sb.storage.from_(bucket).get_public_url(nome_seguro)


# ---------------- Eventos ----------------
def listar_eventos():
    sb = get_client()
    return sb.table("eventos").select("*").order("data_inicio", desc=True).execute().data


def criar_evento(nome, data_inicio, data_fim=None):
    sb = get_client()
    sb.table("eventos").insert({
        "nome": nome,
        "data_inicio": str(data_inicio),
        "data_fim": str(data_fim) if data_fim else None,
    }).execute()


def excluir_evento(evento_id):
    sb = get_client()
    sb.table("eventos").delete().eq("id", evento_id).execute()


# ---------------- Ativações ----------------
def listar_ativacoes(evento_id):
    sb = get_client()
    return sb.table("ativacoes").select("*").eq("evento_id", evento_id).order("created_at").execute().data


def criar_ativacao(evento_id, nome, descricao):
    sb = get_client()
    sb.table("ativacoes").insert({"evento_id": evento_id, "nome": nome, "descricao": descricao}).execute()


def excluir_ativacao(ativacao_id):
    sb = get_client()
    sb.table("ativacoes").delete().eq("id", ativacao_id).execute()


# ---------------- Alocação de brindes em ativações ----------------
def listar_alocacoes(ativacao_id):
    sb = get_client()
    return (
        sb.table("ativacao_brindes")
        .select("*, brindes(nome, foto_url)")
        .eq("ativacao_id", ativacao_id)
        .execute()
        .data
    )


def alocar_brinde(ativacao_id, brinde_id, quantidade):
    sb = get_client()
    sb.rpc("alocar_brinde", {
        "p_ativacao_id": ativacao_id,
        "p_brinde_id": brinde_id,
        "p_quantidade": quantidade,
    }).execute()


def desalocar_brinde(ativacao_brinde_id):
    sb = get_client()
    sb.rpc("desalocar_brinde", {"p_ativacao_brinde_id": ativacao_brinde_id}).execute()


# ---------------- Estruturas ----------------
def listar_estruturas():
    sb = get_client()
    return sb.table("estruturas").select("*").order("nome").execute().data


def criar_estrutura(nome, observacoes, quantidade, localizacao, foto_url=None):
    sb = get_client()
    sb.table("estruturas").insert({
        "nome": nome,
        "observacoes": observacoes,
        "quantidade": quantidade,
        "localizacao": localizacao,
        "foto_url": foto_url,
    }).execute()


def atualizar_estrutura(estrutura_id, dados: dict):
    sb = get_client()
    sb.table("estruturas").update(dados).eq("id", estrutura_id).execute()


def excluir_estrutura(estrutura_id):
    sb = get_client()
    sb.table("estruturas").delete().eq("id", estrutura_id).execute()


# ---------------- Alocação de estruturas em ativações ----------------
def listar_alocacoes_estrutura(ativacao_id):
    sb = get_client()
    return (
        sb.table("ativacao_estruturas")
        .select("*, estruturas(nome, foto_url)")
        .eq("ativacao_id", ativacao_id)
        .execute()
        .data
    )


def alocar_estrutura(ativacao_id, estrutura_id, quantidade):
    sb = get_client()
    sb.rpc("alocar_estrutura", {
        "p_ativacao_id": ativacao_id,
        "p_estrutura_id": estrutura_id,
        "p_quantidade": quantidade,
    }).execute()


def desalocar_estrutura(ativacao_estrutura_id):
    sb = get_client()
    sb.rpc("desalocar_estrutura", {"p_ativacao_estrutura_id": ativacao_estrutura_id}).execute()


# ---------------- Reconciliação pós-evento (Antes/Depois) ----------------
def reconciliar_brinde(ativacao_brinde_id, quantidade_retornada):
    sb = get_client()
    sb.rpc("reconciliar_brinde", {
        "p_ativacao_brinde_id": ativacao_brinde_id,
        "p_quantidade_retornada": quantidade_retornada,
    }).execute()


def reconciliar_estrutura(ativacao_estrutura_id, quantidade_retornada):
    sb = get_client()
    sb.rpc("reconciliar_estrutura", {
        "p_ativacao_estrutura_id": ativacao_estrutura_id,
        "p_quantidade_retornada": quantidade_retornada,
    }).execute()
