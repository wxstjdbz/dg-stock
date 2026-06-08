# pages/00_AI종목추천.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(
page_title="AI 종목 추천",
page_icon="🤖",
layout="wide"
)

st.title("🤖 AI 종목 추천 시스템")

st.markdown(
"""
최근 수익률, 변동성, 기업 규모를 기반으로
AI 점수를 계산합니다.
"""
)

TICKERS = {
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

@st.cache_data(ttl=3600)
def analyze_stock(ticker):

```
stock = yf.Ticker(ticker)

hist = stock.history(period="1y")

if len(hist) < 100:
    return None

info = stock.info

close = hist["Close"]

ret_1m = (close.iloc[-1] / close.iloc[-22] - 1) * 100
ret_3m = (close.iloc[-1] / close.iloc[-66] - 1) * 100
ret_1y = (close.iloc[-1] / close.iloc[0] - 1) * 100

volatility = close.pct_change().std() * np.sqrt(252) * 100

market_cap = info.get("marketCap", 0)

score = (
    ret_1m * 0.2 +
    ret_3m * 0.3 +
    ret_1y * 0.4 -
    volatility * 0.1
)

return {
    "종목": ticker,
    "회사명": info.get("shortName", ticker),
    "1개월수익률": round(ret_1m, 2),
    "3개월수익률": round(ret_3m, 2),
    "1년수익률": round(ret_1y, 2),
    "변동성": round(volatility, 2),
    "시가총액": market_cap,
    "AI점수": round(score, 2)
}
```

if st.button("AI 추천 종목 분석"):

```
results = []

progress = st.progress(0)

for idx, ticker in enumerate(TICKERS.values()):

    try:
        data = analyze_stock(ticker)

        if data:
            results.append(data)

    except Exception:
        pass

    progress.progress((idx + 1) / len(TICKERS))

if len(results) == 0:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

df = pd.DataFrame(results)

df = df.sort_values(
    "AI점수",
    ascending=False
)

st.subheader("🏆 AI 추천 순위")

st.dataframe(
    df,
    use_container_width=True
)

top = df.iloc[0]

st.success(
    f"""
    오늘의 추천 종목:
    {top['회사명']} ({top['종목']})

    AI 점수: {top['AI점수']}
    """
)

st.subheader("📈 투자 의견")

if top["AI점수"] >= 50:
    st.info("강력 추천")

elif top["AI점수"] >= 20:
    st.info("추천")

elif top["AI점수"] >= 0:
    st.warning("중립")

else:
    st.error("주의")
```
