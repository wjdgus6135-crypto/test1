📝 Streamlit 서술형 평가 시스템 (Step 1-2)

이 프로젝트는 Streamlit을 활용하여 학생들이 3개의 서술형 문제에 답안을 작성하고 제출할 수 있는 간단한 웹 인터페이스입니다.
기존의 단일 문항 구조를 확장하여 총 3문항의 입력을 한 번에 처리하도록 구성되었습니다.

📊 시스템 흐름도 (Flowchart)

사용자가 웹 페이지에서 상호작용하는 흐름은 다음과 같습니다.

graph TD
    Start[💻 수업 접속] --> InputID[🆔 학번 입력]
    InputID --> FormBlock{📝 답안 작성 Form}
    
    subgraph "서술형 문항 (3개)"
    FormBlock --> Q1[문항 1: 기체 입자 운동]
    FormBlock --> Q2[문항 2: 보일 법칙]
    FormBlock --> Q3[문항 3: 열에너지 이동]
    end
    
    Q1 & Q2 & Q3 --> SubmitBtn[🚀 제출 버튼 클릭]
    
    SubmitBtn --> Validation{검증 로직}
    Validation -- "빈칸 있음" --> Warning[⚠️ 경고: 모든 항목 입력]
    Validation -- "입력 완료" --> Success[✅ 성공: 제출 완료 메시지]


🛠️ 주요 기능

Form 컨테이너 사용 (st.form)

개별 입력마다 새로고침되지 않고, 모든 답안을 작성 후 제출 버튼을 눌렀을 때만 데이터가 전송됩니다.

확장된 문항 구조

기체 입자, 보일 법칙, 열에너지 이동 등 총 3가지 주제에 대한 서술형 답변을 입력받습니다.

입력값 검증 (Validation)

학번 누락 여부 확인

3개 문항 중 하나라도 비어있는지 확인

📂 코드 구조 설명

코드는 크게 3단계로 나누어져 있습니다.

단계

설명

코드 위치

1. 설정

수업 제목을 설정하고 레이아웃을 잡습니다.

st.title(...)

2. 입력 양식

with st.form(...): 내부에서 학번과 3개의 text_area를 생성합니다.

st.text_input, st.text_area

3. 처리 로직

제출 버튼(st.form_submit_button) 클릭 시 유효성을 검사하고 결과를 출력합니다.

if submitted: ...

🚀 실행 방법

터미널에서 아래 명령어를 입력하여 실행합니다.

# 필수 라이브러리 설치
pip install streamlit

# 앱 실행
streamlit run app.py


🔜 향후 계획 (Next Steps)

현재 단계(Step 1-2)는 UI 및 입력 구조를 잡는 단계입니다. 다음 단계에서는 아래 기능이 추가될 예정입니다.

🤖 AI 자동 채점: 입력된 answers 리스트를 GPT 모델에 보내 피드백 생성

☁️ DB 저장: 학생의 학번과 답안 데이터를 Supabase 데이터베이스에 저장
