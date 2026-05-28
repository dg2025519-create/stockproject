import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# 페이지 기본 설정
st.set_page_config(page_title="한/미 주식 수익률 비교 분석", layout="wide")

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

st.title("📈 한국 및 미국 주요 주식 수익률 비교 및 분석")
st.markdown("""
당곡고등학교 학생 여러분, 환영합니다!  
이 웹앱은 `yfinance`를 이용해 한미 주요 기업의 주가 데이터를 불러오고, 차트 시각화 및 **데이터 기반 기초 투자 분석**을 제공합니다.  
*(주의: 본 분석은 프로그래밍 및 데이터 분석 학습용이며, 실제 투자 권유가 아닙니다.)*
""")

# 사이드바 설정 (UI)
st.sidebar.header("📊 분석 설정")
selected_stocks = st.sidebar.multiselect(
    "비교할 기업을 선택하세요:",
    list(TICKERS.keys()),
    default=["삼성전자 (KR)", "애플 (US)", "엔비디아 (US)"]
)

# 날짜 선택
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

start = st.sidebar.date_input("조회 시작일", start_date)
end = st.sidebar.date_input("조회 종료일", end_date)

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
    st.warning("사이드바에서 비교할 주식을 하나 이상 선택해주세요.")
else:
    # 1. 데이터 로드
    data = load_data(selected_stocks, start, end)

    if not data.empty and len(data) > 1:
        # 2. 누적 수익률 계산
        returns = (data / data.iloc[0] - 1) * 100

        # 시각화 레이아웃
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("달러/원 기준 주가 추이")
            fig_price = px.line(data, x=data.index, y=data.columns, labels={"value": "주가", "variable": "종목"})
            fig_price.update_layout(xaxis_title="날짜", yaxis_title="주가")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("기간 내 누적 수익률 비교 (%)")
            fig_return = px.line(returns, x=returns.index, y=returns.columns, labels={"value": "누적 수익률 (%)", "variable": "종목"})
            fig_return.update_layout(xaxis_title="날짜", yaxis_title="수익률 (%)")
            st.plotly_chart(fig_return, use_container_width=True)

        st.divider()

        # 3. 데이터 기반 분석 시스템 추가
        st.header("💡 데이터 기반 성장세 및 리스크 분석")
        
        # 일일 수익률 계산 (변동성 분석을 위함)
        daily_returns = data.pct_change().dropna()
        
        # 평가 지표 계산
        # 1) 기간 내 총 수익률
        total_returns = returns.iloc[-1]
        
        # 2) 연간 변동성(리스크): 일일 수익률의 표준편차에 1년 거래일(약 252일)의 제곱근을 곱하여 계산
        volatility = daily_returns.std() * np.sqrt(252) * 100

        # 분석 결과를 데이터프레임으로 정리
        analysis_df = pd.DataFrame({
            "총 수익률 (%)": total_returns,
            "변동성 (리스크, %)": volatility
        }).round(2)

        st.dataframe(analysis_df.T, use_container_width=True)

        # 분석 리포트 자동 생성
        best_return_stock = total_returns.idxmax()
        best_return_value = total_returns.max()
        
        safest_stock = volatility.idxmin()
        safest_volatility = volatility.min()

        highest_risk_stock = volatility.idxmax()
        
        st.subheader("📝 AI 데이터 분석 리포트")
        st.info(f"""
        선택하신 기간({start} ~ {end}) 동안의 데이터를 분석한 결과입니다.

        * **가장 성장세가 높았던 종목 (최고 수익률):** `{best_return_stock}` (수익률: {best_return_value:.2f}%)
        * **가장 가격 방어가 잘 된 종목 (최저 리스크):** `{safest_stock}` (변동성: {safest_volatility:.2f}%)
        
        **분석 가이드:**
        * 수익률만 보고 투자하는 것은 위험할 수 있습니다. 예를 들어 `{highest_risk_stock}`의 경우 변동성이 가장 높게 나타났는데, 이는 오를 때 크게 오르지만 내릴 때도 크게 떨어질 수 있다는 뜻입니다.
        * **안정적인 투자**를 원한다면 변동성이 낮은 `{safest_stock}`이 적합할 수 있으며, **공격적인 투자**를 원한다면 성장세가 높은 `{best_return_stock}`에 관심을 가질 수 있습니다.
        * 과거의 데이터가 미래의 성장을 100% 보장하지는 않으므로, 이 데이터는 기업의 재무제표나 향후 산업 전망과 함께 종합적으로 고려해야 합니다!
        """)

        # 4. 원본 데이터
        with st.expander("테이블 형식으로 원본 데이터 보기"):
            st.dataframe(data.sort_index(ascending=False))
    else:
        st.error("데이터를 정상적으로 분석할 수 없습니다. 날짜 범위나 주식 종목을 확인해주세요.")
