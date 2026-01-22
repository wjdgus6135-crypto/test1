# Step 1-2 – 서술형 문제 3개 포맷 (Streamlit)
# --------------------------------------------------
# Step 1-1에서 1문항 구조를 확장해 총 3문항으로 구성했습니다.
# 이후 단계에서는 answers 리스트와 제출 로직을 그대로 두고
# GPT 채점·DB(Supabase) 저장 함수를 추가하면 됩니다.
# --------------------------------------------------

import streamlit as st

# ── 1. 수업 제목 ──
st.title("외부 은하")  # ← 교과별 제목으로 자유롭게 수정하세요.

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

        # ✅ [핵심 수정] 제출 성공 신호를 줘서 아래 GPT 버튼을 활성화시킵니다.
        st.session_state.submitted_ok = True
        st.session_state.gpt_feedbacks = None # 재제출 시 기존 피드백 초기화

# ==================================================
# Step 2 – GPT API 기반 서술형 채점 + 피드백 (최종 수정본)
# --------------------------------------------------
# [사용법]
# 1. Step 1-2 코드의 '제출 성공(else)' 블록 안에 다음 두 줄이 있어야 합니다:
#    st.session_state.submitted_ok = True
#    st.session_state.gpt_feedbacks = None 
# 2. 이 코드를 Step 1-2 코드 맨 아래에 그대로 붙여넣으세요.
# ==================================================

from datetime import datetime, timezone

# ── 0. 세션 상태 초기화(새로고침/리런에도 결과 유지) ──
if "submitted_ok" not in st.session_state:
    st.session_state.submitted_ok = False
if "gpt_feedbacks" not in st.session_state:
    st.session_state.gpt_feedbacks = None
if "gpt_payload" not in st.session_state:
    st.session_state.gpt_payload = None

# ── 1. 문항별 채점 기준(교사가 자유롭게 수정) ──
GRADING_GUIDELINES = {
    1: "기체 입자의 운동은 온도와 비례 관계임을 언급하고, 입자 충돌·속도 증가 예를 기술한다.",
    2: "일정한 온도에서, 기체의 압력과 부피가 서로 반비례한다.",
    3: "전도는 입자 간 직접 충돌, 대류는 유체의 순환, 복사는 전자기파를 통한 열 이동 방식이다.",
}

# ── 2. 모델 출력 후처리(형식/길이 안정화: O:/X: + 한 줄 + 200자) ──
def normalize_feedback(text: str) -> str:
    """AI 응답이 형식을 벗어나더라도 강제로 'O: ...' 또는 'X: ...' 형태로 보정합니다."""
    if not text:
        return "X: 피드백 생성 실패"

    first_line = text.strip().splitlines()[0].strip()

    # 접두사 보정 (예: 'O. 정답' -> 'O: 정답')
    if first_line.startswith("O") and not first_line.startswith("O:"):
        first_line = "O: " + first_line[1:].lstrip(": ").strip()
    if first_line.startswith("X") and not first_line.startswith("X:"):
        first_line = "X: " + first_line[1:].lstrip(": ").strip()
    
    # O나 X로 시작하지 않는 경우 안전하게 X 처리 (혹은 O로 처리할지 선택 가능)
    if not (first_line.startswith("O:") or first_line.startswith("X:")):
        first_line = "X: " + first_line

    head, body = first_line.split(":", 1)
    body = body.strip()

    # 200자 제한 (너무 긴 피드백 방지)
    if len(body) > 200:
        body = body[:200] + "…"

    return f"{head.strip()}: {body}"

# ── 3. GPT 피드백 버튼(제출 성공 시에만 활성화) ──
if st.button("GPT 피드백 확인", disabled=not st.session_state.submitted_ok):

    # [방어] Step 1-2 변수 존재 확인
    # globals() 체크는 코드가 합쳐져서 실행될 때 유효합니다.
    if "student_id" not in globals() or "answers" not in globals():
        st.error("오류: student_id 또는 answers 변수를 찾을 수 없습니다. Step 1-2 코드 아래에 붙여넣으셨나요?")
        st.stop()

    # [비용 방지] 빈 답안이 있으면 호출하지 않기
    if any(ans.strip() == "" for ans in answers):
        st.warning("내용이 비어있는 답안이 있습니다. 제출을 다시 확인해주세요.")
        st.stop()

    # [라이브러리 확인] 버튼 클릭 시점에 체크하여 연수 진행 시 당황 방지
    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        st.error("openai 라이브러리가 설치되지 않았습니다. 터미널에 `pip install openai`를 입력하세요.")
        st.stop()

    # [API 키 확인]
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("⚠️ .streamlit/secrets.toml 파일에 OPENAI_API_KEY가 설정되지 않았습니다.")
        st.stop()

    feedbacks = []

    with st.spinner("AI 선생님이 꼼꼼하게 채점 중입니다... ⏳"):
        for idx, ans in enumerate(answers, start=1):
            criterion = GRADING_GUIDELINES.get(idx, "채점 기준 없음")

            # 프롬프트: 'O/X' 판정과 친절한 피드백 요청
            prompt = (
                f"문항 번호: {idx}\n"
                f"채점 기준: {criterion}\n"
                f"학생 답안: {ans}\n\n"
                "출력 규칙:\n"
                "- 반드시 한 줄로만 출력\n"
                "- 형식은 정확히 'O: ...' 또는 'X: ...'\n"
                "- 피드백은 학생에게 말하듯 친절하게, 200자 이내\n"
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": "너는 친절하지만 정확한 과학 교사다. 출력 규칙을 반드시 지켜라."},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=1000,
                )
                raw_text = response.choices[0].message.content.strip()
            except Exception as e:
                raw_text = f"API 오류: {e}"

            # 응답 정규화(포맷 보정)
            feedbacks.append(normalize_feedback(raw_text))

    # [결과 저장] 세션에 저장하여 리런 되어도 결과 유지
    st.session_state.gpt_feedbacks = feedbacks

    # [Supabase 연동 대비] 데이터 구조화 (Dictionary 형태)
    st.session_state.gpt_payload = {
        "student_id": student_id.strip(),
        "answers": {f"Q{i}": a for i, a in enumerate(answers, start=1)},
        "feedbacks": {f"Q{i}": fb for i, fb in enumerate(feedbacks, start=1)},
        "guidelines": {f"Q{k}": v for k, v in GRADING_GUIDELINES.items()},
        "model": "gpt-5-mini",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

# ── 4. 결과 표시(저장된 값이 있으면 항상 표시) ──
if st.session_state.gpt_feedbacks:
    st.markdown("---")
    st.subheader("📝 AI 피드백 결과")

    for i, fb in enumerate(st.session_state.gpt_feedbacks, start=1):
        # 시각적 구분을 위해 성공/정보 박스 분기
        if fb.startswith("O:"):
            st.success(f"**문항 {i}** : {fb}")
        else:
            st.info(f"**문항 {i}** : {fb}")


    st.success("모든 피드백이 생성되었습니다. (DB 저장용 데이터 준비 완료)")
