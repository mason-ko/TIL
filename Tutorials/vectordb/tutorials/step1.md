# Step 1: ChromaDB 기본 - 벡터 데이터베이스 시작하기

## 목표

- ChromaDB 로컬 설치 및 설정
- 문서 임베딩 및 저장
- 유사도 검색 실습
- RAG의 기초 이해

## Vector Database란?

**텍스트를 숫자 벡터로 변환하여 저장**하고, **의미가 유사한 문서를 찾는** 데이터베이스입니다.

### 일반 DB vs Vector DB

```python
# 일반 DB (키워드 매칭)
SELECT * FROM docs WHERE text LIKE '%강아지%'
→ "강아지"라는 단어가 있는 문서만 찾음
→ "반려견", "개"는 못 찾음 ❌

# Vector DB (의미 검색)
query_vector = embed("강아지 사료")
similar_docs = vectordb.search(query_vector)
→ "반려견 먹이" ✅
→ "개 간식" ✅
→ "강아지 영양" ✅
```

## ChromaDB란?

**로컬에서 실행 가능한 가벼운 벡터 데이터베이스**

### 장점
- ✅ 설치 간단 (pip install)
- ✅ 로컬 실행 (외부 서버 불필요)
- ✅ 무료
- ✅ Python 친화적
- ✅ 자동 임베딩

### 단점
- ❌ 대규모 데이터에는 느림
- ❌ 분산 처리 미지원

## 설치

```bash
pip install chromadb
```

## 핵심 개념

### 1. Embedding (임베딩)

텍스트 → 숫자 벡터로 변환

```python
"강아지 사료" → [0.1, 0.3, -0.2, 0.8, ...]  # 384차원 벡터

유사한 의미 = 가까운 벡터
다른 의미 = 먼 벡터
```

### 2. Collection (컬렉션)

문서들을 담는 그룹 (DB의 테이블과 유사)

```python
collection = client.create_collection("my_documents")
```

### 3. Query (검색)

쿼리 텍스트와 유사한 문서 찾기

```python
results = collection.query(
    query_texts=["강아지 사료"],
    n_results=5  # 상위 5개
)
```

## 코드 예제

### 예제 1: 기본 사용법

```python
import chromadb

# 1. 클라이언트 생성
client = chromadb.Client()

# 2. 컬렉션 생성
collection = client.create_collection(name="my_docs")

# 3. 문서 추가
collection.add(
    documents=[
        "강아지 사료 추천해주세요",
        "고양이 간식 어떤게 좋나요",
        "반려견 영양제 필요할까요"
    ],
    ids=["doc1", "doc2", "doc3"]
)

# 4. 검색
results = collection.query(
    query_texts=["개 먹이"],
    n_results=2
)

print(results)
# → ["강아지 사료 추천해주세요", "반려견 영양제 필요할까요"]
```

### 예제 2: 메타데이터 활용

```python
collection.add(
    documents=[
        "Python은 프로그래밍 언어입니다",
        "JavaScript는 웹 개발에 사용됩니다",
        "Rust는 시스템 프로그래밍 언어입니다"
    ],
    metadatas=[
        {"category": "language", "level": "beginner"},
        {"category": "language", "level": "beginner"},
        {"category": "language", "level": "advanced"}
    ],
    ids=["py", "js", "rust"]
)

# 메타데이터 필터링
results = collection.query(
    query_texts=["프로그래밍 언어"],
    n_results=2,
    where={"level": "beginner"}  # 초급만
)
```

### 예제 3: 영구 저장

```python
# 디스크에 저장
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("persistent")

collection.add(
    documents=["문서 내용"],
    ids=["id1"]
)

# 프로그램 종료 후 재실행해도 데이터 유지됨
```

### 예제 4: 실전 RAG 기초

```python
from langchain_community.llms import Ollama

# 1. 문서 저장
collection.add(
    documents=[
        "LangGraph는 상태 기반 워크플로우를 만드는 라이브러리입니다",
        "Langfuse는 LLM 모니터링 플랫폼입니다",
        "ChromaDB는 벡터 데이터베이스입니다"
    ],
    ids=["doc1", "doc2", "doc3"]
)

# 2. 질문에 관련 문서 검색
question = "LLM을 모니터링하는 도구는?"
results = collection.query(
    query_texts=[question],
    n_results=1
)

context = results['documents'][0][0]

# 3. LLM에 컨텍스트와 함께 질문
llm = Ollama(model="llama3")
prompt = f"""
다음 정보를 바탕으로 질문에 답하세요:

정보: {context}

질문: {question}
"""

answer = llm.invoke(prompt)
print(answer)
```

## 거리 메트릭

벡터 간 유사도를 측정하는 방법

```python
collection = client.create_collection(
    name="test",
    metadata={"hnsw:space": "cosine"}  # 또는 "l2", "ip"
)
```

| 메트릭 | 설명 | 사용 |
|--------|------|------|
| **cosine** | 코사인 유사도 | 대부분 (권장) |
| **l2** | 유클리디안 거리 | 절대 거리 중요 |
| **ip** | 내적 | 특수 케이스 |

## 실습 과제

### 1. 기본 검색

```python
# TODO: 5개 문서 추가 후 검색
# 주제: 프로그래밍 언어
# 검색: "웹 개발 언어"
```

### 2. 메타데이터 필터링

```python
# TODO: 난이도 메타데이터 추가
# 검색: "초급자용 언어"만 필터링
```

### 3. 간단한 RAG

```python
# TODO: 회사 정보 3개 저장
# 질문: "회사 위치는?"
# Ollama로 답변 생성
```

## 다음 단계

**Step 2: 임베딩 모델**에서는:
- 다양한 임베딩 모델 비교
- 한국어 임베딩 최적화
- 커스텀 임베딩 사용

## 핵심 요약

1. **Vector DB = 의미 기반 검색**
2. **ChromaDB = 로컬, 무료, 간단**
3. **자동 임베딩 지원**
4. **메타데이터 필터링 가능**
5. **RAG의 핵심 컴포넌트**

---

**다음**: `step2.md` - 임베딩 모델 선택 및 최적화
