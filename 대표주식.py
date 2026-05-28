import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="상어의 주식 바다 탐험", layout="wide", page_icon="🦈")

# 2. 상어와 바다 컨셉 커스텀 CSS 적용
# 구글 폰트 'Jua'를 불러오고, 배경을 바다 느낌의 그라데이션으로 바꿉니다.
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

/* 전체 폰트 적용 */
html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
}

/* 배경 그라데이션 (바다 느낌) */
.stApp {
    background: linear-gradient(180deg, #E0F7FA 0%, #81D4FA 100%);
}

/* 글씨 색상 (깊은 바다색) */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: #01579B !important;
}

/* 사이드바 배경 */
[data-testid="stSidebar"] {
    background-color: #B3E5FC !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# 주요 주식 티커(Ticker) 딕셔너리
TICKERS = {
    "삼성전자 (KR)": "005930.KS",
    "SK하이닉스 (KR)": "000660.KS",
    "NAVER (KR)": "035420.KS",
    "현대차 (KR)": "005380.KS",
    "애플 (US)": "AAPL",
    "마이크로소프트 (US)": "MSFT",
    "엔비디아 (US)": "NVDA",
    "테슬라 (US)": "TSLA"
}

st.title("🦈 아기 상어의 한·미 주식 바다 탐험 🌊")
st.markdown("""
당곡고등학교 친구들 안녕! 나는 주식 바다를 헤엄치는 아기 상어 탐험가야. 🐟  
내가 물어온 데이터를 바탕으로, 어떤 물고기(주식)가 쑥쑥 자라고 있는지 분석해 줄게! 뽀글뽀글 🫧
""")

# 사이드바 설정 (UI)
st.sidebar.header("📊 탐험 설정")
selected_stocks = st.sidebar.multiselect(
    "어떤 주식을 구경할까?",
    list(TICKERS.keys()),
    default=["삼성전자 (KR)", "애플 (US)", "엔비디아 (US)"]
)

# 날짜 선택
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

# 데이터 불러오기 함수
@st.cache_data
def load_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        symbol = TICKERS[t]
        ticker_data = yf.download(symbol, start=start, end=end, progress=False)
        if not ticker_data.empty:
            df_close[t] = ticker_data['Close']
    return df_close

if not selected_stocks:
    st.warning("사이드바에서 구경할 주식을 하나 이상 선택해 줘! 🦈")
else:
    # 데이터 로드
    data = load_data(selected_stocks, start, end)

    if not data.empty and len(data) > 1:
        # 누적 수익률 계산
        returns = (data / data.iloc[0] - 1) * 100

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("달러/원 기준 주가 파도 🌊")
            fig_price = px.line(data, x=data.index, y=data.columns)
            # 차트 배경 투명하게 설정
            fig_price.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("누적 수익률 달리기 🏁 (%)")
            fig_return = px.line(returns, x=returns.index, y=returns.columns)
            fig_return.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_return, use_container_width=True)

        st.divider()

        # ---------------------------------------------------------
        # 💡 새로운 기능: 아기 상어의 종목별 1:1 맞춤 평가 시스템
        # ---------------------------------------------------------
        st.header("🔍 아기 상어의 주식 성장세 평가 보고서 📝")
        st.markdown("최근 주가의 흐름(20일 및 60일 이동평균선)을 바탕으로 현재 이 주식이 어떤 파도를 타고 있는지 분석해 줄게!")

        for stock in selected_stocks:
            stock_data = data[stock].dropna()
            
            # 최소 60일의 데이터가 있어야 장기 분석이 가능함
            if len(stock_data) < 60:
                st.info(f"**{stock}**: 아직 데이터가 부족해서 분석하기 어려워! 조금 더 긴 기간을 선택해 줘. 🥲")
                continue

            # 최근 종가, 20일 평균(단기 추세), 60일 평균(중장기 추세) 계산
            current_price = stock_data.iloc[-1]
            ma20 = stock_data.rolling(window=20).mean().iloc[-1]
            ma60 = stock_data.rolling(window=60).mean().iloc[-1]
            
            # 전체 기간(선택한 기간) 동안의 수익률
            total_return = (current_price / stock_data.iloc[0] - 1) * 100

            # 평가 알고리즘 로직
            if current_price > ma20 and ma20 > ma60:
                trend_eval = "단기적으로도, 장기적으로도 모두 쑥쑥 자라나는 완벽한 상승 파도를 탔어(정배열)! 🚀 가장 활기찬 물고기야!"
                emoji = "🦈✨"
            elif current_price < ma20 and ma20 < ma60:
                trend_eval = "최근 힘이 빠져서 바다 밑으로 가라앉고 있어(역배열). 💤 당장은 섣불리 다가가지 말고 지켜보는 게 좋겠어."
                emoji = "🐢💧"
            elif current_price > ma20 and ma20 <= ma60:
                trend_eval = "장기적으로는 조금 내려가는 중이었지만, 최근 들어 다시 힘차게 꼬리치기를 시작했어! 🐟 상승 반전일까?"
                emoji = "🐬🌊"
            elif current_price < ma20 and ma20 >= ma60:
                trend_eval = "그동안 쑥쑥 크고 있었는데, 최근 단기적으로는 조금 지쳐서 쉬고 있네. 잠시 숨을 고르는 중일지도 몰라. 🐡"
                emoji = "🐳💨"
            else:
                trend_eval = "파도가 이리저리 치고 있어. 방향을 잡아가고 있는 중이야. 🌊"
                emoji = "🐠"

            # 화면에 평가 결과 출력
            with st.expander(f"{emoji} {stock} 분석 보기 (기간 수익률: {total_return:.2f}%)"):
                st.write(f"**현재 추세 평가:** {trend_eval}")
                st.write(f"- 현재 주가: {current_price:.2f}")
                st.write(f"- 최근 20일 평균 주가(단기): {ma20:.2f}")
                st.write(f"- 최근 60일 평균 주가(중장기): {ma60:.2f}")

        # 원본 데이터 보기
        st.divider()
        with st.expander("테이블 형식으로 원본 데이터 보기 📋"):
            st.dataframe(data.sort_index(ascending=False))
            
    else:
        st.error("데이터를 정상적으로 분석할 수 없어! 날짜 범위나 주식 종목을 확인해 줘. 🥺")
