import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import requests
import json

# ==========================================
# 1. 시각적 정점에 도달한 iOS 스타일링 (CSS)
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 리포트",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
    <style>
    /* 폰트 및 배경 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background-color: #FBFBFD;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 메인 컨테이너 패딩 조절 */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        max-width: 1000px !important;
    }

    /* iOS 스타일 카드 디자인 */
    .ios-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 28px;
        padding: 40px;
        margin-bottom: 60px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04);
        transition: transform 0.3s ease;
    }

    /* 텍스트 스타일링 */
    .ios-title {
        color: #1D1D1F;
        font-size: 42px;
        font-weight: 700;
        letter-spacing: -1.5px;
        text-align: center;
        margin-bottom: 10px;
    }
    .ios-subtitle {
        color: #86868B;
        font-size: 18px;
        font-weight: 400;
        text-align: center;
        margin-bottom: 50px;
    }
    .section-header {
        color: #1D1D1F;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 25px;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
    }
    .section-header::before {
        content: "";
        width: 4px;
        height: 24px;
        background-color: #007AFF;
        margin-right: 12px;
        border-radius: 2px;
    }

    /* 인사이트 및 SQL 박스 */
    .insight-box {
        background-color: #F5F5F7;
        border-radius: 18px;
        padding: 25px;
        margin-top: 30px;
    }
    .insight-label {
        color: #007AFF;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .insight-content {
        color: #3A3A3C;
        line-height: 1.7;
        font-size: 15px;
    }
    
    /* Streamlit 기본 Expander 디자인 수정 */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        border: none !important;
        font-weight: 600 !important;
        color: #86868B !important;
    }

    /* 구분선 */
    hr {
        border: 0;
        height: 1px;
        background: #E5E5EA;
        margin: 60px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 처리 및 리소스 관리 (Expert Logic)
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
    try:
        return requests.get(url).json()
    except:
        return None

# 자치구명 영-한 매핑 테이블 (데이터 정밀도 보장)
district_mapping = {
    'Jongno-gu': '종로구', 'Jung-gu': '중구', 'Yongsan-gu': '용산구',
    'Seongdong-gu': '성동구', 'Gwangjin-gu': '광진구', 'Dongdaemun-gu': '동대문구',
    'Jungnang-gu': '중랑구', 'Seongbuk-gu': '성북구', 'Gangbuk-gu': '강북구',
    'Dobong-gu': '도봉구', 'Nowon-gu': '노원구', 'Eunpyeong-gu': '은평구',
    'Seodaemun-gu': '서대문구', 'Mapo-gu': '마포구', 'Yangcheon-gu': '양천구',
    'Gangseo-gu': '강서구', 'Guro-gu': '구로구', 'Geumcheon-gu': '금천구',
    'Yeongdeungpo-gu': '영등포구', 'Dongjak-gu': '동작구', 'Gwanak-gu': '관악구',
    'Seocho-gu': '서초구', 'Gangnam-gu': '강남구', 'Songpa-gu': '송파구',
    'Gangdong-gu': '강동구'
}

# iOS 시스템 컬러셋
IOS_BLUE = "#007AFF"
IOS_RED = "#FF3B30"
IOS_GRAY = "#8E8E93"
IOS_WHITE = "#FFFFFF"

# ==========================================
# 3. 리포트 헤더
# ==========================================
st.markdown('<p class="ios-title">Seoul Traffic Safety Report</p>', unsafe_allow_html=True)
st.markdown('<p class="ios-subtitle">2023 - 2024 통합 데이터 기반 정밀 분석 리포트</p>', unsafe_allow_html=True)

# 시각화 통합 빌더 함수
def render_ios_section(title, fig, sql, insight):
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    
    # Plotly 레이아웃 iOS 최적화
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#1D1D1F"),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    if hasattr(fig.data[0], 'marker'):
        fig.update_traces(marker=dict(line=dict(width=0))) # 불필요한 선 제거
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 인사이트 섹션
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">Analysis Insight</div>
        <div class="insight-content">{insight}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # SQL 소스 (숨김 처리 가능)
    with st.expander("Technical Data Source (SQL Query)"):
        st.code(sql, language='sql')
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 시각화 렌더링 (1줄 1차트)
# ==========================================

# ① 월별 교통사고 추이
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)
fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
              line_shape='spline', render_mode='svg',
              color_discrete_sequence=[IOS_BLUE, IOS_RED])
fig1.update_traces(line=dict(width=4), marker=dict(size=10))
insight_1 = "2023년과 2024년의 월별 교통사고 발생 추이를 비교하여 계절적 패턴과 사고 증가 시점을 분석하였다. 2023년과 2024년 모두 하반기로 갈수록 사고가 증가하는 경향이 나타났다. 특히 9~11월 구간에서 사고 건수가 높게 나타났으며, 이는 가을철 교통량 증가와 연관 가능성이 있다. 2024년 10월의 사고 건수가 가장 높게 나타나 특정 시기의 교통 위험성이 증가했음을 확인할 수 있었다."
render_ios_section("① 월별 교통사고 추이 분석", fig1, sql_1, insight_1)


