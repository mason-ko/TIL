# Step 5: RAG 통합

## 목표

- LangChain Vector Store 완전 활용
- Retrieval Chain 구성
- 컨텍스트 관리 고급 기법
- 프로덕션급 RAG 시스템 구축

## LangChain Vector Store

LangChain은 다양한 Vector DB를 통합된 인터페이스로 제공합니다.

### 지원되는 Vector Store

```python
from langchain_community.vectorstores import (
    Chroma,      # 로컬
    Pinecone,    # 클라우드
    Qdrant,      # 오픈소스
    Weaviate,    # GraphQL
    FAISS,       # Facebook AI
)
```

### 통합 인터페이스

```python
# 모든 Vector Store가 동일한 메서드 제공
vectorstore.add_documents(documents)
vectorstore.similarity_search(query, k=5)
vectorstore.as_retriever()
```

## Retriever 패턴

### 기본 Retriever

```python
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Vector Store 생성
vectorstore = Chroma(
    persist_directory="./db",
    embedding_function=OpenAIEmbeddings()
)

# Retriever로 변환
retriever = vectorstore.as_retriever(
    search_type="similarity",  # 유사도 검색
    search_kwargs={"k": 3}      # 상위 3개
)

# 검색
docs = retriever.invoke("질문")
```

### 다양한 검색 타입

```python
# 1. Similarity (유사도)
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# 2. MMR (Maximal Marginal Relevance)
# 다양성을 고려한 검색
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,      # 후보 20개에서
        "lambda_mult": 0.5   # 유사도 vs 다양성 균형
    }
)

# 3. Similarity Score Threshold
# 임계값 이상만 반환
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.8,  # 80% 이상 유사
        "k": 5
    }
)
```

## Retrieval Chain

### 기본 RAG Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Retriever
retriever = vectorstore.as_retriever(k=3)

# 2. Prompt
template = """다음 컨텍스트를 바탕으로 질문에 답하세요.
컨텍스트에 없는 내용은 추측하지 마세요.

컨텍스트:
{context}

질문: {question}

답변:"""

prompt = ChatPromptTemplate.from_template(template)

# 3. LLM
llm = Ollama(model="llama3")

# 4. Chain 구성
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. 실행
answer = rag_chain.invoke("질문")
```

### Context Formatting

```python
from langchain_core.runnables import RunnableLambda

def format_docs(docs):
    """문서를 문자열로 포맷팅"""
    return "\n\n".join([
        f"출처: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
        for doc in docs
    ])

rag_chain = (
    {"context": retriever | RunnableLambda(format_docs),
     "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

## 고급 RAG 패턴

### 1. ConversationalRetrievalChain

대화 이력을 고려한 검색:

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 메모리 설정
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# Chain 생성
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)

# 대화
result1 = qa_chain({"question": "Python이 뭐야?"})
# → 메모리에 저장

result2 = qa_chain({"question": "언제 만들어졌어?"})
# → "Python"을 기억하고 검색
```

### 2. RetrievalQA with Sources

출처 포함한 답변:

```python
from langchain.chains import RetrievalQAWithSourcesChain

qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

result = qa_chain({"question": "질문"})

print(f"답변: {result['answer']}")
print(f"출처: {result['sources']}")
```

### 3. Multi-Query Retriever

질문을 여러 버전으로 변환하여 검색:

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

multi_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# "Python 성능"을 다음처럼 변환:
# - "Python은 빠른가?"
# - "Python 속도는 어떤가?"
# - "Python 성능 특징"

docs = multi_retriever.get_relevant_documents("Python 성능")
```

### 4. Contextual Compression

관련 부분만 추출:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Compressor
compressor = LLMChainExtractor.from_llm(llm)

# Compression Retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# 검색 → 압축 → 관련 부분만 반환
docs = compression_retriever.get_relevant_documents("질문")
```

## 컨텍스트 관리

### 1. 토큰 제한 고려

```python
from langchain.text_splitter import TokenTextSplitter

def limit_context_tokens(docs, max_tokens=2000):
    """토큰 제한"""
    splitter = TokenTextSplitter(chunk_size=max_tokens)

    # 문서 결합
    combined = "\n\n".join([doc.page_content for doc in docs])

    # 토큰 제한
    if splitter.count_tokens(combined) > max_tokens:
        chunks = splitter.split_text(combined)
        return chunks[0]  # 첫 번째 청크만

    return combined
```

### 2. 중복 제거

```python
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter
)

