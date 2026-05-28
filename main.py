import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 기본 설정
st.set_page_config(page_title="한/미 주식 수익률 비교 분석", layout="wide")

# 주요 주식 티커(Ticker) 딕셔너리
# 한국 주식은 종목코드 뒤에 '.KS'(코스피) 또는 '.KQ'(코스닥)를 붙입니다.
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

st.title("📈 한국 및 미국 주요 주식 수익률 비교")
st.markdown("""
당곡고등학교 학생 여러분, 환영합니다!  
이 웹앱은 `yfinance`를 이용해 한미 주요 기업의 주가 데이터를 불러오고, `plotly`를 통해 상호작용 가능한 차트로 보여줍니다.
""")

# 사이드바 설정 (UI)
st.sidebar.header("📊 분석 설정")
selected_stocks = st.sidebar.multiselect(
    "비교할 기업을 선택하세요:",
    list(TICKERS.keys()),
    default=["삼성전자 (KR)", "애플 (US)", "엔비디아 (US)"]
)

# 날짜 선택 (기본값: 최근 1년)
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

start = st.sidebar.date_input("조회 시작일", start_date)
end = st.sidebar.date_input("조회 종료일", end_date)

# 데이터 불러오기 함수 (캐싱을 통해 속도 향상 및 중복 요청 방지)
@st.cache_data
def load_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        symbol = TICKERS[t]
        # yfinance를 통해 종가(Close) 데이터만 가져옵니다.
        ticker_data = yf.download(symbol, start=start, end=end, progress=False)
        if not ticker_data.empty:
            df_close[t] = ticker_data['Close']
    return df_close

if not selected_stocks:
    st.warning("사이드바에서 비교할 주식을 하나 이상 선택해주세요.")
else:
    # 1. 데이터 로드
    data = load_data(selected_stocks, start, end)

    # 2. 누적 수익률 계산
    # (현재 주가 - 시작 주가) / 시작 주가 * 100 
    # 첫 번째 유효한 데이터를 기준(0%)으로 삼아 이후의 등락률을 계산합니다.
    if not data.empty:
        returns = (data / data.iloc[0] - 1) * 100

        # 레이아웃을 2개의 컬럼으로 나눔
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("달러/원 기준 주가 추이 (단순 종가)")
            # 각 주식의 단순 가격을 보여주는 차트
            fig_price = px.line(data, x=data.index, y=data.columns, labels={"value": "주가", "variable": "종목"})
            fig_price.update_layout(xaxis_title="날짜", yaxis_title="주가 (KRW/USD)")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("기간 내 누적 수익률 비교 (%)")
            # 여러 주식의 성과를 '수익률'로 동일한 선상에서 비교하는 차트
            fig_return = px.line(returns, x=returns.index, y=returns.columns, labels={"value": "누적 수익률 (%)", "variable": "종목"})
            fig_return.update_layout(xaxis_title="날짜", yaxis_title="수익률 (%)")
            st.plotly_chart(fig_return, use_container_width=True)

        # 3. 원본 데이터 표 확인하기
        with st.expander("테이블 형식으로 원본 데이터 보기"):
            st.dataframe(data.sort_index(ascending=False))
    else:
        st.error("데이터를 불러오지 못했습니다. 날짜 설정을 확인해주세요.")
