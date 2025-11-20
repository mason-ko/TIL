# Langfuse 튜토리얼

오픈소스 LLM Observability 플랫폼 - 로컬 LLM 최적화

## 개요

**Langfuse**는 LLM 애플리케이션을 모니터링하고 디버깅하기 위한 **오픈소스** 플랫폼입니다.

### 왜 Langfuse인가?

| 특징 | Langfuse | LangSmith |
|------|----------|-----------|
| **라이선스** | 오픈소스 (MIT) ✅ | 클로즈드 소스 |
| **비용** | 무료 (Self-hosted) ✅ | $39/월~ |
| **데이터** | 내 서버 저장 ✅ | 외부 클라우드 |
| **로컬 LLM** | 완벽 지원 ✅ | API 중심 |
| **커스터마이징** | 자유롭게 ✅ | 제한적 |

## 핵심 기능

### 1. Tracing (추적)
```python
모든 LLM 호출 자동 기록
- 입력/출력
- 지연시간
- 토큰 사용량 (로컬 LLM도 측정)
- 에러 추적
```

### 2. Evaluation (평가)
```python
모델 출력 품질 자동 측정
- 정확도
- 관련성
- 사용자 피드백
```

### 3. Datasets (데이터셋)
```python
테스트 케이스 관리
- 프로덕션 데이터 수집
- 회귀 테스트
- A/B 테스팅
```

### 4. Metrics (메트릭)
```python
실시간 대시보드
- 처리량
- 평균 지연시간
- 에러율
- 비용 (API 사용 시)
```

## 로컬 LLM과의 완벽한 조합

### Ollama + Langfuse

```python
from langfuse import Langfuse
from langchain_community.llms import Ollama

# Langfuse 초기화 (로컬)
langfuse = Langfuse(
    public_key="pk-local",
    secret_key="sk-local",
    host="http://localhost:3000"  # 로컬 서버
)

# Ollama 모델
llm = Ollama(model="llama3")

# 자동 트레이싱
trace = langfuse.trace(name="local-chat")
response = llm.invoke("안녕하세요!")

# 모든 것이 로컬에 저장됨!
```

### vLLM + Langfuse

```python
# vLLM API 서버와 연동
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

# Langfuse로 추적
trace = langfuse.trace(name="vllm-inference")
response = client.chat.completions.create(
    model="meta-llama/Llama-3-8B",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 설치 및 설정

### Self-hosted (권장)

```bash
# Docker Compose로 설치
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# 환경 변수 설정
cp .env.example .env

# 실행
docker compose up -d

# 접속: http://localhost:3000
```

### 클라우드 (선택사항)

```bash
# Langfuse Cloud (무료 티어 있음)
# https://cloud.langfuse.com
```

## 환경 설정

`.env` 파일:

```bash
# Langfuse 서버
LANGFUSE_PUBLIC_KEY=pk-local
LANGFUSE_SECRET_KEY=sk-local
LANGFUSE_HOST=http://localhost:3000

# LLM (Ollama 또는 다른 것)
# 로컬 LLM이라면 API Key 불필요
```

## 학습 목차

### Step 1: Langfuse 설치 및 기본 설정
- Docker로 로컬 서버 설치
- 첫 trace 생성
- UI 살펴보기

**파일**: `tutorials/step1.md`, `tutorials/step1.py`

### Step 2: Ollama 연동
- Langfuse + Ollama 통합
- 로컬 LLM 트레이싱
- 성능 측정

**파일**: `tutorials/step2.md`, `tutorials/step2.py`

### Step 3: 평가 (Evaluation)
- 자동 평가 설정
- 품질 메트릭
- 프롬프트 비교

**파일**: `tutorials/step3.md`, `tutorials/step3.py`

### Step 4: 데이터셋 관리
- 테스트 데이터셋 생성
- 프로덕션 데이터 수집
- 회귀 테스트

**파일**: `tutorials/step4.md`, `tutorials/step4.py`

### Step 5: 프로덕션 모니터링
- 실시간 메트릭 대시보드
- 알림 설정
- 에러 추적

**파일**: `tutorials/step5.md`, `tutorials/step5.py`

### Step 6: 고급 기능
- 사용자 피드백 수집
- 세션 관리
- 커스텀 메타데이터

**파일**: `tutorials/step6.md`, `tutorials/step6.py`

## 빠른 시작

```python
from langfuse import Langfuse
from langchain_community.llms import Ollama

