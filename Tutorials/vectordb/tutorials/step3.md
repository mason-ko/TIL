# Step 3: RAG 실전 구현

## 목표

- 실제 RAG 시스템 구축
- 문서 분할 전략 이해
- 검색 품질 최적화

## RAG (Retrieval-Augmented Generation)란?

**검색(Retrieval) + 생성(Generation)**

```
1. 사용자 질문
   ↓
2. 관련 문서 검색 (Vector DB)
   ↓
3. LLM에 컨텍스트와 함께 질문
   ↓
4. 정확한 답변 생성
```

### RAG가 필요한 이유

```python
# RAG 없이
Q: "우리 회사 휴가 정책은?"
A: "죄송합니다. 저는 그 정보를 모릅니다." ❌

# RAG 사용
Q: "우리 회사 휴가 정책은?"
→ [회사 문서 검색]
→ [관련 문서 발견: "연차 15일..."]
A: "연차는 15일이며, 병가는 별도입니다." ✅
```

## RAG 구현 단계

### 1. 문서 수집

```python
documents = [
    "LangGraph는 상태 기반 워크플로우 라이브러리입니다...",
    "Langfuse는 오픈소스 LLM 모니터링 도구입니다...",
    "ChromaDB는 벡터 데이터베이스입니다..."
]
```

### 2. 문서 분할 (Chunking)

**왜 분할?**
- 긴 문서는 검색 정확도 낮음
- 작은 청크가 더 정확한 매칭

**분할 전략:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,      # 청크 크기
    chunk_overlap=20     # 겹침 (컨텍스트 유지)
)

chunks = splitter.split_text(long_document)
```

**좋은 청크 크기:**
- 너무 크면: 관련 없는 내용 포함
- 너무 작으면: 컨텍스트 부족
- 권장: 200-500자 (한국어)

### 3. 벡터 DB에 저장

```python
client = chromadb.PersistentClient(path="./rag_db")
collection = client.get_or_create_collection("knowledge")

collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)
```

### 4. 검색 (Retrieval)

```python
question = "로컬 LLM을 모니터링하는 도구는?"

results = collection.query(
    query_texts=[question],
    n_results=2  # 상위 2개
)

context = "\n".join(results['documents'][0])
```

### 5. LLM에 질문 (Generation)

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

prompt = f"""다음 정보를 바탕으로 질문에 답하세요.

정보:
{context}

질문: {question}

답변:"""

answer = llm.invoke(prompt)
```

## 실전 예제

### 예제 1: 회사 문서 RAG

```python
# 1. 회사 문서
company_docs = [
    "휴가 정책: 연차 15일, 병가 10일",
    "근무 시간: 9시-6시, 유연 근무제",
    "복지: 중식 제공, 간식 무료"
]

# 2. 저장
collection.add(
    documents=company_docs,
    ids=[f"doc{i}" for i in range(len(company_docs))]
)

# 3. RAG 질의
question = "연차는 몇 일?"
results = collection.query(query_texts=[question], n_results=1)
context = results['documents'][0][0]

prompt = f"""
정보: {context}
질문: {question}
답변:"""

answer = llm.invoke(prompt)
# → "연차는 15일입니다."
```

### 예제 2: 긴 문서 처리

```python
long_doc = """
LangGraph는 LangChain 팀이 만든 라이브러리입니다.
상태 기반 워크플로우를 쉽게 구현할 수 있습니다.
노드와 엣지로 복잡한 AI 에이전트를 만듭니다.
체크포인트 기능으로 대화를 저장할 수 있습니다.
"""

# 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10
)
chunks = splitter.split_text(long_doc)

# 각 청크 저장
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}")
```

## 검색 품질 향상 팁

### 1. 적절한 n_results

```python
# 너무 적으면: 관련 정보 놓침
results = collection.query(query_texts=[q], n_results=1)  # 부족할 수 있음

# 적당히: 관련 정보 충분히 수집
results = collection.query(query_texts=[q], n_results=3)  # 권장

# 너무 많으면: 관련 없는 정보 포함
results = collection.query(query_texts=[q], n_results=10)  # 과다
```

### 2. 메타데이터 활용

```python
collection.add(
    documents=["문서 내용..."],
    metadatas=[{"source": "manual", "page": 1}],
    ids=["doc1"]
)

# 특정 소스만 검색
results = collection.query(
    query_texts=["질문"],
    where={"source": "manual"}
)
```

### 3. 컨텍스트 압축

```python
# LLM 토큰 제한 고려
MAX_CONTEXT_LENGTH = 2000

context = "\n".join(results['documents'][0])
if len(context) > MAX_CONTEXT_LENGTH:
    context = context[:MAX_CONTEXT_LENGTH] + "..."
```

## 영구 저장

```python
# 디스크에 저장
client = chromadb.PersistentClient(path="./my_rag_db")

# 프로그램 재시작 후에도 데이터 유지
collection = client.get_or_create_collection("knowledge")

# 데이터 추가
collection.add(documents=docs, ids=ids)

# 나중에 다시 로드
# → ./my_rag_db 폴더에서 자동 로드
```

## 실무 체크리스트

- [ ] 문서 분할 크기 결정 (200-500자)
- [ ] 중복 제거
- [ ] 메타데이터 추가 (출처, 날짜 등)
- [ ] n_results 최적화 (보통 2-5개)
- [ ] 영구 저장 설정
- [ ] 검색 결과 품질 테스트

## 다음 단계

**Step 4: 검색 품질 향상**
- Hybrid Search (키워드 + 벡터)
- Reranking
- 컨텍스트 압축

---

**핵심 요약:**
1. 문서 분할 (200-500자)
2. 벡터 DB 저장
3. 검색 (n_results=2-5)
4. LLM에 컨텍스트 제공
5. 정확한 답변 생성 ✅
