import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="ELSI Early-Warning Framework",
    page_icon="🏦",
    layout="wide",
)

# 2. Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to Slide / Section:",
    [
        "1. Executive Summary",
        "2. Macro Theory",
        "3. Benchmark Splicing",
        "4. Model Architecture",
        "5. Live ELSI Dashboard",
    ],
)


# 3. Data Engine Loading Function
@st.cache_data
def load_and_process_data():
    file_name = "ELSI_Framework_A.csv"
    if os.path.exists(file_name):
        path = file_name
    elif os.path.exists(os.path.join("..", file_name)):
        path = os.path.join("..", file_name)
    else:
        st.error(f"❌ Could not find '{file_name}'. Ensure CSV is in project directory!")
        st.stop()

    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)

    # 12-Month Rolling Normalization
    window = 12
    z_er = -(df["excess_reserves"] - df["excess_reserves"].rolling(window).mean()) / df["excess_reserves"].rolling(window).std()
    z_sr = (df["short_rate"] - df["short_rate"].rolling(window).mean()) / df["short_rate"].rolling(window).std()
    z_gy = (df["govt_yield_10y"] - df["govt_yield_10y"].rolling(window).mean()) / df["govt_yield_10y"].rolling(window).std()
    z_ltd = (df["ltd_ratio_calc"] - df["ltd_ratio_calc"].rolling(window).mean()) / df["ltd_ratio_calc"].rolling(window).std()

    df["Z_ExcessReserves"] = z_er
    df["Z_ShortRate"] = z_sr
    df["Z_GovtYield10Y"] = z_gy
    df["Z_LTDRatio"] = z_ltd

    # Composite CDF Score
    df["Composite_Z"] = (z_er + z_sr + z_gy + z_ltd) / 4.0
    df["ELSI_Score"] = norm.cdf(df["Composite_Z"]) * 100.0

    def get_tier(score):
        if pd.isna(score):
            return "N/A"
        elif score >= 75:
            return "RED: Systemic Stress"
        elif score >= 50:
            return "ORANGE: Tightening Alert"
        elif score >= 25:
            return "YELLOW: Friction"
        else:
            return "GREEN: Normal"

    df["Risk_Level"] = df["ELSI_Score"].apply(get_tier)
    return df.dropna(subset=["ELSI_Score"])


df = load_and_process_data()


# 4. Page Routing
if page == "1. Executive Summary":
    st.title("🏦 Eurozone Liquidity Stress Index (ELSI)")
    st.markdown("### Executive Overview & Project Scope")
    st.write(
        "Institutional-grade quantitative risk engine spanning 22 years of ECB monetary policy (2004–2026)."
    )

elif page == "2. Macro Theory":
    st.title("📜 Macroeconomic Theory & Central Bank Liquidity")
    st.write("Explaining Excess Reserves vs. Short Rates (€STR / EONIA).")
    st.write("**Scarce vs. Abundant Liquidity:** Pre-2008 corridor system vs. post-2015 floor system.")

elif page == "3. Benchmark Splicing":
    st.title("🌁 Benchmark Transition: EONIA to €STR")
    st.write("Structural transition under EU Benchmarks Regulation (BMR) using the -8.5 bps spread adjustment.")

elif page == "4. Model Architecture":
    st.title("📐 Econometric Engine & Z-Score Methodology")
    st.write("ADF stationarity tests, 12-month rolling Z-scores, and Normal CDF mapping.")