# 1. Langfuse 초기화
langfuse = Langfuse(
    public_key="pk-local",
    secret_key="sk-local",
    host="http://localhost:3000"
)

# 2. LLM 설정 (Ollama)
llm = Ollama(model="llama3")

# 3. 트레이싱
trace = langfuse.trace(name="chat")

generation = trace.generation(
    name="llama3-call",
    model="llama3",
    input="Python이란?"
)

response = llm.invoke("Python이란?")

generation.end(output=response)

print(f"Response: {response}")
print(f"Trace URL: {trace.get_trace_url()}")
```

## Langfuse vs LangSmith

### Langfuse가 더 나은 경우

✅ **로컬 LLM 사용** (Ollama, vLLM)
```python
이유:
- Self-hosted 가능
- 데이터가 외부로 나가지 않음
- 비용 $0
```

✅ **데이터 프라이버시 중요**
```python
이유:
- 모든 데이터가 내 서버
- GDPR 준수 쉬움
```

✅ **비용 절감**
```python
이유:
- Self-hosted는 무료
- 인프라 비용만 발생
```

✅ **커스터마이징 필요**
```python
이유:
- 오픈소스라 코드 수정 가능
- 자체 기능 추가 가능
```

### LangSmith가 더 나은 경우

✅ **API 기반 LLM 집중 사용** (OpenAI, Claude, Gemini)
```python
이유:
- LangChain 네이티브 통합
- 토큰 비용 자동 계산
```

✅ **빠른 시작 원함**
```python
이유:
- 클라우드 서비스 (설치 불필요)
- 5분 만에 시작
```

✅ **인프라 관리 싫음**
```python
이유:
- 관리형 서비스
- 업데이트 자동
```

## 실무 권장 스택

### 로컬 LLM 스택 (비용 최소화)

```
모니터링:
├─ Langfuse (LLM 전용) - $0
└─ Prometheus + Grafana (인프라) - $0

모델:
├─ Ollama (개발/테스트) - $0
└─ vLLM (프로덕션) - 서버 비용만

Vector DB:
├─ ChromaDB (로컬) - $0
└─ Qdrant (Self-hosted) - $0

총 비용: 서버 인프라만 ($100~500/월)
vs API 기반: $1,000~10,000/월
```

### 하이브리드 스택 (품질 + 비용)

```
중요한 쿼리:
└─ OpenAI GPT-4 (LangSmith)

일반 쿼리:
└─ Ollama Llama3 (Langfuse)

비용: 90% 절감
품질: 핵심만 고품질
```

## 프로덕션 체크리스트

- [ ] Langfuse Self-hosted 설치
- [ ] PostgreSQL 백업 설정
- [ ] Nginx reverse proxy 설정
- [ ] SSL 인증서 (HTTPS)
- [ ] 모니터링 대시보드 구성
- [ ] 알림 설정 (Slack, Email)
- [ ] 데이터 보관 정책

## 성능 벤치마크

### Langfuse (Self-hosted)

```
처리량: 10,000 traces/초
지연시간: < 10ms (추가 오버헤드)
저장소: PostgreSQL
확장성: 수평 확장 가능
```

### 리소스 요구사항

```
최소:
- CPU: 2 cores
- RAM: 4GB
- Disk: 50GB

권장 (프로덕션):
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 200GB+ (SSD)
```

## 다음 단계

Langfuse 마스터 후:

1. **Prometheus + Grafana**: 인프라 메트릭
2. **Advanced RAG**: 검색 품질 개선
3. **Multi-Agent**: 복잡한 시스템 디버깅

## 참고 자료

- [Langfuse 공식 문서](https://langfuse.com/docs)
- [GitHub](https://github.com/langfuse/langfuse)
- [Discord 커뮤니티](https://discord.gg/7NXusRtqYU)
- [Self-hosting 가이드](https://langfuse.com/docs/deployment/self-host)

## 문제 해결

### Docker 컨테이너 시작 안 됨

```bash
# 로그 확인
docker compose logs

# 포트 충돌 확인
lsof -i :3000
```

### PostgreSQL 연결 오류

```bash
# .env 파일에서 DATABASE_URL 확인
DATABASE_URL=postgresql://postgres:postgres@db:5432/langfuse
```

### Trace가 UI에 안 보임

```python
# Flush 명시적 호출
langfuse.flush()
```

---

**학습 목표**: Langfuse를 Self-hosted로 운영하며 로컬 LLM 애플리케이션을 모니터링하고, 비용 없이 프로덕션 품질을 유지할 수 있다.
