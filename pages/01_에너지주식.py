import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="에너지 바다 탐험", layout="wide", page_icon="⚡")

# 애니메이션 CSS 적용
custom_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
html, body, [class*="css"] { font-family: 'Jua', sans-serif !important; }
.stApp { background: linear-gradient(180deg, #E0F7FA 0%, #29B6F6 100%); }
h1, h2, h3, h4, h5, h6, p, span, label { color: #01579B !important; }
[data-testid="stSidebar"] { background-color: rgba(179, 229, 252, 0.7) !important; }
.shark-bob { font-size: 100px; text-align: center; animation: bob 3s ease-in-out infinite; margin: 10px 0; }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
.bubble { position: fixed; bottom: -50px; background: rgba(255,255,255,0.4); border-radius: 50%; animation: rise infinite ease-in; z-index: 0; pointer-events: none; }
.bubble:nth-child(1) { width: 45px; height: 45px; left: 15%; animation-duration: 9s; }
.bubble:nth-child(2) { width: 25px; height: 25px; left: 60%; animation-duration: 7s; animation-delay: 1s; }
@keyframes rise { 0% { bottom: -50px; transform: translateX(0); opacity: 0.8;} 50% { transform: translateX(20px); } 100% { bottom: 100vh; transform: translateX(-20px); opacity: 0;} }
.fish { position: fixed; font-size: 3rem; animation: swim linear infinite; z-index: 0; pointer-events: none; }
.fish1 { top: 80%; left: -10%; animation-duration: 18s; font-size: 2.5rem; }
@keyframes swim { 0% { left: -10%; transform: scaleX(-1); } 100% { left: 110%; transform: scaleX(-1); } }
</style>
<div class="bubble"></div><div class="bubble"></div>
<div class="fish fish1">전기장어 ⚡</div>
"""
st.markdown(custom_html, unsafe_allow_html=True)

st.markdown('<div class="shark-bob">🌋🦈</div>', unsafe_allow_html=True)
st.title("아기 상어의 에너지 바다 탐험 ⚡")

ENERGY_TICKERS = {
    "LG에너지솔루션 (KR)": "373220.KS", "SK이노베이션 (KR)": "096770.KS", "S-Oil (KR)": "010950.KS",
    "엑슨모빌 (US)": "XOM", "셰브론 (US)": "CVX", "넥스트에라 에너지 (US)": "NEE"
}

st.sidebar.header("⚡ 에너지 탐험 설정")
selected_energy_stocks = st.sidebar.multiselect("어떤 에너지 주식을 구경할까?", list(ENERGY_TICKERS.keys()), default=["엑슨모빌 (US)", "LG에너지솔루션 (KR)"])

end_date = datetime.today()
start_date = end_date - timedelta(days=365)
start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

@st.cache_data
def load_energy_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        ticker_data = yf.download(ENERGY_TICKERS[t], start=start, end=end, progress=False)
        if not ticker_data.empty: df_close[t] = ticker_data['Close']
    return df_close

if selected_energy_stocks:
    data = load_energy_data(selected_energy_stocks, start, end)
    if not data.empty and len(data) > 1:
        returns = (data / data.iloc[0] - 1) * 100
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("주가 파도 🌊")
            fig1 = px.line(data, x=data.index, y=data.columns)
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.4)")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.subheader("수익률 달리기 🏁 (%)")
            fig2 = px.line(returns, x=returns.index, y=returns.columns)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.4)")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.divider()
        st.header("🔋 에너지 충전 상태 평가 📝")
        for stock in selected_energy_stocks:
            stock_data = data[stock].dropna()
            if len(stock_data) >= 60:
                cur, ma20, ma60 = stock_data.iloc[-1], stock_data.rolling(20).mean().iloc[-1], stock_data.rolling(60).mean().iloc[-1]
                if cur > ma20 and ma20 > ma60: st.success(f"🦈⚡ **{stock}**: 배터리가 100% 충전됐어! 에너지를 뿜어내며 상승 중!")
                elif cur < ma20 and ma20 < ma60: st.error(f"🐢🔌 **{stock}**: 에너지가 떨어져서 가라앉고 있어. 충전이 필요해.")
                else: st.info(f"🌋 **{stock}**: 에너지를 모으면서 다음 분출을 준비하거나 열을 식히는 중이야.")
