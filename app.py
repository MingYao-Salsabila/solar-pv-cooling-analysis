"""
Solar PV Temperature vs Output Analysis Dashboard
Streamlit port of the original Tkinter desktop app.

Local run:
    pip install -r requirements.txt
    streamlit run app.py

Deploy (Streamlit Community Cloud):
    Push this folder to a GitHub repo, then connect it at share.streamlit.io.
    Set the main file to  app.py  — no other config required.
"""

# ---------------------------------------------------------------------------
# Backend must be set before pyplot is imported (needed in headless/cloud env)
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ── Page config (must be the very first Streamlit call) ─────────────────────
st.set_page_config(
    page_title="Solar PV Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════
# DATASET
# ═══════════════════════════════════════════════════════════════════════════
_RAW = [
    {"Day": 1, "Time": 11, "Temperature_Standard": 41, "Temperature_Cooled": 35, "Power_Standard": 19.68, "Power_Cooled": 19.16, "Weather": "Sunny",  "Lux": 4341},
    {"Day": 1, "Time": 12, "Temperature_Standard": 36, "Temperature_Cooled": 36, "Power_Standard": 14.74, "Power_Cooled": 93.57, "Weather": "Sunny",  "Lux": 2423},
    {"Day": 1, "Time": 13, "Temperature_Standard": 45, "Temperature_Cooled": 40, "Power_Standard": 16.39, "Power_Cooled": 23.25, "Weather": "Sunny",  "Lux": 5493},
    {"Day": 1, "Time": 14, "Temperature_Standard": 49, "Temperature_Cooled": 37, "Power_Standard": 51.33, "Power_Cooled": 31.31, "Weather": "Sunny",  "Lux": 7430},
    {"Day": 1, "Time": 15, "Temperature_Standard": 45, "Temperature_Cooled": 34, "Power_Standard":  1.28, "Power_Cooled": 25.61, "Weather": "Sunny",  "Lux": 6445},
    {"Day": 2, "Time": 11, "Temperature_Standard": 50, "Temperature_Cooled": 40, "Power_Standard":  9.81, "Power_Cooled": 23.65, "Weather": "Sunny",  "Lux": 1475},
    {"Day": 2, "Time": 12, "Temperature_Standard": 51, "Temperature_Cooled": 41, "Power_Standard": 10.07, "Power_Cooled": 56.49, "Weather": "Sunny",  "Lux": 1011},
    {"Day": 2, "Time": 13, "Temperature_Standard": 40, "Temperature_Cooled": 36, "Power_Standard": 51.14, "Power_Cooled": 23.96, "Weather": "Cloudy", "Lux": 1358},
    {"Day": 2, "Time": 14, "Temperature_Standard": 41, "Temperature_Cooled": 35, "Power_Standard": 25.79, "Power_Cooled": 73.19, "Weather": "Cloudy", "Lux": 2172},
    {"Day": 2, "Time": 15, "Temperature_Standard": 32, "Temperature_Cooled": 29, "Power_Standard":  3.75, "Power_Cooled": 16.91, "Weather": "Cloudy", "Lux": 1055},
    {"Day": 3, "Time": 11, "Temperature_Standard": 41, "Temperature_Cooled": 36, "Power_Standard": 57.95, "Power_Cooled": 81.26, "Weather": "Cloudy", "Lux": 1820},
    {"Day": 3, "Time": 12, "Temperature_Standard": 45, "Temperature_Cooled": 36, "Power_Standard": 19.51, "Power_Cooled": 16.11, "Weather": "Sunny",  "Lux": 1019},
    {"Day": 3, "Time": 13, "Temperature_Standard": 44, "Temperature_Cooled": 40, "Power_Standard": 24.79, "Power_Cooled": 15.72, "Weather": "Sunny",  "Lux":  176},
    {"Day": 3, "Time": 14, "Temperature_Standard": 49, "Temperature_Cooled": 39, "Power_Standard": 39.29, "Power_Cooled": 36.71, "Weather": "Sunny",  "Lux": 2771},
    {"Day": 3, "Time": 15, "Temperature_Standard": 49, "Temperature_Cooled": 39, "Power_Standard": 41.44, "Power_Cooled": 35.13, "Weather": "Sunny",  "Lux": 1713},
]

df = pd.DataFrame(_RAW)


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
ALPHA   = 0.004
T_REF   = 25
P_RATED = 50.0
R       = 0.5


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def safe_div(num, den):
    """Division that returns NaN instead of raising ZeroDivisionError."""
    try:
        if den in (0, 0.0) or np.isnan(float(den)):
            return np.nan
        return num / den
    except (TypeError, ValueError):
        return np.nan


def thermal_loss(temp):
    return ALPHA * (temp - T_REF) * P_RATED


def fmt(v, decimals=3):
    """Format a scalar for display; NaN → 'N/A', n==0 → int."""
    try:
        fv = float(v)
        if np.isnan(fv):
            return "N/A"
        r = round(fv, decimals)
        return int(r) if decimals == 0 else r
    except (TypeError, ValueError):
        return "N/A"


def compute_df(weather_filter):
    out = df[df["Weather"].isin(weather_filter)].copy().sort_values(["Day", "Time"])
    out["Relative_Power_Gain"] = np.where(
        out["Power_Standard"] != 0,
        (out["Power_Cooled"] - out["Power_Standard"]) / out["Power_Standard"] * 100,
        np.nan,
    )
    out["Thermal_Loss_Standard"] = ALPHA * (out["Temperature_Standard"] - T_REF) * P_RATED
    out["Thermal_Loss_Cooled"]   = ALPHA * (out["Temperature_Cooled"]   - T_REF) * P_RATED
    out["Estimated_Irradiance"]  = out["Lux"] * 0.0079
    return out


# ═══════════════════════════════════════════════════════════════════════════
# CHART BUILDERS  (each returns a Figure; caller must plt.close() it)
# ═══════════════════════════════════════════════════════════════════════════
def build_power_chart(fdf):
    fig, ax = plt.subplots(figsize=(9, 5))
    for day in sorted(fdf["Day"].unique()):
        d = fdf[fdf["Day"] == day].sort_values("Time")
        ax.plot(d["Time"], d["Power_Standard"], marker="o", label=f"Day {day} – Standard")
        ax.plot(d["Time"], d["Power_Cooled"],   marker="o", label=f"Day {day} – Cooled")
    ax.set_xlabel("Time (hour)")
    ax.set_ylabel("Power Output (W)")
    ax.set_title("Multi-Day Power Output")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def build_gain_chart(fdf):
    fig, ax = plt.subplots(figsize=(9, 5))
    for weather in sorted(fdf["Weather"].unique()):
        d = fdf[fdf["Weather"] == weather]
        sizes = np.clip(d["Lux"] / 15, 20, 250)
        ax.scatter(d["Temperature_Standard"], d["Relative_Power_Gain"],
                   s=sizes, alpha=0.8, label=weather)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Relative Power Gain (%)")
    ax.set_title("Relative Gain vs Standard Panel Temperature")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def build_thermal_chart(fdf):
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(fdf))
    w = 0.4
    ax.bar(x - w / 2, fdf["Thermal_Loss_Standard"], w, label="Standard Panel Loss")
    ax.bar(x + w / 2, fdf["Thermal_Loss_Cooled"],   w, label="Cooled Panel Loss")
    ax.set_xlabel("Measurement Index")
    ax.set_ylabel("Thermal Loss (W)")
    ax.set_title("Thermal Loss Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(fdf.index.astype(str), rotation=45)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def build_stability_chart(fdf):
    fig, ax = plt.subplots(figsize=(9, 5))
    for day in sorted(fdf["Day"].unique()):
        d = fdf[fdf["Day"] == day].sort_values("Time")
        ax.plot(d["Time"], d["Power_Standard"], marker="o",          label=f"Day {day} – Standard")
        ax.plot(d["Time"], d["Power_Cooled"],   marker="o", ls="--", label=f"Day {day} – Cooled")
    ax.set_xlabel("Time (hour)")
    ax.set_ylabel("Power Output (W)")
    ax.set_title("Time-Series Stability")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def build_sim_chart(pred_std, pred_cooled):
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(["Standard", "Cooled"], [pred_std, pred_cooled],
                  color=["steelblue", "seagreen"])
    ax.bar_label(bars, fmt="%.1f W", padding=3)
    ax.set_ylabel("Predicted Output (W)")
    ax.set_title("Real-Time Performance Simulation")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# FORMULA REFERENCE TEXT
# ═══════════════════════════════════════════════════════════════════════════
FORMULA_REF = """\
SUNNY CONDITIONS
  FF_sunny  = (Vmp x Imp) / (Voc x Isc)
  Pin_sunny = E_sunny x A
  Pout_sunny = Voc x Isc x FF_sunny
  eta_sunny = (Pout / Pin) x 100%

CLOUDY CONDITIONS
  FF_cloudy  = (Vmp x Imp) / (Voc x Isc)
  Pin_cloudy = E_cloudy x A   [E_cloudy = E_sunny x 0.65]
  eta_cloudy = (Pout / Pin) x 100%

STANDARD vs. COOLED
  Delta_P       = Pmax_Cooled - Pmax_Standard
  eta_gain      = (Delta_P / Pmax_Standard) x 100%
  Delta_T_cool  = T_Standard - T_Cooled

SYSTEM LEVEL
  eta_sys = eta_panel x eta_inv x eta_cables
  L_total = Ploss_thermal + L_cable + L_inverter + L_soiling + Ploss_mismatch

PLANT LEVEL
  PR   = (Actual Yield / Nominal Yield) x 100%
  LCOE = Total Cost / Total Lifetime Energy

BATTERY
  E_bat = (Daily Load x Autonomy) / (DoD x eta_battery)
  I_cc  = Isc_array x 1.25
"""


# ═══════════════════════════════════════════════════════════════════════════
# ENGINEERING METRICS COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════
def compute_formula_metrics(ambient_temp, irradiance, pred_std, pred_cooled, fdf):
    # ── IV parameters ─────────────────────────────────────────
    Voc_s, Isc_s, Vmp_s, Imp_s = 20.5, 2.81, 12.6, 2.69   # sunny
    Voc_c, Isc_c, Vmp_c, Imp_c = 19.4, 2.35, 11.8, 2.20   # cloudy
    A = 0.35  # panel area (m²)

    E_s = irradiance
    E_c = irradiance * 0.65   # irradiance under cloud

    FF_s = safe_div(Vmp_s * Imp_s, Voc_s * Isc_s)
    FF_c = safe_div(Vmp_c * Imp_c, Voc_c * Isc_c)

    Pin_s  = E_s * A;  Pout_s = Voc_s * Isc_s * FF_s
    Pin_c  = E_c * A;  Pout_c = Voc_c * Isc_c * FF_c

    Eff_s = safe_div(Pout_s, Pin_s) * 100
    Eff_c = safe_div(Pout_c, Pin_c) * 100

    Pmax_s_ = pred_std    if pred_std    > 0 else 50.0
    Pmax_c_ = pred_cooled if pred_cooled > 0 else 42.0

    # ── Loss components ───────────────────────────────────────
    Tp_s = ambient_temp
    Tp_c = ambient_temp - 2

    Pl_th_s  = thermal_loss(Tp_s)
    Pl_res_s = Isc_s ** 2 * R
    Pl_opt_s = 0.03 * Pin_s
    Pl_mis_s = 0.015 * Pmax_s_

    Pl_th_c  = thermal_loss(Tp_c)
    Pl_res_c = Isc_c ** 2 * R
    Pl_opt_c = 0.03 * Pin_c
    Pl_mis_c = 0.015 * Pmax_c_

    Pl_weather    = Pout_s - Pout_c
    Pl_degradation = 0.007 * P_RATED

    # ── Standard vs cooled (IV model) ─────────────────────────
    s_voc, s_isc, s_vmp, s_imp    = 20.5, 2.81, 12.6, 2.69
    co_voc, co_isc, co_vmp, co_imp = 21.0, 2.90, 13.1, 2.75
    Pmax_Std = s_vmp  * s_imp
    Pmax_Coo = co_vmp * co_imp
    Eta_gain = safe_div(Pmax_Coo - Pmax_Std, Pmax_Std) * 100

    # ── System-level metrics ──────────────────────────────────
    E_est   = df["Lux"].mean() * 0.0079
    gamma   = -0.0045
    P_actual = P_RATED * (1 + gamma * (ambient_temp - T_REF))

    eta_inv   = 0.94
    P_DC_in   = safe_div(pred_cooled, eta_inv)
    L_cable   = (12 ** 2 * 0.0175 * 10) / 4
    eta_panel  = (Eff_s / 100) if not np.isnan(Eff_s) else np.nan
    eta_cables = 1 - safe_div(L_cable, max(P_DC_in if not np.isnan(P_DC_in) else 1, 1))
    eta_sys    = eta_panel * eta_inv * eta_cables   # may be NaN
    L_total    = (Pl_th_s + L_cable
                  + (P_DC_in - pred_cooled if not np.isnan(P_DC_in) else 0)
                  + Pl_opt_s + 0.02 * (P_DC_in if not np.isnan(P_DC_in) else 0)
                  + Pl_mis_s)

    # ── Plant / battery constants ─────────────────────────────
    PR   = safe_div(120, 150) * 100
    CF   = safe_div(240, 15 * 24)
    Y_f  = safe_div(240, 15)
    Y_a  = safe_div(220, 15)
    LCOE = safe_div(12000, 35000)
    E_bat = safe_div(120 * 2, 0.8 * 0.9)
    I_cc  = 8.5 * 1.25

    # ── KPI summary dict ──────────────────────────────────────
    kpi = {
        "Avg Standard Power (W)": fmt(fdf["Power_Standard"].mean(), 2),
        "Avg Cooled Power (W)":   fmt(fdf["Power_Cooled"].mean(),   2),
        "Avg Relative Gain (%)":  fmt(fdf["Relative_Power_Gain"].mean(), 2),
        "Avg Lux":                fmt(fdf["Lux"].mean(), 0),
        "Sunny FF":               fmt(FF_s, 3),
        "Sunny η (%)":            fmt(Eff_s, 2),
        "Cloudy η (%)":           fmt(Eff_c, 2),
        "Weather Loss (W)":       fmt(Pl_weather, 2),
        "Cooling Gain (%)":       fmt(Eta_gain, 2),
        "Est. Irradiance (W/m²)": fmt(E_est, 2),
        "Inverter η (%)":         fmt(eta_inv * 100, 2),
        "Battery Cap (Wh)":       fmt(E_bat, 2),
    }

    # ── Detailed metrics table ────────────────────────────────
    eta_sys_pct = fmt(eta_sys * 100 if not np.isnan(eta_sys) else np.nan, 3)
    metrics_df = pd.DataFrame([
        {"Metric": "Ploss_thermal_sunny",    "Value": fmt(Pl_th_s),        "Unit": "W"},
        {"Metric": "Ploss_resistive_sunny",  "Value": fmt(Pl_res_s),       "Unit": "W"},
        {"Metric": "Ploss_optical_sunny",    "Value": fmt(Pl_opt_s),       "Unit": "W"},
        {"Metric": "Ploss_mismatch_sunny",   "Value": fmt(Pl_mis_s),       "Unit": "W"},
        {"Metric": "Ploss_thermal_cloudy",   "Value": fmt(Pl_th_c),        "Unit": "W"},
        {"Metric": "Ploss_resistive_cloudy", "Value": fmt(Pl_res_c),       "Unit": "W"},
        {"Metric": "Ploss_optical_cloudy",   "Value": fmt(Pl_opt_c),       "Unit": "W"},
        {"Metric": "Ploss_mismatch_cloudy",  "Value": fmt(Pl_mis_c),       "Unit": "W"},
        {"Metric": "Ploss_degradation",      "Value": fmt(Pl_degradation), "Unit": "W"},
        {"Metric": "P_actual",               "Value": fmt(P_actual),       "Unit": "W"},
        {"Metric": "eta_sys",                "Value": eta_sys_pct,          "Unit": "%"},
        {"Metric": "L_total",                "Value": fmt(L_total),        "Unit": "W"},
        {"Metric": "PR",                     "Value": fmt(PR),             "Unit": "%"},
        {"Metric": "CF",                     "Value": fmt(CF * 100),       "Unit": "%"},
        {"Metric": "Y_f",                    "Value": fmt(Y_f),            "Unit": "kWh/kWp"},
        {"Metric": "Y_a",                    "Value": fmt(Y_a),            "Unit": "kWh/kWp"},
        {"Metric": "LCOE",                   "Value": fmt(LCOE),           "Unit": "cost/kWh"},
        {"Metric": "I_cc",                   "Value": fmt(I_cc),           "Unit": "A"},
    ])

    return kpi, metrics_df


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR  (controls – Streamlit reruns automatically on every widget change)
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("☀️ Controls")

    st.markdown("**Weather Filter**")
    show_sunny  = st.checkbox("Sunny",  value=True)
    show_cloudy = st.checkbox("Cloudy", value=True)

    st.divider()

    ambient_temp = st.slider("Ambient Temperature (°C)", 20, 60, 35, step=1)
    irradiance   = st.slider("Solar Irradiance (W/m²)", 100, 1200, 800, step=10)

    st.divider()
    st.caption("Sliders update all charts automatically — no button needed.")


# ═══════════════════════════════════════════════════════════════════════════
# COMPUTE
# ═══════════════════════════════════════════════════════════════════════════
weather_choices = []
if show_sunny:
    weather_choices.append("Sunny")
if show_cloudy:
    weather_choices.append("Cloudy")
if not weather_choices:                  # guard: if neither is ticked, show all
    weather_choices = ["Sunny", "Cloudy"]

filtered_df = compute_df(weather_choices)

if filtered_df.empty:
    st.warning("No data matches the current filter. Adjust the weather checkboxes.")
    st.stop()

# Predicted power output from the simulator
base_eff_std    = 0.18
base_eff_cooled = 0.22
std_penalty    = max(0.0, ambient_temp - 25) * 0.005
cooled_penalty = max(0.0, ambient_temp - 25) * 0.0025

pred_standard = max(irradiance * (base_eff_std    - std_penalty),    0.0)
pred_cooled   = max(irradiance * (base_eff_cooled - cooled_penalty), 0.0)

kpi, metrics_df = compute_formula_metrics(
    ambient_temp, irradiance, pred_standard, pred_cooled, filtered_df
)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═══════════════════════════════════════════════════════════════════════════
st.title("☀️ Solar PV Temperature vs Output Analysis Dashboard")

# ── KPI strip (4 per row) ────────────────────────────────────────────────
kpi_items = list(kpi.items())
for row_start in range(0, len(kpi_items), 4):
    cols = st.columns(4)
    for col, (label, value) in zip(cols, kpi_items[row_start:row_start + 4]):
        col.metric(label, value)

st.divider()

# ── 7 tabs ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Multi-Day Power Output",
    "📊 Relative Power Gain",
    "🌡️ Thermal Loss Comparison",
    "⏱️ Time-Series Stability",
    "⚡ Performance Simulator",
    "🔬 Engineering Formula Analysis",
    "📋 Experimental Dataset",
])


def show_fig(fig):
    """Render a matplotlib figure then close it to free memory."""
    st.pyplot(fig)
    plt.close(fig)


with tab1:
    show_fig(build_power_chart(filtered_df))

with tab2:
    show_fig(build_gain_chart(filtered_df))

with tab3:
    show_fig(build_thermal_chart(filtered_df))

with tab4:
    show_fig(build_stability_chart(filtered_df))

with tab5:
    show_fig(build_sim_chart(pred_standard, pred_cooled))
    st.markdown(
        f"**Standard:** `{pred_standard:.1f} W`  ·  "
        f"**Cooled:** `{pred_cooled:.1f} W`  ·  "
        f"**Gain:** `{pred_cooled - pred_standard:+.1f} W`"
    )

with tab6:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Formula Reference")
        st.code(FORMULA_REF, language=None)
    with col_b:
        st.subheader("Engineering Metrics")
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

with tab7:
    st.subheader("Filtered Dataset")
    st.dataframe(
        filtered_df.reset_index(drop=True),
        use_container_width=True,
    )
    st.caption(f"{len(filtered_df)} rows · weather filter: {', '.join(weather_choices)}")
