# Step 1: 기본 RAG (Retrieval-Augmented Generation) 개념

## 개요
GraphRAG를 이해하기 전에 먼저 기본 RAG를 배워야 합니다.
RAG는 외부 지식을 검색하여 LLM의 답변을 향상시키는 핵심 기법입니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install google-generativeai langchain langchain-google-genai langchain-community faiss-cpu
```

### 실행
```bash
python tutorials/step1.py
```

## RAG가 필요한 이유

### LLM의 한계

1. **지식의 시간 제한**
   - LLM은 학습 시점까지의 데이터만 알고 있음
   - 최신 정보를 모름

2. **도메인 특화 지식 부족**
   - 회사 내부 정보, 개인 문서 등을 모름
   - 특정 도메인의 전문 지식이 제한적

3. **환각(Hallucination)**
   - 모르는 내용을 그럴듯하게 지어낼 수 있음
   - 사실이 아닌 정보를 제공할 위험

### RAG의 해결책

```
사용자 질문
    ↓
지식 베이스에서 관련 문서 검색
    ↓
검색된 문서 + 질문 → LLM
    ↓
근거 있는 답변 생성
```

## RAG의 작동 원리

### 1. 인덱싱 단계 (사전 작업)

```
문서들 → 청킹 → 임베딩 → 벡터 DB 저장
```

**청킹(Chunking):**
- 긴 문서를 작은 조각으로 분할
- 예: 500-1000자 단위

**임베딩(Embedding):**
- 텍스트를 숫자 벡터로 변환
- 의미적으로 유사한 텍스트는 유사한 벡터

**벡터 DB:**
- FAISS, Pinecone, Weaviate 등
- 빠른 유사도 검색 지원

### 2. 검색 단계 (실시간)

```
사용자 질문 → 임베딩 → 벡터 DB에서 유사 문서 검색
```

**유사도 계산:**
- 코사인 유사도, 유클리드 거리 등
- 벡터 간 거리로 유사성 측정

### 3. 생성 단계

```
검색된 문서 + 질문 → LLM → 답변
```

**프롬프트 구조:**
```
System: 다음 문서를 참고하여 답변하세요.
문서: [검색된 내용]

User: [질문]
```

## 코드 설명

### 1. RAG 없이 LLM만 사용 (`without_rag_example`)

```python
question = "우리 회사의 2024년 신제품 출시 일정은?"
response = llm.invoke(question)
```

**문제점:**
- LLM은 회사 내부 정보를 모름
- "죄송하지만 정보가 없습니다" 또는 잘못된 추측

### 2. 간단한 RAG 구현 (`simple_rag_example`)

**단계별 구현:**

**Step 1: 문서 준비**
```python
documents = [
    Document(
        page_content="2024년 신제품 Alpha는 3월 15일에 출시...",
        metadata={"source": "product_roadmap.pdf"}
    ),
    # ...
]
```

`Document` 객체:
- `page_content`: 실제 텍스트 내용
- `metadata`: 출처, 카테고리 등 메타 정보

**Step 2: 임베딩 모델 초기화**
```python
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
```

Google의 `embedding-001` 모델 사용:
- 768 차원 벡터
- 의미적 유사성을 잘 포착
- 다국어 지원

**Step 3: 벡터 저장소 생성**
```python
vectorstore = FAISS.from_documents(documents, embeddings)
```

FAISS (Facebook AI Similarity Search):
- Meta에서 개발한 고속 벡터 검색 라이브러리
- 메모리 내에서 동작 (빠름)
- 프로덕션에서는 Pinecone, Weaviate 등 사용

**Step 4: 관련 문서 검색**
```python
retrieved_docs = vectorstore.similarity_search(question, k=2)
```

- `k=2`: 상위 2개 문서 반환
- 코사인 유사도 기반 검색

**Step 5: LLM에게 전달**
```python
context = "\n\n".join([doc.page_content for doc in retrieved_docs])

prompt = f"""
다음 문서를 참고하여 답변하세요:
{context}

질문: {question}
"""

response = llm.invoke(prompt)
```

### 3. 임베딩과 유사도 (`embedding_similarity_example`)

**임베딩이란?**
```
"고양이는 귀여운 동물입니다"
    ↓ 임베딩
[0.234, -0.456, 0.789, ..., 0.123]  # 1536개 숫자
```

**유사도 측정:**
```python
results = vectorstore.similarity_search_with_score(query, k=4)

