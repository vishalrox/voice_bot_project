# dashboard.py

import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from backend import DB_PATH  # make sure backend.py defines DB_PATH = "bot_data.db"


# ------------- Helpers ------------- #

def load_logs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT timestamp, user_query, intent, response, success
        FROM interaction_logs
        ORDER BY timestamp DESC
        """,
        conn,
    )
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ------------- Page Config & Custom Theme ------------- #

st.set_page_config(
    page_title="Simplotel Voice Bot Analytics",
    page_icon="🏨",
    layout="wide",
)

PRIMARY = "#0078FF"   # Simplotel blue
ACCENT = "#FF8A00"    # warm accent
BG_LIGHT = "#F5F7FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2933"

# Custom CSS to make it feel like a polished SaaS dashboard
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {BG_LIGHT};
            font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        .main-title {{
            font-size: 32px;
            font-weight: 700;
            color: {TEXT_DARK};
            margin-bottom: 0.25rem;
        }}
        .sub-title {{
            font-size: 14px;
            color: #6B7280;
            margin-bottom: 1.5rem;
        }}
        .metric-card {{
            background: {CARD_BG};
            padding: 1rem 1.25rem;
            border-radius: 14px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
            border: 1px solid #E5E7EB;
        }}
        .metric-label {{
            font-size: 13px;
            text-transform: uppercase;
            color: #6B7280;
            letter-spacing: 0.08em;
        }}
        .metric-value {{
            font-size: 26px;
            font-weight: 700;
            color: {TEXT_DARK};
        }}
        .metric-chip {{
            display: inline-block;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(0,120,255,0.08);
            color: {PRIMARY};
            margin-top: 0.35rem;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: {TEXT_DARK};
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}
        .intent-bar .stPlotlyChart, .intent-bar .stAltairChart {{
            background: {CARD_BG};
            padding: 1rem 1.25rem 0.5rem 1.25rem;
            border-radius: 14px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
            border: 1px solid #E5E7EB;
        }}
        .dataframe-container {{
            background: {CARD_BG};
            padding: 1rem 1.25rem;
            border-radius: 14px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
            border: 1px solid #E5E7EB;
        }}
        .small-label {{
            font-size: 11px;
            color: #9CA3AF;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------- Header ------------- #

st.markdown(
    """
    <div>
        <div class="main-title">Voice Bot Analytics Dashboard</div>
        <div class="sub-title">
            Live insights from your Simplotel voice assistant – track intents, performance, and user queries.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

df = load_logs()

if df.empty:
    st.info("No interactions logged yet. Start the bot and talk to it to see analytics here.")
    st.stop()

# ------------- Filters Row ------------- #

with st.expander("Filters", expanded=False):
    col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 1])

    with col_f1:
        date_range = st.date_input(
            "Filter by date range",
            value=[df["timestamp"].min().date(), df["timestamp"].max().date()],
        )
    with col_f2:
        intents_list = ["All"] + sorted(df["intent"].unique().tolist())
        selected_intent = st.selectbox("Filter by intent", intents_list, index=0)
    with col_f3:
        search_text = st.text_input("Search in user queries", "")

    # Apply filters
    filtered = df.copy()
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["timestamp"].dt.date >= start_date)
            & (filtered["timestamp"].dt.date <= end_date)
        ]

    if selected_intent != "All":
        filtered = filtered[filtered["intent"] == selected_intent]

    if search_text.strip():
        filtered = filtered[filtered["user_query"].str.contains(search_text.strip(), case=False)]

    if filtered.empty:
        st.warning("No records match the selected filters.")
        st.stop()

# ------------- KPI Cards ------------- #

total = len(filtered)
success = filtered["success"].sum()
success_rate = round((success / total) * 100, 2) if total > 0 else 0.0
unique_intents = filtered["intent"].nunique()
latest_ts = filtered["timestamp"].max()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total interactions</div>
            <div class="metric-value">{total}</div>
            <div class="metric-chip">Across all filtered sessions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Successful responses</div>
            <div class="metric-value">{int(success)}</div>
            <div class="metric-chip">User queries handled confidently</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Success rate</div>
            <div class="metric-value">{success_rate}%</div>
            <div class="metric-chip">Higher is better 😀</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active intents</div>
            <div class="metric-value">{unique_intents}</div>
            <div class="metric-chip">Last activity: {latest_ts.strftime('%d %b %Y, %H:%M')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------- Intent Distribution + Trend ------------- #

st.markdown('<div class="section-title">Intent distribution</div>', unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns([1.3, 1])

# Bar chart – intents
with col_chart1:
    intent_counts = (
        filtered["intent"]
        .value_counts()
        .rename_axis("intent")
        .reset_index(name="count")
    )
    intent_counts = intent_counts.sort_values("count", ascending=True)

    st.markdown('<div class="intent-bar">', unsafe_allow_html=True)
    st.bar_chart(
        data=intent_counts,
        x="intent",
        y="count",
        height=260,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Success vs failure mini-summary
with col_chart2:
    success_df = filtered.copy()
    success_df["status"] = success_df["success"].map({1: "Success", 0: "Fallback"})
    status_counts = success_df["status"].value_counts()

    st.markdown(
        f"""
        <div class="metric-card" style="margin-top: 0.25rem;">
            <div class="metric-label">Response quality</div>
            <div class="metric-value">{int(status_counts.get('Success', 0))} good</div>
            <div class="small-label">
                {int(status_counts.get('Fallback', 0))} fallbacks • Try adding more intents or training data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------- Recent Interactions Table ------------- #

st.markdown('<div class="section-title">Recent interactions</div>', unsafe_allow_html=True)

display_df = filtered.copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)
st.markdown('</div>', unsafe_allow_html=True)
