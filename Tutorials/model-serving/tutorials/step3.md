# Step 3: 모델 비교 및 선택

## 목표

- 주요 로컬 LLM 모델 이해
- 성능 벤치마크 방법
- 용도별 모델 추천
- 하드웨어 요구사항 파악

## 주요 로컬 LLM 모델

### 1. Llama 3 (Meta)

**가장 인기 있는 오픈소스 모델**

```bash
ollama pull llama3:8b   # 8B 파라미터
ollama pull llama3:70b  # 70B 파라미터
```

**특징:**
- 크기: 8B, 70B
- 언어: 다국어 (한국어 포함)
- 용도: 범용
- 성능: ⭐⭐⭐⭐⭐

**장점:**
- 균형 잡힌 성능
- 다양한 작업에 우수
- 활발한 커뮤니티

### 2. Mistral (Mistral AI)

**코딩에 강한 모델**

```bash
ollama pull mistral:7b
```

**특징:**
- 크기: 7B
- 용도: 코드 생성, 기술 문서
- 성능: ⭐⭐⭐⭐

**장점:**
- 코드 품질 우수
- 빠른 추론 속도
- 효율적인 메모리 사용

### 3. Gemma (Google)

**Google의 경량 모델**

```bash
ollama pull gemma:7b
ollama pull gemma:2b   # 초경량
```

**특징:**
- 크기: 2B, 7B
- 용도: 빠른 응답, 경량화
- 성능: ⭐⭐⭐

**장점:**
- 빠른 속도
- 낮은 메모리 사용
- Google 기술력

### 4. Phi-3 (Microsoft)

**CPU에서도 실행 가능**

```bash
ollama pull phi3:mini   # 3.8B
```

**특징:**
- 크기: 3.8B
- 용도: 경량 작업, CPU 환경
- 성능: ⭐⭐

**장점:**
- GPU 없이 실행 가능
- 매우 가벼움
- 빠른 응답

## 모델 성능 비교

### 벤치마크 실행

```python
from langchain_community.llms import Ollama
import time

def benchmark_model(model_name, question):
    llm = Ollama(model=model_name)

    start = time.time()
    response = llm.invoke(question)
    elapsed = time.time() - start

    return {
        "time": elapsed,
        "length": len(response)
    }

question = "Python과 JavaScript의 차이를 3줄로 설명해줘"

models = ["llama3:8b", "mistral:7b", "gemma:7b"]

for model in models:
    result = benchmark_model(model, question)
    print(f"{model}: {result['time']:.2f}초, {result['length']}자")
```

**결과 예시:**
```
llama3:8b  : 3.45초, 234자
mistral:7b : 2.87초, 198자
gemma:7b   : 2.12초, 176자
```

### 품질 vs 속도

```
속도 ←─────────────────────→ 품질

phi3:mini → gemma:7b → mistral:7b → llama3:8b → llama3:70b
  (빠름)                                          (느림)
  (낮음)                                          (높음)
```

## 용도별 모델 추천

### 개발/테스트 환경

**추천: llama3:8b**

```python
llm = Ollama(model="llama3:8b")
```

**이유:**
- 균형 잡힌 성능
- 8GB VRAM에서 실행
- 대부분의 작업 처리

### 코드 생성

**추천: mistral:7b**

```python
llm = Ollama(model="mistral:7b")

code = llm.invoke("""
FastAPI로 사용자 등록 엔드포인트를 만들어줘.
Pydantic 모델 포함.
""")
```

**이유:**
- 코드 품질 우수
- 기술 문서 이해 뛰어남
- 프로그래밍 패턴 인식

### 빠른 응답 필요

**추천: gemma:7b**

```python
llm = Ollama(model="gemma:7b")
```

**이유:**
- 빠른 추론 속도
- 짧은 답변에 적합
- 챗봇 서비스

### CPU 환경

**추천: phi3:mini**

```python
llm = Ollama(model="phi3:mini")
```

**이유:**
- GPU 불필요
- 매우 가벼움 (3.8B)
- 기본 질의응답 가능

