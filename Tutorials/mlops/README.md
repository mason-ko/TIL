# MLOps 기초 튜토리얼

LLM 애플리케이션의 배포, 모니터링, 운영

## 개요

LLM 애플리케이션을 **프로덕션 환경에서 안정적으로 운영**하는 방법을 학습합니다.

## MLOps란?

**ML + DevOps** = 머신러닝 시스템의 지속적 배포 및 운영

### 일반 소프트웨어 vs ML 시스템

| 구분 | 일반 SW | ML 시스템 |
|------|---------|----------|
| **배포 단위** | 코드 | 코드 + 모델 + 데이터 |
| **테스트** | 단위 테스트 | + 모델 성능 테스트 |
| **모니터링** | 에러, 지연시간 | + 품질, 비용, 드리프트 |
| **업데이트** | 코드 배포 | 모델 재학습 필요 |

## MLOps 파이프라인

```
1. 개발
   ├─ 모델 선택
   ├─ 프롬프트 개발
   └─ 평가

2. 배포
   ├─ 컨테이너화 (Docker)
   ├─ API 서버 (FastAPI)
   └─ CI/CD (GitHub Actions)

3. 모니터링
   ├─ 성능 (지연시간, 처리량)
   ├─ 품질 (정확도, 관련성)
   └─ 비용 (토큰, API 호출)

4. 운영
   ├─ A/B 테스팅
   ├─ 모델 업데이트
   └─ 스케일링
```

## 학습 목차

**Step 1**: Docker 컨테이너화
**Step 2**: FastAPI 서버 구축
**Step 3**: CI/CD 파이프라인
**Step 4**: 모니터링 (Prometheus, Grafana)
**Step 5**: 로깅 및 추적
**Step 6**: 프로덕션 최적화

## 주요 도구

### 배포
- **Docker**: 컨테이너화
- **Kubernetes**: 오케스트레이션
- **FastAPI**: API 서버
- **LangServe**: LangChain 배포

### 모니터링
- **LangSmith**: LLM 전용 모니터링
- **Prometheus**: 메트릭 수집
- **Grafana**: 시각화
- **Sentry**: 에러 추적

### CI/CD
- **GitHub Actions**: 자동 배포
- **GitLab CI**: CI/CD
- **ArgoCD**: GitOps

## 프로덕션 체크리스트

### 1. 성능
- [ ] 응답 시간 < 3초
- [ ] 처리량 목표 달성
- [ ] 캐싱 적용
- [ ] 배치 처리

### 2. 안정성
- [ ] 에러 핸들링
- [ ] 재시도 로직
- [ ] Rate Limiting
- [ ] Fallback 전략

### 3. 모니터링
- [ ] 실시간 메트릭
- [ ] 알림 설정
- [ ] 로그 수집
- [ ] 비용 추적

### 4. 보안
- [ ] API Key 관리
- [ ] Input 검증
- [ ] Rate Limiting
- [ ] 데이터 암호화

## 빠른 시작

```python
# FastAPI 서버
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI

app = FastAPI()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

@app.post("/chat")
async def chat(message: str):
    response = llm.invoke(message)
    return {"response": response.content}
```

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 배포
docker build -t my-llm-app .
docker run -p 8000:8000 my-llm-app
```

## 모니터링 메트릭

### 성능
- **Latency**: 응답 시간 (P50, P95, P99)
- **Throughput**: 초당 요청 수
- **Error Rate**: 에러 비율

### 품질
- **Accuracy**: 정확도
- **Relevance**: 관련성
- **User Satisfaction**: 사용자 피드백

### 비용
- **Token Usage**: 토큰 사용량
- **API Cost**: API 비용
- **Infrastructure**: 인프라 비용

---

**학습 목표**: LLM 애플리케이션을 프로덕션 환경에 배포하고 안정적으로 운영할 수 있다.
