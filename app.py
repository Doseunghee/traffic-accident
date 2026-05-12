import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import requests

# ==========================================
# 1. 압도적 비주얼의 iOS Typography & UI (CSS)
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 리포트",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* 기본 배경 */
    .stApp {
        background-color: #FFFFFF;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* 메인 타이틀 디자인 */
    .main-title {
        font-size: 54px !important;
        font-weight: 800 !important;
        color: #1D1D1F;
        letter-spacing: -3px !important;
        text-align: center;
        margin-top: 60px !important;
        margin-bottom: 10px !important;
        line-height: 1.1;
    }
    .main-subtitle {
        font-size: 28px !important;
        color: #86868B;
        text-align: center;
        margin-bottom: 80px !important;
        font-weight: 400;
        letter-spacing: -0.5px;
    }

    /* 섹션 제목 */
    .section-title {
        font-size: 32px;
        font-weight: 700;
        color: #1D1D1F;
        margin-bottom: 25px;
        letter-spacing: -1px;
    }

    /* 리포트 카드 디자인 (그림자 최적화) */
    .report-card {
        background: #FFFFFF;
        border-radius: 30px;
        padding: 0px 20px 60px 20px;
        margin-bottom: 100px;
    }

    /* 인사이트 박스 (깔끔한 텍스트 중심) */
    .insight-container {
        margin-top: 30px;
        padding: 30px;
        background-color: #F5F5F7;
        border-radius: 20px;
    }
    .insight-label {
        font-size: 14px;
        font-weight: 700;
        color: #007AFF;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .insight-text {
        font-size: 18px;
        line-height: 1.8;
        color: #1D1D1F;
        word-break: keep-all;
    }

    /* SQL 코드 영역 스타일 */
    .stExpander {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    
    /* 불필요한 위젯 여백 제거 */
    .block-container {
        max-width: 1100px !important;
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 처리 엔진 (Expert Logic)
# ==========================================
@st.cache_resource
def get_connection():
    return sqlite3.connect('교통사고.db', check_same_thread=False)

def run_query(query):
    with get_connection() as conn:
        return pd.read_sql(query, conn)

@st.cache_data
def get_seoul_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    try: return requests.get(url).json()
    except: return None

# 자치구명 영-한 매핑 (DB 데이터와 지도 데이터 정밀 매칭)
district_mapping = {
    'Jongno-gu': '종로구', 'Jung-gu': '중구', 'Yongsan-gu': '용산구',
    'Seongdong-gu': '성동구', 'Gwangjin-gu': '광진구', 'Dongdaemun-gu': '동대문구',
    'Jungnang-gu': '중랑구', 'Seong북-gu': '성북구', 'Gangbuk-gu': '강북구',
    'Dobong-gu': '도봉구', 'Nowon-gu': '노원구', 'Eunpyeong-gu': '은평구',
    'Seodaemun-gu': '서대문구', 'Mapo-gu': '마포구', 'Yangcheon-gu': '양천구',
    'Gangseo-gu': '강서구', 'Guro-gu': '구로구', 'Geumcheon-gu': '금천구',
    'Yeongdeungpo-gu': '영등포구', 'Dongjak-gu': '동작구', 'Gwanak-gu': '관악구',
    'Seocho-gu': '서초구', 'Gangnam-gu': '강남구', 'Songpa-gu': '송파구',
    'Gangdong-gu': '강동구', 'Seongbuk-gu': '성북구'
}

# iOS 시스템 컬러
IOS_BLUE = "#007AFF"
IOS_RED = "#FF3B30"

# ==========================================
# 3. 리포트 헤더 (초대형 제목)
# ==========================================
st.markdown('<h1 class="main-title">Seoul Traffic Safety Report</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">2023 - 2024 통합 데이터 기반 정밀 분석 리포트</p>', unsafe_allow_html=True)

# 시각화 통합 빌더
def render_report_section(title, fig, sql, insight):
    st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    
    # Plotly 레이아웃 iOS 최적화
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=14, color="#1D1D1F"),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 인사이트
    st.markdown(f"""
    <div class="insight-container">
        <div class="insight-label">ANALYSIS INSIGHT</div>
        <div class="insight-text">{insight}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # SQL 소스
    with st.expander("TECHNICAL DATA SOURCE (SQL)"):
        st.code(sql, language='sql')
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 시각화 본문 (통합 인사이트 적용)
# ==========================================

# ① 월별 교통사고 추이
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)
fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
              line_shape='spline', color_discrete_sequence=[IOS_BLUE, IOS_RED])
fig1.update_traces(line=dict(width=5), marker=dict(size=12))
insight_1 = "2023년과 2024년의 월별 교통사고 발생 추이를 비교하여 계절적 패턴과 사고 증가 시점을 분석하였다. 2023년과 2024년 모두 하반기로 갈수록 사고가 증가하는 경향이 나타났다. 특히 9~11월 구간에서 사고 건수가 높게 나타났으며, 이는 가을철 교통량 증가와 연관 가능성이 있다. 2024년 10월의 사고 건수가 가장 높게 나타나 특정 시기의 교통 위험성이 증가했음을 확인할 수 있었다."
render_report_section("① 월별 교통사고 추이 분석", fig1, sql_1, insight_1)

# ② 요일별 교통사고 비교
sql_2 = "SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents GROUP BY day ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;"
df_2 = run_query(sql_2)
fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE])
insight_2 = "요일별 교통사고 발생 차이를 비교하여 특정 요일의 사고 집중 현상을 분석하였다. 금요일의 사고 건수가 가장 높게 나타났다. 평일의 사고량이 주말보다 전반적으로 높게 나타났으며, 이는 출퇴근 교통량의 영향으로 해석할 수 있다. 일요일은 사고 건수가 가장 적었으며, 상대적으로 이동량이 감소한 영향으로 추정된다."
render_report_section("② 요일별 교통사고 비교", fig2, sql_2, insight_2)

# ③ 시간대별 사고 위험도 분석
sql_3 = "SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents GROUP BY start_hour ORDER BY start_hour;"
df_3 = run_query(sql_3)
fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED])
insight_3 = "시간대별 사고 발생 패턴을 분석하여 위험 시간대를 확인하였다. 16시~20시 구간에서 사고가 가장 많이 발생하였다. 퇴근 시간대 교통 혼잡이 사고 증가에 큰 영향을 미친 것으로 보인다. 새벽 시간대(02시~06시)는 상대적으로 사고 건수가 낮게 나타났다."
render_report_section("③ 시간대별 사고 위험도 분석", fig3, sql_3, insight_3)

# ④ 기상상태별 교통사고 비율 분석
sql_4 = "SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents GROUP BY weather;"
df_4 = run_query(sql_4)
fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.6, color_discrete_sequence=px.colors.sequential.RdBu)
insight_4 = "날씨 조건에 따른 교통사고 비율 차이를 분석하였다. 맑은 날의 사고 비율이 가장 높게 나타났다. 이는 단순히 날씨가 좋아서 안전한 것이 아니라, 차량 운행량 자체가 증가했기 때문으로 해석할 수 있다. 비 오는 날에는 전체 사고 건수는 적지만, 미끄러운 노면 등으로 인해 위험성이 증가할 가능성이 있다."
render_report_section("④ 기상상태별 교통사고 비율 분석", fig4, sql_4, insight_4)

# ⑤ 교통법규 위반 유형별 사고 분석
sql_5 = "SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents GROUP BY violation ORDER BY total_accidents DESC;"
df_5 = run_query(sql_5)
fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', color_discrete_sequence=[IOS_RED])
fig5.update_layout(yaxis={'categoryorder':'total ascending'})
insight_5 = "교통사고의 주요 원인을 분석하기 위해 법규위반 유형별 사고 건수를 비교하였다. “안전운전 의무 불이행”이 압도적으로 높은 비율을 차지하였다. 이는 단순한 운전자 부주의가 교통사고의 핵심 원인임을 보여준다. 신호위반과 안전거리 미확보 역시 주요 사고 원인으로 확인되었다."
render_report_section("⑤ 교통법규 위반 유형별 사고 분석", fig5, sql_5, insight_5)

# ⑥ 자치구별 교통사고 발생 분석 (지도 및 SQL 포함)
sql_6 = "SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents GROUP BY administrative_district;"
df_6 = run_query(sql_6)
seoul_geo = get_seoul_geojson()

if seoul_geo and not df_6.empty:
    df_6['display_name'] = df_6['administrative_district'].map(district_mapping)
    fig6 = px.choropleth(
        df_6, geojson=seoul_geo, locations='display_name',
        featureidkey="properties.name", color='total_accidents',
        color_continuous_scale="Reds"
    )
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(height=600, coloraxis_showscale=True)
    insight_6 = "서울시 자치구별 사고 발생 차이를 공간적으로 분석하였다. 강남구의 사고 건수가 가장 높게 나타났다. 송파구와 서초구 역시 높은 사고 발생량을 보였으며, 교통량과 상업시설 밀집의 영향을 받는 것으로 추정된다. 서울 동남권 지역에서 상대적으로 사고가 집중되는 공간적 패턴을 확인할 수 있었다."
    render_report_section("⑥ 자치구별 교통사고 발생 분석", fig6, sql_6, insight_6)

# 푸터
st.markdown("<div style='text-align: center; color: #86868B; margin: 100px 0;'>Data Source: 한국도로교통공단 교통사고분석시스템 (TASS)</div>", unsafe_allow_html=True)