elif page == "5. Live ELSI Dashboard":
    st.subheader("Eurozone Liquidity Stress Trajectory & Policy Regimes (2004–2026)")

    # Sidebar Date Control
    date_index = pd.DatetimeIndex(df.index)
    start_year, end_year = st.sidebar.slider(
        "Select Time Period:",
        min_value=int(date_index.year.min()),
        max_value=int(date_index.year.max()),
        value=(int(date_index.year.min()), int(date_index.year.max())),
    )
    filtered_df = df.loc[f"{start_year}-01-01":f"{end_year}-12-31"]

    # Top KPI Metrics
    latest = filtered_df.iloc[-1]
    score = latest["ELSI_Score"]
    tier = latest["Risk_Level"]

    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    with col1:
        st.metric(label="Latest ELSI Index Score", value=f"{score:.1f} / 100")
    with col2:
        st.metric(label="Risk Tier Classification", value=str(tier))
    with col3:
        st.metric(label="Historical Sample Size", value=f"{len(filtered_df)} Months")

    st.markdown("---")

    # Interactive Plotly Chart with MP Stance Events
    fig = go.Figure()

    # Main Stress Score Line
    fig.add_trace(
        go.Scatter(
            x=filtered_df.index,
            y=filtered_df["ELSI_Score"],
            mode="lines",
            name="ELSI Score",
            line=dict(color="#0f172a", width=2.5),
        )
    )

    # Risk Tier Shaded Bands
    fig.add_hrect(y0=0, y1=25, fillcolor="#22c55e", opacity=0.12, line_width=0, annotation_text="Normal (0-25)")
    fig.add_hrect(y0=25, y1=50, fillcolor="#eab308", opacity=0.15, line_width=0, annotation_text="Friction (25-50)")
    fig.add_hrect(y0=50, y1=75, fillcolor="#f97316", opacity=0.15, line_width=0, annotation_text="Tightening Alert (50-75)")
    fig.add_hrect(y0=75, y1=100, fillcolor="#ef4444", opacity=0.12, line_width=0, annotation_text="Systemic Stress (75-100)")

    # Key Monetary Policy (MP) Events
    events = {
        "2007-08-01": "2007 Interbank Freeze",
        "2008-10-01": "2008 GFC / FRFA Allotment",
        "2011-11-01": "2011 Sovereign Debt Crisis",
        "2015-03-01": "2015 Expanded APP (QE)",
        "2020-03-01": "2020 COVID / PEPP Launch",
        "2022-07-01": "2022 Rate Hike Cycle (+450bps)",
        "2023-03-01": "2023 SVB / CS Stress & QT",
    }

    # Draw Vertical Lines & Annotations for Events
    for date_str, event_label in events.items():
        event_date = pd.to_datetime(date_str)
        if filtered_df.index.min() <= event_date <= filtered_df.index.max():
            fig.add_vline(
                x=event_date,
                line_width=1.2,
                line_dash="dash",
                line_color="#475569",
            )
            fig.add_annotation(
                x=event_date,
                y=92,
                text=event_label,
                showarrow=False,
                textangle=-90,
                font=dict(size=9, color="#1e293b"),
                xanchor="right",
            )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Composite Stress Score (0–100 Scale)",
        yaxis=dict(range=[0, 100]),
        height=500,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 5. NEW: HYPOTHETICAL STRESS SCENARIO / SENSITIVITY SIMULATOR
    st.subheader("⚡ Sensitivity & Hypothetical Stress Scenario Simulator")
    st.caption(
        "Simulate realistic macro shocks. Excess reserves sit at ~€3,000B, so shifts are calibrated in €100B increments."
    )

    base_er = latest["excess_reserves"]
    base_sr = latest["short_rate"]
    base_gy = latest["govt_yield_10y"]
    base_ltd = latest["ltd_ratio_calc"]

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        # Calibrated to Hundreds of Billions (€100B to €2,000B)
        delta_er = (
            st.slider(
                "Excess Reserves Shift (€B)",
                min_value=-2000.0,
                max_value=1000.0,
                value=0.0,
                step=100.0,
                help="Base excess liquidity is ~€3 Trillion. A €500B-€1,000B drain represents aggressive QT.",
            )
        )
    with col_s2:
        # Capped to realistic monetary policy bounds (-100 bps to +150 bps)
        delta_sr = (
            st.slider(
                "€STR Short Rate Shift (bps)",
                min_value=-100.0,
                max_value=150.0,
                value=0.0,
                step=25.0,
                help="ECB rate hikes/cuts in 25 bps steps.",
            )
            / 100.0
        )
    with col_s3:
        # Bond yield shocks (-100 bps to +150 bps)
        delta_gy = (
            st.slider(
                "10Y Bund Yield Shift (bps)",
                min_value=-100.0,
                max_value=150.0,
                value=0.0,
                step=25.0,
            )
            / 100.0
        )
    with col_s4:
        # Banking LTD shift (-5% to +5%)
        delta_ltd = (
            st.slider(
                "Banking LTD Shift (%)",
                min_value=-5.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
            )
            / 100.0
        )

    # Calculate Shocked Z-Scores against 12-Month Volatility
    last_12 = df.tail(12)

    sim_er = base_er + delta_er
    sim_sr = base_sr + delta_sr
    sim_gy = base_gy + delta_gy
    sim_ltd = base_ltd + delta_ltd

    # Prevent division by zero if std is tiny
    std_er = last_12["excess_reserves"].std() if last_12["excess_reserves"].std() > 0 else 1.0
    std_sr = last_12["short_rate"].std() if last_12["short_rate"].std() > 0 else 0.1
    std_gy = last_12["govt_yield_10y"].std() if last_12["govt_yield_10y"].std() > 0 else 0.1
    std_ltd = last_12["ltd_ratio_calc"].std() if last_12["ltd_ratio_calc"].std() > 0 else 0.01

    z_er_sim = -(sim_er - last_12["excess_reserves"].mean()) / std_er
    z_sr_sim = (sim_sr - last_12["short_rate"].mean()) / std_sr
    z_gy_sim = (sim_gy - last_12["govt_yield_10y"].mean()) / std_gy
    z_ltd_sim = (sim_ltd - last_12["ltd_ratio_calc"].mean()) / std_ltd

    composite_z_sim = (z_er_sim + z_sr_sim + z_gy_sim + z_ltd_sim) / 4.0
    sim_elsi_score = norm.cdf(composite_z_sim) * 100.0

    if sim_elsi_score >= 75:
        sim_tier = "🔴 Systemic Stress"
    elif sim_elsi_score >= 50:
        sim_tier = "🟠 Tightening Alert"
    elif sim_elsi_score >= 25:
        sim_tier = "🟡 Friction"
    else:
        sim_tier = "🟢 Normal"

    # Display Results
    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        st.metric(
            label="Simulated ELSI Score",
            value=f"{sim_elsi_score:.1f} / 100",
            delta=f"{sim_elsi_score - score:+.1f} pts vs. Baseline",
            delta_color="inverse",
        )
    with res_col2:
        st.metric(label="Simulated Risk Tier Signal", value=sim_tier)
    with res_col3:
        st.metric(label="Composite Z-Score Shift", value=f"{composite_z_sim:.2f} σ")