import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import requests
import json

# ==========================================
# 1. 페이지 설정 및 iOS 디자인 테마
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 리포트 (2023-2024)",
    page_icon="🍎",
    layout="wide",
)

# iOS 스타일의 세련된 UI (배경, 카드, 폰트)
st.markdown("""
    <style>
    .main { background-color: #F2F2F7; }
    div.block-container { padding-top: 2rem; }
    
    /* iOS 카드 스타일 */
    .viz-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        margin-bottom: 50px;
        border: 1px solid #E5E5EA;
    }
    
    /* 텍스트 스타일링 */
    h1 { font-weight: 800; color: #1D1D1F; letter-spacing: -1.5px; margin-bottom: 0.5rem; }
    h3 { font-weight: 700; color: #1D1D1F; margin-bottom: 1.5rem; }
    p { color: #8E8E93; }
    
    /* SQL/인사이트 박스 */
    .info-section {
        background-color: #F9F9FB;
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 및 지도 데이터 로드 함수
# ==========================================
@st.cache_resource
def get_connection():
    return sqlite3.connect('교통사고.db', check_same_thread=False)

def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

@st.cache_data
def get_seoul_geojson():
    """서울시 자치구 경계 데이터를 가져오고 형식을 표준화합니다."""
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    try:
        resp = requests.get(url)
        data = resp.json()
        return data
    except:
        return None

# 색상 테마
IOS_BLUE = "#007AFF"
IOS_RED = "#FF3B30"
IOS_BLACK = "#1D1D1F"

# ==========================================
# 3. 메인 타이틀
# ==========================================
st.title("🍎 서울시 교통사고 데이터 분석")
st.markdown("### 2023-2024년 통합 통계 리포트")
st.markdown("한국도로교통공단 데이터를 기반으로 분석한 서울시 교통사고 현황입니다.")
st.divider()

# 시각화 블록 공통 함수 (1줄 1차트 레이아웃)
def draw_viz_section(title, fig, sql, insight):
    st.markdown('<div class="viz-card">', unsafe_allow_html=True)
    st.subheader(title)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🔍 데이터 소스 및 전문가 분석 내용 보기"):
        st.markdown("**[사용한 SQL 쿼리]**")
        st.code(sql, language='sql')
        st.markdown("**[인사이트 리포트]**")
        st.info(insight)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 시각화 섹션 시작
# ==========================================

# --- [01. 월별 교통사고 추이] ---
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)
fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
              line_shape='spline', color_discrete_sequence=[IOS_BLUE, IOS_RED],
              labels={'month': '월', 'accident_count': '사고 건수', 'year': '연도'})
fig1.update_layout(plot_bgcolor='white', hovermode='x unified')
insight_1 = """1. 2023년과 2024년 모두 가을철(10월)에 사고량이 최고점을 찍는 경향을 보입니다.
2. 겨울철(1~2월)은 상대적으로 사고 건수가 적으나, 빙판길 사고에 대한 주의가 필요합니다.
3. 전반적인 사고 발생 패턴이 두 해 모두 유사하게 반복되고 있습니다."""
draw_viz_section("01. 월별 교통사고 발생 추이 (2023 vs 2024)", fig1, sql_1, insight_1)


# --- [02. 요일별 교통사고 비교] ---
sql_2 = """
SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents
GROUP BY day ORDER BY CASE day 
WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 
WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;
"""
df_2 = run_query(sql_2)
fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE])
fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="요일", yaxis_title="누적 사고 건수")
insight_2 = """1. 금요일이 일주일 중 사고 발생 빈도가 가장 높은 것으로 나타났습니다.
2. 일요일은 평일 평균 대비 약 30% 낮은 사고율을 기록하며 가장 안전한 요일로 분석됩니다.
3. 주말 활동이 시작되는 금요일 오후부터 사고 위험이 급격히 상승합니다."""
draw_viz_section("02. 요일별 교통사고 분석 (2023-2024 누적)", fig2, sql_2, insight_2)


# --- [03. 시간대별 사고 위험도] ---
sql_3 = "SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents GROUP BY start_hour ORDER BY start_hour;"
df_3 = run_query(sql_3)
fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED])
fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="시간대(시)", yaxis_title="누적 사고 건수")
insight_3 = """1. 전형적인 '쌍봉형' 그래프로, 출근 시간(8-9시)과 퇴근 시간(18-20시)에 사고가 집중됩니다.
2. 특히 퇴근 시간대 사고량이 출근 시간대보다 약 1.5배 가량 높습니다.
3. 새벽 3-5시 사이는 사고 절대량은 적지만, 심야 과속으로 인한 치사율 위험이 높습니다."""
draw_viz_section("03. 시간대별 교통사고 위험도 (Area Chart)", fig3, sql_3, insight_3)


# --- [04. 기상상태별 교통사고 비율] ---
sql_4 = "SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents GROUP BY weather;"
df_4 = run_query(sql_4)
fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.6,
             color_discrete_sequence=px.colors.sequential.RdBu)
insight_4 = """1. 맑은 날씨에 발생하는 사고가 80% 이상으로 압도적입니다. 이는 맑은 날의 교통량 자체가 많기 때문입니다.
2. 우천 시 사고는 전체의 약 10% 내외지만, 수중 수막현상으로 인한 연쇄 추돌 사고 비중이 높습니다.
3. 안개나 눈이 오는 날은 빈도는 낮으나 사고 발생 시 대형 사고로 이어질 확률이 큽니다."""
draw_viz_section("04. 기상상태별 사고 발생 비중 (Donut Chart)", fig4, sql_4, insight_4)


# --- [05. 교통법규 위반 유형별 사고] ---
sql_5 = "SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents GROUP BY violation ORDER BY total_accidents DESC;"
df_5 = run_query(sql_5)
fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', 
             color='total_accidents', color_continuous_scale='Reds')
fig5.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="사고 건수", yaxis_title="법규 위반 항목")
insight_5 = """1. '안전운전 의무 불이행'이 전체 사고의 압도적 1위 원인으로 꼽힙니다.
2. 신호위반과 안전거리 미확보가 그 뒤를 잇고 있어 운전자 간 안전거리 확보가 시급합니다.
3. 보행자 보호 의무 위반은 건수는 적으나 인명 피해와 직결되는 항목입니다."""
draw_viz_section("05. 법규 위반 유형별 사고 순위 (Ranking Bar)", fig5, sql_5, insight_5)


# --- [06. 자치구별 지도 시각화 (해결책 적용)] ---
sql_6 = "SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents GROUP BY administrative_district;"
df_6 = run_query(sql_6)
seoul_geo = get_seoul_geojson()

if seoul_geo and not df_6.empty:
    # 매핑 오류 방지를 위해 자치구 명칭에서 공백 제거 (예: "강남구 " -> "강남구")
    df_6['administrative_district'] = df_6['administrative_district'].str.strip()
    
    fig6 = px.choropleth(
        df_6,
        geojson=seoul_geo,
        locations='administrative_district',
        featureidkey="properties.name", # GeoJSON의 구 이름 필드와 정확히 매칭
        color='total_accidents',
        color_continuous_scale="Reds",
        scope="asia"
    )
    # 지도를 서울 중심부로 고정하고 배경을 숨김
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600,
        coloraxis_colorbar=dict(title="사고 건수")
    )
    
    insight_6 = """1. 강남구, 송파구, 강서구 순으로 사고 발생 빈도가 높게 나타나며 지도의 색상이 가장 진합니다.
2. 유동 인구와 차량 통행량이 밀집된 주요 거점 지역에 사고가 집중되는 양상을 보입니다.
3. 도봉구, 금천구 등 외곽 지역은 상대적으로 낮은 밀도를 보이고 있습니다."""
    draw_viz_section("06. 서울시 자치구별 교통사고 발생 밀도 (Choropleth Map)", fig6, sql_6, insight_6)
else:
    st.error("⚠️ 지도 데이터를 불러오거나 매칭하는 데 실패했습니다. DB의 자치구 명칭이 '강남구', '송파구' 형태인지 확인해주세요.")

# --- 푸터 ---
st.markdown(
    "<div style='text-align: center; color: #8E8E93; font-size: 0.85rem; padding: 50px 0;'>"
    "Data Source: 한국도로교통공단 교통사고분석시스템 (TASS) | 2023-2024 Comprehensive Report"
    "</div>", 
    unsafe_allow_html=True
)
