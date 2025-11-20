# Step 1: Ollama로 로컬 LLM 실행하기

## 목표

- Ollama 설치 및 설정
- Llama 3 모델 실행
- Python에서 Ollama 사용
- API 비용 $0 달성

## Ollama란?

**로컬에서 LLM을 쉽게 실행**할 수 있게 해주는 도구

### 장점
- ✅ 완전 무료
- ✅ 설치 간단
- ✅ 다양한 모델 (Llama 3, Mistral, Gemma 등)
- ✅ API 호환 (OpenAI API와 유사)

### 비용 비교
```
OpenAI GPT-3.5: $0.50 / 1M tokens
Ollama Llama 3: $0 (로컬 실행)

월 10M 토큰 사용 시:
- OpenAI: $5,000
- Ollama: $0
```

## 설치

```bash
# Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# https://ollama.com/download
```

## 모델 다운로드

```bash
# Llama 3 (8B)
ollama pull llama3

# Mistral (7B)
ollama pull mistral

# 모델 목록 확인
ollama list
```

## 실행

```bash
# CLI에서 대화
ollama run llama3

# 백그라운드 서버 실행
ollama serve
```

## Python 사용

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
response = llm.invoke("안녕하세요!")
print(response)
```

## 핵심 요약

- **Ollama = 로컬 LLM 실행 도구**
- **비용 $0**
- **설치 5분, 사용 간단**

---

**다음**: step2 - vLLM으로 고성능 배포
