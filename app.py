import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ELSI Early-Warning Framework",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("", unsafe_allow_html=True)

#sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to Slide / Section:",
    [
        "1. Executive Summary",
        "2. Macro Theory Timeline",
        "3. Benchmark Splicing",
        "4. Model Architecture",
        "5. Live ELSI Dashboard",
        "6. Stress Simulator & Pillar Inspector",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Developed by:** Alma Zhantleuova")
st.sidebar.markdown("Ex-National Bank Analyst | Treasury & Financial Risk Analyst")
st.sidebar.markdown("[LinkedIn Profile](https://www.linkedin.com/in/alma-zhantleuova/)")

#loading the data - framework A to get historical data for 22 years
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

    #12-month rolling normalization
    window = 12
    z_er = -(df["excess_reserves"] - df["excess_reserves"].rolling(window).mean()) / df["excess_reserves"].rolling(window).std()
    z_sr = (df["short_rate"] - df["short_rate"].rolling(window).mean()) / df["short_rate"].rolling(window).std()
    z_gy = (df["govt_yield_10y"] - df["govt_yield_10y"].rolling(window).mean()) / df["govt_yield_10y"].rolling(window).std()
    z_ltd = (df["ltd_ratio_calc"] - df["ltd_ratio_calc"].rolling(window).mean()) / df["ltd_ratio_calc"].rolling(window).std()

    df["Z_ExcessReserves"] = z_er
    df["Z_ShortRate"] = z_sr
    df["Z_GovtYield10Y"] = z_gy
    df["Z_LTDRatio"] = z_ltd

    #composite equal weight CDF score (25% each)
    df["Composite_Z"] = (z_er + z_sr + z_gy + z_ltd) / 4.0
    df["ELSI_Score"] = norm.cdf(df["Composite_Z"]) * 100.0

    def get_tier(score):
        if pd.isna(score):
            return "N/A"
        elif score >= 75:       
            return "🔴 Systemic Stress"
        elif score >= 50:      
            return "🟠 Tightening Alert"
        elif score >= 25:       
            return "🟡 Friction"
        else:
            return "🟢 Normal"


    df["Risk_Level"] = df["ELSI_Score"].apply(get_tier)
    return df.dropna(subset=["ELSI_Score"])


df = load_and_process_data()


#page content based on selection
if page == "1. Executive Summary":
    st.title("Eurozone Liquidity Stress Index (ELSI)")
    st.caption("Quantitative Early-Warning Engine for Commercial Bank Treasury & Balance Sheet Risk")

    st.markdown("---")

    #summary card
    st.info(
        "**Mission Objective:** ELSI translates 22 years of ECB market data (2004–2026) into a single 0–100 risk score, "
        "giving treasury desks an early warning to optimize funding duration, protect LCR buffers, and manage NIM before liquidity squeezes hit."
    )

    st.markdown("### Core Definition: What are Excess Reserves ($ER$)?")
    st.markdown(
        "For commercial banks, **Excess Reserves** are central bank deposits held above statutory minimum requirements. "
        "They form the primary cash buffer for intraday interbank clearing, deposit outflows, and settlement shocks."
    )

    st.markdown("---")
    st.markdown("### The Commercial Treasury Trade-off")

    #side-by-side comparison card
    col_under, col_over = st.columns(2)

    with col_under:
        st.error("**Cost of Under-Reservation (Liquidity Squeeze)**")
        st.markdown("""
        * **Funding Premium:** Forced overnight borrowing above €STR during market friction.
        * **Fire-Sale Risk:** Forced liquidation of sovereign bonds (Bunds) at a discount.
        * **Regulatory Squeeze:** Threat of breaching LCR ($>100\%$) and NSFR limits.
        """)

    with col_over:
        st.warning("**Cost of Over-Conservation (Cash Hoarding)**")
        st.markdown("""
        * **Negative Carry:** Idle cash at the Deposit Facility Rate yields less than commercial credit.
        * **NIM Drag:** Compressed Net Interest Margins relative to market peers.
        * **Opportunity Cost:** Trapped capital that cannot fund higher-yielding corporate loans.
        """)

    st.markdown("---")

    #the purpose of ELSI
    st.success(
        "**Bottom Line for Risk Desks:** ELSI acts as an early-warning radar—signaling when to transition from yield optimization to precautionary cash preservation before market tightening turns expensive."
    )

    #adding citation footer
    st.markdown("---")
    st.caption(
        "**Data Sources & Lineage:** Ingested via the official **ECB Data Portal API** (`https://data-api.ecb.europa.eu/service/data`). "
        "Key series: Excess Reserves (`ILM`), €STR/EONIA (`EST`/`FM`), 10Y Sovereign Yields (`YC`), and BSI Loans/Deposits (`BSI`)."
    )

elif page == "2. Macro Theory Timeline":
    st.title("Macroeconomic Theory & Policy Regimes (2004–2026)")
    st.caption("Evolution of Eurosystem Liquidity Frameworks & Central Bank Operational Regimes")

    st.markdown("---")

    #regimes 1 and 2
    col1, col2 = st.columns(2)

    with col1:
        st.info("**1. Corridor Era (2004–2008)**")
        st.markdown("""
        * **Regime:** Structural Corridor System (Scarce Reserves).
        * **Operational Target:** Short rates (EONIA) anchored to the **MRO Rate**.
        * **Liquidity State:** Reserves kept scarce via weekly fine-tuning operations.
        """)

    with col2:
        st.warning("**2. Crisis Management & FRFA (2008–2014)**")
        st.markdown("""
        * **Regime:** Fixed-Rate Full Allotment (FRFA).
        * **Operational Target:** Post-GFC & Sovereign Debt Crisis response.
        * **Liquidity State:** ECB provided unlimited liquidity against collateral to halt interbank freezes.
        """)

    st.markdown("---")

    #regimes 3 and 4
    col3, col4 = st.columns(2)

    with col3:
        st.success("**3. Abundant QE Floor Era (2015–2021)**")
        st.markdown("""
        * **Regime:** De-Facto Floor System (APP & PEPP).
        * **Operational Target:** Short rates (€STR) pinned tightly to the **Deposit Facility Rate (DFR)**.
        * **Liquidity State:** Asset purchases pushed excess reserves into the trillions (€3T+).
        """)

    with col4:
        st.error("**4. Rapid Policy Tightening (2022–2024)**")
        st.markdown("""
        * **Regime:** Post-COVID Inflation Shock & Rate Hikes.
        * **Operational Target:** +450 bps rate hikes in record time + Quantitative Tightening (QT).
        * **Liquidity State:** TLTRO repayments & balance sheet runoff sharply contract reserve buffers.
        """)

    st.markdown("---")

    #the current MP stance
    st.subheader("5. New Operational Framework & Normalization (2025–2026+)")
    st.markdown("""
    * **Current Hybrid Regime:** The ECB operates a flexible floor framework where QT gradually drains surplus liquidity while structural credit operations provide a safety net for commercial bank demand.
    * **Treasury Implication:** Commercial banks can no longer passively rely on infinite QE surplus—active liquidity risk management via **ELSI** is essential.
    """)

elif page == "3. Benchmark Splicing":
    st.title("Benchmark Transition: EONIA to €STR")
    st.caption("Structural Splicing Methodology under EU Benchmarks Regulation (BMR)")

    st.markdown("---")

    col_eonia, col_estr = st.columns(2)

    with col_eonia:
        st.error("**Legacy Benchmark: EONIA**")
        st.markdown("""
        * **Full Name:** Euro OverNight Index Average (2004–2019).
        * **Calculation:** Weighted average of survey estimates from panel banks.
        * **Structural Flaw:** Low underlying trading volumes and vulnerability to manipulation led to regulatory phase-out under EU BMR.
        """)

    with col_estr:
        st.success("**Modern Benchmark: €STR**")
        st.markdown("""
        * **Full Name:** Euro Short-Term Rate (2019–Present).
        * **Calculation:** Direct ECB transaction-level reporting across Eurosystem money markets.
        * **Key Advantage:** Fully robust, transaction-backed wholesale overnight funding rate.
        """)

    st.markdown("---")

    st.subheader("The Official ECB Splicing Equation")
    st.markdown(
        "To construct a seamless 22-year historical time series (2004–2026), EONIA is bridged to €STR using the ECB's official fixed spread adjustment of **$-8.5\\text{ bps}$** ($-0.085\\%$):"
    )

    st.latex(r"""
    \text{Rate}_{\text{Unified}, t} = 
    \begin{cases} 
    \text{EONIA}_t - 0.085\% & \text{for } t < \text{October 2019} \\[6pt]
    \text{€STR}_t & \text{for } t \ge \text{October 2019} 
    \end{cases}
    """)

    st.markdown("---")

    st.info(
        "**Econometric Integrity:** Splicing the two series eliminates structural regime breaks in short-term "
        "interest rates, allowing the 12-month rolling Z-score algorithm to operate smoothly across the full 22-year horizon."
    )

elif page == "4. Model Architecture":
    st.title("Econometric Engine & Z-Score Methodology")
    st.caption("Mathematical Transformation Pipeline & Signal Standardization")

    st.markdown("---")

    # NEW SECTION: Input Variables Breakdown Grid
    st.markdown("#### Model Input Pillars (The 4 Variables)")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown("**1. Excess Reserves (\(ER\))**")
        st.caption("""
        * **Source:** ECB Eurosystem Balance Sheet
        * **Unit:** € Billions
        * **Role:** Primary cash buffer for bank clearing. *(Inverted in model)*
        """)

    with p2:
        st.markdown("**2. Overnight Short Rate (\(SR\))**")
        st.caption("""
        * **Source:** ECB (€STR / Spliced EONIA)
        * **Unit:** Percentage (%)
        * **Role:** Wholesale interbank overnight borrowing cost benchmark.
        """)

    with p3:
        st.markdown("**3. 10Y Sovereign Yield (\(GY\))**")
        st.caption("""
        * **Source:** German Bund 10Y Benchmark
        * **Unit:** Percentage (%)
        * **Role:** Term premium & sovereign risk discount rate.
        """)

    with p4:
        st.markdown("**4. Loan-to-Deposit Ratio (\(LTD\))**")
        st.caption("""
        * **Source:** Eurozone Banking Aggregates
        * **Unit:** Ratio (%)
        * **Role:** Commercial credit expansion vs. sticky deposit funding.
        """)

    st.markdown("---")

    col_math1, col_math2 = st.columns(2)

    with col_math1:
        st.markdown("#### 12-Month Rolling Normalization")
        st.markdown(
            "Transforms non-stationary \(I(1)\) variables relative to prevailing 12m localized market volatility:"
        )
        st.latex(r"Z_{i, t} = \frac{X_{i, t} - \mu_{i, 12m}}{\sigma_{i, 12m}}")
        st.caption("*(Excess Reserves are inverted: lower reserves = higher stress).*")

    with col_math2:
        st.markdown("#### Equal-Weighted Composite & CDF Mapping")
        st.markdown(
            "Aggregates equal-weighted Z-scores into a composite score, mapped onto a bounded 0 to 100 risk scale via Normal CDF \(\Phi(\cdot)\):"
        )
        st.latex(r"\text{ELSI}_t = \Phi\left(\frac{Z_{ER} + Z_{SR} + Z_{GY} + Z_{LTD}}{4}\right) \times 100")

    st.markdown("---")

    st.markdown("#### Operational Risk Tier Classifications")

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)

    with t_col1:
        st.success("🟢 **0 – 25: Normal**\n\nAccommodative conditions.")
    with t_col2:
        st.warning("🟡 **25 – 50: Friction**\n\nMild interbank tightening.")
    with t_col3:
        st.info("🟠 **50 – 75: Tightening**\n\nElevated funding friction.")
    with t_col4:
        st.error("🔴 **75 – 100: Stress**\n\nAcute liquidity squeeze.")
        
