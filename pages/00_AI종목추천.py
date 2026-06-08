import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI

# ------------------------
# 설정
# ------------------------

st.set_page_config(
    page_title="AI 종목 추천",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI 주식 추천 시스템")

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password"
)

if not api_key:
    st.info("OpenAI API Key를 입력하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------
# 종목 리스트
# ------------------------

tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "AMD": "AMD",
    "Broadcom": "AVGO",
    "Palantir": "PLTR"
}

selected_stock = st.selectbox(
    "종목 선택",
    list(tickers.keys())
)

# ------------------------
# 데이터 수집
# ------------------------

@st.cache_data(ttl=3600)
def get_stock_info(ticker):

    stock = yf.Ticker(ticker)

    info = stock.info

    hist = stock.history(period="1y")

    current_price = hist["Close"].iloc[-1]

    return_1m = (
        current_price /
        hist["Close"].iloc[-22] - 1
    ) * 100

    return_3m = (
        current_price /
        hist["Close"].iloc[-66] - 1
    ) * 100

    return_1y = (
        current_price /
        hist["Close"].iloc[0] - 1
    ) * 100

    return {
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "market_cap": info.get("marketCap"),
        "pe": info.get("trailingPE"),
        "current_price": round(current_price, 2),
        "return_1m": round(return_1m, 2),
        "return_3m": round(return_3m, 2),
        "return_1y": round(return_1y, 2),
    }

ticker = tickers[selected_stock]

data = get_stock_info(ticker)

# ------------------------
# 정보 표시
# ------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "현재가",
    f"${data['current_price']}"
)

col2.metric(
    "1개월 수익률",
    f"{data['return_1m']}%"
)

col3.metric(
    "1년 수익률",
    f"{data['return_1y']}%"
)

st.write("### 기업 정보")

st.json(data)

# ------------------------
# AI 분석
# ------------------------

if st.button("AI 종목 분석"):

    with st.spinner("AI 분석 중..."):

        prompt = f"""
        다음 종목을 분석해줘.

        기업명: {data['company']}
        섹터: {data['sector']}
        PER: {data['pe']}
        시가총액: {data['market_cap']}
        1개월 수익률: {data['return_1m']}%
        3개월 수익률: {data['return_3m']}%
        1년 수익률: {data['return_1y']}%

        아래 형식으로 답변:

        1. 기업 요약
        2. 강점
        3. 리스크
        4. 향후 성장성
        5. 투자 의견
           - 추천
           - 중립
           - 주의

        한국어로 작성.
        """

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content

        st.markdown(result)
