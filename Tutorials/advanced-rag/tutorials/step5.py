"""
Advanced RAG Step 5: Parent Document Retrieval

pip install chromadb
"""

import chromadb
from typing import Dict, List


class ParentDocumentStore:
    """Parent-Child 문서 저장소"""

    def __init__(self):
        self.parents = {}  # parent_id -> full document
        self.child_to_parent = {}  # child_id -> parent_id

    def add_document(self, parent_id: str, parent_doc: str, child_chunks: List[str]):
        """부모 문서와 자식 청크 저장"""
        self.parents[parent_id] = parent_doc

        for i, chunk in enumerate(child_chunks):
            child_id = f"{parent_id}_chunk{i}"
            self.child_to_parent[child_id] = parent_id

    def get_parent(self, child_id: str) -> str:
        """자식 ID로 부모 문서 가져오기"""
        parent_id = self.child_to_parent.get(child_id)
        return self.parents.get(parent_id, "")


def split_into_chunks(text: str, chunk_size: int = 100) -> List[str]:
    """문서를 작은 청크로 분할"""
    sentences = text.split('. ')
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += sentence + ". "
        else:
            if current:
                chunks.append(current.strip())
            current = sentence + ". "

    if current:
        chunks.append(current.strip())

    return chunks


def main():
    print("=== Parent Document Retrieval ===\n")

    # 부모 문서 (긴 문서)
    parent_docs = [
        {
            "id": "doc1",
            "content": """LangGraph는 LangChain 기반 워크플로우 라이브러리입니다.
            StateGraph를 사용하여 상태를 관리합니다.
            노드와 엣지로 복잡한 플로우를 구성할 수 있습니다.
            체크포인트 기능으로 영속성을 제공합니다.
            복잡한 AI 에이전트 구축에 최적화되어 있습니다."""
        },
        {
            "id": "doc2",
            "content": """ChromaDB는 로컬 벡터 데이터베이스입니다.
            Python으로 쉽게 사용할 수 있습니다.
            자동으로 임베딩을 생성합니다.
            RAG 시스템 구축에 필수적입니다.
            무료로 사용 가능합니다."""
        }
    ]

    # Parent-Child 저장소
    store = ParentDocumentStore()

    # ChromaDB (자식 청크만 저장)
    client = chromadb.Client()
    try:
        client.delete_collection("chunks")
    except:
        pass

    collection = client.create_collection("chunks")

    # 데이터 처리
    all_chunks = []
    all_ids = []

    for doc in parent_docs:
        # 작은 청크로 분할
        chunks = split_into_chunks(doc['content'], chunk_size=80)

        # 저장소에 추가
        store.add_document(doc['id'], doc['content'], chunks)

        # ChromaDB에 청크 추가
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['id']}_chunk{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)

    collection.add(documents=all_chunks, ids=all_ids)

    print(f"✅ {len(parent_docs)}개 부모 문서, {len(all_chunks)}개 자식 청크\n")
    print("="*60)

    # 검색
    query = "AI 에이전트"
    print(f"🔍 질문: {query}\n")

    # 1. 작은 청크로 검색
    results = collection.query(query_texts=[query], n_results=1)

    child_id = results['ids'][0][0]
    child_chunk = results['documents'][0][0]

    print(f"📝 검색된 청크 (Child):")
    print(f"   ID: {child_id}")
    print(f"   내용: {child_chunk}\n")

    # 2. 부모 문서 가져오기
    parent_doc = store.get_parent(child_id)

    print("="*60)
    print(f"📄 반환된 부모 문서 (Parent):")
    print(f"   {parent_doc}\n")

    print("💡 장점:")
    print("   1. 작은 청크 → 검색 정확도 ↑")
    print("   2. 부모 문서 → 풍부한 컨텍스트")
    print("\n📚 다음: step6.py - Self-Query\n")


if __name__ == "__main__":
    main()
