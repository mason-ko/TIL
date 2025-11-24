# Step 4: Pinecone 프로덕션

## 목표

- 클라우드 Vector DB 설정
- 대규모 데이터 인덱싱
- 성능 최적화
- 프로덕션 환경 고려사항

## 왜 Pinecone인가?

### ChromaDB vs Pinecone

| 항목 | ChromaDB | Pinecone |
|------|----------|----------|
| **배포** | 로컬/Self-hosted | 클라우드 관리형 |
| **확장성** | 수백만 벡터 | 수십억 벡터 |
| **비용** | 무료 | 유료 ($70/월~) |
| **관리** | 직접 관리 | 자동 관리 |
| **속도** | 빠름 | 매우 빠름 |
| **용도** | 개발, 소규모 | 프로덕션, 대규모 |

### 언제 Pinecone을 사용할까?

**Pinecone이 필요한 경우:**
- ✅ 수백만 개 이상의 문서
- ✅ 글로벌 서비스 (낮은 레이턴시)
- ✅ 자동 확장 필요
- ✅ 인프라 관리 부담 없음

**ChromaDB가 충분한 경우:**
- ✅ 개발/프로토타입
- ✅ 소규모 데이터 (< 100만 벡터)
- ✅ 비용 절감 중요
- ✅ 데이터 프라이버시

## Pinecone 설정

### 1. 계정 생성

```bash
# https://app.pinecone.io/ 접속
# 무료 티어: 1개 인덱스, 100만 벡터
```

### 2. API 키 발급

```bash
# .env 파일
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=your-environment  # 예: us-east-1-aws
```

### 3. 설치

```bash
pip install pinecone-client langchain-pinecone
```

## Pinecone 기본 사용

### 인덱스 생성

```python
import pinecone
import os

# 초기화
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

# 인덱스 생성
index_name = "knowledge-base"

if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # OpenAI 임베딩 차원
        metric="cosine"  # 유사도 메트릭
    )

# 인덱스 연결
index = pinecone.Index(index_name)
```

### 데이터 추가

```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

documents = [
    "LangGraph는 상태 기반 워크플로우 라이브러리입니다.",
    "Langfuse는 오픈소스 LLM 모니터링 도구입니다.",
    "ChromaDB는 로컬 벡터 데이터베이스입니다."
]

# 임베딩 생성
vectors = embeddings.embed_documents(documents)

# Pinecone에 업로드
index.upsert(vectors=[
    (f"doc{i}", vector, {"text": doc})
    for i, (vector, doc) in enumerate(zip(vectors, documents))
])
```

### 검색

```python
# 질문 임베딩
query = "로컬 벡터 DB는?"
query_vector = embeddings.embed_query(query)

# 검색
results = index.query(
    vector=query_vector,
    top_k=3,
    include_metadata=True
)

for match in results['matches']:
    print(f"Score: {match['score']}")
    print(f"Text: {match['metadata']['text']}\n")
```

## LangChain 통합

```python
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 임베딩
embeddings = OpenAIEmbeddings()

# 문서 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

documents = text_splitter.create_documents([
    "긴 문서 내용...",
    "또 다른 문서..."
])

# Pinecone Vector Store
vectorstore = PineconeVectorStore.from_documents(
    documents,
    embeddings,
    index_name="knowledge-base"
)

# 검색
results = vectorstore.similarity_search("질문", k=3)

for doc in results:
    print(doc.page_content)
```

## 성능 최적화

### 1. 배치 업로드

```python
# 느림 (하나씩)
for doc in documents:
    vector = embeddings.embed_query(doc)
    index.upsert([(id, vector, {"text": doc})])

# 빠름 (배치)
BATCH_SIZE = 100

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i+BATCH_SIZE]
    vectors = embeddings.embed_documents(batch)

    index.upsert(vectors=[
        (f"doc{i+j}", vec, {"text": doc})
        for j, (vec, doc) in enumerate(zip(vectors, batch))
    ])
```

### 2. 메타데이터 필터링

