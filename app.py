# ============================================================
#   VALCEREAL — Coberturas  v3.0
#   Analizador de Opciones Agro · Streamlit Web App
# ============================================================

import io
import textwrap
from datetime import date

import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

# Paleta para múltiples operaciones
COLORES_OPS = ["#009B67", "#2E86C1", "#8E44AD", "#E67E22", "#E74C3C", "#17A589"]

MESES_VALIDOS = ["Mayo", "Julio", "Septiembre", "Diciembre", "Marzo"]

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background-color: {VC_GRIS_FONDO}; }}
  [data-testid="stSidebar"] {{ background-color: {VC_VERDE_OSC}; }}
  [data-testid="stSidebar"] * {{ color: white !important; }}

  .seccion {{
    background-color: {VC_VERDE_OSC};
    color: white !important;
    padding: 0.45rem 0.9rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.95rem;
    margin: 1rem 0 0.5rem 0;
  }}
  .hint {{
    font-size: 0.8rem;
    color: {VC_GRIS_LIN};
    margin-top: -0.3rem;
    margin-bottom: 0.5rem;
  }}

  /* Botón Calcular */
  div[data-testid="stButton"] > button[kind="primary"] {{
    background-color: {VC_VERDE} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    margin-top: 0.8rem;
  }}
  div[data-testid="stButton"] > button[kind="primary"]:hover {{
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
    2. Agregá los futuros de referencia
    3. Cargá una o más opciones
    4. Hacé clic en **Calcular posición**
    """)
    st.markdown("---")
    st.caption(f"v3.0  ·  {date.today().strftime('%d/%m/%Y')}")

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
# SECCIÓN 1 — Cliente
# ════════════════════════════════════════════════════════════
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

# ════════════════════════════════════════════════════════════
# SECCIÓN 2 — Futuros (tabla dinámica)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="seccion">📈 &nbsp; Futuros de referencia</div>',
            unsafe_allow_html=True)
st.markdown('<p class="hint">Podés agregar múltiples contratos de futuros. '
            'Usá el botón ＋ al final de la tabla.</p>', unsafe_allow_html=True)

futuros_default = pd.DataFrame({
    "Mes":             ["Mayo"],
    "Precio (USD/tn)": [315.0],
})

futuros_df = st.data_editor(
    futuros_default,
    num_rows="dynamic",
    use_container_width=True,
    key="futuros_editor",
    column_config={
        "Mes": st.column_config.SelectboxColumn(
            "Mes de vencimiento",
            options=MESES_VALIDOS,
            required=True,
            width="medium",
        ),
        "Precio (USD/tn)": st.column_config.NumberColumn(
            "Precio del futuro (USD/tn)",
            min_value=1.0, step=0.5, format="%.2f",
            required=True,
            width="medium",
        ),
    },
    hide_index=True,
    column_order=["Mes", "Precio (USD/tn)"],
)

# ════════════════════════════════════════════════════════════
# SECCIÓN 3 — Opciones (tabla dinámica)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="seccion">⚙️ &nbsp; Opciones &nbsp;'
            '<span style="font-weight:400; font-size:0.83rem;">'
            '(mismo mes de vencimiento que el futuro)</span></div>',
            unsafe_allow_html=True)
st.markdown('<p class="hint">Cargá una o más opciones. '
            'Usá el botón ＋ para agregar filas.</p>', unsafe_allow_html=True)

opciones_default = pd.DataFrame({
    "Tipo":            ["Put"],
    "Posición":        ["Compra"],
    "Strike (USD/tn)": [315.0],
    "Prima (USD/tn)":  [3.5],
})

opciones_df = st.data_editor(
    opciones_default,
    num_rows="dynamic",
    use_container_width=True,
    key="opciones_editor",
    column_config={
        "Tipo": st.column_config.SelectboxColumn(
            "Tipo", options=["Put", "Call"],
            required=True, width="small",
        ),
        "Posición": st.column_config.SelectboxColumn(
            "Posición", options=["Compra", "Venta"],
            required=True, width="small",
        ),
        "Strike (USD/tn)": st.column_config.NumberColumn(
            "Strike (USD/tn)", min_value=1.0, step=0.5, format="%.2f",
            required=True, width="medium",
        ),
        "Prima (USD/tn)": st.column_config.NumberColumn(
            "Prima (USD/tn)", min_value=0.01, step=0.05, format="%.2f",
            required=True, width="medium",
        ),
    },
    hide_index=True,
    column_order=["Tipo", "Posición", "Strike (USD/tn)", "Prima (USD/tn)"],
)

# ── Botón Calcular ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
calcular = st.button("📊  Calcular posición", type="primary", use_container_width=True)

if calcular:
    # Validar que haya al menos una opción completa
    ops_validas = opciones_df.dropna(subset=["Tipo", "Posición", "Strike (USD/tn)", "Prima (USD/tn)"])
    if len(ops_validas) == 0:
        st.error("⚠  Ingresá al menos una opción completa para calcular.")
        st.stop()

    # Guardar inputs en session_state para que persistan si el usuario edita la tabla
    st.session_state["mostrar"]  = True
    st.session_state["snapshot"] = {
        "cliente":     CLIENTE,
        "producto":    PRODUCTO,
        "precio_spot": PRECIO_SPOT,
        "futuros":     futuros_df.dropna().to_dict("records"),
        "opciones":    ops_validas.to_dict("records"),
        "fecha":       date.today().strftime("%d/%m/%Y"),
    }

# ════════════════════════════════════════════════════════════
# RESULTADOS
# ════════════════════════════════════════════════════════════
if not st.session_state.get("mostrar", False):
    st.markdown(
        f"<p style='color:{VC_GRIS_LIN}; text-align:center; margin-top:2rem;'>"
        "Completá el formulario y hacé clic en <b>Calcular posición</b>.</p>",
        unsafe_allow_html=True
    )
    st.stop()

snap     = st.session_state["snapshot"]
futuros  = snap["futuros"]
opciones = snap["opciones"]
CLIENTE  = snap["cliente"]
PRODUCTO = snap["producto"]
PRECIO_SPOT = snap["precio_spot"]
UNIDAD   = "USD/tn"

# Determinar mes de la primera opción/futuro para el título
primer_mes = futuros[0]["Mes"] if futuros else "—"
año_actual = date.today().year

# ── Rango de precios ─────────────────────────────────────────
todos_precios_ref = (
    [PRECIO_SPOT] +
    [f["Precio (USD/tn)"] for f in futuros] +
    [o["Strike (USD/tn)"] for o in opciones]
)
precio_min = min(todos_precios_ref) * 0.78
precio_max = max(todos_precios_ref) * 1.22
precios    = np.linspace(precio_min, precio_max, 600)

# ── Calcular P&L de cada opción ──────────────────────────────
op_lines   = []   # (y_array, label, color, tipo, posicion, strike, prima)
y_combined = np.zeros_like(precios)

for i, op in enumerate(opciones):
    tipo     = str(op["Tipo"]).lower()
    posicion = str(op["Posición"]).lower()
    K        = float(op["Strike (USD/tn)"])
    P        = float(op["Prima (USD/tn)"])
    color    = COLORES_OPS[i % len(COLORES_OPS)]

    if tipo == "put" and posicion == "compra":
        y_op  = np.maximum(K - precios, 0) - P
        label = f"Put Compra  K=${K:.0f}  P=${P}"
        clave_txt = f"Piso: ${K - P:.1f}/tn"
    elif tipo == "put" and posicion == "venta":
        y_op  = P - np.maximum(K - precios, 0)
        label = f"Put Venta   K=${K:.0f}  P=+${P}"
        clave_txt = f"Breakeven: ${K - P:.1f}/tn"
    elif tipo == "call" and posicion == "compra":
        y_op  = np.maximum(precios - K, 0) - P
        label = f"Call Compra K=${K:.0f}  P=${P}"
        clave_txt = f"Breakeven: ${K + P:.1f}/tn"
    else:  # call venta
        y_op  = P - np.maximum(precios - K, 0)
        label = f"Call Venta  K=${K:.0f}  P=+${P}"
        clave_txt = f"Cap: ${K + P:.1f}/tn"

    y_combined += y_op
    op_lines.append((y_op, label, color, tipo, posicion, K, P, clave_txt))

# Estadísticas de la posición combinada
max_gain   = float(y_combined.max())
max_loss   = float(y_combined.min())
prima_neta = sum(
    (-o["Prima (USD/tn)"] if str(o["Posición"]).lower() == "compra" else o["Prima (USD/tn)"])
    for o in opciones
)

# Breakevens numéricos (cruces con cero)
zero_crossings = []
for j in range(len(y_combined) - 1):
    if y_combined[j] * y_combined[j + 1] < 0:
        x0, x1 = precios[j], precios[j + 1]
        y0, y1 = y_combined[j], y_combined[j + 1]
        zero_crossings.append(x0 - y0 * (x1 - x0) / (y1 - y0))

be_str = "  /  ".join(f"${x:.1f}" for x in zero_crossings) if zero_crossings else "No hay en el rango"

# ── Texto de análisis ─────────────────────────────────────────
n_ops = len(opciones)
if n_ops == 1:
    op = opciones[0]
    tipo = str(op["Tipo"]).lower()
    pos  = str(op["Posición"]).lower()
    K    = float(op["Strike (USD/tn)"])
    P    = float(op["Prima (USD/tn)"])
    if tipo == "put" and pos == "compra":
        explicacion = (
            f"{CLIENTE} adquirió un Put sobre {PRODUCTO} con strike en ${K:.0f}/tn "
            f"y vencimiento en {primer_mes}, pagando una prima de ${P}/tn. "
            f"Esta cobertura garantiza un precio mínimo de venta de ${K - P:.1f}/tn, "
            f"independientemente de cuánto caiga el mercado. "
            f"Si los precios suben, el productor participa de la suba descontando únicamente la prima."
        )
    elif tipo == "put" and pos == "venta":
        explicacion = (
            f"{CLIENTE} vendió un Put sobre {PRODUCTO} con strike en ${K:.0f}/tn, "
            f"cobrando una prima de ${P}/tn. Asume la obligación de comprar {PRODUCTO} "
            f"a ${K:.0f}/tn si el precio cae por debajo de ese nivel. "
            f"La ganancia máxima es la prima cobrada (${P}/tn) cuando el precio finaliza sobre el strike. "
            f"El breakeven se ubica en ${K - P:.1f}/tn."
        )
    elif tipo == "call" and pos == "compra":
        explicacion = (
            f"{CLIENTE} adquirió un Call sobre {PRODUCTO} con strike en ${K:.0f}/tn, "
            f"pagando una prima de ${P}/tn. Esta posición permite participar de una suba "
            f"por encima de ${K:.0f}/tn con pérdida máxima limitada a la prima. "
            f"El punto de equilibrio se alcanza en ${K + P:.1f}/tn."
        )
    else:
        explicacion = (
            f"{CLIENTE} vendió un Call sobre {PRODUCTO} con strike en ${K:.0f}/tn, "
            f"cobrando una prima de ${P}/tn. Cede el upside por encima del strike a cambio "
            f"de ingresar la prima. La ganancia máxima es ${P}/tn. "
            f"Por encima de ${K + P:.1f}/tn la posición genera pérdidas ilimitadas."
        )
else:
    bullet_lines = []
    for op in opciones:
        tipo = str(op["Tipo"]).lower()
        pos  = str(op["Posición"]).lower()
        K    = float(op["Strike (USD/tn)"])
        P    = float(op["Prima (USD/tn)"])
        signo = "-" if pos == "compra" else "+"
        bullet_lines.append(
            f"{op['Tipo'].upper()} {op['Posición'].capitalize()} — "
            f"Strike ${K:.0f}/tn | Prima {signo}${P}/tn."
        )
    bullets = "  ·  ".join(bullet_lines)
    be_display = be_str if zero_crossings else "no hay breakeven en el rango simulado"
    explicacion = (
        f"{CLIENTE} estructuró una posición en derivados de {PRODUCTO} vto. {primer_mes} "
        f"con {n_ops} operaciones: {bullets}  "
        f"Prima neta: {'−' if prima_neta < 0 else '+'}"
        f"${abs(prima_neta):.2f}/tn.  "
        f"Breakeven(s): {be_display}."
    )

# ── Métricas rápidas ─────────────────────────────────────────
st.markdown("---")
n_fut = len(futuros)
col_count = min(3 + n_ops, 6)
m_cols = st.columns(col_count)
m_cols[0].metric("Producto", f"{PRODUCTO}")
m_cols[1].metric("Operaciones", f"{n_ops} opción{'es' if n_ops > 1 else ''}")
m_cols[2].metric("Prima neta", f"{'−' if prima_neta < 0 else '+'}${abs(prima_neta):.2f}/tn")
if len(m_cols) > 3 and zero_crossings:
    m_cols[3].metric("Breakeven", f"${zero_crossings[0]:.1f}/tn")
if len(m_cols) > 4:
    m_cols[4].metric("Máx. ganancia", f"${max_gain:.2f}/tn")
if len(m_cols) > 5:
    m_cols[5].metric("Máx. pérdida", f"${max_loss:.2f}/tn")

st.caption(f"Resultados al {snap['fecha']}. Cambiá los inputs y volvé a calcular para actualizar.")
st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# FUNCIÓN: generar figura matplotlib
# ════════════════════════════════════════════════════════════
def generar_figura():
    fig = plt.figure(figsize=(13.0, 9.0), facecolor=VC_BLANCO)

    # ── Posiciones exactas: subir el chart para dejar espacio al footer ──
    ax_chart = fig.add_axes([0.06, 0.28, 0.56, 0.54])   # bottom=28% (era 20%)
    ax_info  = fig.add_axes([0.67, 0.28, 0.29, 0.54])

    # ── Gráfico ──────────────────────────────────────────────
    ax = ax_chart
    ax.set_facecolor(VC_GRIS_FONDO)
    ax.grid(True, color=VC_BLANCO, linewidth=1.1, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']:
        ax.spines[sp].set_color('#CCCCCC')
        ax.spines[sp].set_linewidth(0.8)

    # Línea de referencia (cero)
    ax.axhline(0, color=VC_GRIS_LIN, linewidth=1.8, linestyle='--',
               label='Sin posición (ref.)', zorder=2, alpha=0.7)

    # Área combinada
    ax.fill_between(precios, 0, y_combined,
                    where=(y_combined >= 0), color=VC_VERDE,  alpha=0.10, zorder=1)
    ax.fill_between(precios, y_combined, 0,
                    where=(y_combined < 0),  color=VC_ROJO,   alpha=0.10, zorder=1)

    # Curvas individuales (si hay más de 1 opción)
    if len(op_lines) > 1:
        for y_op, label, color, *_ in op_lines:
            ax.plot(precios, y_op, color=color, linewidth=1.4,
                    linestyle=':', alpha=0.65, label=label, zorder=3)

    # Curva combinada
    lbl_combined = "P&L combinado" if n_ops > 1 else op_lines[0][1]
    color_combined = VC_VERDE_OSC if n_ops > 1 else op_lines[0][2]
    ax.plot(precios, y_combined, color=color_combined, linewidth=2.8,
            linestyle='-', label=lbl_combined, zorder=4)

    # Línea vertical: spot actual
    ax.axvline(PRECIO_SPOT, color=VC_AMARILLO, linewidth=1.4,
               linestyle=':', alpha=0.90, zorder=2)

    # Líneas verticales: futuros
    for fut in futuros:
        pf   = float(fut["Precio (USD/tn)"])
        mes  = fut["Mes"]
        ax.axvline(pf, color=VC_VERDE_OSC, linewidth=1.2,
                   linestyle=':', alpha=0.55, zorder=2)
        idx  = np.argmin(np.abs(precios - pf))
        ypos = y_combined[idx]
        ax.annotate(
            f"Fut. {mes}\n${pf:.0f}/tn",
            xy=(pf, ypos),
            xytext=(pf - (precio_max - precio_min) * 0.14, ypos + (y_combined.max() - y_combined.min()) * 0.12),
            fontsize=7.5, fontweight='bold', color=VC_VERDE_OSC,
            arrowprops=dict(arrowstyle='->', color=VC_VERDE_OSC, lw=1.0),
            bbox=dict(boxstyle='round,pad=0.25', fc=VC_BLANCO, ec=VC_VERDE_OSC, alpha=0.92, lw=0.9),
        )

    # Anotación spot
    y_spot = float(y_combined[np.argmin(np.abs(precios - PRECIO_SPOT))])
    _rng   = y_combined.max() - y_combined.min()
    ax.annotate(
        f"Spot\n${PRECIO_SPOT:.0f}/tn",
        xy=(PRECIO_SPOT, y_spot),
        xytext=(PRECIO_SPOT + (precio_max - precio_min) * 0.05, y_spot - _rng * 0.18),
        fontsize=7.5, fontweight='bold', color=VC_AMARILLO,
        arrowprops=dict(arrowstyle='->', color=VC_AMARILLO, lw=1.0),
        bbox=dict(boxstyle='round,pad=0.25', fc=VC_BLANCO, ec=VC_AMARILLO, alpha=0.92, lw=0.9),
    )

    # Breakeven(s)
    for xbe in zero_crossings[:2]:   # max 2 anotaciones
        ax.axvline(xbe, color=VC_GRIS_LIN, linewidth=0.9, linestyle='-.', alpha=0.5, zorder=2)
        ax.annotate(
            f"BE ${xbe:.1f}",
            xy=(xbe, 0),
            xytext=(xbe + (precio_max - precio_min) * 0.02, _rng * 0.08),
            fontsize=7.2, color=VC_GRIS_LIN,
            bbox=dict(boxstyle='round,pad=0.2', fc=VC_BLANCO, ec=VC_GRIS_LIN, alpha=0.85, lw=0.8),
        )

    ax.set_xlabel(f"Precio {PRODUCTO} {primer_mes} (USD/tn)", fontsize=10, color=VC_NEGRO, labelpad=10)
    ax.set_ylabel("P&L Derivados (USD/tn)", fontsize=10, color=VC_NEGRO, labelpad=8)
    ax.set_xlim(precio_min, precio_max + (precio_max - precio_min) * 0.08)
    ax.tick_params(colors='#555555', labelsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f'${y:.1f}'))
    ax.legend(loc='upper left', fontsize=7.8, frameon=True, framealpha=0.95,
              edgecolor='#DDDDDD', facecolor=VC_BLANCO, ncol=1)

    # ── Panel derecho ─────────────────────────────────────────
    ax_info.set_facecolor(VC_BLANCO)
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)
    ax_info.axis('off')

    ax_info.add_patch(mpatches.FancyBboxPatch(
        (0.04, 0.02), 0.92, 0.96, boxstyle="round,pad=0.02",
        facecolor=VC_GRIS_FONDO, edgecolor=VC_VERDE_OSC,
        linewidth=1.2, zorder=0, transform=ax_info.transAxes))

    ax_info.text(0.50, 0.94, "RESUMEN DE POSICIÓN",
                 transform=ax_info.transAxes, fontsize=8.8, fontweight='bold',
                 color=VC_VERDE_OSC, ha='center', va='top')
    ax_info.plot([0.06, 0.94], [0.91, 0.91], color=VC_VERDE_OSC,
                 linewidth=0.8, transform=ax_info.transAxes, clip_on=False)

    # Info del cliente y generales
    metricas_top = [
        ("Cliente",  CLIENTE[:22]),
        ("Producto", f"{PRODUCTO}  vto. {primer_mes}"),
        ("Spot",     f"${PRECIO_SPOT:.2f}/tn"),
        ("Prima neta", f"{'−' if prima_neta < 0 else '+'}${abs(prima_neta):.2f}/tn"),
        ("─" * 20,   "─" * 8),
    ]
    for fx, fut in enumerate(futuros[:3]):
        metricas_top.append((f"Futuro {fut['Mes'][:3]}.", f"${float(fut['Precio (USD/tn)']):.2f}/tn"))
    metricas_top.append(("─" * 20, "─" * 8))

    # Una línea por opción
    for ix, op in enumerate(opciones[:5]):   # máximo 5
        K     = float(op["Strike (USD/tn)"])
        P     = float(op["Prima (USD/tn)"])
        signo = "−" if str(op["Posición"]).lower() == "compra" else "+"
        metricas_top.append((
            f"{op['Tipo'].upper()[:4]} {op['Posición'][:3]}.  K${K:.0f}",
            f"P {signo}${P}"
        ))

    metricas_top += [
        ("─" * 20,       "─" * 8),
        ("Breakeven(s)", be_str if zero_crossings else "—"),
        ("Máx. ganancia", f"${max_gain:.2f}/tn"),
        ("Máx. pérdida",  f"${max_loss:.2f}/tn"),
    ]

    n = len(metricas_top)
    for i, (k, v) in enumerate(metricas_top):
        y_pos  = 0.88 - i * (0.80 / n)
        is_sep = k.startswith("─")
        c_k    = VC_NEGRO if not is_sep else '#BBBBBB'
        c_v    = VC_VERDE_OSC if not is_sep else '#BBBBBB'
        fw     = 'normal'
        if k == "Máx. pérdida":
            c_v = VC_ROJO
        if k in ("Breakeven(s)", "Máx. ganancia"):
            c_v = VC_VERDE; fw = 'bold'
        ax_info.text(0.08, y_pos, k, transform=ax_info.transAxes,
                     fontsize=7.5, color=c_k, va='top', fontfamily='monospace')
        ax_info.text(0.94, y_pos, v, transform=ax_info.transAxes,
                     fontsize=7.5, color=c_v, va='top', ha='right',
                     fontweight=fw, fontfamily='monospace')

    # ── Header de la figura ───────────────────────────────────
    titulo_op = (
        f"{'Estrategia de Cobertura' if n_ops > 1 else op_lines[0][1].split('K=')[0].strip()} "
        f"— {PRODUCTO} {primer_mes} {año_actual}"
    )
    fig.add_artist(mpatches.FancyBboxPatch(
        (0.0, 0.90), 1.0, 0.10, boxstyle="square,pad=0",
        facecolor=VC_VERDE_OSC, edgecolor='none',
        transform=fig.transFigure, zorder=10, clip_on=False))
    fig.text(0.035, 0.975, "VALCEREAL",
             fontsize=15, fontweight='bold', color=VC_BLANCO,
             transform=fig.transFigure, va='top', zorder=11)
    fig.text(0.035, 0.935, "Asesoramiento Financiero",
             fontsize=8, color='#AADDCC',
             transform=fig.transFigure, va='top', zorder=11)
    fig.text(0.50, 0.972, titulo_op,
             fontsize=12, fontweight='bold', color=VC_BLANCO,
             transform=fig.transFigure, va='top', ha='center', zorder=11)
    hoy = date.today().strftime("%d/%m/%Y")
    fig.text(0.965, 0.975, CLIENTE,
             fontsize=9, color=VC_BLANCO, fontweight='bold',
             transform=fig.transFigure, va='top', ha='right', zorder=11)
    fig.text(0.965, 0.935, hoy,
             fontsize=8, color='#AADDCC',
             transform=fig.transFigure, va='top', ha='right', zorder=11)

    # ── Footer / Análisis — bien separado del gráfico ─────────
    # Footer va de 0% a 24%; el chart empieza en 28% → gap de 4%
    fig.add_artist(mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 0.24, boxstyle="square,pad=0",
        facecolor=VC_GRIS_FONDO, edgecolor='none',
        transform=fig.transFigure, zorder=0, clip_on=False))
    fig.add_artist(plt.Line2D(
        [0.035, 0.965], [0.235, 0.235], transform=fig.transFigure,
        color=VC_VERDE_OSC, linewidth=0.8, zorder=5))

    fig.text(0.035, 0.224, "ANÁLISIS DE LA POSICIÓN",
             fontsize=8.5, fontweight='bold', color=VC_VERDE_OSC,
             transform=fig.transFigure, va='top', zorder=5)

    for i, line in enumerate(textwrap.wrap(explicacion, width=155)[:3]):
        fig.text(0.035, 0.205 - i * 0.050, line,
                 fontsize=8.0, color=VC_NEGRO,
                 transform=fig.transFigure, va='top', zorder=5)

    fig.text(0.035, 0.018,
             f"Valcereal  ·  Análisis orientativo, no constituye asesoramiento de inversión  ·  {hoy}",
             fontsize=7.5, color='#999999',
             transform=fig.transFigure, va='bottom', zorder=5)

    return fig


# ── Renderizar en pantalla ────────────────────────────────────
with st.spinner("Generando análisis..."):
    fig = generar_figura()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.markdown("---")

# ── Descarga PDF ──────────────────────────────────────────────
st.markdown("#### 📄 Exportar One-Pager")
col_desc, col_btn = st.columns([3, 1])
with col_desc:
    ops_resumen = "  |  ".join(
        f"{o['Tipo'].upper()} {o['Posición'][:3]}. K${float(o['Strike (USD/tn)']):.0f}"
        for o in opciones
    )
    st.markdown(
        f"**{CLIENTE}** &nbsp;·&nbsp; {PRODUCTO} {primer_mes} &nbsp;·&nbsp; {ops_resumen}  \n"
        f"*Generado el {snap['fecha']}*"
    )
with col_btn:
    fig_dl = generar_figura()
    buf    = io.BytesIO()
    with PdfPages(buf) as pdf:
        pdf.savefig(fig_dl, bbox_inches='tight', facecolor=VC_BLANCO)
    buf.seek(0)
    plt.close(fig_dl)

    nombre_pdf = (
        f"Valcereal_{PRODUCTO}_{primer_mes}_"
        f"{CLIENTE.replace(' ', '_')}_"
        f"{date.today().strftime('%Y%m%d')}.pdf"
    )
    st.download_button(
        label="⬇  Descargar PDF",
        data=buf.read(),
        file_name=nombre_pdf,
        mime="application/pdf",
    )

with st.expander("📝 Ver análisis completo"):
    st.write(explicacion)
