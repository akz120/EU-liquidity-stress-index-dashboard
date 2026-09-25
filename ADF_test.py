import pandas as pd
from statsmodels.tsa.stattools import adfuller

#loading the pre-processed dataframes for framework A and B from CSV files
df_framework_A = pd.read_csv(
    "ELSI_Framework_A.csv",
    index_col=0,
    parse_dates=True
)

df_framework_B = pd.read_csv(
    "ELSI_Framework_B.csv",
    index_col=0,
    parse_dates=True
)

significance_level = 0.10

#defining a function to run the ADF test on each variable in the dataframe and print the results
def run_full_adf_suite(df, framework_name):
    print(f"   MODULE 2: ADF DIAGNOSTICS — {framework_name} ")
    print(f"(α = {significance_level:.2f})")

    results = []

    for col in df.columns:
        #ADF test on raw values
        res_level = adfuller(df[col].dropna())
        stat_lvl, pval_lvl = res_level[0], res_level[1]
        status_lvl = (
            "Stationary I(0)" if pval_lvl < significance_level else "Non-Stationary / Unit Root Not Rejected"
        )

        #ADF test on first differences
        df_diff = df[col].diff().dropna()
        res_diff = adfuller(df_diff)
        stat_diff, pval_diff = res_diff[0], res_diff[1]
        status_diff = (
            "Stationary I(0)" if pval_diff < significance_level else "Non-Stationary / Unit Root Not Rejected"
        )

        results.append(
            {
                "Variable": col,
                "Lvl Stat": f"{stat_lvl:8.3f}",
                "Lvl p-val": f"{pval_lvl:7.4f}",
                "Lvl Status": status_lvl,
                "Diff Stat": f"{stat_diff:8.3f}",
                "Diff p-val": f"{pval_diff:7.4f}",
                "Diff Status": status_diff,
            }
        )

    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    return res_df

#running the ADF diagnostics suite for both frameworks and storing the results in separate dataframes
adf_A = run_full_adf_suite(
    df_framework_A,
    f"FRAMEWORK A (N={len(df_framework_A)})"
)

adf_B = run_full_adf_suite(
    df_framework_B,
    f"FRAMEWORK B (N={len(df_framework_B)})"
)