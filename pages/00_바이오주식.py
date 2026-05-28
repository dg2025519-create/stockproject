import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 (페이지 이름과 아이콘 설정)
st.set_page_config(page_title="바이오 바다 탐험", layout="wide", page_icon="💊")

# 2. 상어와 바다 컨셉 커스텀 CSS 적용 (메인 페이지와 동일한 바다 컨셉 유지)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #E0F7FA 0%, #81D4FA 100%);
}

h1, h2, h3, h4, h5, h6, p, span, label {
    color: #01579B !important;
}

[data-testid="stSidebar"] {
    background-color: #B3E5FC !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. 바이오 시장 대표 주식 티커(Ticker) 딕셔너리
BIO_TICKERS = {
    "삼성바이오로직스 (KR)": "207940.KS",
    "셀트리온 (KR)": "068270.KS",
    "유한양행 (KR)": "000100.KS",
    "일라이 릴리 (US)": "LLY",       # 비만 치료제로 유명한 글로벌 제약사
    "노보 노디스크 (US)": "NVO",      # 당뇨/비만 치료제 강자
    "존슨앤드존슨 (US)": "JNJ",      # 글로벌 종합 제약/헬스케어
    "화이자 (US)": "PFE",          # 백신 및 치료제 대표 기업
    "모더나 (US)": "MRNA"          # mRNA 백신 대표 기업
}

st.title("🦈 아기 상어의 바이오(Bio) 바다 탐험 🧬")
st.markdown("""
안녕! 여기는 신약을 개발하고 사람들의 건강을 책임지는 **'바이오/제약 바다 구역'**이야. 💊  
이곳의 물고기들은 임상 시험 결과나 신약 발표에 따라 파도를 엄청나게 세게 타기도 해!  
과연 어떤 바이오 물고기가 쑥쑥 자라고 있는지 내가 분석해 줄게! 뽀글뽀글 🫧
""")

# 사이드바 설정 (UI)
st.sidebar.header("🧪 바이오 탐험 설정")
selected_bio_stocks = st.sidebar.multiselect(
    "어떤 바이오 주식을 구경할까?",
    list(BIO_TICKERS.keys()),
    default=["삼성바이오로직스 (KR)", "일라이 릴리 (US)", "노보 노디스크 (US)"]
)

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

start = st.sidebar.date_input("탐험 시작일", start_date)
end = st.sidebar.date_input("탐험 종료일", end_date)

# 데이터 불러오기 함수 (메인 페이지와 겹치지 않게 이름 변경)
@st.cache_data
def load_bio_data(tickers, start, end):
    df_close = pd.DataFrame()
    for t in tickers:
        symbol = BIO_TICKERS[t]
        ticker_data = yf.download(symbol, start=start, end=end, progress=False)
        if not ticker_data.empty:
            df_close[t] = ticker_data['Close']
    return df_close

if not selected_bio_stocks:
    st.warning("사이드바에서 구경할 바이오 주식을 하나 이상 선택해 줘! 🦈")
else:
    data = load_bio_data(selected_bio_stocks, start, end)

    if not data.empty and len(data) > 1:
        returns = (data / data.iloc[0] - 1) * 100

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("달러/원 기준 바이오 주가 파도 🌊")
            fig_price = px.line(data, x=data.index, y=data.columns)
            fig_price.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            st.subheader("누적 수익률 달리기 🏁 (%)")
            fig_return = px.line(returns, x=returns.index, y=returns.columns)
            fig_return.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.5)")
            st.plotly_chart(fig_return, use_container_width=True)

        st.divider()

        # ---------------------------------------------------------
        # 아기 상어의 바이오 종목 맞춤 평가 시스템 (이동평균선 기반)
        # ---------------------------------------------------------
        st.header("🩺 아기 상어의 바이오 주식 건강 검진 결과 📝")
        st.markdown("최근 주가의 흐름(20일 및 60일 이동평균선)을 바탕으로 이 바이오 주식이 얼마나 건강하게 크고 있는지 진단해 줄게!")

        for stock in selected_bio_stocks:
            stock_data = data[stock].dropna()
            
            if len(stock_data) < 60:
                st.info(f"**{stock}**: 아직 데이터가 부족해서 건강 검진을 하기 어려워! 조금 더 긴 기간을 선택해 줘. 🥲")
                continue

            current_price = stock_data.iloc[-1]
            ma20 = stock_data.rolling(window=20).mean().iloc[-1]
            ma60 = stock_data.rolling(window=60).mean().iloc[-1]
            total_return = (current_price / stock_data.iloc[0] - 1) * 100

            # 바이오 테마에 맞춘 평가 로직 문구 변경
            if current_price > ma20 and ma20 > ma60:
                trend_eval = "단기적으로도, 장기적으로도 아주 건강하게 성장하고 있어! 🚀 신약 개발 소식이라도 있는 걸까? 에너지가 넘쳐!"
                emoji = "🦈✨"
            elif current_price < ma20 and ma20 < ma60:
                trend_eval = "최근 활력이 많이 떨어졌어. 💤 임상 시험 결과가 안 좋았거나 휴식이 필요한가 봐. 지켜보는 게 좋겠어."
                emoji = "🐢💧"
            elif current_price > ma20 and ma20 <= ma60:
                trend_eval = "장기적으로는 조금 아팠지만, 최근 들어 다시 건강을 회복하고 힘차게 헤엄치기 시작했어! 💊 회복세야!"
                emoji = "🐬🌊"
            elif current_price < ma20 and ma20 >= ma60:
                trend_eval = "그동안 튼튼하게 잘 자랐는데, 최근엔 조금 지쳐서 쉬고 있네. 잠시 숨을 고르는 중일지도 몰라. 🐡"
                emoji = "🐳💨"
            else:
                trend_eval = "파도가 이리저리 치고 있어. 방향을 잡아가고 있는 중이야. 🌊"
                emoji = "🐠"

            with st.expander(f"{emoji} {stock} 검진 결과 보기 (기간 수익률: {total_return:.2f}%)"):
                st.write(f"**현재 건강 상태(추세):** {trend_eval}")
                st.write(f"- 현재 주가: {current_price:.2f}")
                st.write(f"- 최근 20일 평균(단기 체력): {ma20:.2f}")
                st.write(f"- 최근 60일 평균(기초 체력): {ma60:.2f}")

        st.divider()
        with st.expander("테이블 형식으로 원본 데이터 보기 📋"):
            st.dataframe(data.sort_index(ascending=False))
            
    else:
        st.error("데이터를 정상적으로 분석할 수 없어! 날짜 범위나 주식 종목을 확인해 줘. 🥺")
