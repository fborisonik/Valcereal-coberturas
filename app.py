# ============================================================
#   VALCEREAL — Home  v4.0
#   app.py  ·  Página principal del multi-page app
# ============================================================

from datetime import date
import streamlit as st

st.set_page_config(
    page_title="Valcereal — Herramientas Financieras",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

VC_VERDE     = "#009B67"
VC_VERDE_OSC = "#0B5641"
VC_AMARILLO  = "#C9A030"
VC_GRIS_FONDO = "#F4F6F4"

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background-color: {VC_GRIS_FONDO}; }}
  [data-testid="stSidebar"] {{ background-color: {VC_VERDE_OSC}; }}
  [data-testid="stSidebar"] * {{ color: white !important; }}

  .modulo-card {{
    background: white;
    border-radius: 10px;
    padding: 1.6rem 1.8rem;
    border-left: 5px solid {VC_VERDE};
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  }}
  .modulo-card h3 {{
    color: {VC_VERDE_OSC};
    font-size: 1.15rem;
    margin: 0 0 0.4rem 0;
  }}
  .modulo-card p {{
    color: #555;
    font-size: 0.9rem;
    margin: 0;
  }}
  .tag {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    margin-top: 0.7rem;
  }}
  .tag-activo {{
    background: {VC_VERDE};
    color: white;
  }}
  .tag-pronto {{
    background: {VC_AMARILLO};
    color: white;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1rem 0'>
      <p style='font-size:1.5rem; font-weight:800; color:white; margin:0'>VALCEREAL</p>
      <p style='color:#AADDCC; font-size:0.8rem; margin:0'>Herramientas Financieras</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Módulos**")
    st.page_link("pages/1_Coberturas.py", label="📈  Coberturas Agro", icon=None)
    st.markdown("---")
    st.caption(f"v4.0  ·  {date.today().strftime('%d/%m/%Y')}")

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div style="background-color:{VC_VERDE_OSC}; padding:2rem 2.2rem;
            border-radius:10px; margin-bottom:2rem;">
  <p style="font-size:2.2rem; font-weight:900; color:white;
            letter-spacing:2px; margin:0 0 0.3rem 0;">VALCEREAL</p>
  <p style="font-size:1.05rem; color:#AADDCC; margin:0;">
    Herramientas de análisis financiero para el agro argentino
  </p>
</div>
""", unsafe_allow_html=True)

# ── Cards de módulos ─────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="modulo-card">
      <h3>📈  Coberturas Agro</h3>
      <p>Armá y analizá posiciones de cobertura con futuros y opciones sobre granos.
         Simulá el impacto de múltiples operaciones, calculá breakevens y
         exportá un one-pager PDF con el análisis completo.</p>
      <span class="tag tag-activo">✓ Disponible</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="modulo-card">
      <h3>🏦  Renta Fija Argentina</h3>
      <p>Curva de rendimientos de LECAPs, BONCAPs y duales.
         Métricas de TNA, TEM y TEA por instrumento.
         Visualización de la curva TEM vs. días al vencimiento.</p>
      <span class="tag tag-pronto">⏳ Próximamente</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CTA ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding:1.5rem; background:white;
            border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,0.07);">
  <p style="color:{VC_VERDE_OSC}; font-weight:700; font-size:1.05rem; margin-bottom:0.4rem;">
    Empezá con el simulador de coberturas
  </p>
  <p style="color:#777; font-size:0.88rem;">
    Cargá futuros y opciones, calculá el P&L combinado y descargá el one-pager para tu cliente.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("📈  Ir a Coberturas Agro", type="primary", use_container_width=False):
    st.switch_page("pages/1_Coberturas.py")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption(
    f"Valcereal  ·  Análisis orientativo, no constituye asesoramiento de inversión  "
    f"·  {date.today().strftime('%d/%m/%Y')}"
)
