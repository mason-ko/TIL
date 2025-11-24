# Step 2: 임베딩 모델 선택 및 최적화

## 목표

- 다양한 임베딩 모델 이해
- 한국어 최적화 모델 선택
- 임베딩 품질 비교

## 임베딩이란?

**텍스트를 숫자 벡터로 변환**하는 과정

```python
"강아지" → [0.1, 0.3, -0.2, 0.8, ...]  # 384차원 벡터
"개"     → [0.11, 0.29, -0.21, 0.79, ...] # 유사한 벡터

벡터 간 거리 = 의미 유사도
```

## 주요 임베딩 모델

### 1. all-MiniLM-L6-v2 (기본)

ChromaDB의 기본 모델

**특징:**
- 크기: 384차원
- 속도: 빠름
- 언어: 영어 중심
- 용도: 범용

**사용법:**
```python
# ChromaDB는 자동으로 사용
collection = client.create_collection("default")
```

### 2. paraphrase-multilingual-MiniLM-L12-v2 (한국어)

다국어 지원, **한국어 권장**

**특징:**
- 크기: 384차원
- 속도: 빠름
- 언어: 50개 언어 (한국어 포함)
- 용도: 다국어 환경

**사용법:**
```python
from chromadb.utils import embedding_functions

multilingual_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

collection = client.create_collection(
    "multilingual",
    embedding_function=multilingual_ef
)
```

### 3. text-embedding-3-small (OpenAI)

최고 품질, 유료

**특징:**
- 크기: 1536차원
- 속도: API 호출
- 언어: 모든 언어
- 비용: $0.02 / 1M tokens

**사용법:**
```python
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    "openai",
    embedding_function=openai_ef
)
```

## 모델 비교표

| 모델 | 차원 | 속도 | 품질 | 비용 | 한국어 |
|------|------|------|------|------|--------|
| all-MiniLM-L6-v2 | 384 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 무료 | △ |
| paraphrase-multilingual | 384 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 무료 | ✅ |
| text-embedding-3-small | 1536 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 유료 | ✅ |

## 언제 어떤 모델?

### 영어 중심
```python
→ all-MiniLM-L6-v2 (기본)
```

### 한국어 / 다국어
```python
→ paraphrase-multilingual-MiniLM-L12-v2 ✅
```

### 최고 품질 필요
```python
→ OpenAI text-embedding-3-small
   (비용 고려 필요)
```

## 실습 예제

### 예제 1: 기본 vs 다국어 비교

```python
# 기본 모델
collection_default = client.create_collection("default")
collection_default.add(
    documents=["강아지가 뛰어놀고 있다", "고양이가 자고 있다"],
    ids=["d1", "d2"]
)

# 검색: "개가 노는 모습"
results = collection_default.query(query_texts=["개가 노는 모습"], n_results=1)
# → 한국어라 정확도 낮을 수 있음

# 다국어 모델
multilingual_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

collection_multi = client.create_collection(
    "multilingual",
    embedding_function=multilingual_ef
)

collection_multi.add(
    documents=["강아지가 뛰어놀고 있다", "고양이가 자고 있다"],
    ids=["d1", "d2"]
)

results = collection_multi.query(query_texts=["개가 노는 모습"], n_results=1)
# → "강아지가 뛰어놀고 있다" 정확하게 찾음 ✅
```

### 예제 2: 커스텀 임베딩 함수

```python
from sentence_transformers import SentenceTransformer

# 직접 모델 로드
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 임베딩 생성
texts = ["안녕하세요", "Hello"]
embeddings = model.encode(texts)

print(f"벡터 크기: {embeddings.shape}")
# → (2, 384)
```

## 성능 최적화

### 1. 모델 캐싱

첫 실행 시 모델 다운로드 → 이후 캐시 사용

```python
# 첫 실행: 모델 다운로드 (시간 소요)
# 두 번째 실행: 캐시에서 로드 (빠름)
```

### 2. 배치 임베딩

여러 문서를 한 번에 임베딩

```python
# 비효율적
for doc in documents:
    embedding = model.encode(doc)

# 효율적
embeddings = model.encode(documents, batch_size=32)
```

## 실무 권장사항

**한국어 서비스:**
```python
paraphrase-multilingual-MiniLM-L12-v2
- 무료
- 한국어 성능 우수
- 빠른 속도
```

**다국어 서비스:**
```python
같은 모델 사용
- 50개 언어 지원
- 일관된 품질
```

**최고 품질 필요:**
```python
OpenAI text-embedding-3-small
- 비용 고려 ($0.02/1M tokens)
- API 지연시간 고려
```

## 다음 단계

**Step 3: RAG 실전 구현**에서는:
- 실제 문서 처리
- 검색 시스템 구축
- LLM과 통합

---

**핵심 요약:**
- 한국어 → paraphrase-multilingual ✅
- 무료 + 품질 좋음
- ChromaDB와 쉽게 통합
