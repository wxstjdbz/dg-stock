import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="글로벌 주식 수익률 비교",
    page_icon="📈",
    layout="wide"
)

st.title("📈 한국 vs 미국 주요 주식 수익률 비교")
st.markdown("yfinance 기반 글로벌 주식 비교 대시보드")

# -----------------------
# 종목 목록
# -----------------------

stocks = {
    "한국": {
        "삼성전자": "005930.KS",
        "SK하이닉스": "000660.KS",
        "NAVER": "035420.KS",
        "카카오": "035720.KS",
        "현대차": "005380.KS",
        "LG에너지솔루션": "373220.KS",
        "POSCO홀딩스": "005490.KS"
    },
    "미국": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Nvidia": "NVDA",
        "Amazon": "AMZN",
        "Google": "GOOGL",
        "Meta": "META",
        "Tesla": "TSLA"
    }
}

# -----------------------
# 사이드바
# -----------------------

st.sidebar.header("설정")

period = st.sidebar.selectbox(
    "조회 기간",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

selected_korea = st.sidebar.multiselect(
    "한국 주식",
    list(stocks["한국"].keys()),
    default=["삼성전자", "SK하이닉스"]
)

selected_us = st.sidebar.multiselect(
    "미국 주식",
    list(stocks["미국"].keys()),
    default=["Apple", "Nvidia"]
)

selected_names = selected_korea + selected_us

if len(selected_names) == 0:
    st.warning("최소 1개 종목을 선택하세요.")
    st.stop()

# -----------------------
# 데이터 다운로드
# -----------------------

@st.cache_data(ttl=3600)
def load_data(ticker, period):
    df = yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False
    )
    return df

returns_df = pd.DataFrame()

for name in selected_names:

    if name in stocks["한국"]:
        ticker = stocks["한국"][name]
    else:
        ticker = stocks["미국"][name]

    data = load_data(ticker, period)

    if len(data) == 0:
        continue

    normalized = (
        data["Close"] /
        data["Close"].iloc[0] - 1
    ) * 100

    returns_df[name] = normalized

returns_df = returns_df.dropna(how="all")

# -----------------------
# 수익률 차트
# -----------------------

st.subheader("📊 누적 수익률 비교 (%)")

fig = px.line(
    returns_df,
    x=returns_df.index,
    y=returns_df.columns,
    labels={
        "value": "수익률 (%)",
        "index": "날짜"
    }
)

fig.update_layout(
    height=650,
    legend_title="종목",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------
# 현재 성과 테이블
# -----------------------

performance = (
    returns_df.iloc[-1]
    .sort_values(ascending=False)
    .reset_index()
)

performance.columns = [
    "종목",
    "누적수익률(%)"
]

st.subheader("🏆 기간별 성과 순위")

st.dataframe(
    performance,
    use_container_width=True
)

# -----------------------
# 시장별 요약
# -----------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("🇰🇷 한국 시장")

    korea_cols = [
        x for x in returns_df.columns
        if x in selected_korea
    ]

    if korea_cols:
        st.metric(
            "평균 수익률",
            f"{returns_df[korea_cols].iloc[-1].mean():.2f}%"
        )

with col2:
    st.subheader("🇺🇸 미국 시장")

    us_cols = [
        x for x in returns_df.columns
        if x in selected_us
    ]

    if us_cols:
        st.metric(
            "평균 수익률",
            f"{returns_df[us_cols].iloc[-1].mean():.2f}%"
        )

# -----------------------
# 원본 데이터
# -----------------------

with st.expander("원본 수익률 데이터"):
    st.dataframe(
        returns_df.round(2),
        use_container_width=True
    )
