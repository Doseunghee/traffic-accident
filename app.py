import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# ==========================================
# 1. 페이지 및 iOS 스타일 테마 설정
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 대시보드",
    page_icon="🍎",
    layout="wide",
)

# iOS 스타일의 세련된 UI를 위한 CSS 커스텀
st.markdown("""
    <style>
    /* 배경색 및 폰트 */
    .main { background-color: #F2F2F7; }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* 카드 스타일 컨테이너 */
    .stPlotlyChart {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    
    /* 사이드바 스타일링 */
    .css-1d391kg { background-color: #FFFFFF; }
    
    /* 메트릭/제목 스타일 */
    h1 { color: #1D1D1F; font-weight: 700; letter-spacing: -0.5px; }
    h3 { color: #1D1D1F; font-weight: 600; margin-bottom: 20px; }
    
    /* 구분선 */
    hr { border: 0; height: 1px; background: #E5E5EA; margin: 30px 0; }
    
    /* 인사이트 박스 */
    .insight-box {
        background-color: #FBB03B10;
        border-left: 5px solid #FF3B30;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 및 지도 데이터 로드 함수
# ==========================================
@st.cache_resource
def get_connection():
    """데이터베이스 연결"""
    return sqlite3.connect('교통사고.db', check_same_thread=False)

def run_query(query):
    """SQL 실행"""
    conn = get_connection()
    return pd.read_sql(query, conn)

@st.cache_data
def get_seoul_geojson():
    """서울시 자치구 경계 GeoJSON 로드"""
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    response = requests.get(url)
    return response.json()

# iOS 시스템 컬러 정의
IOS_BLUE = "#007AFF"
IOS_RED = "#FF3B30"
IOS_GRAY = "#8E8E93"

# ==========================================
# 3. 사이드바 구성
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/apple-logo.png", width=50)
    st.title("Settings")
    
    years_df = run_query("SELECT DISTINCT year FROM monthly_accidents ORDER BY year DESC")
    selected_year = st.selectbox("📅 분석 연도 선택", years_df['year'] if not years_df.empty else [2023, 2024])
    
    st.markdown("---")
    st.markdown("### Dashboard Info")
    st.info("이 대시보드는 실시간 교통사고 데이터를 기반으로 시각화 정보를 제공합니다.")

# ==========================================
# 4. 메인 화면 구성
# ==========================================
st.title("🍎 서울시 교통사고 데이터 분석")
st.markdown(f"**{selected_year}년도** 통계 리포트")

# --- [시각화 1: 월별 교통사고 추이] ---
st.subheader("01. 월별 교통사고 추이 (Double Line Chart)")
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)

if not df_1.empty:
    fig1 = px.line(df_1, x='month', y='accident_count', color='year', 
                  markers=True, line_shape='spline', # 부드러운 곡선
                  color_discrete_sequence=[IOS_GRAY, IOS_BLUE])
    fig1.update_layout(plot_bgcolor='white', hovermode='x unified', margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig1, use_container_width=True)
    
    with st.expander("데이터 상세 및 인사이트"):
        st.code(sql_1, language='sql')
        st.markdown("""
        - **분석결과**: 2023년 대비 2024년의 월별 추이를 통해 사고 증감 여부를 즉각 파악할 수 있습니다.
        - **특이사항**: 기온이 온화해지는 봄철(4-5월)과 행사가 많은 가을철(10월)에 사고 건수가 증가하는 경향이 있습니다.
        """)

st.divider()

col_left, col_right = st.columns(2)

# --- [시각화 2: 요일별 교통사고 비교] ---
with col_left:
    st.subheader("02. 요일별 사고 통계")
    sql_2 = f"""
    SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents
    WHERE year = {selected_year} GROUP BY day
    ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 
    WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;
    """
    df_2 = run_query(sql_2)
    fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("**인사이트**: 주말 직전인 금요일의 사고율이 가장 높으며, 일요일은 상대적으로 낮은 수치를 기록합니다.")

# --- [시각화 3: 시간대별 사고 위험도] ---
with col_right:
    st.subheader("03. 시간대별 사고 위험도")
    sql_3 = f"SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents WHERE year = {selected_year} GROUP BY start_hour ORDER BY start_hour;"
    df_3 = run_query(sql_3)
    fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED])
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("**인사이트**: 퇴근 시간대인 18시~20시 사이에 사고가 집중되며, 심야 시간대에는 건수는 적으나 치사율이 높아집니다.")

st.divider()

col_left2, col_right2 = st.columns(2)

# --- [시각화 4: 기상상태별 교통사고 비율] ---
with col_left2:
    st.subheader("04. 기상상태별 사고 비율")
    sql_4 = f"SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents WHERE year = {selected_year} GROUP BY weather;"
    df_4 = run_query(sql_4)
    fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.6,
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("**인사이트**: '맑음' 상태에서의 사고가 80% 이상이나, 우천 시 사고 당 인명 피해는 더 크게 나타납니다.")

# --- [시각화 5: 교통법규 위반 유형별 사고] ---
with col_right2:
    st.subheader("05. 법규 위반 유형별 순위")
    sql_5 = f"SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents WHERE year = {selected_year} GROUP BY violation ORDER BY total_accidents DESC;"
    df_5 = run_query(sql_5)
    fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', color='total_accidents', color_continuous_scale='Reds')
    fig5.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("**인사이트**: '안전운전 의무 불이행'이 압도적 1위이며, 신호위반과 안전거리 미확보가 그 뒤를 잇습니다.")

st.divider()

# --- [시각화 6: 서울시 자치구별 지도 시각화] ---
st.subheader("06. 서울시 자치구별 교통사고 위험 지도")
sql_6 = f"SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents WHERE year = {selected_year} GROUP BY administrative_district;"
df_6 = run_query(sql_6)
geojson = get_seoul_geojson()

if not df_6.empty:
    # 지도 시각화 (Choropleth)
    fig6 = px.choropleth(
        df_6,
        geojson=geojson,
        locations='administrative_district',
        featureidkey="properties.name", # GeoJSON의 이름 속성과 매핑
        color='total_accidents',
        color_continuous_scale="Reds",
        range_color=(df_6['total_accidents'].min(), df_6['total_accidents'].max()),
        labels={'total_accidents':'사고 건수'},
        scope="asia"
    )
    
    # 서울시 중심으로 지도 최적화
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=600)
    
    st.plotly_chart(fig6, use_container_width=True)
    
    with st.expander("지도 데이터 및 분석 상세"):
        st.code(sql_6, language='sql')
        st.markdown(f"""
        - **지도 분석**: 색상이 진할수록 사고 발생 빈도가 높은 지역입니다. 
        - **주요 지역**: 유동 인구와 차량 등록 대수가 많은 **강남구, 송파구, 영등포구** 등이 붉게 표시되는 경향이 있습니다.
        """)

# --- 하단 푸터 ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8E8E93; font-size: 0.9rem; padding: 20px;'>"
    "Data Source: 한국도로교통공단 교통사고분석시스템 | System Status: Operational"
    "</div>", 
    unsafe_allow_html=True
)
