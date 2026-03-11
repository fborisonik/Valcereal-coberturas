# ============================================================
#   VALCEREAL — Coberturas
#   Analizador de Opciones Agro · Streamlit Web App
# ============================================================

import io
import textwrap
from datetime import date

import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Valcereal Coberturas",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colores Valcereal ────────────────────────────────────────
VC_VERDE      = "#009B67"
VC_VERDE_OSC  = "#0B5641"
VC_AMARILLO   = "#C9A030"
VC_GRIS_LIN   = "#8A8A8A"
VC_GRIS_FONDO = "#F4F6F4"
VC_BLANCO     = "#FFFFFF"
VC_NEGRO      = "#1A1A1A"

# ── CSS personalizado ────────────────────────────────────────
st.markdown(f"""
<style>
  /* Fondo general */
  [data-testid="stAppViewContainer"] {{ background-color: {VC_GRIS_FONDO}; }}

  /* Sidebar verde oscuro */
  [data-testid="stSidebar"] {{ background-color: {VC_VERDE_OSC}; }}
  [data-testid="stSidebar"] label  {{ color: #AADDCC !important; font-size: 0.83rem; }}
  [data-testid="stSidebar"] p      {{ color: white !important; }}
  [data-testid="stSidebar"] h3     {{ color: white !important; }}
  [data-testid="stSidebar"] hr     {{ border-color: #1a7a5a; }}
  [data-testid="stSidebar"] input  {{ background-color: #0d6e4f !important; color: white !important; }}
  [data-testid="stSidebar"] .stSelectbox div[data-baseweb] {{ background-color: #0d6e4f; color: white; }}

  /* Botón descarga */
  [data-testid="stDownloadButton"] button {{
    background-color: {VC_VERDE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    margin-top: 0.5rem;
  }}
  [data-testid="stDownloadButton"] button:hover {{
    background-color: {VC_VERDE_OSC} !important;
  }}

  /* Métricas */
  [data-testid="metric-container"] {{
    background-color: white;
    border-left: 4px solid {VC_VERDE};
    border-radius: 6px;
    padding: 0.6rem 1rem;
  }}

  /* Header */
  .vc-header {{
    background-color: {VC_VERDE_OSC};
    padding: 1.1rem 1.8rem;
    border-radius: 8px;
    margin-bottom: 1.2rem;
  }}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SIDEBAR — Inputs
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📋 Datos de la Operación")
    st.markdown("---")

    CLIENTE     = st.text_input("Nombre del cliente",    value="Productor Agropecuario")
    INSTRUMENTO = st.text_input("Instrumento",           value="Soja")
    MES         = st.text_input("Mes de vencimiento",    value="Mayo 2025")
    UNIDAD      = st.text_input("Unidad de precio",      value="USD/tn")

    st.markdown("---")

    TIPO = st.selectbox(
        "Tipo de opción",
        options=["put", "call"],
        format_func=lambda x: (
            "PUT comprado  —  Cobertura a la baja" if x == "put"
            else "CALL comprado  —  Posición alcista"
        ),
    )

    PRECIO_SPOT = st.number_input("Precio spot actual",   value=323.0, step=0.5,  format="%.2f")
    STRIKE      = st.number_input("Strike de la opción",  value=315.0, step=0.5,  format="%.2f")
    PRIMA       = st.number_input("Prima pagada",         value=3.5,   step=0.05, format="%.2f", min_value=0.01)

    st.markdown("---")
    st.caption("Valcereal · Asesoramiento Financiero")


# ════════════════════════════════════════════════════════════
# CÁLCULOS
# ════════════════════════════════════════════════════════════
precio_min = min(PRECIO_SPOT, STRIKE) * 0.78
precio_max = max(PRECIO_SPOT, STRIKE) * 1.22
precios    = np.linspace(precio_min, precio_max, 600)

if TIPO == "put":
    payoff       = np.maximum(STRIKE - precios, 0)
    y_con        = precios + payoff - PRIMA
    y_sin        = precios
    precio_piso  = STRIKE - PRIMA
    breakeven    = STRIKE - PRIMA
    y_spot_con   = PRECIO_SPOT + max(STRIKE - PRECIO_SPOT, 0) - PRIMA
    y_spot_sin   = PRECIO_SPOT
    itm_otm      = "OTM" if PRECIO_SPOT > STRIKE else "ITM"
    diff_strike  = abs(PRECIO_SPOT - STRIKE)
    y_label      = f"Precio Efectivo de Venta ({UNIDAD})"
    titulo_op    = f"Cobertura a la Baja — Put Comprado | Vto. {MES}"
    explicacion  = (
        f"La posición consiste en un Put comprado sobre {INSTRUMENTO} con strike en "
        f"${STRIKE:.0f}/tn y vencimiento en {MES}. El cliente paga una prima de ${PRIMA}/tn "
        f"para garantizar un precio mínimo de venta de ${precio_piso:.1f}/tn, "
        f"independientemente de cuánto caiga el mercado. "
        f"La opción se encuentra actualmente {itm_otm} en ${diff_strike:.0f}/tn, "
        f"con el futuro de {MES} cotizando a ${PRECIO_SPOT:.0f}/tn. "
        f"Si los precios suben, el productor participa del alza descontando únicamente la prima pagada (${PRIMA}/tn)."
    )
else:
    payoff       = np.maximum(precios - STRIKE, 0)
    y_con        = payoff - PRIMA
    y_sin        = np.zeros_like(precios)
    precio_piso  = -PRIMA
    breakeven    = STRIKE + PRIMA
    y_spot_con   = max(PRECIO_SPOT - STRIKE, 0) - PRIMA
    y_spot_sin   = 0.0
    itm_otm      = "ITM" if PRECIO_SPOT > STRIKE else "OTM"
    diff_strike  = abs(PRECIO_SPOT - STRIKE)
    y_label      = f"Ganancia / Pérdida ({UNIDAD})"
    titulo_op    = f"Posición Alcista — Call Comprado | Vto. {MES}"
    explicacion  = (
        f"La posición consiste en un Call comprado sobre {INSTRUMENTO} con strike en "
        f"${STRIKE:.0f}/tn y vencimiento en {MES}. El cliente paga una prima de ${PRIMA}/tn "
        f"para participar de una suba del mercado por encima de ${STRIKE:.0f}/tn. "
        f"La pérdida máxima se limita a la prima pagada: ${PRIMA}/tn. "
        f"El punto de equilibrio se alcanza cuando el precio supera ${breakeven:.1f}/tn. "
        f"La opción está actualmente {itm_otm} en ${diff_strike:.0f}/tn, "
        f"con el futuro de {MES} en ${PRECIO_SPOT:.0f}/tn."
    )


# ════════════════════════════════════════════════════════════
# FUNCIÓN: generar figura matplotlib (usada para preview y PDF)
# ════════════════════════════════════════════════════════════
def generar_figura():
    fig = plt.figure(figsize=(13.0, 8.5), facecolor=VC_BLANCO)
    ax_chart = fig.add_axes([0.06, 0.20, 0.57, 0.59])
    ax_info  = fig.add_axes([0.67, 0.20, 0.29, 0.59])

    # ── Gráfico principal ────────────────────────────────────
    ax = ax_chart
    ax.set_facecolor(VC_GRIS_FONDO)
    ax.grid(True, color=VC_BLANCO, linewidth=1.1, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']:
        ax.spines[sp].set_color('#CCCCCC')
        ax.spines[sp].set_linewidth(0.8)

    # Área sombreada
    if TIPO == "put":
        ax.fill_between(precios, y_sin, y_con, where=(y_con >= y_sin),
                        color=VC_VERDE, alpha=0.13, zorder=1, label="Zona de protección")
    else:
        ax.fill_between(precios, 0, y_con, where=(y_con > 0),
                        color=VC_VERDE, alpha=0.13, zorder=1, label="Zona de ganancia")
        ax.fill_between(precios, y_con, 0, where=(y_con < 0),
                        color=VC_AMARILLO, alpha=0.10, zorder=1, label="Zona de pérdida")

    # Líneas
    if TIPO == "put":
        ax.plot(precios, y_sin, color=VC_GRIS_LIN, linewidth=2.0, linestyle='--',
                label='Sin cobertura', zorder=3)
    else:
        ax.axhline(0, color=VC_GRIS_LIN, linewidth=2.0, linestyle='--',
                   label='Referencia (sin posición)', zorder=3)

    ax.plot(precios, y_con, color=VC_VERDE, linewidth=2.8, linestyle='-',
            label=f"Con {TIPO.capitalize()} ${STRIKE:.0f} | Prima ${PRIMA}", zorder=4)

    ax.axvline(PRECIO_SPOT, color=VC_AMARILLO,  linewidth=1.5, linestyle=':', alpha=0.85, zorder=2)
    ax.axvline(STRIKE,      color=VC_VERDE_OSC, linewidth=1.5, linestyle=':', alpha=0.60, zorder=2)

    ax.scatter([PRECIO_SPOT], [y_spot_con], color=VC_VERDE,    s=55, zorder=5)
    ax.scatter([PRECIO_SPOT], [y_spot_sin], color=VC_GRIS_LIN, s=55, zorder=5)

    # Helper anotaciones
    def anotar(texto, xy, xytext, color):
        ax.annotate(texto, xy=xy, xytext=xytext,
                    fontsize=8.5, fontweight='bold', color=color,
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
                    bbox=dict(boxstyle='round,pad=0.3', fc=VC_BLANCO, ec=color, alpha=0.95, lw=1.0))

    _off = (precio_max - precio_min) * 0.10
    anotar(f'Spot actual\n${PRECIO_SPOT:.0f}/tn',
           xy=(PRECIO_SPOT, y_spot_sin),
           xytext=(PRECIO_SPOT + (precio_max - precio_min)*0.04, y_spot_sin - _off),
           color=VC_AMARILLO)

    _idx  = np.argmin(np.abs(precios - STRIKE))
    _ymid = (y_con[_idx] + y_sin[_idx]) / 2
    anotar(f'Strike\n${STRIKE:.0f}/tn',
           xy=(STRIKE, _ymid),
           xytext=(STRIKE - (precio_max - precio_min)*0.15, _ymid + _off * 0.8),
           color=VC_VERDE_OSC)

    if TIPO == "put":
        ax.hlines(precio_piso, precio_min, STRIKE,
                  colors=VC_VERDE, linewidths=1.1, linestyles=':', alpha=0.55, zorder=2)
        anotar(f'Piso: ${precio_piso:.1f}/tn',
               xy=(precio_min + (STRIKE - precio_min)*0.25, precio_piso),
               xytext=(precio_min + (STRIKE - precio_min)*0.25, precio_piso - _off * 0.9),
               color=VC_VERDE)
    else:
        ax.axvline(breakeven, color=VC_VERDE, linewidth=1.2, linestyle='-.', alpha=0.6, zorder=2)
        anotar(f'Breakeven\n${breakeven:.1f}/tn',
               xy=(breakeven, 0),
               xytext=(breakeven + (precio_max - precio_min)*0.04, _off * 0.5),
               color=VC_VERDE)

    _xe = precio_max + (precio_max - precio_min) * 0.01
    if TIPO == "put":
        ax.text(_xe, y_sin[-1],  'Sin cobertura',      fontsize=8.5, color=VC_GRIS_LIN,
                fontweight='bold', va='center', clip_on=False)
        ax.text(_xe, y_con[-1],  f'Con Put\n−${PRIMA}/tn', fontsize=8.5, color=VC_VERDE,
                fontweight='bold', va='center', clip_on=False)
    else:
        ax.text(_xe, y_con[-1], f'P&L Call\n−${PRIMA}/tn', fontsize=8.5, color=VC_VERDE,
                fontweight='bold', va='center', clip_on=False)

    ax.set_xlabel(f'Precio {INSTRUMENTO} {MES} ({UNIDAD})', fontsize=10, color=VC_NEGRO, labelpad=8)
    ax.set_ylabel(y_label, fontsize=10, color=VC_NEGRO, labelpad=8)
    ax.set_xlim(precio_min, precio_max + (precio_max - precio_min)*0.13)
    ax.tick_params(colors='#555555', labelsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f'${y:.0f}'))
    ax.legend(loc='upper left', fontsize=8.5, frameon=True, framealpha=0.95,
              edgecolor='#DDDDDD', facecolor=VC_BLANCO)

    # ── Panel derecho de métricas ────────────────────────────
    ax_info.set_facecolor(VC_BLANCO)
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)
    ax_info.axis('off')

    ax_info.add_patch(mpatches.FancyBboxPatch(
        (0.04, 0.02), 0.92, 0.96,
        boxstyle="round,pad=0.02",
        facecolor=VC_GRIS_FONDO, edgecolor=VC_VERDE_OSC,
        linewidth=1.2, zorder=0, transform=ax_info.transAxes))

    ax_info.text(0.50, 0.94, "RESUMEN DE POSICIÓN", transform=ax_info.transAxes,
                 fontsize=9, fontweight='bold', color=VC_VERDE_OSC, ha='center', va='top')
    ax_info.plot([0.06, 0.94], [0.91, 0.91], color=VC_VERDE_OSC,
                 linewidth=0.8, transform=ax_info.transAxes, clip_on=False)

    metricas = [
        ("Instrumento",     f"{INSTRUMENTO} {MES}"),
        ("Tipo",            f"{TIPO.upper()} COMPRADO"),
        ("Precio Spot",     f"${PRECIO_SPOT:.2f}/tn"),
        ("Strike",          f"${STRIKE:.2f}/tn"),
        ("Prima pagada",    f"${PRIMA:.2f}/tn"),
        ("─" * 18,          "─" * 10),
        ("Estado",          f"{itm_otm} en ${diff_strike:.1f}/tn"),
    ]
    if TIPO == "put":
        metricas += [("Piso garantizado", f"${precio_piso:.2f}/tn"),
                     ("Costo al alza",    f"-${PRIMA:.2f}/tn")]
    else:
        metricas += [("Breakeven",        f"${breakeven:.2f}/tn"),
                     ("Pérdida máxima",   f"-${PRIMA:.2f}/tn"),
                     ("Ganancia máxima",  "Ilimitada")]

    for i, (k, v) in enumerate(metricas):
        y_pos   = 0.87 - i * (0.78 / len(metricas))
        is_sep  = k.startswith("─")
        c_k = VC_NEGRO if not is_sep else '#BBBBBB'
        c_v = VC_VERDE_OSC if not is_sep else '#BBBBBB'
        fw  = 'bold' if k in ("Piso garantizado", "Breakeven") else 'normal'
        c_v = VC_VERDE if k in ("Piso garantizado", "Breakeven") else c_v
        ax_info.text(0.10, y_pos, k, transform=ax_info.transAxes,
                     fontsize=8.3, color=c_k, va='top', fontfamily='monospace')
        ax_info.text(0.92, y_pos, v, transform=ax_info.transAxes,
                     fontsize=8.3, color=c_v, va='top', ha='right',
                     fontweight=fw, fontfamily='monospace')

    badge_color = VC_VERDE if itm_otm == "ITM" else VC_AMARILLO
    ax_info.add_patch(mpatches.FancyBboxPatch(
        (0.18, 0.025), 0.64, 0.065,
        boxstyle="round,pad=0.01",
        facecolor=badge_color, edgecolor='none',
        transform=ax_info.transAxes, zorder=5))
    ax_info.text(0.50, 0.058, f"  Opción {itm_otm} | ${diff_strike:.0f}/tn del strike  ",
                 transform=ax_info.transAxes, fontsize=8.5, color=VC_BLANCO,
                 ha='center', va='center', fontweight='bold', zorder=6)

    # ── Header ──────────────────────────────────────────────
    fig.add_artist(mpatches.FancyBboxPatch(
        (0.0, 0.865), 1.0, 0.135, boxstyle="square,pad=0",
        facecolor=VC_VERDE_OSC, edgecolor='none',
        transform=fig.transFigure, zorder=10, clip_on=False))
    fig.text(0.035, 0.953, "VALCEREAL",
             fontsize=16, fontweight='bold', color=VC_BLANCO,
             transform=fig.transFigure, va='top', zorder=11)
    fig.text(0.035, 0.913, "Asesoramiento Financiero",
             fontsize=8.5, color='#AADDCC',
             transform=fig.transFigure, va='top', zorder=11)
    fig.text(0.50, 0.948, titulo_op,
             fontsize=13, fontweight='bold', color=VC_BLANCO,
             transform=fig.transFigure, va='top', ha='center', zorder=11)
    hoy = date.today().strftime("%d/%m/%Y")
    fig.text(0.965, 0.953, CLIENTE,
             fontsize=9.5, color=VC_BLANCO, fontweight='bold',
             transform=fig.transFigure, va='top', ha='right', zorder=11)
    fig.text(0.965, 0.913, hoy,
             fontsize=8.5, color='#AADDCC',
             transform=fig.transFigure, va='top', ha='right', zorder=11)

    # ── Footer con análisis ──────────────────────────────────
    fig.add_artist(mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 0.185, boxstyle="square,pad=0",
        facecolor=VC_GRIS_FONDO, edgecolor='none',
        transform=fig.transFigure, zorder=0, clip_on=False))
    fig.add_artist(plt.Line2D(
        [0.035, 0.965], [0.182, 0.182], transform=fig.transFigure,
        color=VC_VERDE_OSC, linewidth=0.8, zorder=5))
    fig.text(0.035, 0.173, "ANÁLISIS DE LA POSICIÓN",
             fontsize=8.5, fontweight='bold', color=VC_VERDE_OSC,
             transform=fig.transFigure, va='top', zorder=5)
    for i, line in enumerate(textwrap.wrap(explicacion, width=155)[:3]):
        fig.text(0.035, 0.155 - i * 0.038, line, fontsize=8.3, color=VC_NEGRO,
                 transform=fig.transFigure, va='top', zorder=5)
    fig.text(0.035, 0.015,
             f"Valcereal  ·  Análisis orientativo, no constituye asesoramiento de inversión  ·  {hoy}",
             fontsize=7.5, color='#999999', transform=fig.transFigure, va='bottom', zorder=5)

    plt.tight_layout(rect=[0, 0.04, 1, 0.90])
    return fig


# ════════════════════════════════════════════════════════════
# FUNCIÓN: exportar figura a bytes PDF
# ════════════════════════════════════════════════════════════
def figura_a_pdf(fig) -> bytes:
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        pdf.savefig(fig, bbox_inches='tight', facecolor=VC_BLANCO)
    buf.seek(0)
    return buf.read()


# ════════════════════════════════════════════════════════════
# MAIN — Header + métricas rápidas + gráfico + descarga
# ════════════════════════════════════════════════════════════

# Header de la página
st.markdown(f"""
<div class="vc-header">
  <span style="font-size:1.7rem; font-weight:800; color:white; letter-spacing:1px;">VALCEREAL</span>
  <span style="font-size:1rem; color:#AADDCC; margin-left:1rem;">Coberturas — Analizador de Opciones Agro</span>
</div>
""", unsafe_allow_html=True)

# Métricas rápidas en la parte superior
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Instrumento", f"{INSTRUMENTO} {MES}")
with col2:
    st.metric("Tipo", f"{TIPO.upper()} Comprado")
with col3:
    st.metric("Spot actual", f"${PRECIO_SPOT:.2f}/tn")
with col4:
    val_key = "Piso garantizado" if TIPO == "put" else "Breakeven"
    val_num = (STRIKE - PRIMA) if TIPO == "put" else (STRIKE + PRIMA)
    st.metric(val_key, f"${val_num:.2f}/tn")
with col5:
    badge = f"{'🟢' if itm_otm == 'ITM' else '🟡'} {itm_otm}  (${diff_strike:.0f}/tn del strike)"
    st.metric("Estado opción", badge)

st.markdown("---")

# Gráfico (se regenera automáticamente ante cualquier cambio de inputs)
with st.spinner("Actualizando gráfico..."):
    fig = generar_figura()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.markdown("---")

# Sección de descarga
st.markdown("#### 📄 Exportar One-Pager")
col_txt, col_btn = st.columns([2, 1])
with col_txt:
    st.markdown(
        f"**{CLIENTE}** · {INSTRUMENTO} {MES} · {TIPO.upper()} ${STRIKE:.0f} | Prima ${PRIMA}  \n"
        f"*Generado el {date.today().strftime('%d/%m/%Y')}*"
    )
with col_btn:
    fig_dl   = generar_figura()
    pdf_bytes = figura_a_pdf(fig_dl)
    plt.close(fig_dl)

    nombre_pdf = (
        f"Valcereal_{INSTRUMENTO}_{TIPO.upper()}_{MES.replace(' ', '_')}_"
        f"{CLIENTE.replace(' ', '_')}.pdf"
    )
    st.download_button(
        label="⬇ Descargar PDF",
        data=pdf_bytes,
        file_name=nombre_pdf,
        mime="application/pdf",
    )

# Explicación al pie
with st.expander("📝 Ver análisis de la posición"):
    st.write(explicacion)
