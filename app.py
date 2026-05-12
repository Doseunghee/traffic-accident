import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정 (iOS 스타일 디자인 테마)
# ==========================================
st.set_page_config(
    page_title="서울시 교통사고 분석 대시보드",
    page_icon="🚗",
    layout="wide",
)

# 커스텀 CSS: iOS 느낌의 깔끔한 디자인 적용
st.markdown("""
    <style>
    .main { background-color: #F5F5F7; }
    .stApp { color: #1D1D1F; }
    .css-1y4p8pa { padding: 2rem 1rem; }
    div[data-testid="stMetricValue"] { color: #007AFF; font-weight: bold; }
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    h1, h2, h3 { font-family: 'SF Pro Display', sans-serif; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터베이스 연결 함수
# ==========================================
def get_connection():
    """SQLite 데이터베이스에 연결합니다."""
    try:
        conn = sqlite3.connect('교통사고.db', check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return None

def run_query(query):
    """SQL 쿼리를 실행하고 결과를 데이터프레임으로 반환합니다."""
    conn = get_connection()
    if conn:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# ==========================================
# 3. 사이드바 (필터 설정)
# ==========================================
st.sidebar.header("🎨 필터 설정")
# 데이터에서 선택 가능한 연도 가져오기 (연도 필터)
years_df = run_query("SELECT DISTINCT year FROM monthly_accidents ORDER BY year DESC")
selected_year = st.sidebar.selectbox("연도를 선택하세요", years_df['year'] if not years_df.empty else [2023, 2024])

st.sidebar.markdown("---")
st.sidebar.info("본 대시보드는 공공데이터를 기반으로 서울시 교통사고 통계를 시각화합니다.")

# ==========================================
# 4. 메인 대시보드 화면 구성
# ==========================================
st.title("🍎 서울시 교통사고 데이터 분석 대시보드")
st.markdown(f"**현재 선택된 분석 연도:** {selected_year}년")
st.divider()

# --- [시각화 1: 월별 교통사고 추이] ---
st.subheader("1. 월별 교통사고 추이 (2023 vs 2024 비교)")
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)

if not df_1.empty:
    fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
                  title="월별 사고 발생량 추이",
                  color_discrete_sequence=['#FF3B30', '#007AFF'], # 레드 & 블루
                  labels={'month':'월', 'accident_count':'사고 건수', 'year':'연도'})
    st.plotly_chart(fig1, use_container_width=True)
    with st.expander("SQL 쿼리 및 인사이트 보기"):
        st.code(sql_1, language='sql')
        st.write("- **인사이트**: 특정 월(예: 5월, 10월)에 사고가 집중되는 경향이 있는지 확인합니다.")
        st.write("- 2023년 대비 2024년의 전반적인 사고 증감률을 비교할 수 있습니다.")

st.divider()

# --- [시각화 2: 요일별 교통사고 비교] ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2. 요일별 교통사고 비교")
    sql_2 = """
    SELECT day, SUM(accident_count) AS total_accidents
    FROM weekday_accidents
    WHERE year = {0}
    GROUP BY day
    ORDER BY
        CASE day
            WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END;
    """.format(selected_year)
    df_2 = run_query(sql_2)
    
    if not df_2.empty:
        fig2 = px.bar(df_2, x='day', y='total_accidents', 
                     title=f"{selected_year}년 요일별 사고 건수",
                     color_discrete_sequence=['#007AFF'])
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("SQL 쿼리 및 인사이트"):
            st.code(sql_2, language='sql')
            st.write("- **인사이트**: 주말보다 활동량이 많은 평일(특히 금요일)에 사고율이 높은지 확인합니다.")

# --- [시각화 3: 시간대별 사고 위험도] ---
with col2:
    st.subheader("3. 시간대별 사고 위험도")
    sql_3 = f"SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents WHERE year = {selected_year} GROUP BY start_hour ORDER BY start_hour;"
    df_3 = run_query(sql_3)
    
    if not df_3.empty:
        fig3 = px.area(df_3, x='start_hour', y='total_accidents', 
                      title=f"{selected_year}년 시간대별 사고 분포",
                      color_discrete_sequence=['#FF3B30'])
        st.plotly_chart(fig3, use_container_width=True)
        with st.expander("SQL 쿼리 및 인사이트"):
            st.code(sql_3, language='sql')
            st.write("- **인사이트**: 출퇴근 시간대(08시, 18시)에 사고가 집중되는 전형적인 도시형 패턴을 보입니다.")

st.divider()

# --- [시각화 4: 기상상태별 교통사고 비율] ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("4. 기상상태별 교통사고 비율")
    sql_4 = f"SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents WHERE year = {selected_year} GROUP BY weather;"
    df_4 = run_query(sql_4)
    
    if not df_4.empty:
        fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.4,
                     title="날씨별 사고 비중",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig4, use_container_width=True)
        with st.expander("SQL 쿼리 및 인사이트"):
            st.code(sql_4, language='sql')
            st.write("- **인사이트**: 맑은 날 사고가 절대적으로 많으나, 비/눈 오는 날의 치사율을 함께 고려할 필요가 있습니다.")

# --- [시각화 5: 교통법규 위반 유형별 사고] ---
with col4:
    st.subheader("5. 법규 위반별 사고 순위")
    sql_5 = f"SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents WHERE year = {selected_year} GROUP BY violation ORDER BY total_accidents DESC;"
    df_5 = run_query(sql_5)
    
    if not df_5.empty:
        fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h',
                     title="법규 위반 원인 TOP 순위",
                     color='total_accidents', color_continuous_scale='Reds')
        st.plotly_chart(fig5, use_container_width=True)
        with st.expander("SQL 쿼리 및 인사이트"):
            st.code(sql_5, language='sql')
            st.write("- **인사이트**: '안전운전 의무 불이행'이 가장 높은 비중을 차지하므로 운전자 의식 개선이 시급합니다.")

st.divider()

# --- [시각화 6: 자치구별 교통사고 발생 분석] ---
st.subheader("6. 서울시 자치구별 교통사고 위험도 분석")
sql_6 = f"SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents WHERE year = {selected_year} GROUP BY administrative_district ORDER BY total_accidents DESC;"
df_6 = run_query(sql_6)

if not df_6.empty:
    # 지도를 대신하여 구별 막대 차트로 시각화 (정확한 위치 기반 지도는 GeoJSON 데이터 필요)
    fig6 = px.bar(df_6, x='administrative_district', y='total_accidents',
                 title="자치구별 사고 발생 건수",
                 color='total_accidents',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig6, use_container_width=True)
    with st.expander("SQL 쿼리 및 인사이트"):
        st.code(sql_6, language='sql')
        st.write("- **인사이트**: 강남구, 송파구 등 유동인구가 많은 지역에서 사고 발생 건수가 상대적으로 높게 나타납니다.")

# 하단 정보
st.caption("Data Source: 서울시 공공데이터 포털 | Developed by Senior Data Developer")