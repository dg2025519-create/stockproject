import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(page_title="상어의 주식 바다 탐험", layout="wide", page_icon="🦈")

# 2. 바다 컨셉 CSS 및 애니메이션 HTML 추가 (보글보글 방울 & 헤엄치는 물고기)
custom_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
}

/* 바다 배경 그라데이션 (위는 얕은 바다, 아래는 깊은 바다) */
.stApp {
    background: linear-gradient(180deg, #E0F7FA 0%, #29B6F6 100%);
}

h1, h2, h3, h4, h5, h6, p, span, label {
    color: #01579B !important;
}

[data-testid="stSidebar"] {
    background-color: rgba(179, 229, 252, 0.7) !important;
}

/* 둥둥 떠다니는 상어 애니메이션 */
.shark-bob {
    font-size: 100px;
    text-align: center;
    animation: bob 3s ease-in-out infinite;
    margin: 10px 0;
}

@keyframes bob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}

/* 보글보글 물방울 애니메이션 */
.bubble {
    position: fixed;
    bottom: -50px;
    background: rgba(255, 255, 255, 0.4);
    border-radius: 50%;
    animation: rise infinite ease-in;
    z-index: 0;
    pointer-events: none; /* 클릭 방해 금지 */
}
.bubble:nth-child(1) { width: 40px; height: 40px; left: 10%; animation-duration: 8s; }
.bubble:nth-child(2) { width: 20px; height: 20px; left: 30%; animation-duration: 5s; animation-delay: 1s;}
.bubble:nth-child(3) { width: 50px; height: 50px; left: 50%; animation-duration: 7s; animation-delay: 2s;}
.bubble:nth-child(4) { width: 30px; height: 30px; left: 70%; animation-duration: 11s;}
.bubble:nth-child(5) { width: 25px; height: 25px; left: 90%; animation-duration: 6s; animation-delay: 3s;}

@keyframes rise {
    0% { bottom: -50px; transform: translateX(0); opacity: 0.8;}
    50% { transform: translateX(20px); }
    100% { bottom: 100vh; transform: translateX(-20px); opacity: 0;}
}

/* 지나가는 귀여운 물고기들 */
.fish {
    position: fixed;
    font-size: 3rem;
    animation: swim linear infinite;
    z-index: 0;
    pointer-events: none;
}
.fish1 { top: 15%; left: -10%; animation-duration: 15s; animation-delay: 0s; }
.fish2 { top: 70%; left: -10%; animation-duration: 25s; animation-delay: 5s; font-size: 2rem; }
.fish3 { top: 40%; right: -10%; animation: swim-reverse 18s linear infinite; font-size: 4rem; }

@keyframes swim {
    0% { left: -10%; transform: scaleX(-1); }
    100% { left: 110%; transform: scaleX(-1); }
}
@keyframes swim-reverse {
    0% { right: -10%; transform: scaleX(1); }
    100% { right: 110%; transform: scaleX(1); }
}
</style>

<!-- 화면에 표시될 물방울과 물고기 HTML 태그 -->
<div class="bubble"></div><div class="bubble"></div><div class="bubble"></div>
<div class="bubble"></div><div class="bubble"></div>
<div class="fish fish1">🐠</div><div class="fish fish2">🐡</div><div class="fish fish3">🐟</div>
"""
st.markdown(custom_html, unsafe_allow_html=True)

# 3. 둥둥 떠다니는 귀여운 상어 타이틀
st.markdown('<div class="shark-bob">🦈</div>', unsafe_allow_html=True)
st.title("아기 상어의 한·미 주식 바다 탐험 🌊")
st.markdown("""
당곡고등학교 친구들 안녕! 나는 주식 바다를 헤엄치는 아기 상어 탐험가야. 🐟  
내가 물어온 데이터를 바탕으로, 어떤 물고기(주식)가 쑥쑥 자라고 있는지 분석해 줄게! 뽀글뽀글 🫧
""")

TICKERS = {
    "삼성전자 (KR)": "005930.KS", "SK하이닉스 (KR)": "000660.KS", "NAVER (KR)": "035420.KS",
    "현대차 (KR)": "005380.KS", "애플 (US)": "AAPL", "마이크로소프트 (US)": "MSFT",
    "엔비디아 (US)": "NVDA", "테슬라 (US)": "TSLA"
}

st.sidebar.header("📊 탐험 설정")
selected_stocks = st.sidebar.multiselect("어떤 주식을 구경할까?", list(TICKERS.keys()), default=["삼성전자 (KR)", "애플 (US)", "엔비디아 (US)"])

end_date = datetime.today()
start_date = end_date - timedelta(days=365)
start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

@st.cache_data
def load_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        ticker_data = yf.download(TICKERS[t], start=start, end=end, progress=False)
        if not ticker_data.empty: df_close[t] = ticker_data['Close']
    return df_close

if not selected_stocks:
    st.warning("사이드바에서 구경할 주식을 하나 이상 선택해 줘! 🦈")
else:
    data = load_data(selected_stocks, start, end)
    if not data.empty and len(data) > 1:
        returns = (data / data.iloc[0] - 1) * 100
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("달러/원 기준 주가 파도 🌊")
            fig_price = px.line(data, x=data.index, y=data.columns)
            fig_price.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.4)")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("누적 수익률 달리기 🏁 (%)")
            fig_return = px.line(returns, x=returns.index, y=returns.columns)
            fig_return.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.4)")
            st.plotly_chart(fig_return, use_container_width=True)

        st.divider()
        st.header("🔍 아기 상어의 주식 성장세 평가 보고서 📝")
        
        for stock in selected_stocks:
            stock_data = data[stock].dropna()
            if len(stock_data) < 60:
                st.info(f"**{stock}**: 아직 데이터가 부족해! 조금 더 긴 기간을 선택해 줘. 🥲")
                continue

            current_price = stock_data.iloc[-1]
            ma20 = stock_data.rolling(window=20).mean().iloc[-1]
            ma60 = stock_data.rolling(window=60).mean().iloc[-1]
            total_return = (current_price / stock_data.iloc[0] - 1) * 100

            if current_price > ma20 and ma20 > ma60:
                trend_eval, emoji = "완벽한 상승 파도를 탔어! 🚀 가장 활기찬 물고기야!", "🦈✨"
            elif current_price < ma20 and ma20 < ma60:
                trend_eval, emoji = "바다 밑으로 가라앉고 있어. 💤 당장은 지켜보는 게 좋겠어.", "🐢💧"
            elif current_price > ma20 and ma20 <= ma60:
                trend_eval, emoji = "다시 힘차게 꼬리치기를 시작했어! 🐟 상승 반전일까?", "🐬🌊"
            elif current_price < ma20 and ma20 >= ma60:
                trend_eval, emoji = "최근엔 조금 지쳐서 쉬고 있네. 숨을 고르는 중일지도 몰라. 🐡", "🐳💨"
            else:
                trend_eval, emoji = "파도가 이리저리 치고 있어. 방향을 잡아가고 있는 중이야. 🌊", "🐠"

            with st.expander(f"{emoji} {stock} 분석 보기 (기간 수익률: {total_return:.2f}%)"):
                st.write(f"**현재 추세 평가:** {trend_eval}")
                st.write(f"- 현재 주가: {current_price:.2f}")
                st.write(f"- 20일 평균 주가(단기): {ma20:.2f}")
                st.write(f"- 60일 평균 주가(중장기): {ma60:.2f}")

        st.divider()
        with st.expander("테이블 형식으로 원본 데이터 보기 📋"):
            st.dataframe(data.sort_index(ascending=False))