# 출력 예:
# 1. (유사도: 0.3421) 고양이는 귀여운 동물입니다.
# 2. (유사도: 0.3856) 강아지는 충성스러운 반려동물입니다.
# 3. (유사도: 0.8234) Python은 프로그래밍 언어입니다.
# 4. (유사도: 0.8456) 자바스크립트는 웹 개발에 사용됩니다.
```

**점수 해석:**
- FAISS는 거리를 반환 (낮을수록 유사)
- 0에 가까울수록 매우 유사
- 의미적으로 관련 없으면 점수 높음

### 4. 다양한 검색 방법 (`retrieval_methods_example`)

**Similarity Search (기본):**
```python
results = vectorstore.similarity_search(query, k=2)
```
- 가장 유사한 상위 k개 반환
- 간단하고 빠름

**MMR (Maximum Marginal Relevance):**
```python
results = vectorstore.max_marginal_relevance_search(query, k=2)
```
- 유사성과 다양성의 균형
- 비슷한 내용의 중복 문서 방지
- 더 다양한 관점 제공

**Score Threshold:**
```python
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.5}
)
```
- 특정 유사도 이상의 문서만 반환
- 관련 없는 문서 필터링

### 5. 완전한 RAG 체인 (`rag_chain_example`)

**RetrievalQA 사용:**
```python
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

result = qa_chain.invoke({"query": question})
```

**chain_type 옵션:**

1. **"stuff"** (기본)
   - 모든 문서를 한 번에 프롬프트에 넣음
   - 빠르지만 토큰 제한 있음

2. **"map_reduce"**
   - 각 문서에 대해 별도로 처리 후 결합
   - 문서가 많을 때 유용

3. **"refine"**
   - 순차적으로 답변을 개선
   - 더 정교한 답변

4. **"map_rerank"**
   - 각 문서로부터 답변 생성 후 점수화
   - 가장 좋은 답변 선택

## 벡터 저장소 비교

| 저장소 | 특징 | 사용 사례 |
|--------|------|-----------|
| **FAISS** | 메모리 내, 빠름, 무료 | 프로토타입, 소규모 |
| **Pinecone** | 관리형, 확장성, 유료 | 프로덕션, 대규모 |
| **Weaviate** | 오픈소스, 하이브리드 검색 | 복잡한 쿼리 |
| **Chroma** | 간단, 로컬 우선 | 개발, 테스트 |
| **Qdrant** | 고성능, 필터링 | 대규모, 필터 필요 |

## RAG의 장단점

### 장점
✅ 최신 정보 제공 (DB 업데이트만 하면 됨)
✅ 도메인 특화 지식 활용
✅ 환각 감소 (근거 있는 답변)
✅ 출처 추적 가능 (투명성)
✅ LLM 재학습 불필요

### 단점
❌ 검색 품질에 의존 (잘못 검색하면 잘못된 답변)
❌ 추가 인프라 필요 (벡터 DB)
❌ 지연 시간 증가 (검색 시간)
❌ 토큰 사용량 증가 (문서 포함)
❌ 청킹 품질이 중요

## RAG 성능 향상 팁

### 1. 좋은 청킹
```python
# 너무 작으면: 문맥 손실
# 너무 크면: 관련 없는 내용 포함
chunk_size = 500  # 적절한 크기
chunk_overlap = 50  # 문맥 유지
```

### 2. 메타데이터 활용
```python
Document(
    page_content="...",
    metadata={
        "source": "doc.pdf",
        "page": 5,
        "category": "product",
        "date": "2024-01-15"
    }
)

# 필터링 검색
results = vectorstore.similarity_search(
    query,
    filter={"category": "product"}
)
```

### 3. 하이브리드 검색
- 벡터 검색 + 키워드 검색 (BM25)
- 서로 보완적

### 4. 재순위화 (Reranking)
```
1차 검색: 상위 20개
    ↓
재순위 모델로 정밀 평가
    ↓
최종 상위 5개 선택
```

## 핵심 개념 정리

### 1. RAG = Retrieval + Generation
- 검색으로 관련 문서 찾기
- 문서를 바탕으로 답변 생성

### 2. 임베딩
- 텍스트 → 숫자 벡터
- 의미적 유사성 표현

### 3. 벡터 검색
- 벡터 간 거리/유사도 계산
- 가장 가까운 문서 찾기

### 4. 프롬프트 엔지니어링
- 검색 문서를 효과적으로 활용
- 출처 명시 요청

## 다음 단계

기본 RAG를 이해했습니다!

다음 단계(Step 2)에서는 **문서 처리와 청킹**을 심화 학습합니다.

**Step 2에서 배울 내용:**
- 다양한 문서 로더 (PDF, HTML, CSV 등)
- 효과적인 청킹 전략
- 메타데이터 추출
- 문서 전처리
