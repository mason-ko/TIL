# LangGraph 학습 튜토리얼

LangGraph 기반 에이전트 개발을 위한 단계별 학습 가이드입니다.
LLM과 LangGraph를 처음 접하는 백엔드 개발자를 위해 기초부터 차근차근 설명합니다.

## 대상 독자

- 백엔드 개발 경험이 있는 개발자
- LLM 및 LangGraph를 처음 배우는 분
- Python 기본 문법을 알고 있는 분
- **실제로 동작하는 코드**와 **작동 원리 이해**가 목표인 분

## 사전 준비

### 1. Python 환경
Python 3.9 이상 권장

### 2. 필요한 패키지 설치
```bash
pip install openai langchain langchain-openai langgraph pydantic
```

### 3. Google Gemini API 키 설정

[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요.

**방법 1: .env 파일 사용 (추천)**

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

`.env` 파일을 열고 API 키를 입력하세요:
```
GOOGLE_API_KEY=your-actual-api-key-here
```

**방법 2: 환경변수 직접 설정**

Linux/Mac:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Windows (PowerShell):
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

Windows (CMD):
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**중요:** `.env` 파일은 절대 Git에 커밋하지 마세요! (`.gitignore`에 포함되어 있어야 합니다)

## 튜토리얼 구조

각 단계마다 두 개의 파일이 있습니다:
- `stepN.py`: 실행 가능한 Python 코드
- `stepN.md`: 상세한 설명과 개념 정리

### Step 1: 기본 LLM 호출
**위치:** `tutorials/step1.py`, `tutorials/step1.md`

**내용:**
- OpenAI API 직접 사용
- 기본적인 LLM 호출 방법
- 대화 이력 관리
- 스트리밍 응답

**실행:**
```bash
python tutorials/step1.py
```

**핵심 개념:**
- LLM은 상태가 없다 (Stateless)
- 토큰과 비용
- 메시지 역할 (system, user, assistant)
- Temperature 파라미터

### Step 2: LangChain 기본 사용
**위치:** `tutorials/step2.py`, `tutorials/step2.md`

**내용:**
- LangChain의 ChatOpenAI 사용
- 프롬프트 템플릿
- 체인 구성 (LCEL)
- 구조화된 출력 (JSON)

**실행:**
```bash
python tutorials/step2.py
```

**핵심 개념:**
- LangChain이 필요한 이유
- 프롬프트 템플릿의 재사용성
- 체인: 파이프라인 구성
- Output Parser

### Step 3: LangGraph 기본 구조
**위치:** `tutorials/step3.py`, `tutorials/step3.md`

**내용:**
- LangGraph 소개
- State, Node, Edge 개념
- 그래프 생성과 실행
- 병렬 처리

**실행:**
```bash
python tutorials/step3.py
```

**핵심 개념:**
- 그래프 구성 요소 (State, Node, Edge)
- START와 END
- add_messages Reducer
- 병렬 실행

### Step 4: State 관리
**위치:** `tutorials/step4.py`, `tutorials/step4.md`

**내용:**
- 복잡한 State 구조
- Reducer 함수
- 체크포인트와 영속성
- State 설계 패턴

**실행:**
```bash
python tutorials/step4.py
```

**핵심 개념:**
- 덮어쓰기 vs 병합
- 커스텀 Reducer
- operator 모듈 활용
- 체크포인터 (MemorySaver, SqliteSaver)

### Step 5: 조건부 엣지와 라우팅
**위치:** `tutorials/step5.py`, `tutorials/step5.md`

**내용:**
- 조건부 분기
- 루프 (사이클)
- LLM 기반 의사결정
- 최대 반복 제한

**실행:**
```bash
python tutorials/step5.py
```

**핵심 개념:**
- 일반 엣지 vs 조건부 엣지
- 라우팅 함수
- 루프 생성과 종료 조건
- LLM의 판단에 따른 분기

### Step 6: 실용적인 에이전트
**위치:** `tutorials/step6.py`, `tutorials/step6.md`

**내용:**
- Tool 정의와 사용
- ReAct 패턴
- 스트리밍 Agent
- 에러 처리

**실행:**
```bash
python tutorials/step6.py
```

**핵심 개념:**
- Tool 정의 (@tool 데코레이터)
- LLM에 Tool 바인딩
- ToolNode
- ReAct: Reasoning + Acting

## 학습 순서

1. **Step 1부터 순서대로 진행하세요**
   - 각 단계가 이전 단계를 기반으로 합니다

2. **코드를 직접 실행하세요**
   - 결과를 보면서 이해도를 높이세요

3. **코드를 수정해보세요**
   - 파라미터를 바꿔보고 결과를 관찰하세요
   - 새로운 노드나 Tool을 추가해보세요

4. **문서를 함께 읽으세요**
   - `.md` 파일에 개념 설명과 내부 동작이 상세히 나와 있습니다

## 프로젝트 구조

```
rangg/
├── README.md                 # 이 파일
├── work.md                   # 작업 요구사항
├── tutorials/
│   ├── step1.py             # Step 1 코드
│   ├── step1.md             # Step 1 설명
│   ├── step2.py             # Step 2 코드
│   ├── step2.md             # Step 2 설명
│   ├── step3.py             # Step 3 코드
│   ├── step3.md             # Step 3 설명
│   ├── step4.py             # Step 4 코드
│   ├── step4.md             # Step 4 설명
│   ├── step5.py             # Step 5 코드
│   ├── step5.md             # Step 5 설명
│   ├── step6.py             # Step 6 코드
│   └── step6.md             # Step 6 설명
```

## 주요 개념 요약

### LangGraph 핵심 요소

| 요소 | 설명 | 예시 |
|------|------|------|
| **State** | 그래프 내 데이터 구조 | `class State(TypedDict): ...` |
| **Node** | 작업을 수행하는 함수 | `def my_node(state): ...` |
| **Edge** | 노드 간 연결 | `workflow.add_edge("a", "b")` |
| **Conditional Edge** | 조건부 분기 | `workflow.add_conditional_edges(...)` |
| **Reducer** | State 병합 방식 | `Annotated[list, add_messages]` |
| **Checkpointer** | 상태 영속성 | `MemorySaver()` |

### 학습 경로

```
기본 LLM 호출 (Step 1)
    ↓
LangChain 체인 (Step 2)
    ↓
LangGraph 그래프 구조 (Step 3)
    ↓
복잡한 State 관리 (Step 4)
    ↓
조건부 분기와 루프 (Step 5)
    ↓
실용적인 Tool Agent (Step 6)
```

## 문제 해결

### API 키 오류
```
Error: API key not found
```
→ 환경변수 `GOOGLE_API_KEY`가 설정되었는지 확인하세요.

### 패키지 import 오류
```
ModuleNotFoundError: No module named 'langgraph'
```
→ `pip install langgraph langchain-openai` 실행하세요.

### 무한 루프
```
RecursionError: maximum recursion depth exceeded
```
→ 그래프에 종료 조건이 있는지 확인하세요.
→ `recursion_limit` 파라미터를 조정하세요.

## 참고 자료

### 공식 문서
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangChain 공식 문서](https://python.langchain.com/)
- [Google Gemini API 문서](https://ai.google.dev/docs)

### 추가 학습
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)

## 다음 단계

이 튜토리얼을 완료했다면:

1. **자신만의 프로젝트 시작**
   - 실제 문제를 해결하는 Agent 만들기
   - 커스텀 Tool 개발

2. **고급 기능 탐색**
   - Subgraphs: 계층적 그래프 구조
   - Human-in-the-loop: 사람의 검토/승인
   - 다양한 Checkpointer: PostgreSQL, Redis 등

3. **성능 최적화**
   - 프롬프트 엔지니어링
   - 비용 최적화 (모델 선택, 토큰 관리)
   - Latency 개선

4. **프로덕션 배포**
   - 에러 처리 강화
   - 로깅과 모니터링
   - 확장성 고려

## 기여

이 튜토리얼에 대한 피드백이나 개선 사항이 있다면 이슈를 열어주세요!

## 라이센스

이 튜토리얼은 학습 목적으로 자유롭게 사용할 수 있습니다.

---

**Happy Learning! 🚀**

LangGraph로 강력한 AI 에이전트를 만들어보세요!