# 유사한 문서 제거
embeddings_filter = EmbeddingsFilter(
    embeddings=OpenAIEmbeddings(),
    similarity_threshold=0.85  # 85% 이상 유사하면 중복
)

pipeline = DocumentCompressorPipeline(
    transformers=[embeddings_filter]
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline,
    base_retriever=retriever
)
```

### 3. 메타데이터 활용

```python
# 메타데이터로 필터링
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "official-docs"}  # 공식 문서만
    }
)

# 메타데이터 기반 재정렬
def rerank_by_date(docs):
    """최신 문서 우선"""
    return sorted(
        docs,
        key=lambda d: d.metadata.get("date", "2000-01-01"),
        reverse=True
    )
```

## 실전 예제: 완전한 RAG 시스템

```python
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory

class ProductionRAG:
    def __init__(self, persist_directory="./rag_db"):
        # Vector Store
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=OpenAIEmbeddings()
        )

        # Retriever (MMR로 다양성 확보)
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 10}
        )

        # LLM
        self.llm = Ollama(model="llama3", temperature=0)

        # Prompt
        self.prompt = ChatPromptTemplate.from_template("""
다음 컨텍스트를 참고하여 질문에 답하세요.
모르면 모른다고 답하세요.

컨텍스트:
{context}

질문: {question}

답변:""")

        # Memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            output_key="answer"
        )

    def format_docs(self, docs):
        """문서 포맷팅"""
        return "\n\n".join([
            f"[출처: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in docs
        ])

    def add_documents(self, documents):
        """문서 추가"""
        self.vectorstore.add_documents(documents)

    def query(self, question):
        """질의응답"""
        # Retrieve
        docs = self.retriever.get_relevant_documents(question)

        # Format
        context = self.format_docs(docs)

        # Generate
        chain = self.prompt | self.llm
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # Save to memory
        self.memory.save_context(
            {"input": question},
            {"answer": answer}
        )

        return {
            "answer": answer,
            "sources": [doc.metadata for doc in docs],
            "context": context
        }

# 사용
rag = ProductionRAG()
result = rag.query("질문")
print(result["answer"])
```

## 평가 및 모니터링

### 검색 품질 평가

```python
from langchain.evaluation import RetrievalQA

# 테스트 세트
test_cases = [
    {"question": "...", "expected": "..."},
    # ...
]

# 평가
for case in test_cases:
    docs = retriever.get_relevant_documents(case["question"])

    # 정확도
    relevant = any(case["expected"] in doc.page_content for doc in docs)

    # 지연시간
    import time
    start = time.time()
    retriever.get_relevant_documents(case["question"])
    latency = time.time() - start

    print(f"Relevant: {relevant}, Latency: {latency:.3f}s")
```

## 프로덕션 체크리스트

- [ ] Retriever 타입 선택 (similarity/mmr/threshold)
- [ ] k 값 최적화 (보통 3-5)
- [ ] 토큰 제한 설정
- [ ] 메타데이터 필터링
- [ ] 중복 제거
- [ ] 대화 이력 관리 (필요시)
- [ ] 출처 정보 포함
- [ ] 에러 핸들링
- [ ] 성능 모니터링
- [ ] 비용 추적

## 다음 단계

이제 Vector DB와 RAG의 기초를 마쳤습니다!

**추가 학습:**
1. **Advanced RAG**: Hybrid Search, Reranking
2. **Multi-Modal**: 이미지 + 텍스트 검색
3. **LangSmith/Langfuse**: RAG 모니터링
4. **GraphRAG**: 지식 그래프 기반 검색

---

**핵심 요약:**
1. LangChain Vector Store: 통합 인터페이스 ✅
2. Retriever 패턴: 검색 로직 캡슐화 ✅
3. Retrieval Chain: 검색 + LLM 통합 ✅
4. 컨텍스트 관리: 토큰 제한, 중복 제거 ✅
5. 프로덕션: 평가, 모니터링 ✅
