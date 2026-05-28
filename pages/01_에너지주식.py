import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(page_title="에너지 바다 탐험", layout="wide", page_icon="⚡")

# 2. 상어와 바다 컨셉 커스텀 CSS 적용
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
html, body, [class*="css"] { font-family: 'Jua', sans-serif !important; }
.stApp { background: linear-gradient(180deg, #E0F7FA 0%, #81D4FA 100%); }
h1, h2, h3, h4, h5, h6, p, span, label { color: #01579B !important; }
[data-testid="stSidebar"] { background-color: #B3E5FC !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. 에너지 시장 대표 주식 티커
ENERGY_TICKERS = {
    "LG에너지솔루션 (KR)": "373220.KS", # 2차전지(배터리)
    "SK이노베이션 (KR)": "096770.KS",   # 정유 및 배터리
    "S-Oil (KR)": "010950.KS",        # 정유
    "엑슨모빌 (US)": "XOM",            # 글로벌 최대 석유 기업
    "셰브론 (US)": "CVX",             # 글로벌 석유 기업
    "넥스트에라 에너지 (US)": "NEE",     # 친환경/재생에너지
    "엔페이즈 에너지 (US)": "ENPH"      # 태양광
}

st.title("🦈 아기 상어의 에너지 바다 탐험 ⚡")
st.markdown("""
안녕! 여기는 바다 깊은 곳, 에너지가 뿜어져 나오는 **'심해 화산 지대(에너지 섹터)'**야. 🌋  
석유 같은 전통 에너지부터 전기장어를 닮은 배터리, 친환경 에너지까지!  
어떤 물고기들이 가장 뜨거운 에너지를 뿜어내고 있는지 확인해 볼까? 뽀글뽀글 🫧
""")

st.sidebar.header("⚡ 에너지 탐험 설정")
selected_energy_stocks = st.sidebar.multiselect(
    "어떤 에너지 주식을 구경할까?",
    list(ENERGY_TICKERS.keys()),
    default=["엑슨모빌 (US)", "LG에너지솔루션 (KR)", "넥스트에라 에너지 (US)"]
)

end_date = datetime.today()
start_date = end_date - timedelta(days=365)
start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

@st.cache_data
def load_energy_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        symbol = ENERGY_TICKERS[t]
        ticker_data = yf.download(symbol, start=start, end=end, progress=False)
        if not ticker_data.empty:
            df_close[t] = ticker_data['Close']
    return df_close

if not selected_energy_stocks:
    st.warning("사이드바에서 구경할 에너지 주식을 하나 이상 선택해 줘! 🦈")
else:
    data = load_energy_data(selected_energy_stocks, start, end)

    if not data.empty and len(data) > 1:
        returns = (data / data.iloc[0] - 1) * 100
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("달러/원 기준 주가 파도 🌊")
            fig_price = px.line(data, x=data.index, y=data.columns)
            fig_price.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("누적 수익률 달리기 🏁 (%)")
            fig_return = px.line(returns, x=returns.index, y=returns.columns)
            fig_return.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_return, use_container_width=True)

        st.divider()
        st.header("🔋 아기 상어의 에너지 충전 상태 평가 📝")
        
        for stock in selected_energy_stocks:
            stock_data = data[stock].dropna()
            if len(stock_data) < 60:
                st.info(f"**{stock}**: 데이터가 부족해! 조금 더 긴 기간을 선택해 줘. 🥲")
                continue

            current_price = stock_data.iloc[-1]
            ma20 = stock_data.rolling(window=20).mean().iloc[-1]
            ma60 = stock_data.rolling(window=60).mean().iloc[-1]
            total_return = (current_price / stock_data.iloc[0] - 1) * 100

            if current_price > ma20 and ma20 > ma60:
                trend_eval = "배터리가 100% 충전됐어! 🚀 에너지를 뿜어내며 바다를 가르고 상승 중이야!"
                emoji = "🦈⚡"
            elif current_price < ma20 and ma20 < ma60:
                trend_eval = "에너지가 다 떨어져서 바닥으로 가라앉고 있어. 💤 충전이 필요해 보여."
                emoji = "🐢🔌"
            elif current_price > ma20 and ma20 <= ma60:
                trend_eval = "한동안 힘이 없었는데, 다시 전기를 찌릿찌릿 뿜어내며 상승하기 시작했어! 🔋"
                emoji = "전기장어 ⚡"
            elif current_price < ma20 and ma20 >= ma60:
                trend_eval = "아주 뜨겁게 달아올랐다가 지금은 잠시 엔진을 식히는 중이야. 과열 방지! 🌋"
                emoji = "🐳💨"
            else:
                trend_eval = "에너지를 모으면서 다음 분출을 준비하고 있는 중이야. 🌊"
                emoji = "🐠"

            with st.expander(f"{emoji} {stock} 충전율 보기 (기간 수익률: {total_return:.2f}%)"):
                st.write(f"**현재 에너지 상태:** {trend_eval}")
                st.write(f"- 현재 주가: {current_price:.2f}")
                st.write(f"- 20일 평균(단기 에너지): {ma20:.2f}")
                st.write(f"- 60일 평균(장기 에너지): {ma60:.2f}")

        st.divider()
        with st.expander("테이블 형식으로 원본 데이터 보기 📋"):
            st.dataframe(data.sort_index(ascending=False))