# ② 요일별 교통사고 비교
sql_2 = """
SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents
GROUP BY day ORDER BY CASE day 
WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 
WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;"""
df_2 = run_query(sql_2)
fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE])
fig2.update_traces(marker_color=IOS_BLUE, opacity=0.8)
insight_2 = "요일별 교통사고 발생 차이를 비교하여 특정 요일의 사고 집중 현상을 분석하였다. 금요일의 사고 건수가 가장 높게 나타났다. 평일의 사고량이 주말보다 전반적으로 높게 나타났으며, 이는 출퇴근 교통량의 영향으로 해석할 수 있다. 일요일은 사고 건수가 가장 적었으며, 상대적으로 이동량이 감소한 영향으로 추정된다."
render_ios_section("② 요일별 교통사고 비교", fig2, sql_2, insight_2)


# ③ 시간대별 사고 위험도 분석
sql_3 = "SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents GROUP BY start_hour ORDER BY start_hour;"
df_3 = run_query(sql_3)
fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED])
fig3.update_traces(fillcolor='rgba(255, 59, 48, 0.1)', line=dict(width=3))
insight_3 = "시간대별 사고 발생 패턴을 분석하여 위험 시간대를 확인하였다. 16시~20시 구간에서 사고가 가장 많이 발생하였다. 퇴근 시간대 교통 혼잡이 사고 증가에 큰 영향을 미친 것으로 보인다. 새벽 시간대(02시~06시)는 상대적으로 사고 건수가 낮게 나타났다."
render_ios_section("③ 시간대별 사고 위험도 분석", fig3, sql_3, insight_3)


# ④ 기상상태별 교통사고 비율 분석
sql_4 = "SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents GROUP BY weather;"
df_4 = run_query(sql_4)
fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.7,
             color_discrete_sequence=[IOS_BLUE, "#5856D6", "#AF52DE", "#FF9500", "#FFCC00"])
fig4.update_traces(textposition='inside', textinfo='percent+label')
insight_4 = "날씨 조건에 따른 교통사고 비율 차이를 분석하였다. 맑은 날의 사고 비율이 가장 높게 나타났다. 이는 단순히 날씨가 좋아서 안전한 것이 아니라, 차량 운행량 자체가 증가했기 때문으로 해석할 수 있다. 비 오는 날에는 전체 사고 건수는 적지만, 미끄러운 노면 등으로 인해 위험성이 증가할 가능성이 있다."
render_ios_section("④ 기상상태별 교통사고 비율 분석", fig4, sql_4, insight_4)


# ⑤ 교통법규 위반 유형별 사고 분석
sql_5 = "SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents GROUP BY violation ORDER BY total_accidents DESC;"
df_5 = run_query(sql_5)
fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', color_discrete_sequence=[IOS_RED])
fig5.update_layout(yaxis={'categoryorder':'total ascending'})
fig5.update_traces(opacity=0.8)
insight_5 = "교통사고의 주요 원인을 분석하기 위해 법규위반 유형별 사고 건수를 비교하였다. “안전운전 의무 불이행”이 압도적으로 높은 비율을 차지하였다. 이는 단순한 운전자 부주의가 교통사고의 핵심 원인임을 보여준다. 신호위반과 안전거리 미확보 역시 주요 사고 원인으로 확인되었다."
render_ios_section("⑤ 교통법규 위반 유형별 사고 분석", fig5, sql_5, insight_5)


# ⑥ 자치구별 교통사고 발생 분석 (Map)
sql_6 = "SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents GROUP BY administrative_district;"
df_6 = run_query(sql_6)
seoul_geo = get_seoul_geojson()

if seoul_geo and not df_6.empty:
    df_6['display_name'] = df_6['administrative_district'].map(district_mapping)
    
    fig6 = px.choropleth(
        df_6,
        geojson=seoul_geo,
        locations='display_name',
        featureidkey="properties.name",
        color='total_accidents',
        color_continuous_scale="Purples", # iOS Indigo 느낌
    )
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(height=500, coloraxis_showscale=False)
    
    insight_6 = "서울시 자치구별 사고 발생 차이를 공간적으로 분석하였다. 강남구의 사고 건수가 가장 높게 나타났다. 송파구와 서초구 역시 높은 사고 발생량을 보였으며, 교통량과 상업시설 밀집의 영향을 받는 것으로 추정된다. 서울 동남권 지역에서 상대적으로 사고가 집중되는 공간적 패턴을 확인할 수 있었다."
    render_ios_section("⑥ 자치구별 교통사고 발생 분석", fig6, sql_6, insight_6)

# --- 푸터 ---
st.markdown(f"""
    <div style="text-align: center; color: #86868B; font-size: 13px; margin-top: 40px; padding-bottom: 60px;">
        Data Source: 한국도로교통공단 교통사고분석시스템 (TASS)<br>
        © 2024 Traffic Data Lab. All rights reserved.
    </div>
""", unsafe_allow_html=True)
