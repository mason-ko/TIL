# Step 2: Docker 컨테이너화

## 목표

- Docker로 LLM API 패키징
- 이식성 확보 (어디서나 실행)
- 배포 자동화 기초
- 환경 일관성 보장

## 왜 Docker?

### 문제: "내 컴퓨터에서는 되는데..."

```bash
# 개발자 A (Mac)
Python 3.11, pip install fastapi
→ 작동 ✅

# 개발자 B (Windows)
Python 3.9, pip install fastapi
→ 오류 ❌ (버전 차이)

# 서버 (Ubuntu)
Python 3.10, pip install fastapi
→ 오류 ❌ (의존성 충돌)
```

### 해결: Docker 컨테이너

```bash
# 모든 환경에서
docker run llm-api
→ 작동 ✅ (동일한 환경)
```

**Docker = 앱 + 환경을 하나로 패키징**

## Docker 기본 개념

### 이미지 vs 컨테이너

```
[이미지]                [컨테이너]
설계도, 템플릿    →      실행 중인 인스턴스

예:
Python:3.11 이미지  →   실제 Python 프로세스
FastAPI 앱 이미지   →   실행 중인 API 서버
```

### 비유

```
이미지 = 요리 레시피
컨테이너 = 실제 음식

하나의 레시피로 → 여러 음식 만들기 가능
```

## Dockerfile 작성

### 기본 구조

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 각 줄 설명

```dockerfile
# 1. 베이스 이미지 선택
FROM python:3.11-slim
# slim = 경량화 버전 (500MB → 150MB)

# 2. 작업 디렉토리 설정
WORKDIR /app
# 이후 모든 명령은 /app에서 실행

# 3. 의존성 파일 복사
COPY requirements.txt .
# 먼저 복사 → 캐싱 효율

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir = 캐시 삭제 (용량 절약)

# 5. 앱 코드 복사
COPY . .
# 현재 디렉토리 전체 → /app

# 6. 포트 노출
EXPOSE 8000
# 문서화 목적 (실제로는 -p 옵션 필요)

# 7. 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 컨테이너 시작 시 실행
```

## requirements.txt

### 최소 버전

```txt
fastapi==0.109.0
uvicorn==0.27.0
langchain-community==0.0.38
python-dotenv==1.0.0
```

### 권장: 버전 고정

```txt
# 나쁜 예
fastapi>=0.100.0  # 버전 변동 가능

# 좋은 예
fastapi==0.109.0  # 버전 고정
```

**이유:** 재현 가능성 (reproducibility)

## FastAPI 앱 (main.py)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LLM API")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def root():
    return {
        "message": "LLM API Server",
        "status": "running"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # 실제로는 Ollama 호출
    # 여기서는 Echo 예제
    return ChatResponse(
        response=f"Echo: {request.message}"
    )

@app.get("/health")
def health():
    return {"status": "healthy"}
```

### Health Check 엔드포인트

```python
@app.get("/health")
def health():
    return {"status": "healthy"}
```

**용도:**
- Kubernetes liveness probe
- 로드밸런서 체크
- 모니터링 시스템

## Docker 빌드

### 1. 이미지 빌드

```bash
docker build -t llm-api .
```

**플래그 설명:**
- `-t llm-api`: 이미지 이름 (태그)
- `.`: Dockerfile 위치 (현재 디렉토리)

### 2. 빌드 과정

```
Step 1/7 : FROM python:3.11-slim
 → Pulling from library/python
Step 2/7 : WORKDIR /app
 → Running in abc123...
Step 3/7 : COPY requirements.txt .
 → 복사 완료
Step 4/7 : RUN pip install...
 → 패키지 설치 중...
Step 5/7 : COPY . .
 → 코드 복사
Step 6/7 : EXPOSE 8000
Step 7/7 : CMD ["uvicorn"...]
Successfully built xyz789
Successfully tagged llm-api:latest
```

### 3. 이미지 확인

```bash
docker images

REPOSITORY   TAG       SIZE
llm-api      latest    234MB
python       3.11-slim 151MB
```

## Docker 실행

### 1. 기본 실행

```bash
docker run -p 8000:8000 llm-api
```

**플래그:**
- `-p 8000:8000`: 포트 매핑 (호스트:컨테이너)

### 2. 백그라운드 실행

```bash
docker run -d -p 8000:8000 llm-api
```

**플래그:**
- `-d`: detached mode (백그라운드)

**출력:**
```
abc123def456  # 컨테이너 ID
```

### 3. 이름 지정

```bash
docker run -d -p 8000:8000 --name my-llm-api llm-api
```

**플래그:**
- `--name`: 컨테이너 이름 지정

### 4. 환경 변수

```bash
docker run -d -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  llm-api
```

**플래그:**
- `-e`: 환경 변수 설정

## Docker 관리

### 로그 확인

```bash
# 실시간 로그
docker logs -f my-llm-api

# 최근 100줄
docker logs --tail 100 my-llm-api
```

### 컨테이너 목록

```bash
# 실행 중
docker ps

# 전체
docker ps -a
```

### 컨테이너 중지/시작

```bash
# 중지
docker stop my-llm-api

# 시작
docker start my-llm-api

# 재시작
docker restart my-llm-api
```

### 컨테이너 삭제

```bash
# 중지 후 삭제
docker stop my-llm-api
docker rm my-llm-api

# 강제 삭제 (실행 중이어도)
docker rm -f my-llm-api
```

### 이미지 삭제

```bash
docker rmi llm-api
```

## 테스트

### 1. Health Check

```bash
curl http://localhost:8000/health

# 응답
{"status": "healthy"}
```

### 2. Root 엔드포인트

```bash
curl http://localhost:8000

# 응답
{"message": "LLM API Server", "status": "running"}
```

### 3. Chat 엔드포인트

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# 응답
{"response": "Echo: Hello"}
```

## 실무 팁

### 1. .dockerignore

```
# .dockerignore
__pycache__/
*.pyc
.env
.git/
*.log
venv/
.vscode/
```

**효과:** 빌드 속도 향상, 이미지 크기 감소

### 2. 멀티 스테이지 빌드

```dockerfile
# 빌드 스테이지
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 실행 스테이지
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**효과:** 더 작은 이미지 (빌드 도구 제외)

### 3. 레이어 캐싱

```dockerfile
# 나쁜 예 (캐시 무효화)
COPY . .
RUN pip install -r requirements.txt

# 좋은 예 (캐시 활용)
COPY requirements.txt .
RUN pip install -r requirements.txt  # 캐시됨
COPY . .  # 코드 변경해도 위는 재사용
```

## Ollama 연동

### Host 네트워크 사용

```bash
docker run -d -p 8000:8000 \
  --network host \
  llm-api
```

### 환경 변수로 Ollama 주소 전달

```python
# main.py
import os
from langchain_community.llms import Ollama

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
llm = Ollama(model="llama3", base_url=OLLAMA_HOST)
```

```bash
docker run -d -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  llm-api
```

## 다음 단계

**Step 3: Kubernetes 배포**
- 여러 컨테이너 오케스트레이션
- 자동 스케일링
- 로드 밸런싱
- 프로덕션 배포

---

**핵심 요약:**
1. Dockerfile = 앱 + 환경 정의
2. `docker build` = 이미지 생성
3. `docker run` = 컨테이너 실행
4. 이식성 ↑ (어디서나 동일하게 실행)

**Docker = MLOps의 기본, 모든 배포의 시작점** ✅
