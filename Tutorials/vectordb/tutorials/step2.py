"""
Vector DB Step 2: 임베딩 모델 선택

pip install chromadb sentence-transformers
"""

import chromadb
from chromadb.utils import embedding_functions


def example1_default_embedding():
    """예제 1: 기본 임베딩 (자동)"""
    print("=== 기본 임베딩 ===\n")

    client = chromadb.Client()
    collection = client.create_collection("default")

    docs = ["Python 프로그래밍", "자바스크립트 개발"]
    collection.add(documents=docs, ids=["d1", "d2"])

    print("✅ 기본 임베딩 모델 사용 (all-MiniLM-L6-v2)\n")


def example2_multilingual():
    """예제 2: 다국어 임베딩 (한국어 최적화)"""
    print("=== 다국어 임베딩 ===\n")

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    client = chromadb.Client()
    collection = client.create_collection(
        "multilingual",
        embedding_function=sentence_transformer_ef
    )

    docs = [
        "강아지가 공원에서 뛰어놀고 있다",
        "고양이가 창가에 앉아있다",
        "Dog is playing in the park"
    ]

    collection.add(documents=docs, ids=[f"d{i}" for i in range(len(docs))])

    # 한국어로 검색
    results = collection.query(query_texts=["개가 노는 모습"], n_results=2)

    print("검색어: '개가 노는 모습'")
    for doc in results['documents'][0]:
        print(f"  - {doc}")
    print("\n✅ 한국어도 잘 찾음!\n")


def example3_custom_openai():
    """예제 3: OpenAI 임베딩 (고품질, 유료)"""
    print("=== OpenAI 임베딩 (참고용) ===\n")

    print("OpenAI Embeddings:")
    print("  - 모델: text-embedding-3-small")
    print("  - 차원: 1536")
    print("  - 품질: 매우 높음")
    print("  - 비용: $0.02 / 1M tokens")
    print("\n사용법:")
    print("  openai_ef = embedding_functions.OpenAIEmbeddingFunction(")
    print("      api_key='your-key',")
    print("      model_name='text-embedding-3-small'")
    print("  )\n")


def compare_models():
    """임베딩 모델 비교"""
    print("=== 임베딩 모델 비교 ===\n")

    models = [
        ("all-MiniLM-L6-v2", "384차원", "영어 중심", "기본값"),
        ("paraphrase-multilingual", "384차원", "다국어", "한국어 추천"),
        ("text-embedding-3-small", "1536차원", "최고 품질", "유료"),
    ]

    print("모델               | 차원   | 특징      | 용도")
    print("-" * 60)
    for name, dim, feature, use in models:
        print(f"{name:20} | {dim:6} | {feature:10} | {use}")

    print()


if __name__ == "__main__":
    example1_default_embedding()
    print("-" * 60)
    example2_multilingual()
    print("-" * 60)
    example3_custom_openai()
    print("-" * 60)
    compare_models()

    print("=" * 60)
    print("\n✅ 임베딩 모델 이해 완료!")
    print("\n💡 권장: 한국어 → paraphrase-multilingual")
    print("📚 다음: step3.py - RAG 실전 구현\n")