### 프로덕션 (최고 품질)

**추천: llama3:70b**

```python
llm = Ollama(model="llama3:70b")
```

**요구사항:**
- 40GB+ VRAM (RTX A6000 x2)
- 또는 양자화 버전 사용

## 하드웨어 요구사항

### 메모리 계산 공식

```
필요 메모리 = 모델 크기 x 1.2 ~ 1.5

예: 7B 모델 = 7B x 4bytes = 28GB
    실제 = 28GB x 1.2 = ~34GB (여유 포함)
```

### GPU 권장사항

| 모델 크기 | 최소 VRAM | 권장 GPU | 속도 |
|----------|----------|----------|------|
| 3B-7B | 8GB | RTX 3070, 4060 Ti | 보통 |
| 7B-13B | 16GB | RTX 3090, 4080 | 빠름 |
| 13B-30B | 24GB | RTX 3090, 4090 | 빠름 ✅ |
| 70B+ | 40GB+ | A6000 x2 | 매우 빠름 |

### CPU 실행

```bash
# 작은 모델만 가능
ollama run phi3:mini
ollama run gemma:2b
```

**성능:**
- 7B 모델: 매우 느림 (15-30초/응답)
- 3B 모델: 느림 (5-10초/응답)

**권장 RAM:**
- 7B: 16GB 이상
- 3B: 8GB 이상

## 모델 선택 가이드

### 플로우차트

```
GPU 있음?
├─ 예
│  ├─ 24GB+ VRAM → llama3:70b (최고 품질)
│  ├─ 16GB VRAM  → llama3:13b (고품질)
│  └─ 8GB VRAM   → llama3:8b (권장) ✅
└─ 아니오
   └─ phi3:mini (CPU, 기본 작업만)

용도별
├─ 범용      → llama3:8b
├─ 코딩      → mistral:7b
├─ 빠른 응답 → gemma:7b
└─ 경량      → phi3:mini
```

## 양자화 (Quantization)

### 모델 크기 줄이기

```bash
# 기본 (FP16)
ollama pull llama3:8b

# 양자화 버전 (4-bit)
ollama pull llama3:8b-q4_0
```

**효과:**
```
llama3:70b (FP16) : 140GB
llama3:70b-q4_0   : 40GB   (3.5배 작음)
```

**트레이드오프:**
- 메모리: 1/3 수준
- 속도: 더 빠름
- 품질: 약간 하락 (보통 무시 가능)

## 실전 조합

### 개인 프로젝트

```python
# 로컬 개발
llm = Ollama(model="llama3:8b")
```

**환경:** RTX 3070 (8GB)

### 스타트업 서비스

```python
# API 서버
llm = Ollama(model="llama3:70b-q4_0")
```

**환경:** RTX 4090 (24GB) x2

### 엔터프라이즈

```python
# vLLM로 서빙
# llama3:70b 여러 대 로드밸런싱
```

**환경:** A100 (40GB) x4

## 핵심 요약

| 시나리오 | 추천 모델 | 필요 GPU |
|---------|----------|---------|
| 개발/학습 | llama3:8b | RTX 3070 (8GB) |
| 코드 생성 | mistral:7b | RTX 3070 (8GB) |
| 빠른 챗봇 | gemma:7b | RTX 3060 (6GB) |
| CPU 환경 | phi3:mini | GPU 불필요 |
| 프로덕션 | llama3:70b | A100 (40GB) |

## 다음 단계

**Advanced RAG Tutorial**
- Hybrid Search (BM25 + Vector)
- Reranking으로 정확도 향상
- 로컬 LLM + RAG 조합

---

**실습 체크리스트:**
- [ ] 3개 이상 모델 다운로드
- [ ] 동일 질문으로 성능 비교
- [ ] 응답 시간 측정
- [ ] 내 GPU로 실행 가능한 최대 모델 확인
- [ ] 용도에 맞는 모델 선택

**모델 선택 = 성능 vs 비용 vs 속도의 균형** ✅