elif page == "5. Live ELSI Dashboard":
    st.subheader("Eurozone Liquidity Stress Trajectory (2004–2026)")

    #filtering the time period based on user selection
    date_index = pd.DatetimeIndex(df.index)
    start_year, end_year = st.sidebar.slider(
        "Select Time Period:",
        min_value=int(date_index.year.min()),
        max_value=int(date_index.year.max()),
        value=(int(date_index.year.min()), int(date_index.year.max())),
    )
    filtered_df = df.loc[f"{start_year}-01-01":f"{end_year}-12-31"]

    #key metrics for the latest month in the filtered range
    latest = filtered_df.iloc[-1]
    score = latest["ELSI_Score"]
    tier = latest["Risk_Level"]

    #color coding for the risk tier display
    if "Systemic" in str(tier):
        tier_display = "🔴 Systemic Stress"
    elif "Tightening" in str(tier):
        tier_display = "🟠 Tightening Alert"
    elif "Friction" in str(tier):
        tier_display = "🟡 Friction"
    else:
        tier_display = "🟢 Normal"

    col1, col2, col3 = st.columns([1.0, 1.8, 1.0])
    with col1:
        st.metric(label="Latest ELSI Index Score", value=f"{score:.1f} / 100")
    with col2:
        st.metric(label="Risk Tier Classification", value=tier_display)
    with col3:
        st.metric(label="Historical Sample Size", value=f"{len(filtered_df)} Months")

    st.markdown("---")

    #interactive line chart with shaded risk bands and event annotations
    fig = go.Figure()

    #ELSI score line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df.index,
            y=filtered_df["ELSI_Score"],
            mode="lines",
            name="ELSI Score",
            line=dict(color="#0f172a", width=2.5),
        )
    )

    #risk tier shaded bands
    fig.add_hrect(y0=0, y1=25, fillcolor="#22c55e", opacity=0.12, line_width=0, annotation_text="Normal (0-25)")
    fig.add_hrect(y0=25, y1=50, fillcolor="#eab308", opacity=0.15, line_width=0, annotation_text="Friction (25-50)")
    fig.add_hrect(y0=50, y1=75, fillcolor="#f97316", opacity=0.15, line_width=0, annotation_text="Tightening Alert (50-75)")
    fig.add_hrect(y0=75, y1=100, fillcolor="#ef4444", opacity=0.12, line_width=0, annotation_text="Systemic Stress (75-100)")

    #annotated historical events
    events = {
        "2007-08-01": "2007 Interbank Freeze",
        "2008-10-01": "2008 GFC / FRFA Allotment",
        "2011-11-01": "2011 Sovereign Debt Crisis",
        "2015-03-01": "2015 Expanded APP (QE)",
        "2020-03-01": "2020 COVID / PEPP Launch",
        "2022-07-01": "2022 Rate Hike Cycle (+450bps)",
        "2023-03-01": "2023 SVB / CS Stress & QT",
    }
    
    #event lines and annotations only if within the filtered date range 
    min_date = filtered_df.index.min()
    max_date = filtered_df.index.max()

    for date_str, event_label in events.items():
        event_date = pd.to_datetime(date_str)
        if min_date <= event_date <= max_date:
            fig.add_vline(
                x=event_date,
                line_width=1.2,
                line_dash="dash",
                line_color="#475569",
            )
            fig.add_annotation(
                x=event_date,
                y=78,  # Anchored lower to avoid top border overlap
                text=f" {event_label} ",
                showarrow=False,
                textangle=-90,
                font=dict(size=9, color="#0f172a"),
                bgcolor="rgba(255, 255, 255, 0.85)",  # Crisp background box
                bordercolor="#cbd5e1",
                borderwidth=1,
                xanchor="right",
                yanchor="top",
            )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Composite Stress Score (0–100 Scale)",
        xaxis=dict(range=[min_date, max_date]),  # Forces full 2004-2026 view
        yaxis=dict(range=[0, 100]),
        height=500,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "6. Stress Simulator & Pillar Inspector":
    st.subheader("Policy Shock Simulator & Risk Inspector")
    st.caption("Test how central bank policy moves and market shocks impact systemic bank liquidity in real time.")

    st.markdown("---")

    #preset stress scenarios for quick selection
    st.markdown("### 1. Select a Quick-Stress Scenario:")
    sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)

    #preset stress scenarios stored in session state to persist across reruns
    if "p_er" not in st.session_state:
        st.session_state.p_er = 0.0
        st.session_state.p_sr = 0.0
        st.session_state.p_gy = 0.0
        st.session_state.p_ltd = 0.0

    with sc_col1:
        if st.button("Reset Baseline (Today)"):
            st.session_state.p_er = 0.0
            st.session_state.p_sr = 0.0
            st.session_state.p_gy = 0.0
            st.session_state.p_ltd = 0.0
    with sc_col2:
        if st.button("Rate Hike (+75 bps)"):
            st.session_state.p_er = -200.0
            st.session_state.p_sr = 75.0
            st.session_state.p_gy = 50.0
            st.session_state.p_ltd = 1.0
    with sc_col3:
        if st.button("Aggressive QT (-€1 Trillion)"):
            st.session_state.p_er = -1000.0
            st.session_state.p_sr = 25.0
            st.session_state.p_gy = 25.0
            st.session_state.p_ltd = 2.0
    with sc_col4:
        if st.button("Credit Freeze (Severe Shock)"):
            st.session_state.p_er = -1500.0
            st.session_state.p_sr = 125.0
            st.session_state.p_gy = 100.0
            st.session_state.p_ltd = 10.0

    st.markdown("---")

    #interactive sliders for customised stress to be used in the simulator 
    col_inputs, col_results = st.columns([1.2, 1.0])

    latest = df.iloc[-1]
    base_er = latest["excess_reserves"]
    base_sr = latest["short_rate"]
    base_gy = latest["govt_yield_10y"]
    base_ltd = latest["ltd_ratio_calc"]
    baseline_score = latest["ELSI_Score"]

    with col_inputs:
        st.markdown("### 2. Custom Shock Parameters")

        #excess reserves 
        delta_er_billions = st.slider(
            "Central Bank Cash Buffer (Excess Reserves €B)",
            -2000.0, 1000.0, float(st.session_state.p_er), 100.0,
            help="Simulates ECB Quantitative Tightening (QT). Negative numbers mean cash is draining."
        )

        #short rates
        delta_sr = st.slider(
            "Overnight Rate Shift (€STR in basis points)",
            -100.0, 150.0, float(st.session_state.p_sr), 25.0,
            help="100 basis points = 1.00% rate hike or cut by the central bank."
        ) / 100.0

        #gov bonds yields
        delta_gy = st.slider(
            "10Y Sovereign Bond Yield Shift (Bunds in bps)",
            -100.0, 150.0, float(st.session_state.p_gy), 25.0,
            help="Reflects long-term borrowing costs for governments and corporations."
        ) / 100.0

        #loan to deposits ratio
        delta_ltd = st.slider(
            "Commercial Bank Loan Squeeze (LTD Ratio %)",
            -20.0, 20.0, float(st.session_state.p_ltd), 0.5,
            help="Higher LTD means banks have loaned out more money relative to their deposits."
        ) / 100.0

    #calculate shocked Z-Scores
    er_scale = 1000.0 if base_er > 100000 else 1.0
    delta_er = delta_er_billions * er_scale

    last_12 = df.tail(12)
    sim_er = base_er + delta_er
    sim_sr = base_sr + delta_sr
    sim_gy = base_gy + delta_gy
    sim_ltd = base_ltd + delta_ltd

    std_er = last_12["excess_reserves"].std() if last_12["excess_reserves"].std() > 0 else 1.0
    std_sr = last_12["short_rate"].std() if last_12["short_rate"].std() > 0 else 0.1
    std_gy = last_12["govt_yield_10y"].std() if last_12["govt_yield_10y"].std() > 0 else 0.1
    std_ltd = last_12["ltd_ratio_calc"].std() if last_12["ltd_ratio_calc"].std() > 0 else 0.01

    z_er_sim = -(sim_er - last_12["excess_reserves"].mean()) / std_er
    z_sr_sim = (sim_sr - last_12["short_rate"].mean()) / std_sr
    z_gy_sim = (sim_gy - last_12["govt_yield_10y"].mean()) / std_gy
    z_ltd_sim = (sim_ltd - last_12["ltd_ratio_calc"].mean()) / std_ltd

    #determine if each shock is significant enough to be considered a "shock" for the simulation
    has_er_shock = abs(delta_er_billions) > 150.0  
    has_sr_shock = abs(delta_sr * 100.0) > 30.0   
    has_gy_shock = abs(delta_gy * 100.0) > 30.0    
    has_ltd_shock = abs(delta_ltd * 100.0) > 0.8   