```python
# 메타데이터 추가
index.upsert(vectors=[
    ("doc1", vector1, {
        "text": "내용...",
        "source": "manual",
        "date": "2024-01-01",
        "category": "technical"
    })
])

# 필터링 검색
results = index.query(
    vector=query_vector,
    top_k=10,
    filter={
        "source": {"$eq": "manual"},
        "category": {"$in": ["technical", "guide"]}
    }
)
```

### 3. 네임스페이스 분리

```python
# 다른 데이터셋을 네임스페이스로 분리
index.upsert(
    vectors=[...],
    namespace="company-docs"
)

index.upsert(
    vectors=[...],
    namespace="technical-manual"
)

# 특정 네임스페이스만 검색
results = index.query(
    vector=query_vector,
    top_k=5,
    namespace="company-docs"
)
```

## 대규모 데이터 인덱싱

### 전략

```python
import time

def batch_upsert(documents, batch_size=100):
    """대용량 데이터 안전하게 업로드"""

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        try:
            # 임베딩 생성
            vectors = embeddings.embed_documents(batch)

            # Pinecone 업로드
            index.upsert(vectors=[
                (f"doc{i+j}", vec, {"text": doc})
                for j, (vec, doc) in enumerate(zip(vectors, batch))
            ])

            print(f"✅ {i+batch_size}/{len(documents)} 완료")

            # Rate limit 방지
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ 배치 {i} 실패: {e}")
            # 재시도 로직...
```

## 비용 최적화

### Pinecone 요금제

```
Starter (무료):
- 1개 인덱스
- 100만 벡터
- 단일 리전

Standard ($70/월):
- 최대 5 인덱스
- 무제한 벡터
- 다중 리전

Enterprise (맞춤):
- 전용 인프라
- SLA 보장
```

### 비용 절감 팁

```python
# 1. 불필요한 메타데이터 제거
# 비용 발생: 벡터 + 메타데이터
metadata = {
    "text": doc[:500],  # 전체 텍스트 대신 요약만
    "source": source     # 필수 정보만
}

# 2. 주기적인 정리
index.delete(filter={"date": {"$lt": "2023-01-01"}})

# 3. 임베딩 캐싱
cache = {}

def get_embedding(text):
    if text in cache:
        return cache[text]

    emb = embeddings.embed_query(text)
    cache[text] = emb
    return emb
```

## 모니터링

```python
# 인덱스 통계
stats = index.describe_index_stats()

print(f"총 벡터 수: {stats['total_vector_count']}")
print(f"네임스페이스: {stats['namespaces']}")

# 쿼리 성능
import time

start = time.time()
results = index.query(vector=query_vector, top_k=10)
latency = time.time() - start

print(f"검색 지연시간: {latency*1000:.2f}ms")
```

## ChromaDB → Pinecone 마이그레이션

```python
import chromadb
import pinecone

# 1. ChromaDB에서 데이터 로드
chroma_client = chromadb.PersistentClient(path="./rag_db")
chroma_collection = chroma_client.get_collection("knowledge")

all_data = chroma_collection.get()

# 2. Pinecone으로 전송
pinecone_index = pinecone.Index("knowledge-base")

for i, (doc_id, doc, embedding) in enumerate(
    zip(all_data['ids'], all_data['documents'], all_data['embeddings'])
):
    pinecone_index.upsert([(
        doc_id,
        embedding,
        {"text": doc}
    )])

    if i % 100 == 0:
        print(f"✅ {i}개 마이그레이션 완료")
```

## 프로덕션 체크리스트

- [ ] API 키 환경 변수 설정
- [ ] 인덱스 이름 및 차원 설정
- [ ] 배치 업로드 구현
- [ ] 에러 핸들링 및 재시도
- [ ] Rate limiting 고려
- [ ] 모니터링 설정
- [ ] 비용 알림 설정
- [ ] 백업 전략

## 다음 단계

**Step 5: RAG 통합**
- LangChain Vector Store 완전 활용
- Retrieval Chain 구성
- 컨텍스트 관리 고급 기법

---

**핵심 요약:**
1. ChromaDB: 개발/프로토타입 ✅
2. Pinecone: 프로덕션/대규모 ✅
3. 배치 처리로 성능 최적화
4. 메타데이터 필터링으로 정확도 향상
5. 비용 모니터링 필수
