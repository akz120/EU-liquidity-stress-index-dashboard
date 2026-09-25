import io
import pandas as pd
import requests

BASE_URL = "https://data-api.ecb.europa.eu/service/data"

#verified series keys from ECB SDW API (https://sdw-wsrest.ecb.europa.eu/help/)
SERIES_MAP = {
    "excess_reserves": "ILM/M.U2.C.L020100MP.U2.EUR",
    "eonia_rate": "FM/M.U2.EUR.4F.MM.EONIA.HSTA",
    "estr_rate": "EST/B.EU000A2X2A25.WT",
    "govt_yield_10y": "YC/B.U2.EUR.4F.G_N_C.SV_C_YM.PY_10Y",
    "total_deposits": "BSI/M.U2.N.A.L20.A.1.U2.0000.Z01.E",
    "total_loans": "BSI/M.U2.N.A.A20.A.1.U2.0000.Z01.E",
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
raw_dfs = {}

#fetching the data from ECB SDW API and storing in raw_dfs dictionary
for name, key in SERIES_MAP.items():
    url = f"{BASE_URL}/{key}?format=csvdata"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    df = pd.read_csv(io.StringIO(resp.text))
    df = df[["TIME_PERIOD", "OBS_VALUE"]].copy()
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"], format="mixed")
    df.set_index("TIME_PERIOD", inplace=True)
    raw_dfs[name] = df

#converting the raw dataframes to monthly frequency and storing in a master dataframe
monthly_series = {}
for name in SERIES_MAP.keys():
    monthly_series[name] = raw_dfs[name]["OBS_VALUE"].resample("MS").mean()

df_master = pd.DataFrame(monthly_series)

#forward filling missing values in the 'excess_reserves' column since the data gets published 
#with a lag and doesnt follow the classical calendar month-end convention
df_master["excess_reserves"] = df_master["excess_reserves"].ffill()

#calculating the loan-to-deposit ratio and storing it in a new column 'ltd_ratio_calc'
df_master["ltd_ratio_calc"] = (
    df_master["total_loans"] / df_master["total_deposits"]
) * 100

#creating a continuous series by adjusting EONIA and filling missing values with €STR
df_master["eonia_adjusted"] = df_master["eonia_rate"] - 0.085
df_master["short_rate"] = df_master["estr_rate"].fillna(
    df_master["eonia_adjusted"]
)

#framework A with the longer historical horizon (2004 – 2026) 
#and spliced EONIA/€STR continuous short rate
df_framework_A = df_master[
    ["excess_reserves", "short_rate", "govt_yield_10y", "ltd_ratio_calc"]
].dropna()

#framework B with the modern ESTR rate (2019-2026)
df_framework_B = df_master.loc[
    "2019-10-01":,
    ["excess_reserves", "estr_rate", "govt_yield_10y", "ltd_ratio_calc"],
].dropna()

#saving the two frameworks to CSV files for further analysis or reporting
df_framework_A.to_csv("ELSI_Framework_A.csv", index=True)
df_framework_B.to_csv("ELSI_Framework_B.csv", index=True)

#verifying the name and variables
print("=== FRAMEWORK A — Long Horizon (Spliced EONIA/€STR) ===")
print(
    f"Shape: {df_framework_A.shape} | "
    f"Start: {df_framework_A.index.min().strftime('%Y-%m')} | "
    f"End: {df_framework_A.index.max().strftime('%Y-%m')}"
)
print("Columns:", list(df_framework_A.columns))

print("\n=== FRAMEWORK B — Modern €STR Regime ===")
print(
    f"Shape: {df_framework_B.shape} | "
    f"Start: {df_framework_B.index.min().strftime('%Y-%m')} | "
    f"End: {df_framework_B.index.max().strftime('%Y-%m')}"
)
print("Columns:", list(df_framework_B.columns))