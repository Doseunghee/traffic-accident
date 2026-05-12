import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import requests

# ==========================================
# 1. 페이지 설정 및 iOS 디자인 테마
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 리포트",
    layout="wide",
)

# iOS 스타일의 세련된 UI (애플 아이콘 제거)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600;700&display=swap');
    
    .main { background-color: #F2F2F7; font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; }
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
    
    /* SQL/인사이트 박스 */
    .stExpander { border: none !important; background-color: #F9F9FB !important; border-radius: 12px; }
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
    """서울시 자치구 경계 데이터를 가져옵니다."""
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    try:
        resp = requests.get(url)
        return resp.json()
    except Exception as e:
        st.error(f"지도 로딩 실패: {e}")
        return None

# 영문 자치구명을 한글로 변환하는 매핑 딕셔너리 (제공해주신 데이터 기준)
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

# 시스템 컬러
IOS_BLUE = "#007AFF"
IOS_RED = "#FF3B30"

# ==========================================
# 3. 메인 타이틀
# ==========================================
st.title("서울시 교통사고 데이터 분석")
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
# 4. 시각화 섹션 (1줄에 1개씩)
# ==========================================

# 01. 월별 교통사고 추이
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)
fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
              line_shape='spline', color_discrete_sequence=[IOS_BLUE, IOS_RED])
insight_1 = "2023년과 2024년 모두 하반기(10월)에 사고가 집중되는 경향을 보입니다. 이는 행락철 유동인구 증가가 주요 원인으로 분석됩니다."
draw_viz_section("01. 월별 교통사고 발생 추이 (2023-2024)", fig1, sql_1, insight_1)

# 02. 요일별 교통사고 비교
sql_2 = """
SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents
GROUP BY day ORDER BY CASE day 
WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 
WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;"""
df_2 = run_query(sql_2)
fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE])
insight_2 = "금요일의 사고 발생량이 가장 높으며, 일요일은 상대적으로 가장 안전한 요일로 나타납니다. 평일 경제 활동 인구의 이동량과 정비례하는 양상입니다."
draw_viz_section("02. 요일별 교통사고 비교", fig2, sql_2, insight_2)

# 03. 시간대별 사고 위험도
sql_3 = "SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents GROUP BY start_hour ORDER BY start_hour;"
df_3 = run_query(sql_3)
fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED])
insight_3 = "오전 8시(출근)와 오후 6~8시(퇴근) 시간대에 사고가 집중됩니다. 특히 퇴근 시간대의 사고 피크가 출근 시간보다 약 1.4배 더 높게 형성됩니다."
draw_viz_section("03. 시간대별 사고 위험도 분석", fig3, sql_3, insight_3)

# 04. 기상상태별 교통사고 비율
sql_4 = "SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents GROUP BY weather;"
df_4 = run_query(sql_4)
fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.6, color_discrete_sequence=px.colors.sequential.RdBu)
insight_4 = "맑은 날씨에 발생하는 사고 비중이 압도적이지만, 기상 악화(비/눈) 시 발생하는 사고는 다중 추돌과 같은 대형 사고로 이어질 위험이 높습니다."
draw_viz_section("04. 기상상태별 사고 발생 비율", fig4, sql_4, insight_4)

# 05. 교통법규 위반 유형별 사고
sql_5 = "SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents GROUP BY violation ORDER BY total_accidents DESC;"
df_5 = run_query(sql_5)
fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', color='total_accidents', color_continuous_scale='Reds')
insight_5 = "안전운전 의무 불이행이 전체 사고 원인의 절반 이상을 차지합니다. 전방 주시 태만과 같은 운전자 부주의에 대한 경각심이 필요합니다."
draw_viz_section("05. 법규 위반 유형별 사고 순위", fig5, sql_5, insight_5)

# 06. 자치구별 지도 시각화 (핵심 수정 부분)
sql_6 = "SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents GROUP BY administrative_district;"
df_6 = run_query(sql_6)
seoul_geo = get_seoul_geojson()

if seoul_geo and not df_6.empty:
    # [매핑 로직] DB의 영문 구 이름을 한글로 변환하여 GeoJSON과 일치시킴
    df_6['display_name'] = df_6['administrative_district'].map(district_mapping)
    
    fig6 = px.choropleth(
        df_6,
        geojson=seoul_geo,
        locations='display_name',
        featureidkey="properties.name", # GeoJSON의 한글 이름 필드와 매핑
        color='total_accidents',
        color_continuous_scale="Reds",
        labels={'total_accidents':'사고 건수', 'display_name':'자치구'}
    )
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
    
    insight_6 = "강남구, 송파구, 영등포구 순으로 사고 발생 빈도가 높습니다. 이 지역들은 차량 통행량이 많고 복잡한 교차로가 밀집된 공통점이 있습니다."
    draw_viz_section("06. 서울시 자치구별 교통사고 밀도 지도 (2023-2024)", fig6, sql_6, insight_6)
else:
    st.error("데이터를 불러올 수 없거나 지도 매핑에 실패했습니다.")

# --- 푸터 ---
st.markdown("<div style='text-align: center; color: #8E8E93; padding: 50px;'>Data Source: 한국도로교통공단 교통사고분석시스템</div>", unsafe_allow_html=True)
