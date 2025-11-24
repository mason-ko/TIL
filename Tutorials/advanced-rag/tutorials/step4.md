# Step 4: Contextual Compression (컨텍스트 압축)

## 목표

- 검색 결과에서 관련 부분만 추출
- 토큰 사용량 감소
- LLM 성능 향상

## 문제

```python
# 긴 문서 검색
doc = """
LangChain은 LLM 애플리케이션 프레임워크입니다.
[500줄의 다른 내용...]
LangGraph는 워크플로우 라이브러리입니다.
[500줄의 다른 내용...]
"""

# 질문: "LangGraph는 뭐야?"
# → 1000줄 전체를 LLM에 전달 (비효율)
```

## 해결: Contextual Compression

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.llms import Ollama

# Compressor
llm = Ollama(model="llama3")
compressor = LLMChainExtractor.from_llm(llm)

# Compression Retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)

# 검색 → 압축 → 관련 부분만 반환
docs = compression_retriever.get_relevant_documents("LangGraph")
# → "LangGraph는 워크플로우 라이브러리입니다." (핵심만 추출)
```

## 압축 방식

### 1. LLM Extraction

```python
# LLM이 관련 부분 추출
compressor = LLMChainExtractor.from_llm(llm)
```

### 2. Embeddings Filter

```python
from langchain.retrievers.document_compressors import EmbeddingsFilter

# 유사도 임계값 기반
embeddings_filter = EmbeddingsFilter(
    embeddings=OpenAIEmbeddings(),
    similarity_threshold=0.76
)
```

### 3. Pipeline

```python
# 여러 압축 단계 조합
from langchain.retrievers.document_compressors import DocumentCompressorPipeline

pipeline = DocumentCompressorPipeline(
    transformers=[
        EmbeddingsFilter(similarity_threshold=0.8),
        LLMChainExtractor.from_llm(llm)
    ]
)
```

## 실전 예제

```python
# 긴 문서
long_doc = """
[100줄의 회사 정책...]
휴가 정책: 연차 15일, 병가 10일
[100줄의 다른 정책...]
"""

# 압축 없이
raw_context = retrieve_documents("연차")  # 200줄 전체

# 압축 사용
compressed_context = compress_documents("연차")
# → "휴가 정책: 연차 15일, 병가 10일" (관련 부분만)

# 토큰 절감: 200줄 → 1줄 (99% 감소)
```

---

**핵심**: 긴 문서에서 관련 부분만 추출하여 효율성 향상