# Count how many shocks are active
    active_shocks = sum([has_er_shock, has_sr_shock, has_gy_shock, has_ltd_shock])

# Determine amplification factor based on the number of active shocks
    if active_shocks >= 3:
        amplification = 1.0    #correlated shock across three or more markets
    elif active_shocks == 2:
        amplification = 0.55   #correlated shock across two markets
    else:
        amplification = 0.25   #isolated shock in one market

#final simulated ELSI score calculation
    if (
        delta_er_billions == 0.0
        and delta_sr == 0.0
        and delta_gy == 0.0
        and delta_ltd == 0.0
        ):
        sim_elsi_score = baseline_score
    else:
        composite_z_sim = (
        (z_er_sim + z_sr_sim + z_gy_sim + z_ltd_sim) / 4.0
        ) * amplification

        sim_elsi_score = norm.cdf(composite_z_sim) * 100.0

    with col_results:
        st.markdown("### 3. Simulated Market Impact")

        st.metric(
            label="Simulated ELSI Stress Score",
            value=f"{sim_elsi_score:.1f} / 100",
            delta=f"{sim_elsi_score - baseline_score:+.1f} pts vs. Today",
            delta_color="inverse",
        )

        #interpretation of the results delivered by the simulation 
        if sim_elsi_score >= 75:
            st.error("🔴 **SYSTEMIC STRESS SIGNAL**")
            st.markdown(
                "**Real-World Impact:** Interbank cash is scarce. Overnight borrowing costs spike, "
                "banks restrict lending, and treasury desks must hoard cash buffers immediately."
            )
        elif sim_elsi_score >= 50:
            st.warning("🟠 **TIGHTENING ALERT**")
            st.markdown(
                "**Real-World Impact:** Funding costs are rising. Commercial banks face margin friction "
                "and should start lengthening borrowing duration before liquidity dries up."
            )
        elif sim_elsi_score >= 25:
            st.info("🟡 **FRICTION ZONE**")
            st.markdown(
                "**Real-World Impact:** Normal operational tightening. Minor rate adjustments with minimal "
                "risk of balance sheet contagion."
            )
        else:
            st.success("🟢 **ACCOMMODATIVE / NORMAL**")
            st.markdown(
                "**Real-World Impact:** Abundant liquidity in the system. Banks can freely deploy capital "
                "into commercial loans to maximize Net Interest Margin."
            )