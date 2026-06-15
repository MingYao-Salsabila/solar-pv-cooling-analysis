# ☀️ Solar PV Temperature vs Output Analysis Dashboard

Interactive Streamlit dashboard for analysing solar PV performance:
standard panels vs water-cooled panels across multi-day measurements.

## Folder structure

```
solar_dashboard/
├── app.py                  ← main Streamlit application
├── requirements.txt        ← Python dependencies
├── .streamlit/
│   └── config.toml         ← theme + server settings
└── README.md
```

---

## Run locally

### Option A — inside your existing conda env (py311-core)

```bat
conda activate py311-core
streamlit run app.py
```

### Option B — fresh venv

```bat
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

Opens automatically at **http://localhost:8501**

---

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a **GitHub repository** (public or private).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **"New app"**.
4. Set:
   - **Repository** — your repo
   - **Branch** — `main`
   - **Main file path** — `app.py`  (or `solar_dashboard/app.py` if in a sub-folder)
5. Click **"Deploy!"** — Streamlit installs `requirements.txt` automatically.

Your app will be live at:
`https://<your-username>-<repo>-<hash>.streamlit.app`

---

## Features

| Tab | Description |
|-----|-------------|
| 📈 Multi-Day Power Output | Line chart — Standard vs Cooled power by day and hour |
| 📊 Relative Power Gain | Scatter — gain (%) vs temperature, bubble size = Lux |
| 🌡️ Thermal Loss Comparison | Grouped bar — thermal losses per measurement |
| ⏱️ Time-Series Stability | Dual-line — intra-day stability comparison |
| ⚡ Performance Simulator | Bar chart — predicted output at chosen temp/irradiance |
| 🔬 Engineering Formula Analysis | Formula reference + 18-row engineering metrics table |
| 📋 Experimental Dataset | Full filtered dataframe with computed columns |

**Sidebar controls** (auto-reactive — no button needed):
- Weather filter: Sunny / Cloudy checkboxes
- Ambient Temperature slider: 20 – 60 °C
- Solar Irradiance slider: 100 – 1 200 W/m²

**KPI strip** (12 metrics, updated on every slider move):
Avg power, relative gain, irradiance, fill factors, efficiencies,
weather loss, cooling gain, inverter η, battery capacity.

---

## Requirements

| Package | Min version |
|---------|------------|
| streamlit | 1.32.0 |
| numpy | 1.24.0 |
| pandas | 2.0.0 |
| matplotlib | 3.7.0 |

Python 3.8 or newer.
