# Step 1-2 – 서술형 문제 3개 포맷 (Streamlit)
# --------------------------------------------------
# Step 1-1에서 1문항 구조를 확장해 총 3문항으로 구성했습니다.
# 이후 단계에서는 answers 리스트와 제출 로직을 그대로 두고
# GPT 채점·DB(Supabase) 저장 함수를 추가하면 됩니다.
# --------------------------------------------------

import streamlit as st

# ── 1. 수업 제목 ──
st.title("예시 수업 제목")  # ← 교과별 제목으로 자유롭게 수정하세요.

# ── 2~4. 입력 + 제출을 form 안에 묶기 ──
with st.form("submit_form"):
    # ── 2. 학번 입력 ──
    student_id = st.text_input("학번", help="학생의 학번을 작성하세요. (예: 10130)")

    # ── 3-1. 서술형 문제 1 표시 ──
    QUESTION_1 = "기체 입자들의 운동과 온도의 관계를 서술하세요."
    st.markdown("#### 서술형 문제 1")
    st.write(QUESTION_1)
    answer_1 = st.text_area("답안을 입력하세요", key="answer1", height=150)

    # ── 3-2. 서술형 문제 2 표시 ──
    QUESTION_2 = "보일 법칙에 대해 설명하세요."
    st.markdown("#### 서술형 문제 2")
    st.write(QUESTION_2)
    answer_2 = st.text_area("답안을 입력하세요", key="answer2", height=150)

    # ── 3-3. 서술형 문제 3 표시 ──
    QUESTION_3 = "열에너지 이동 3가지 방식(전도·대류·복사)을 설명하세요."
    st.markdown("#### 서술형 문제 3")
    st.write(QUESTION_3)
    answer_3 = st.text_area("답안을 입력하세요", key="answer3", height=150)

    # 답안을 리스트로 모아 이후 채점/저장 로직에서 재사용하기
    answers = [answer_1, answer_2, answer_3]

    # ── 4. 전체 제출 버튼(form 전용) ──
    submitted = st.form_submit_button("제출")

# ── 제출 처리 로직(제출 버튼을 눌렀을 때만 실행) ──
if submitted:
    if not student_id.strip():
        st.warning("학번을 입력하세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("모든 답안을 작성하세요.")
    else:
        st.success(f"제출 완료! 학번: {student_id}")
        # ⚠️ Step 2에서 GPT 채점 및 DB(Supabase) 저장 로직을 여기에 추가할 예정입니다.
