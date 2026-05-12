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

# iOS 스타일의 세련된 UI (배경, 카드, 폰트 설정)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600;700&display=swap');
    
    .main { background-color: #F2F2F7; font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; }
    div.block-container { padding-top: 2rem; }
    
    /* iOS 카드 스타일 */
    .viz-card {
        background-color: #FFFFFF;
        padding: 35px;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
        margin-bottom: 50px;
        border: 1px solid #E5E5EA;
    }
    
    /* 텍스트 스타일링 */
    h1 { font-weight: 800; color: #1D1D1F; letter-spacing: -1.5px; margin-bottom: 0.5rem; }
    h3 { font-weight: 700; color: #1D1D1F; margin-bottom: 1.5rem; border-left: 5px solid #007AFF; padding-left: 15px; }
    
    /* SQL/인사이트 박스 */
    .stExpander { border: none !important; background-color: #F9F9FB !important; border-radius: 15px; }
    .insight-text { line-height: 1.6; color: #3A3A3C; font-size: 1.05rem; }
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

# 자치구명 영한 매핑 (DB 데이터와 지도 데이터 매칭용)
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
st.title("서울시 교통사고 데이터 분석 대시보드")
st.markdown("### 2023-2024 종합 통계 분석 리포트")
st.divider()

# 시각화 블록 공통 함수 (1줄 1차트 레이아웃)
def draw_viz_section(title, fig, sql, insight):
    st.markdown('<div class="viz-card">', unsafe_allow_html=True)
    st.subheader(title)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🔍 데이터 소스 및 전문가 분석 내용 보기"):
        st.markdown("**[사용한 SQL 쿼리]**")
        st.code(sql, language='sql')
        st.markdown("**[분석 인사이트]**")
        st.markdown(f'<div class="insight-text">{insight}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 시각화 섹션 수행
# ==========================================

# ① 월별 교통사고 추이
sql_1 = "SELECT year, month, accident_count FROM monthly_accidents ORDER BY year, month;"
df_1 = run_query(sql_1)
fig1 = px.line(df_1, x='month', y='accident_count', color='year', markers=True,
              line_shape='spline', color_discrete_sequence=[IOS_BLUE, IOS_RED],
              labels={'month':'월', 'accident_count':'사고 건수', 'year':'연도'})
fig1.update_layout(plot_bgcolor='white', hovermode='x unified')
insight_1 = """2023년과 2024년의 월별 교통사고 발생 추이를 비교하여 계절적 패턴과 사고 증가 시점을 분석하였다. 
2023년과 2024년 모두 하반기로 갈수록 사고가 증가하는 경향이 나타났다. 
특히 9~11월 구간에서 사고 건수가 높게 나타났으며, 이는 가을철 교통량 증가와 연관 가능성이 있다. 
2024년 10월의 사고 건수가 가장 높게 나타나 특정 시기의 교통 위험성이 증가했음을 확인할 수 있었다."""
draw_viz_section("① 월별 교통사고 추이 분석", fig1, sql_1, insight_1)


# ② 요일별 교통사고 비교
sql_2 = """
SELECT day, SUM(accident_count) AS total_accidents FROM weekday_accidents
GROUP BY day ORDER BY CASE day 
WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 
WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END;"""
df_2 = run_query(sql_2)
fig2 = px.bar(df_2, x='day', y='total_accidents', color_discrete_sequence=[IOS_BLUE],
             labels={'day':'요일', 'total_accidents':'사고 건수'})
fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
insight_2 = """요일별 교통사고 발생 차이를 비교하여 특정 요일의 사고 집중 현상을 분석하였다. 
금요일의 사고 건수가 가장 높게 나타났다. 평일의 사고량이 주말보다 전반적으로 높게 나타났으며, 
이는 출퇴근 교통량의 영향으로 해석할 수 있다. 일요일은 사고 건수가 가장 적었으며, 
상대적으로 이동량이 감소한 영향으로 추정된다."""
draw_viz_section("② 요일별 교통사고 비교", fig2, sql_2, insight_2)


# ③ 시간대별 사고 위험도 분석
sql_3 = "SELECT start_hour, SUM(accident_count) AS total_accidents FROM time_accidents GROUP BY start_hour ORDER BY start_hour;"
df_3 = run_query(sql_3)
fig3 = px.area(df_3, x='start_hour', y='total_accidents', color_discrete_sequence=[IOS_RED],
              labels={'start_hour':'시작 시간(시)', 'total_accidents':'사고 건수'})
fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)')
insight_3 = """시간대별 사고 발생 패턴을 분석하여 위험 시간대를 확인하였다. 16시~20시 구간에서 사고가 가장 많이 발생하였다. 
퇴근 시간대 교통 혼잡이 사고 증가에 큰 영향을 미친 것으로 보인다. 
새벽 시간대(02시~06시)는 상대적으로 사고 건수가 낮게 나타났다."""
draw_viz_section("③ 시간대별 사고 위험도 분석", fig3, sql_3, insight_3)


# ④ 기상상태별 교통사고 비율 분석
sql_4 = "SELECT weather, SUM(accident_count) AS total_accidents FROM weather_accidents GROUP BY weather;"
df_4 = run_query(sql_4)
fig4 = px.pie(df_4, values='total_accidents', names='weather', hole=0.6, 
             color_discrete_sequence=px.colors.sequential.RdBu)
insight_4 = """날씨 조건에 따른 교통사고 비율 차이를 분석하였다. 맑은 날의 사고 비율이 가장 높게 나타났다. 
이는 단순히 날씨가 좋아서 안전한 것이 아니라, 차량 운행량 자체가 증가했기 때문으로 해석할 수 있다. 
비 오는 날에는 전체 사고 건수는 적지만, 미끄러운 노면 등으로 인해 위험성이 증가할 가능성이 있다."""
draw_viz_section("④ 기상상태별 교통사고 비율 분석", fig4, sql_4, insight_4)


# ⑤ 교통법규 위반 유형별 사고 분석
sql_5 = "SELECT violation, SUM(accident_count) AS total_accidents FROM violation_accidents GROUP BY violation ORDER BY total_accidents DESC;"
df_5 = run_query(sql_5)
fig5 = px.bar(df_5, x='total_accidents', y='violation', orientation='h', 
             color='total_accidents', color_continuous_scale='Reds',
             labels={'total_accidents':'사고 건수', 'violation':'위반 유형'})
fig5.update_layout(yaxis={'categoryorder':'total ascending'})
insight_5 = """교통사고의 주요 원인을 분석하기 위해 법규위반 유형별 사고 건수를 비교하였다. 
“안전운전 의무 불이행”이 압도적으로 높은 비율을 차지하였다. 
이는 단순한 운전자 부주의가 교통사고의 핵심 원인임을 보여준다. 
신호위반과 안전거리 미확보 역시 주요 사고 원인으로 확인되었다."""
draw_viz_section("⑤ 교통법규 위반 유형별 사고 분석", fig5, sql_5, insight_5)


# ⑥ 자치구별 교통사고 발생 분석 (Map)
sql_6 = "SELECT administrative_district, SUM(accident_count) AS total_accidents FROM administrative_district_accidents GROUP BY administrative_district;"
df_6 = run_query(sql_6)
seoul_geo = get_seoul_geojson()

if seoul_geo and not df_6.empty:
    # DB의 영문 구 이름을 한글 지도 데이터와 매칭
    df_6['display_name'] = df_6['administrative_district'].map(district_mapping)
    
    fig6 = px.choropleth(
        df_6,
        geojson=seoul_geo,
        locations='display_name',
        featureidkey="properties.name",
        color='total_accidents',
        color_continuous_scale="Reds",
        labels={'total_accidents':'사고 건수', 'display_name':'자치구'}
    )
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
    
    insight_6 = """서울시 자치구별 사고 발생 차이를 공간적으로 분석하였다. 강남구의 사고 건수가 가장 높게 나타났다. 
송파구와 서초구 역시 높은 사고 발생량을 보였으며, 교통량과 상업시설 밀집의 영향을 받는 것으로 추정된다. 
서울 동남권 지역에서 상대적으로 사고가 집중되는 공간적 패턴을 확인할 수 있었다."""
    draw_viz_section("⑥ 자치구별 교통사고 발생 분석", fig6, sql_6, insight_6)
else:
    st.error("데이터 매핑 실패: DB의 자치구 이름 형식을 확인해주세요.")

# --- 푸터 ---
st.markdown("<div style='text-align: center; color: #8E8E93; padding: 60px 0;'>Data Source: 한국도로교통공단 교통사고분석시스템 (TASS) | 2023-2024 Report</div>", unsafe_allow_html=True)
