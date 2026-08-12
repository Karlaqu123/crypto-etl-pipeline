import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

st.set_page_config(
    page_title="Crypto Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #FFFFFF;
}

/* Main headings */
h1, h2, h3 {
    color: #166534;
}

/* Normal text */
p {
    color: #374151;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #166534;
    font-weight: 600;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #111827;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    padding: 18px;
    border-radius: 10px;
}

/* Dataframe border */
[data-testid="stDataFrame"] {
    border: 1px solid #DCFCE7;
    border-radius: 8px;
}

/* Selectbox label */
[data-testid="stSelectbox"] label {
    color: #166534;
    font-weight: 600;
}

/* Divider */
hr {
    border-color: #DCFCE7;
}

</style>
""", unsafe_allow_html=True)

st.title("Crypto Market Dashboard")

st.markdown(
    """
    <div style="
        width: 70px;
        height: 4px;
        background-color: #16A34A;
        border-radius: 4px;
        margin-top: -10px;
        margin-bottom: 20px;">
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Historical cryptocurrency market data collected by an automated ETL pipeline."
)

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if database_url is None:
        database_url = st.secrets["DATABASE_URL"]

    return database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


@st.cache_resource
def get_engine():
    return create_engine(get_database_url())


engine = get_engine()


latest_query = """
SELECT *
FROM crypto_market_history
WHERE extracted_at_utc = (
    SELECT MAX(extracted_at_utc)
    FROM crypto_market_history
)
ORDER BY market_cap_rank;
"""

latest_df = pd.read_sql(latest_query, engine)

latest_update = latest_df["extracted_at_utc"].max()

latest_update_ph = (
    pd.Timestamp(latest_update)
    .tz_convert("Asia/Manila")
    .strftime("%b %d, %Y • %I:%M %p PHT")
)

st.caption(f"Last pipeline update: {latest_update_ph}")


# Summary metrics
bitcoin_row = latest_df[latest_df["coin_id"] == "bitcoin"].iloc[0]
ethereum_row = latest_df[latest_df["coin_id"] == "ethereum"].iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Bitcoin Price",
    f"${bitcoin_row['current_price_usd']:,.2f}"
)

col2.metric(
    "Ethereum Price",
    f"${ethereum_row['current_price_usd']:,.2f}"
)

col3.metric(
    "Coins Tracked",
    len(latest_df)
)


st.subheader("Latest Crypto Market Snapshot")

display_df = latest_df[
    [
        "market_cap_rank",
        "coin_name",
        "symbol",
        "current_price_usd",
        "market_cap_usd",
        "price_change_percentage_24h"
    ]
].copy()

def format_market_cap(value):
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.0f}"

display_df = display_df.rename(columns={
    "market_cap_rank": "Rank",
    "coin_name": "Coin",
    "symbol": "Symbol",
    "current_price_usd": "Price (USD)",
    "market_cap_usd": "Market Cap (USD)",
    "price_change_percentage_24h": "24h Change (%)"
})

display_df["Market Cap (USD)"] = display_df["Market Cap (USD)"].apply(
    format_market_cap
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Price (USD)": st.column_config.NumberColumn(
            format="$%.2f"
        ),
        "24h Change (%)": st.column_config.NumberColumn(
            format="%.2f%%"
        )
    }
)


st.subheader("Price History")

coins = latest_df["coin_name"].tolist()

selected_coin = st.selectbox(
    "Select cryptocurrency",
    coins
)

history_query = """
SELECT
    coin_name,
    current_price_usd,
    extracted_at_utc
FROM crypto_market_history
WHERE coin_name = %(coin_name)s
ORDER BY extracted_at_utc;
"""

history_df = pd.read_sql(
    history_query,
    engine,
    params={"coin_name": selected_coin}
)

history_df["extracted_at_utc"] = pd.to_datetime(
    history_df["extracted_at_utc"],
    utc=True
)

history_df["extracted_at_ph"] = (
    history_df["extracted_at_utc"]
    .dt.tz_convert("Asia/Manila")
)

history_df = history_df.set_index("extracted_at_ph")

st.line_chart(
    history_df["current_price_usd"]
)