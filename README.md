# Eurozone Liquidity Stress Index (ELSI)

ELSI is a Streamlit dashboard that converts Eurozone market and banking data into a 0-100 liquidity stress indicator for commercial-bank treasury and balance-sheet risk monitoring.

The dashboard combines four monthly indicators:

- Excess reserves
- Overnight short rate (€STR / spliced EONIA)
- German 10-year government bond yield
- Loan-to-deposit ratio

## Features

Use the sidebar to navigate between six sections:

1. **Executive Summary** - explains the treasury trade-off between liquidity protection and cash hoarding.
2. **Macro Theory Timeline** - summarizes Eurozone liquidity and monetary-policy regimes from 2004 to 2026.
3. **Benchmark Splicing** - documents the EONIA-to-€STR transition and the ECB's fixed -8.5 basis-point adjustment.
4. **Model Architecture** - describes the input pillars, rolling normalization, composite score, and risk tiers.
5. **Live ELSI Dashboard** - plots the historical ELSI trajectory with selectable year ranges, risk bands, and major event annotations.
6. **Stress Simulator & Pillar Inspector** - applies preset or custom shocks to estimate their effect on the current ELSI score.

## Risk tiers

| Score | Classification | Interpretation |
| ---: | --- | --- |
| 0-25 | Normal | Accommodative liquidity conditions |
| 25-50 | Friction | Mild interbank tightening |
| 50-75 | Tightening Alert | Elevated funding friction |
| 75-100 | Systemic Stress | Acute liquidity squeeze |

## Model calculation

Each input is standardized using a 12-month rolling z-score. Excess reserves are inverted so that lower reserves produce a higher stress contribution:

```text
Z_ER  = -(excess_reserves - rolling_mean) / rolling_std
Z_i   =  (input_i - rolling_mean) / rolling_std
```

The four standardized pillars receive equal weight. Their average is mapped through the standard normal cumulative distribution function to produce the bounded ELSI score:

```text
Composite_Z = (Z_ER + Z_SR + Z_GY + Z_LTD) / 4
ELSI_Score  = NormalCDF(Composite_Z) * 100
```

The first 11 months do not have a complete 12-month rolling window and are excluded from the displayed results.

## Requirements

- Python 3.13 or later
- Streamlit
- NumPy
- pandas
- SciPy
- Plotly

Install the runtime dependencies with:

```bash
python -m pip install streamlit numpy pandas scipy plotly
```

## Data files

Place the following files in the project root, alongside `app.py`:

- `ELSI_Framework_A.csv` - historical input data used by the dashboard
- `ELSI_Framework_B.csv` - companion framework dataset included with the project

`app.py` currently loads `ELSI_Framework_A.csv`. The file must contain these columns:

```text
excess_reserves
short_rate
govt_yield_10y
ltd_ratio_calc
```

The first column should contain parseable monthly dates and is used as the DataFrame index.

## Run the dashboard

From the project root:

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally `http://localhost:8501`, which can be opened in a browser.

## Project structure

```text
.
├── app.py
├── ELSI_Framework_A.csv
├── ELSI_Framework_B.csv
├── pyproject.toml
├── README.md
└── src/
	└── python_project/
		├── __init__.py
		├── euro_liquidity.ipynb
		└── test.ipynb
```

## Notes

- The dashboard expects the CSV data files to be available from the project root or its parent directory.
- The stress simulator uses the latest available observation as its baseline and estimates the effect of shocks using the most recent 12 months of data.
- This project is an analytical early-warning tool, not a regulatory liquidity measurement or investment recommendation.
