import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime

# ── 1. 페이지 설정 ──
st.set_page_config(page_title="교사용 서술형 평가 대시보드", layout="wide")

st.title("👨‍🏫 교사용 대시보드: 과학 서술형 평가")
st.markdown("학생들이 제출한 답안과 AI 채점 결과를 실시간으로 확인하고 분석합니다.")

# ── 2. Supabase 연결 설정 (캐싱) ──
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("Secrets가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인하세요.")
        st.stop()

supabase = get_supabase_client()

# ── 3. 데이터 로드 함수 ──
def load_data():
    # 'student_submissions' 테이블의 모든 데이터를 가져옵니다.
    # 최신순으로 정렬 (created_at 내림차순)
    response = supabase.table("student_submissions") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()
    
    rows = response.data
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    
    # 시간대 변환 (UTC -> KST 등 보기 좋게 처리) - 여기서는 문자열 단순 정리
    # 실제 운영 시에는 pd.to_datetime(df['created_at']).dt.tz_convert(...) 권장
    df['submit_time'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    return df

# ── 4. 새로고침 버튼 ──
if st.button("🔄 데이터 새로고침"):
    st.cache_data.clear() # (필요시 캐시 삭제 로직 추가 가능)
    st.rerun()

# ── 5. 데이터 분석 및 시각화 로직 ──
df = load_data()

if df.empty:
    st.warning("아직 제출된 데이터가 없습니다.")
else:
    # --- (1) 상단 요약 지표 (Metrics) ---
    col1, col2, col3 = st.columns(3)
    total_submissions = len(df)
    unique_students = df['student_id'].nunique()
    last_submit = df.iloc[0]['submit_time']

    col1.metric("총 제출 건수", f"{total_submissions}건")
    col2.metric("참여 학생 수", f"{unique_students}명")
    col3.metric("최근 제출 시간", last_submit)

    st.divider()

    # --- (2) 문항별 정답률 분석 ---
    st.subheader("📊 문항별 정답률 (O/X 분석)")

    # 피드백 컬럼에서 O/X 추출하는 헬퍼 함수
    def get_result(text):
        if not isinstance(text, str): return "판독불가"
        text = text.strip()
        if text.startswith("O:") or text.startswith("O."): return "정답 (O)"
        if text.startswith("X:") or text.startswith("X."): return "오답 (X)"
        return "기타"

    # 각 문항별 O/X 카운트 집계
    q1_results = df['feedback_1'].apply(get_result).value_counts()
