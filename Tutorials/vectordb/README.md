# Vector Database 튜토리얼

임베딩 벡터 저장 및 유사도 검색을 위한 벡터 데이터베이스 학습

## 개요

Vector DB는 **임베딩 벡터를 효율적으로 저장하고 검색**하는 데이터베이스입니다. RAG, 의미 검색, 추천 시스템 등에 필수적입니다.

## 왜 Vector DB가 필요한가?

### 문제상황

```python
# 일반 DB (키워드 매칭)
query = "강아지 사료"
result = db.search(WHERE text LIKE "%강아지%" OR text LIKE "%사료%")
→ "강아지" 또는 "사료"라는 단어가 있는 문서만 찾음

# 문제:
- "반려견 먹이" → 못 찾음 (다른 단어)
- "개 간식" → 못 찾음 (유사하지만 다름)
```

### Vector DB의 해결

```python
# Vector DB (의미 검색)
query_embedding = embed("강아지 사료")
results = vectordb.search(query_embedding, top_k=5)

→ "반려견 먹이" ✅ (의미가 비슷)
→ "개 간식" ✅ (관련 있음)
→ "강아지 영양" ✅ (유사한 주제)
```

## 주요 Vector DB

| DB | 특징 | 사용 사례 |
|----|----|--------|
| **ChromaDB** | 가벼움, 로컬 우선 | 개발, 프로토타입 |
| **Pinecone** | 관리형, 확장성 | 프로덕션, 대규모 |
| **Weaviate** | GraphQL, 오픈소스 | 하이브리드 검색 |
| **Qdrant** | 빠름, Rust 기반 | 고성능 필요 |
| **Milvus** | 분산, 대규모 | 엔터프라이즈 |

## 학습 목차

### Step 1: ChromaDB 기본
- 로컬 벡터 DB 설정
- 문서 추가 및 검색
- 메타데이터 필터링

### Step 2: 임베딩 모델
- OpenAI Embeddings
- HuggingFace Embeddings
- 다국어 임베딩

### Step 3: 고급 검색
- 유사도 메트릭 (cosine, euclidean)
- 하이브리드 검색 (키워드 + 벡터)
- MMR (Maximal Marginal Relevance)

### Step 4: Pinecone 프로덕션
- 클라우드 Vector DB 설정
- 대규모 데이터 인덱싱
- 성능 최적화

### Step 5: RAG 통합
- LangChain Vector Store
- Retrieval Chain 구성
- 컨텍스트 관리

## 핵심 개념

### 1. 임베딩 (Embedding)

텍스트를 숫자 벡터로 변환:

```python
text = "강아지 사료"
embedding = [0.1, 0.3, -0.2, ...]  # 1536차원 벡터

유사한 의미 = 가까운 벡터
다른 의미 = 먼 벡터
```

### 2. 유사도 검색

```python
query_vector = [0.1, 0.3, -0.2, ...]
db_vectors = [
    [0.11, 0.29, -0.21, ...],  # 거리: 0.02 ✅ 가장 유사
    [0.5, -0.1, 0.8, ...],     # 거리: 1.5
]
```

### 3. 인덱싱

빠른 검색을 위한 자료구조:
- **HNSW**: 그래프 기반, 빠름
- **IVF**: 클러스터링 기반
- **Flat**: 정확하지만 느림

## 설치

```bash
pip install -r requirements.txt
```

## 빠른 시작

```python
import chromadb

# 1. DB 생성
client = chromadb.Client()
collection = client.create_collection("my_docs")

# 2. 문서 추가
collection.add(
    documents=["강아지 사료", "고양이 간식", "반려견 영양"],
    ids=["doc1", "doc2", "doc3"]
)

# 3. 검색
results = collection.query(
    query_texts=["개 먹이"],
    n_results=2
)

print(results)
# → ["강아지 사료", "반려견 영양"]
```

## 실무 활용

### 1. 문서 검색 (RAG)

```python
# 대량 문서 저장
vectordb.add(documents=all_company_docs)

# 사용자 질문에 관련 문서 검색
relevant_docs = vectordb.search(user_question)

# LLM에 컨텍스트로 제공
answer = llm.invoke(f"Context: {relevant_docs}\n\nQuestion: {user_question}")
```

### 2. 의미 기반 추천

```python
# 사용자가 본 상품
user_viewed = "나이키 운동화"

# 유사한 상품 추천
similar_products = vectordb.search(user_viewed, k=10)
```

### 3. 중복 제거

```python
# 새 문서가 이미 있는지 확인
new_doc = "Python 튜토리얼"
similar = vectordb.search(new_doc, k=1)

if similar[0].similarity > 0.95:
    print("이미 존재하는 문서")
```

## 성능 최적화

### 1. 임베딩 캐싱

```python
# 같은 텍스트는 캐시에서 가져오기
cache = {}

def get_embedding(text):
    if text in cache:
        return cache[text]
    embedding = model.embed(text)
    cache[text] = embedding
    return embedding
```

### 2. 배치 처리

```python
# 한 번에 여러 문서 임베딩
embeddings = model.embed_batch(documents, batch_size=32)
```

### 3. 인덱스 튜닝

```python
# HNSW 파라미터 조정
collection = client.create_collection(
    name="optimized",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:M": 16,  # 연결 수
        "hnsw:efConstruction": 200  # 구축 시 탐색 깊이
    }
)
```

## 다음 단계

Vector DB 마스터 후:
1. **Advanced RAG**: 하이브리드 검색, Reranking
2. **Multi-Modal**: 이미지 + 텍스트 검색
3. **LangSmith**: 검색 품질 모니터링

---

**학습 목표**: Vector DB를 사용하여 대규모 문서에서 의미 기반 검색을 구현하고, RAG 시스템을 구축할 수 있다.
