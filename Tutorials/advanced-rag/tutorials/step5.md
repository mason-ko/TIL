# Step 5: Parent Document Retrieval

## 목표

- 작은 청크로 검색, 큰 컨텍스트 반환
- 검색 정확도와 컨텍스트 풍부함 동시 확보

## 개념

```python
# 문제
큰 청크 검색: 정확도 낮음 (관련 없는 내용 포함)
작은 청크 검색: 컨텍스트 부족 (주변 정보 없음)

# 해결: Parent Document
작은 청크로 검색 → 부모 문서 반환
```

## 구조

```python
Parent Document (부모):
"""
제1조: 근무 시간은 9시-6시입니다.
제2조: 휴가는 연차 15일입니다.
제3조: 병가는 10일입니다.
"""

Child Chunks (자식):
- Chunk 1: "제1조: 근무 시간은 9시-6시입니다."
- Chunk 2: "제2조: 휴가는 연차 15일입니다."
- Chunk 3: "제3조: 병가는 10일입니다."

검색: "연차" → Chunk 2 매칭 → Parent 전체 반환
```

## 구현

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 부모 저장소
store = InMemoryStore()

# 자식 Splitter (작게)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

# 부모 Splitter (크게)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)

# Retriever
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# 문서 추가
retriever.add_documents(documents)

# 검색 (작은 청크로 검색 → 부모 문서 반환)
docs = retriever.get_relevant_documents("연차")
```

## 장점

1. **정확한 검색**: 작은 청크로 정밀 검색
2. **풍부한 컨텍스트**: 부모 문서로 주변 정보 제공
3. **Best of Both Worlds**

## 실전 예제

```python
# 긴 기술 문서
tech_doc = """
# LangGraph 소개

LangGraph는 상태 기반 워크플로우 라이브러리입니다.

## 주요 기능
- StateGraph: 상태 관리
- 노드와 엣지: 워크플로우 구성
- 체크포인트: 영속성

## 사용 사례
복잡한 AI 에이전트 구축에 적합합니다.
"""

# Child chunks로 분할
chunks = [
    "LangGraph는 상태 기반 워크플로우 라이브러리입니다.",
    "StateGraph: 상태 관리",
    "복잡한 AI 에이전트 구축에 적합합니다."
]

# 검색: "에이전트 구축"
# → Chunk 3 매칭
# → Parent 전체 반환 (LangGraph 소개 전체)
```

---

**핵심**: 작은 청크 검색 + 부모 문서 반환 = 정확도 + 컨텍스트
