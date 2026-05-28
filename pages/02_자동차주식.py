import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(page_title="자동차 바다 탐험", layout="wide", page_icon="🏎️")

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

# 3. 자동차/모빌리티 시장 대표 주식 티커
AUTO_TICKERS = {
    "현대차 (KR)": "005380.KS",
    "기아 (KR)": "000270.KS",
    "테슬라 (US)": "TSLA",         # 글로벌 전기차 1위
    "토요타 (US)": "TM",           # 글로벌 자동차 판매 1위 (미국 상장 ADR 기준)
    "포드 (US)": "F",              # 미국 전통 자동차
    "제너럴모터스 (US)": "GM",        # 미국 전통 자동차
    "리비안 (US)": "RIVN"          # 신흥 전기차(픽업트럭)
}

st.title("🦈 아기 상어의 모빌리티(자동차) 바다 탐험 🏎️")
st.markdown("""
안녕! 여기는 물살이 가장 빠른 **'고속 해류 레이싱 구역(자동차/모빌리티 섹터)'**이야. 🌊  
전통적인 지느러미(내연기관)를 가진 물고기부터, 전기 모터를 달고 쌩쌩 달리는 물고기(전기차)까지!  
어떤 물고기가 가장 빠르게 파도를 타고 있는지 중계해 줄게! 뽀글뽀글 🫧
""")

st.sidebar.header("🏎️ 레이싱 탐험 설정")
selected_auto_stocks = st.sidebar.multiselect(
    "어떤 자동차 주식을 구경할까?",
    list(AUTO_TICKERS.keys()),
    default=["현대차 (KR)", "테슬라 (US)", "토요타 (US)"]
)

end_date = datetime.today()
start_date = end_date - timedelta(days=365)
start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

@st.cache_data
def load_auto_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        symbol = AUTO_TICKERS[t]
        ticker_data = yf.download(symbol, start=start, end=end, progress=False)
        if not ticker_data.empty:
            df_close[t] = ticker_data['Close']
    return df_close

if not selected_auto_stocks:
    st.warning("사이드바에서 구경할 자동차 주식을 하나 이상 선택해 줘! 🦈")
else:
    data = load_auto_data(selected_auto_stocks, start, end)

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
        st.header("🏁 아기 상어의 레이싱 속도 평가 📝")
        
        for stock in selected_auto_stocks:
            stock_data = data[stock].dropna()
            if len(stock_data) < 60:
                st.info(f"**{stock}**: 데이터가 부족해! 조금 더 긴 기간을 선택해 줘. 🥲")
                continue

            current_price = stock_data.iloc[-1]
            ma20 = stock_data.rolling(window=20).mean().iloc[-1]
            ma60 = stock_data.rolling(window=60).mean().iloc[-1]
            total_return = (current_price / stock_data.iloc[0] - 1) * 100

            if current_price > ma20 and ma20 > ma60:
                trend_eval = "부스터 온! 🔥 앞지르기를 멈추지 않고 최고 속도로 물살을 가르는 중이야!"
                emoji = "🦈🏎️"
            elif current_price < ma20 and ma20 < ma60:
                trend_eval = "타이어 펑크! 💥 속도가 줄어들면서 꼴찌로 밀려나고 있어. 피트 스탑(수리)이 필요해."
                emoji = "🐢🔧"
            elif current_price > ma20 and ma20 <= ma60:
                trend_eval = "한동안 뒤처져 있었는데, 다시 엑셀을 밟고 무섭게 치고 올라오고 있어! 역전의 명수 🏁"
                emoji = "돌고래 🐬"
            elif current_price < ma20 and ma20 >= ma60:
                trend_eval = "너무 빨리 달렸나 봐! 엔진 과열로 잠시 브레이크를 밟고 속도를 조절 중이야. 🛑"
                emoji = "🐳💨"
            else:
                trend_eval = "다른 물고기들과 치열하게 눈치 싸움을 하며 나란히 헤엄치고 있어. 🌊"
                emoji = "🐠"

            with st.expander(f"{emoji} {stock} 주행 기록 보기 (기간 수익률: {total_return:.2f}%)"):
                st.write(f"**현재 레이싱 상태:** {trend_eval}")
                st.write(f"- 현재 주가(속도): {current_price:.2f}")
                st.write(f"- 20일 평균(최근 가속력): {ma20:.2f}")
                st.write(f"- 60일 평균(기초 속도): {ma60:.2f}")

        st.divider()
        with st.expander("테이블 형식으로 원본 데이터 보기 📋"):
            st.dataframe(data.sort_index(ascending=False))
