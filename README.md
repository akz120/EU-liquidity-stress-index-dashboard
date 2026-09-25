# Eurozone Liquidity Stress Index (ELSI)

ELSI is a Streamlit dashboard and data pipeline for monitoring Eurozone banking-system liquidity stress. It combines market and balance-sheet indicators into a single 0–100 risk score that can be used to track short-term funding pressure and liquidity conditions for treasury and balance-sheet risk teams.

The model currently uses four monthly input pillars:

- excess reserves
- overnight short rate (€STR with EONIA splice)
- German 10-year sovereign yield
- loan-to-deposit ratio

The underlying data are retrieved through the official ECB Data Portal API and include Excess Reserves (ILM), €STR/EONIA (EST/FM), 10Y Sovereign Yields (YC), and banking aggregates used for the loan-to-deposit ratio. These series are assembled into monthly time series and normalized before being combined into the composite stress score.

## What's new in this version

This repository now includes both the interactive dashboard and the upstream data refresh workflow used to generate the framework datasets:

- `update_data.py` retrieves data through the official ECB Data Portal API, constructs the long-horizon and modern-framework CSVs, and saves:
  - `ELSI_Framework_A.csv`
  - `ELSI_Framework_B.csv`
- `ADF_test.py` runs stationarity diagnostics on both frameworks using Augmented Dickey-Fuller tests.
- `app.py` includes a six-section Streamlit workflow with the live ELSI dashboard and the policy-shock simulator.

## Dashboard features

The sidebar navigation includes six sections:

1. Executive Summary
2. Macro Theory Timeline
3. Benchmark Splicing
4. Model Architecture
5. Live ELSI Dashboard
6. Stress Simulator & Pillar Inspector

## Risk tiers

| Score | Classification | Interpretation |
| ---: | --- | --- |
| 0–25 | Normal | Accommodative liquidity conditions |
| 25–50 | Friction | Mild interbank tightening |
| 50–75 | Tightening Alert | Elevated funding friction |
| 75–100 | Systemic Stress | Acute liquidity squeeze |

## Model calculation

Each variable is standardized using a 12-month rolling z-score, expressing deviations from its recent local mean relative to local volatility. Excess reserves are inverted so that falling reserves raise stress:

```text
Z_ER  = -(excess_reserves - rolling_mean) / rolling_std
Z_i   =  (input_i - rolling_mean) / rolling_std
```

The four standardized pillars are averaged and mapped into a bounded stress score using the standard normal cumulative distribution function:

```text
Composite_Z = (Z_ER + Z_SR + Z_GY + Z_LTD) / 4
ELSI_Score  = NormalCDF(Composite_Z) * 100
```

The first 11 months of each series are not used because they do not have a complete 12-month rolling window.

## Project structure

```text
.
├── ADF_test.py
├── ELSI_Framework_A.csv
├── ELSI_Framework_B.csv
├── README.md
├── app.py
├── pyproject.toml
├── requirements.txt
├── update_data.py
├── anaconda_projects/
│   └── db/
├── src/
│   └── python_project/
│       ├── __init__.py
│       └── test.ipynb
└── .gitignore
```

## Requirements

- Python 3.13+
- Streamlit
- pandas
- NumPy
- SciPy
- Plotly

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Update the ECB data files

The repository includes a data-refresh script that pulls market and banking series from the ECB Data Portal API and constructs the model-ready datasets.

```bash
python update_data.py
```

This script creates/updates:

- `ELSI_Framework_A.csv` — long-horizon framework using spliced EONIA/€STR history
- `ELSI_Framework_B.csv` — modern €STR-era framework

## Run the dashboard

From the project root:

```bash
streamlit run app.py
```

A local URL such as `http://localhost:8501` will be printed by Streamlit.

## Run the ADF diagnostics

To check the stationarity properties of the framework datasets:

```bash
python ADF_test.py
```

This prints ADF test statistics and p-values for each variable in both framework files. The diagnostic uses a significance level of 10% (α = 0.10), so a p-value below 0.10 indicates evidence against a unit root and supports treating the series as stationary at that threshold.

## Notes

- The dashboard expects the CSV files to exist in the project root or a parent directory.
- The shock simulator uses the latest available observation as the baseline and measures the effect of custom policy shocks against the most recent rolling history.
- The model is a research and treasury early-warning tool, not a regulatory standard or investment recommendation.
