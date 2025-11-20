# Step 1: Docker로 LLM 앱 컨테이너화

## 목표

- Docker 기본 이해
- FastAPI 서버 구축
- LLM 앱 컨테이너화
- 로컬 배포

## 왜 MLOps?

```python
개발 환경:
- 내 PC에서만 작동
- "내 컴퓨터에선 돼요"

프로덕션:
- 어디서나 작동
- 확장 가능
- 모니터링
```

## Docker란?

**앱을 컨테이너로 패키징**

```
장점:
✅ 어디서나 동일하게 실행
✅ 의존성 충돌 없음
✅ 배포 간단
```

## FastAPI LLM 서버

```python
from fastapi import FastAPI
from langchain_community.llms import Ollama

app = FastAPI()
llm = Ollama(model="llama3")

@app.post("/chat")
def chat(message: str):
    return {"response": llm.invoke(message)}
```

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## 실행

```bash
docker build -t my-llm-app .
docker run -p 8000:8000 my-llm-app
```

## 핵심 요약

- **Docker = 앱 패키징**
- **FastAPI = API 서버**
- **어디서나 배포 가능**

---

**다음**: step2 - CI/CD 파이프라인
