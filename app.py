# ============================================================
#   VALCEREAL — Coberturas  v2.0
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
    initial_sidebar_state="collapsed",
)

# ── Colores Valcereal ────────────────────────────────────────
VC_VERDE      = "#009B67"
VC_VERDE_OSC  = "#0B5641"
VC_AMARILLO   = "#C9A030"
VC_GRIS_LIN   = "#8A8A8A"
VC_GRIS_FONDO = "#F4F6F4"
VC_BLANCO     = "#FFFFFF"
VC_NEGRO      = "#1A1A1A"
VC_ROJO       = "#C0392B"

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background-color: {VC_GRIS_FONDO}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{ background-color: {VC_VERDE_OSC}; }}
  [data-testid="stSidebar"] * {{ color: white !important; }}

  /* Cabeceras de sección */
  .seccion {{
    background-color: {VC_VERDE_OSC};
    color: white !important;
    padding: 0.45rem 0.9rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.95rem;
    margin: 0.8rem 0 0.6rem 0;
  }}

  /* Botón Calcular */
  [data-testid="stFormSubmitButton"] button {{
    background-color: {VC_VERDE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    margin-top: 0.5rem;
  }}
  [data-testid="stFormSubmitButton"] button:hover {{
    background-color: {VC_VERDE_OSC} !important;
  }}

  /* Botón descarga */
  [data-testid="stDownloadButton"] button {{
    background-color: {VC_VERDE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 0.6rem 1rem !important;
  }}

  /* Métricas */
  [data-testid="metric-container"] {{
    background-color: white;
    border-left: 4px solid {VC_VERDE};
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem 0'>
      <p style='font-size:1.4rem; font-weight:800; color:white; margin:0'>VALCEREAL</p>
      <p style='color:#AADDCC; font-size:0.8rem; margin:0'>Asesoramiento Financiero</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    **Cómo usar:**
    1. Completá los datos del cliente
    2. Ingresá el futuro de referencia
    3. Configurá la opción
    4. Hacé clic en **Calcular posición**
    """)
    st.markdown("---")
    st.caption(f"v2.0  ·  {date.today().strftime('%d/%m/%Y')}")

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div style="background-color:{VC_VERDE_OSC}; padding:1.1rem 1.8rem;
            border-radius:8px; margin-bottom:1.5rem;">
  <span style="font-size:1.7rem; font-weight:800; color:white; letter-spacing:1px;">
    VALCEREAL
  </span>
  <span style="font-size:1rem; color:#AADDCC; margin-left:1rem;">
    Coberturas — Analizador de Opciones Agro
  </span>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FORMULARIO DE INPUTS
# ════════════════════════════════════════════════════════════
with st.form("form_posicion"):

    # ── Sección 1: Cliente ───────────────────────────────────
    st.markdown('<div class="seccion">👤 &nbsp; Cliente</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        CLIENTE     = st.text_input("Nombre del cliente", value="Productor Agropecuario",
                                    placeholder="Ej: Juan García")
    with c2:
        PRODUCTO    = st.selectbox("Producto", options=["Soja", "Maíz", "Trigo"])
    with c3:
        PRECIO_SPOT = st.number_input("Precio spot (USD/tn)", value=323.0,
                                      step=0.5, format="%.2f", min_value=1.0)

    # ── Sección 2: Futuros ───────────────────────────────────
    st.markdown('<div class="seccion">📈 &nbsp; Futuro de referencia</div>', unsafe_allow_html=True)
    c4, c5, _ = st.columns([1, 1, 2])
    with c4:
        MES         = st.selectbox("Mes de vencimiento",
                                   options=["Mayo", "Julio", "Septiembre", "Diciembre", "Marzo"])
    with c5:
        PRECIO_FUT  = st.number_input("Precio del futuro (USD/tn)", value=315.0,
                                      step=0.5, format="%.2f", min_value=1.0)

    # ── Sección 3: Opción ────────────────────────────────────
    st.markdown(
        '<div class="seccion">⚙️ &nbsp; Opción &nbsp;'
        '<span style="font-weight:400; font-size:0.83rem;">'
        '(mismo mes de vencimiento)</span></div>',
        unsafe_allow_html=True
    )
    c6, c7, c8, c9 = st.columns(4)
    with c6:
        TIPO        = st.selectbox("Tipo",     options=["Put", "Call"])
    with c7:
        POSICION    = st.selectbox("Posición", options=["Compra", "Venta"])
    with c8:
        STRIKE      = st.number_input("Strike (USD/tn)", value=315.0,
                                      step=0.5, format="%.2f", min_value=1.0)
    with c9:
        PRIMA       = st.number_input("Prima (USD/tn)", value=3.5,
                                      step=0.05, format="%.2f", min_value=0.01)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Botón ────────────────────────────────────────────────
    submitted = st.form_submit_button("📊  Calcular posición", use_container_width=True)


# ════════════════════════════════════════════════════════════
# RESULTADOS (solo tras hacer clic en Calcular)
# ════════════════════════════════════════════════════════════
if not submitted:
    st.markdown(
        f"<p style='color:{VC_GRIS_LIN}; text-align:center; margin-top:2rem;'>"
        "Completá el formulario y hacé clic en <b>Calcular posición</b> para ver el análisis.</p>",
        unsafe_allow_html=True
    )
    st.stop()


# ── Cálculos ─────────────────────────────────────────────────
TIPO     = TIPO.lower()      # "put" / "call"
POSICION = POSICION.lower()  # "compra" / "venta"

precio_min = min(PRECIO_SPOT, STRIKE, PRECIO_FUT) * 0.78
precio_max = max(PRECIO_SPOT, STRIKE, PRECIO_FUT) * 1.22
precios    = np.linspace(precio_min, precio_max, 600)
UNIDAD     = "USD/tn"
año_actual = date.today().year

# ── Lógica de payoffs por los 4 casos ───────────────────────
if TIPO == "put" and POSICION == "compra":
    # Productor compra put → piso garantizado
    payoff      = np.maximum(STRIKE - precios, 0)
    y_con       = precios + payoff - PRIMA         # precio efectivo venta
    y_sin       = precios                           # sin cobertura = vende a spot
    precio_clave = STRIKE - PRIMA                  # piso
    nombre_clave = "Piso garantizado"
    breakeven    = STRIKE - PRIMA
    y_spot_con  = PRECIO_SPOT + max(STRIKE - PRECIO_SPOT, 0) - PRIMA
    y_spot_sin  = PRECIO_SPOT
    itm_otm     = "OTM" if PRECIO_SPOT > STRIKE else "ITM"
    y_label     = f"Precio Efectivo de Venta ({UNIDAD})"
    titulo_op   = f"Cobertura a la Baja — Put Comprado | {MES} {año_actual}"
    color_zona  = VC_VERDE
    zona_label  = "Zona de protección"
    perdida_max = PRIMA
    ganancia_txt = "Ilimitada al alza (menos la prima)"
    explicacion = (
        f"{CLIENTE} adquirió un Put sobre {PRODUCTO} con strike en ${STRIKE:.0f}/tn "
        f"y vencimiento en {MES}. La prima pagada fue de ${PRIMA}/tn, lo que garantiza "
        f"un precio mínimo de venta de ${precio_clave:.1f}/tn independientemente de cuánto "
        f"caiga el mercado. La opción se encuentra {itm_otm} con el futuro de {MES} "
        f"en ${PRECIO_FUT:.0f}/tn. Si el precio sube, el productor participa de la suba "
        f"descontando únicamente la prima pagada."
    )

elif TIPO == "put" and POSICION == "venta":
    # Vende un put → cobra prima, asume obligación de compra si cae
    payoff      = np.maximum(STRIKE - precios, 0)
    y_con       = PRIMA - payoff                   # P&L del vendedor del put
    y_sin       = np.zeros_like(precios)
    precio_clave = STRIKE - PRIMA                  # breakeven (donde P&L = 0)
    nombre_clave = "Breakeven"
    breakeven    = STRIKE - PRIMA
    y_spot_con  = PRIMA - max(STRIKE - PRECIO_SPOT, 0)
    y_spot_sin  = 0.0
    itm_otm     = "OTM" if PRECIO_SPOT > STRIKE else "ITM"
    y_label     = f"Ganancia / Pérdida ({UNIDAD})"
    titulo_op   = f"Put Vendido — Prima Cobrada | {MES} {año_actual}"
    color_zona  = VC_AMARILLO
    zona_label  = "Zona de ganancia"
    perdida_max = f"Ilimitada a la baja (desde ${breakeven:.1f}/tn)"
    ganancia_txt = f"Limitada a la prima: ${PRIMA}/tn"
    explicacion = (
        f"{CLIENTE} vendió un Put sobre {PRODUCTO} con strike en ${STRIKE:.0f}/tn "
        f"y vencimiento en {MES}, cobrando una prima de ${PRIMA}/tn. Al vender el put, "
        f"el cliente asume la obligación de comprar {PRODUCTO} a ${STRIKE:.0f}/tn si el "
        f"precio cae por debajo de ese nivel. La ganancia máxima es la prima cobrada "
        f"(${PRIMA}/tn) y se obtiene cuando el precio finaliza por encima del strike. "
        f"El breakeven se ubica en ${breakeven:.1f}/tn; por debajo, la posición genera pérdidas."
    )

elif TIPO == "call" and POSICION == "compra":
    # Compra un call → apuesta alcista, pérdida máxima = prima
    payoff      = np.maximum(precios - STRIKE, 0)
    y_con       = payoff - PRIMA                   # P&L neto
    y_sin       = np.zeros_like(precios)
    precio_clave = STRIKE + PRIMA                  # breakeven
    nombre_clave = "Breakeven"
    breakeven    = STRIKE + PRIMA
    y_spot_con  = max(PRECIO_SPOT - STRIKE, 0) - PRIMA
    y_spot_sin  = 0.0
    itm_otm     = "ITM" if PRECIO_SPOT > STRIKE else "OTM"
    y_label     = f"Ganancia / Pérdida ({UNIDAD})"
    titulo_op   = f"Posición Alcista — Call Comprado | {MES} {año_actual}"
    color_zona  = VC_VERDE
    zona_label  = "Zona de ganancia"
    perdida_max = PRIMA
    ganancia_txt = "Ilimitada al alza"
    explicacion = (
        f"{CLIENTE} adquirió un Call sobre {PRODUCTO} con strike en ${STRIKE:.0f}/tn "
        f"y vencimiento en {MES}, pagando una prima de ${PRIMA}/tn. Esta posición permite "
        f"participar de una suba del mercado por encima de ${STRIKE:.0f}/tn con pérdida "
        f"máxima limitada a la prima pagada. El punto de equilibrio se alcanza cuando el "
        f"precio supera ${breakeven:.1f}/tn. Con el futuro de {MES} en ${PRECIO_FUT:.0f}/tn, "
        f"la opción se encuentra {itm_otm} en ${abs(PRECIO_FUT - STRIKE):.0f}/tn del strike."
    )

else:  # call + venta
    # Vende un call → cobra prima, cede el upside por encima del strike
    payoff      = np.maximum(precios - STRIKE, 0)
    y_con       = PRIMA - payoff                   # P&L del vendedor del call
    y_sin       = np.zeros_like(precios)
    precio_clave = STRIKE + PRIMA                  # donde empiezan las pérdidas
    nombre_clave = "Cap / Breakeven"
    breakeven    = STRIKE + PRIMA
    y_spot_con  = PRIMA - max(PRECIO_SPOT - STRIKE, 0)
    y_spot_sin  = 0.0
    itm_otm     = "ITM" if PRECIO_SPOT > STRIKE else "OTM"
    y_label     = f"Ganancia / Pérdida ({UNIDAD})"
    titulo_op   = f"Call Vendido — Prima Cobrada | {MES} {año_actual}"
    color_zona  = VC_AMARILLO
    zona_label  = "Zona de ganancia"
    perdida_max = f"Ilimitada al alza (desde ${breakeven:.1f}/tn)"
    ganancia_txt = f"Limitada a la prima: ${PRIMA}/tn"
    explicacion = (
        f"{CLIENTE} vendió un Call sobre {PRODUCTO} con strike en ${STRIKE:.0f}/tn "
        f"y vencimiento en {MES}, cobrando una prima de ${PRIMA}/tn. Al vender el call, "
        f"cede el upside por encima del strike a cambio de ingresar la prima. "
        f"La ganancia máxima es ${PRIMA}/tn (prima cobrada) y se mantiene mientras "
        f"el precio finalice por debajo de ${STRIKE:.0f}/tn. "
        f"Por encima de ${breakeven:.1f}/tn la posición genera pérdidas ilimitadas."
    )

diff_strike = abs(PRECIO_FUT - STRIKE)


# ── Métricas rápidas ─────────────────────────────────────────
st.markdown("---")
m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    st.metric("Producto",     f"{PRODUCTO} {MES}")
with m2:
    st.metric("Opción",       f"{TIPO.upper()} {POSICION.upper()}")
with m3:
    st.metric("Futuro ref.",  f"${PRECIO_FUT:.2f}/tn")
with m4:
    st.metric("Strike",       f"${STRIKE:.2f}/tn")
with m5:
    st.metric(nombre_clave,   f"${precio_clave:.2f}/tn")
with m6:
    badge = f"{'🟢' if itm_otm == 'ITM' else '🟡'} {itm_otm}  (${diff_strike:.1f}/tn)"
    st.metric("Estado opción", badge)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FUNCIÓN: generar figura matplotlib
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

    # Áreas sombreadas
    ax.fill_between(precios, y_sin, y_con,
                    where=(y_con >= y_sin),
                    color=color_zona, alpha=0.13, zorder=1, label=zona_label)
    if POSICION == "venta":
        ax.fill_between(precios, y_con, y_sin,
                        where=(y_con < y_sin),
                        color=VC_ROJO, alpha=0.10, zorder=1, label="Zona de pérdida")

    # Línea de referencia
    lbl_ref = "Sin cobertura" if TIPO == "put" and POSICION == "compra" else "Referencia (sin posición)"
    if TIPO == "put" and POSICION == "compra":
        ax.plot(precios, y_sin, color=VC_GRIS_LIN, linewidth=2.0,
                linestyle='--', label=lbl_ref, zorder=3)
    else:
        ax.axhline(0, color=VC_GRIS_LIN, linewidth=2.0,
                   linestyle='--', label=lbl_ref, zorder=3)

    # Línea de la opción
    lbl_op = f"{TIPO.capitalize()} {POSICION.capitalize()} ${STRIKE:.0f} | Prima ${PRIMA}"
    ax.plot(precios, y_con, color=color_zona if POSICION == "compra" else VC_AMARILLO,
            linewidth=2.8, linestyle='-', label=lbl_op, zorder=4)

    # Líneas verticales
    ax.axvline(PRECIO_SPOT, color=VC_AMARILLO,  linewidth=1.3, linestyle=':', alpha=0.85, zorder=2)
    ax.axvline(PRECIO_FUT,  color=VC_VERDE_OSC, linewidth=1.3, linestyle=':', alpha=0.65, zorder=2)
    ax.axvline(STRIKE,      color=VC_GRIS_LIN,  linewidth=1.0, linestyle=':', alpha=0.45, zorder=2)

    # Puntos en precio actual
    ax.scatter([PRECIO_SPOT], [y_spot_con], color=color_zona if POSICION == "compra" else VC_AMARILLO,
               s=55, zorder=5)
    ax.scatter([PRECIO_SPOT], [y_spot_sin], color=VC_GRIS_LIN, s=55, zorder=5)

    # Anotaciones
    def anotar(texto, xy, xytext, color):
        ax.annotate(texto, xy=xy, xytext=xytext,
                    fontsize=8.2, fontweight='bold', color=color,
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.1),
                    bbox=dict(boxstyle='round,pad=0.3', fc=VC_BLANCO, ec=color, alpha=0.95, lw=1.0))

    _off = (precio_max - precio_min) * 0.10

    # Spot
    anotar(f'Spot\n${PRECIO_SPOT:.0f}/tn',
           xy=(PRECIO_SPOT, y_spot_sin),
           xytext=(PRECIO_SPOT + (precio_max - precio_min)*0.04, y_spot_sin - _off),
           color=VC_AMARILLO)

    # Futuro
    _idx_fut  = np.argmin(np.abs(precios - PRECIO_FUT))
    _y_fut_sin = y_sin[_idx_fut]
    anotar(f'Futuro {MES}\n${PRECIO_FUT:.0f}/tn',
           xy=(PRECIO_FUT, _y_fut_sin),
           xytext=(PRECIO_FUT - (precio_max - precio_min)*0.18, _y_fut_sin + _off * 0.7),
           color=VC_VERDE_OSC)

    # Strike + precio clave
    if TIPO == "put" and POSICION == "compra":
        ax.hlines(precio_clave, precio_min, STRIKE,
                  colors=VC_VERDE, linewidths=1.1, linestyles=':', alpha=0.55, zorder=2)
        anotar(f'{nombre_clave}\n${precio_clave:.1f}/tn',
               xy=(precio_min + (STRIKE - precio_min)*0.25, precio_clave),
               xytext=(precio_min + (STRIKE - precio_min)*0.25, precio_clave - _off * 0.9),
               color=VC_VERDE)
    else:
        ax.axvline(precio_clave, color=color_zona, linewidth=1.2, linestyle='-.', alpha=0.6, zorder=2)
        _idx_be  = np.argmin(np.abs(precios - precio_clave))
        anotar(f'{nombre_clave}\n${precio_clave:.1f}/tn',
               xy=(precio_clave, y_con[_idx_be]),
               xytext=(precio_clave + (precio_max - precio_min)*0.04, y_con[_idx_be] + _off * 0.5),
               color=color_zona)

    # Etiquetas al borde derecho
    _xe = precio_max + (precio_max - precio_min) * 0.01
    _color_linea = color_zona if POSICION == "compra" else VC_AMARILLO
    ax.text(_xe, y_con[-1],  lbl_op.split('|')[0].strip(), fontsize=8.2,
            color=_color_linea, fontweight='bold', va='center', clip_on=False)

    # Ejes
    ax.set_xlabel(f'Precio {PRODUCTO} {MES} ({UNIDAD})', fontsize=10, color=VC_NEGRO, labelpad=8)
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
        (0.04, 0.02), 0.92, 0.96, boxstyle="round,pad=0.02",
        facecolor=VC_GRIS_FONDO, edgecolor=VC_VERDE_OSC,
        linewidth=1.2, zorder=0, transform=ax_info.transAxes))

    ax_info.text(0.50, 0.94, "RESUMEN DE POSICIÓN", transform=ax_info.transAxes,
                 fontsize=9, fontweight='bold', color=VC_VERDE_OSC, ha='center', va='top')
    ax_info.plot([0.06, 0.94], [0.91, 0.91], color=VC_VERDE_OSC,
                 linewidth=0.8, transform=ax_info.transAxes, clip_on=False)

    perdida_str = f"-${perdida_max}/tn" if isinstance(perdida_max, (int, float)) else str(perdida_max)
    metricas = [
        ("Producto",          f"{PRODUCTO} {MES}"),
        ("Tipo",              f"{TIPO.upper()} {POSICION.upper()}"),
        ("Precio Spot",       f"${PRECIO_SPOT:.2f}/tn"),
        ("Futuro referencia", f"${PRECIO_FUT:.2f}/tn"),
        ("Strike",            f"${STRIKE:.2f}/tn"),
        ("Prima",             f"${PRIMA:.2f}/tn"),
        ("─" * 18,            "─" * 10),
        ("Estado",            f"{itm_otm}  ${diff_strike:.1f}/tn del strike"),
        (nombre_clave,        f"${precio_clave:.2f}/tn"),
        ("Pérdida máxima",    perdida_str),
        ("Ganancia máxima",   ganancia_txt if isinstance(ganancia_txt, str) else f"${ganancia_txt}/tn"),
    ]

    for i, (k, v) in enumerate(metricas):
        y_pos  = 0.87 - i * (0.78 / len(metricas))
        is_sep = k.startswith("─")
        c_k    = VC_NEGRO if not is_sep else '#BBBBBB'
        c_v    = VC_VERDE_OSC if not is_sep else '#BBBBBB'
        fw     = 'normal'
        if k == nombre_clave:
            c_v = VC_VERDE; fw = 'bold'
        if k == "Pérdida máxima":
            c_v = VC_ROJO
        ax_info.text(0.10, y_pos, k, transform=ax_info.transAxes,
                     fontsize=7.8, color=c_k, va='top', fontfamily='monospace')
        ax_info.text(0.92, y_pos, v, transform=ax_info.transAxes,
                     fontsize=7.8, color=c_v, va='top', ha='right',
                     fontweight=fw, fontfamily='monospace')

    badge_color = VC_VERDE if itm_otm == "ITM" else VC_AMARILLO
    ax_info.add_patch(mpatches.FancyBboxPatch(
        (0.12, 0.025), 0.76, 0.065, boxstyle="round,pad=0.01",
        facecolor=badge_color, edgecolor='none',
        transform=ax_info.transAxes, zorder=5))
    ax_info.text(0.50, 0.058, f"Opción {itm_otm}  ·  ${diff_strike:.0f}/tn del strike",
                 transform=ax_info.transAxes, fontsize=8.3, color=VC_BLANCO,
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

    # ── Footer / Análisis ────────────────────────────────────
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

    return fig


# ── Renderizar gráfico ────────────────────────────────────────
with st.spinner("Generando análisis..."):
    fig = generar_figura()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.markdown("---")

# ── Descarga PDF ──────────────────────────────────────────────
st.markdown("#### 📄 Exportar One-Pager")
col_desc, col_btn = st.columns([3, 1])
with col_desc:
    st.markdown(
        f"**{CLIENTE}** &nbsp;·&nbsp; {PRODUCTO} {MES} &nbsp;·&nbsp; "
        f"{TIPO.upper()} {POSICION.upper()} — Strike ${STRIKE:.0f} | Prima ${PRIMA}  \n"
        f"*Generado el {date.today().strftime('%d/%m/%Y')}*"
    )
with col_btn:
    fig_dl    = generar_figura()
    buf       = io.BytesIO()
    with PdfPages(buf) as pdf:
        pdf.savefig(fig_dl, bbox_inches='tight', facecolor=VC_BLANCO)
    buf.seek(0)
    plt.close(fig_dl)

    nombre_pdf = (
        f"Valcereal_{PRODUCTO}_{TIPO.upper()}_{POSICION.capitalize()}_"
        f"{MES}_{CLIENTE.replace(' ', '_')}.pdf"
    )
    st.download_button(
        label="⬇  Descargar PDF",
        data=buf.read(),
        file_name=nombre_pdf,
        mime="application/pdf",
    )

# ── Análisis expandible ───────────────────────────────────────
with st.expander("📝 Ver análisis completo de la posición"):
    st.write(explicacion)
