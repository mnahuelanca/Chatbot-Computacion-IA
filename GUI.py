####################
# GUI.py
####################

import streamlit as st

# ── Importar lógica del modelo ─────────────────────────────────────
from modeloCL_v2 import corpus, chat

# ── Configuración de página ────────────────────────────────────────
st.set_page_config(
    page_title="Chatbot GEM — Computación e IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Estilos CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #0f1117;
        color: #e2e8f0;
    }

    .gem-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.5rem;
    }

    .gem-header h1 {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #38bdf8;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .gem-header p {
        color: #64748b;
        font-size: 0.85rem;
        margin: 0.3rem 0 0 0;
        font-family: 'IBM Plex Mono', monospace;
    }

    .msg-user {
        background: #1e3a5f;
        border: 1px solid #2563eb;
        border-radius: 12px 12px 2px 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 0.5rem 3rem;
        color: #bfdbfe;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .msg-bot {
        background: #1a1f2e;
        border: 1px solid #1e293b;
        border-radius: 12px 12px 12px 2px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 3rem 0.5rem 0;
        color: #e2e8f0;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .msg-label-user {
        text-align: right;
        font-size: 0.7rem;
        color: #3b82f6;
        font-family: 'IBM Plex Mono', monospace;
        margin-bottom: 0.15rem;
        padding-right: 0.25rem;
    }

    .msg-label-bot {
        text-align: left;
        font-size: 0.7rem;
        color: #38bdf8;
        font-family: 'IBM Plex Mono', monospace;
        margin-bottom: 0.15rem;
        padding-left: 0.25rem;
    }

    .categoria-badge {
        display: inline-block;
        background: #0f3460;
        color: #38bdf8;
        font-size: 0.65rem;
        font-family: 'IBM Plex Mono', monospace;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        border: 1px solid #1d4ed8;
        margin-bottom: 0.4rem;
    }

    .stTextInput input {
        background: #1a1f2e !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.9rem !important;
    }

    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15) !important;
    }

    .stButton button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.5rem !important;
    }

    .stButton button:hover {
        background: #1d4ed8 !important;
    }

    .sidebar-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .stat-item {
        background: #1a1f2e;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 0.4rem 0.6rem;
        margin: 0.3rem 0;
        font-size: 0.8rem;
        color: #94a3b8;
        font-family: 'IBM Plex Mono', monospace;
    }

    hr {
        border-color: #1e293b !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────
@st.cache_data
def get_datos():
    return corpus

datos_qa = get_datos()

# ── Session State ─────────────────────────────────────────────────
if "historial" not in st.session_state:
    st.session_state.historial = []

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="gem-header">
    <h1>⬡ CHATBOT GEM</h1>
    <p>Asistente universitario — Computación e Inteligencia Artificial</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">📊 Dataset</div>',
        unsafe_allow_html=True
    )

    categorias_all = list(
        set(item.get("categoria", "?") for item in datos_qa)
    )

    st.markdown(
        f'<div class="stat-item">📝 {len(datos_qa)} preguntas cargadas</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="stat-item">🏷 {len(categorias_all)} categorías</div>',
        unsafe_allow_html=True
    )

    for cat in sorted(categorias_all):

        cantidad = sum(
            1 for item in datos_qa
            if item.get("categoria") == cat
        )

        st.markdown(
            f'<div class="stat-item">· {cat}: {cantidad}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    if st.button("🗑 Limpiar chat"):
        st.session_state.historial = []
        st.rerun()

# ── Mostrar historial ─────────────────────────────────────────────
with st.container():

    if not st.session_state.historial:

        st.markdown("""
        <div style="
            text-align:center;
            color:#334155;
            padding:3rem 0;
            font-family:'IBM Plex Mono',monospace;
            font-size:0.85rem;
        ">
            › Realizá una consulta incluida en la base de conocimientos
        </div>
        """, unsafe_allow_html=True)

    else:

        for msg in st.session_state.historial:

            if msg["rol"] == "user":

                st.markdown(
                    '<div class="msg-label-user">tú</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="msg-user">{msg["texto"]}</div>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<div class="msg-label-bot">GEM</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="msg-bot">{msg["texto"]}</div>',
                    unsafe_allow_html=True
                )

# ── Input ─────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:

    pregunta = st.text_input(
        label="pregunta",
        placeholder="Ej: ¿Qué es machine learning?",
        label_visibility="collapsed",
        key=f"input_{st.session_state.input_counter}",
    )

with col2:

    enviar = st.button(
        "Enviar",
        use_container_width=True
    )

# ── Envío ─────────────────────────────────────────────────────────
if enviar and pregunta.strip():

    pregunta_actual = pregunta.strip()

    st.session_state.historial.append({
        "rol": "user",
        "texto": pregunta_actual
    })

    with st.spinner("Consultando LLaMA..."):

        respuesta = chat(
            pregunta_actual
        )

    st.session_state.historial.append({
        "rol": "bot",
        "texto": respuesta
    })

    st.session_state.input_counter += 1

    st.rerun()

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
<div style="
    text-align:center;
    color:#1e293b;
    font-size:0.7rem;
    font-family:'IBM Plex Mono',monospace;
    padding-top:2rem;
">
    GEM Chatbot — Powered by LLaMA 3 + JSON Knowledge Base
</div>
""", unsafe_allow_html=True)