import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="바이오 바다 탐험", layout="wide", page_icon="💊")

# 메인 페이지와 동일한 애니메이션 CSS 적용
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
.bubble:nth-child(1) { width: 40px; height: 40px; left: 20%; animation-duration: 8s; }
.bubble:nth-child(2) { width: 30px; height: 30px; left: 40%; animation-duration: 6s; animation-delay: 2s; }
.bubble:nth-child(3) { width: 50px; height: 50px; left: 80%; animation-duration: 10s; }
@keyframes rise { 0% { bottom: -50px; transform: translateX(0); opacity: 0.8;} 50% { transform: translateX(20px); } 100% { bottom: 100vh; transform: translateX(-20px); opacity: 0;} }
.fish { position: fixed; font-size: 3rem; animation: swim linear infinite; z-index: 0; pointer-events: none; }
.fish1 { top: 25%; left: -10%; animation-duration: 12s; }
.fish2 { top: 55%; right: -10%; animation: swim-reverse 15s linear infinite; font-size: 2.5rem; }
@keyframes swim { 0% { left: -10%; transform: scaleX(-1); } 100% { left: 110%; transform: scaleX(-1); } }
@keyframes swim-reverse { 0% { right: -10%; transform: scaleX(1); } 100% { right: 110%; transform: scaleX(1); } }
</style>
<div class="bubble"></div><div class="bubble"></div><div class="bubble"></div>
<div class="fish fish1">🐡</div><div class="fish fish2">🧬</div>
"""
st.markdown(custom_html, unsafe_allow_html=True)

st.markdown('<div class="shark-bob">🩺🦈</div>', unsafe_allow_html=True)
st.title("아기 상어의 바이오(Bio) 바다 탐험 🧬")

BIO_TICKERS = {
    "삼성바이오로직스 (KR)": "207940.KS", "셀트리온 (KR)": "068270.KS", "유한양행 (KR)": "000100.KS",
    "일라이 릴리 (US)": "LLY", "노보 노디스크 (US)": "NVO", "존슨앤드존슨 (US)": "JNJ", "화이자 (US)": "PFE"
}

st.sidebar.header("🧪 바이오 탐험 설정")
selected_bio_stocks = st.sidebar.multiselect("어떤 바이오 주식을 구경할까?", list(BIO_TICKERS.keys()), default=["삼성바이오로직스 (KR)", "일라이 릴리 (US)"])

end_date = datetime.today()
start_date = end_date - timedelta(days=365)
start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

@st.cache_data
def load_bio_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        ticker_data = yf.download(BIO_TICKERS[t], start=start, end=end, progress=False)
        if not ticker_data.empty: df_close[t] = ticker_data['Close']
    return df_close

if selected_bio_stocks:
    data = load_bio_data(selected_bio_stocks, start, end)
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
        st.header("🩺 바이오 주식 건강 검진 결과 📝")
        for stock in selected_bio_stocks:
            stock_data = data[stock].dropna()
            if len(stock_data) >= 60:
                cur, ma20, ma60 = stock_data.iloc[-1], stock_data.rolling(20).mean().iloc[-1], stock_data.rolling(60).mean().iloc[-1]
                if cur > ma20 and ma20 > ma60: st.success(f"🦈✨ **{stock}**: 아주 건강하게 성장하고 있어! 에너지가 넘쳐!")
                elif cur < ma20 and ma20 < ma60: st.error(f"🐢💧 **{stock}**: 활력이 많이 떨어졌어. 휴식이 필요해 보여.")
                else: st.info(f"🐬🌊 **{stock}**: 건강을 회복하거나 파도를 이리저리 타는 중이야!")
