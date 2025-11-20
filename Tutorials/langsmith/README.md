# LangSmith 튜토리얼

LangChain 애플리케이션의 프로덕션 모니터링, 디버깅, 평가를 위한 플랫폼 학습

## 개요

LangSmith는 LLM 애플리케이션을 프로덕션 환경에서 운영하기 위한 필수 도구입니다:

- **모니터링**: 실시간 요청/응답 추적
- **디버깅**: 체인 실행 과정 시각화
- **평가**: 모델 출력 품질 측정
- **데이터셋**: 테스트 케이스 관리
- **A/B 테스팅**: 프롬프트/모델 비교

## 왜 LangSmith가 필요한가?

### 프로덕션 문제들

```python
# 문제 1: 디버깅이 어려움
user: "왜 이 답변이 나왔죠?"
developer: "... 로그를 봐야..." (수십 단계 추적)

# 문제 2: 품질 측정 불가
"프롬프트를 바꿨는데 더 좋아졌나?"
→ 정량적 측정 불가

# 문제 3: 비용 모니터링 불가
"이번 달 OpenAI 비용이 왜 이렇게 많이 나왔지?"
→ 어떤 요청이 비쌌는지 모름
```

### LangSmith의 해결책

```python
# 해결 1: 자동 트레이싱
모든 LLM 호출 → 자동 기록 → UI에서 시각화

# 해결 2: 평가 프레임워크
100개 테스트 케이스 → 자동 실행 → 점수 비교

# 해결 3: 비용 대시보드
요청별 토큰/비용 → 실시간 집계 → 알림
```

## 설치

```bash
pip install -r requirements.txt
```

## 환경 설정

`.env` 파일 생성 (`.env.example` 참고):

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=your-project-name
GOOGLE_API_KEY=your-google-api-key  # 또는 OPENAI_API_KEY
```

### LangSmith API Key 발급

1. https://smith.langchain.com/ 접속
2. 회원가입 / 로그인
3. Settings → API Keys → Create API Key

## 튜토리얼 목차

### Step 1: LangSmith 기본 설정
- 첫 트레이싱 실행
- UI에서 추적 확인
- 트레이싱 데이터 구조 이해

**파일**: `tutorials/step1.md`, `tutorials/step1.py`

### Step 2: 프로덕션 모니터링
- 실시간 요청 추적
- 에러 모니터링
- 성능 메트릭 (지연시간, 토큰 사용량)
- 필터링 및 검색

**파일**: `tutorials/step2.md`, `tutorials/step2.py`

### Step 3: 평가 (Evaluation)
- Evaluator 작성
- 자동 평가 실행
- 평가 메트릭 (정확도, 관련성, 일관성)
- 평가 결과 비교

**파일**: `tutorials/step3.md`, `tutorials/step3.py`

### Step 4: 데이터셋 관리
- 테스트 데이터셋 생성
- 프로덕션 데이터에서 데이터셋 구성
- 버전 관리
- 반복 테스트

**파일**: `tutorials/step4.md`, `tutorials/step4.py`

### Step 5: A/B 테스팅
- 프롬프트 버전 비교
- 모델 성능 비교
- 통계적 유의성 검증

**파일**: `tutorials/step5.md`, `tutorials/step5.py`

### Step 6: 고급 기능
- Human Feedback 수집
- Annotation (주석)
- Custom Metadata
- 알림 설정

**파일**: `tutorials/step6.md`, `tutorials/step6.py`

## 학습 순서

1. **Step 1-2**: 기본 트레이싱과 모니터링 (필수)
2. **Step 3-4**: 평가와 데이터셋 (중요)
3. **Step 5-6**: A/B 테스팅과 고급 기능 (실무)

## 실행 방법

```bash
# Step 1 실행
python tutorials/step1.py

# 특정 예제만 실행
python tutorials/step1.py --example basic_tracing
```

## 주요 개념

### 1. Tracing (추적)

모든 LLM 호출과 체인 실행을 자동으로 기록:

```
Run (최상위)
  ├─ Chain Run
  │   ├─ LLM Run
  │   ├─ Tool Run
  │   └─ LLM Run
  └─ Output
```

### 2. Run Types

- **Chain**: LangChain 체인 실행
- **LLM**: LLM API 호출
- **Tool**: 도구 실행
- **Retriever**: 검색 실행
- **Agent**: 에이전트 실행

### 3. Evaluation

출력 품질을 자동으로 측정:

```python
# 예시
Correctness: 0.85  # 정답률
Relevance: 0.92    # 관련성
Helpfulness: 0.78  # 유용성
```

## 실무 활용 예시

### 1. 프로덕션 모니터링

```python
# 자동으로 모든 요청이 LangSmith에 기록됨
@traceable
def my_chatbot(user_input):
    return chain.invoke(user_input)
```

**LangSmith UI에서 확인:**
- 응답 시간
- 토큰 사용량
- 에러율
- 비용

### 2. 품질 개선

```python
# Before: 프롬프트 A
"You are a helpful assistant."

# After: 프롬프트 B
"You are a helpful assistant. Be concise and accurate."

# LangSmith에서 비교:
# 프롬프트 A: 정확도 75%
# 프롬프트 B: 정확도 85% ✅
```

### 3. 비용 최적화

```python
# LangSmith에서 발견:
# - 어떤 질문이 가장 많은 토큰을 사용하는가?
# - 불필요하게 긴 컨텍스트는 없는가?
# - 캐싱으로 절약 가능한 부분은?

# 개선:
# GPT-4 → GPT-3.5 for simple queries
# 비용 50% 감소 ✅
```

## 프로덕션 체크리스트

- [ ] LangSmith 트레이싱 설정
- [ ] 에러 알림 설정
- [ ] 평가 데이터셋 구성
- [ ] 정기적인 평가 실행
- [ ] 비용 모니터링 대시보드
- [ ] A/B 테스팅 프로세스

## 다음 단계

LangSmith를 마스터한 후:

1. **LangServe**: API 배포
2. **Vector DB**: 검색 성능 모니터링
3. **Multi-Agent**: 복잡한 시스템 디버깅

## 참고 자료

- [LangSmith 공식 문서](https://docs.smith.langchain.com/)
- [LangSmith Python SDK](https://github.com/langchain-ai/langsmith-sdk)
- [LangChain 공식 문서](https://python.langchain.com/docs/langsmith/)

## 문제 해결

### API Key 오류

```bash
# 환경 변수 확인
echo $LANGCHAIN_API_KEY
```

### 트레이싱이 안 됨

```python
# 환경 변수가 올바르게 설정되었는지 확인
import os
print(os.getenv("LANGCHAIN_TRACING_V2"))  # "true"여야 함
```

### UI에 데이터가 안 보임

- 프로젝트 이름 확인
- API Key 권한 확인
- 네트워크 연결 확인

---

**학습 목표**: LangSmith를 사용하여 LLM 애플리케이션을 프로덕션 환경에서 안정적으로 운영하고, 지속적으로 품질을 개선할 수 있다.
