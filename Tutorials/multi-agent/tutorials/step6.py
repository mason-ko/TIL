"""
Multi-Agent Step 6: 실전 프로젝트 (자동 리서치 봇)

모든 패턴을 통합한 실용적인 Multi-Agent 시스템

pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Literal
from typing import Annotated
import operator


class ResearchState(TypedDict):
    topic: str
    sub_questions: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]
    analysis: str
    draft_report: str
    final_report: str
    current_agent: str
    status: Literal["planning", "searching", "analyzing", "writing", "reviewing", "completed"]
    feedback: Annotated[list, operator.add]


def planner(state: ResearchState) -> ResearchState:
    """1. Planner: 리서치 계획"""
    print("\n[1. Planner] 리서치 계획 수립 중...")

    topic = state['topic']

    # 하위 질문 생성
    sub_questions = [
        f"{topic}이란 무엇인가?",
        f"{topic}의 주요 특징은?",
        f"{topic}의 활용 사례는?"
    ]

    print(f"   └─ {len(sub_questions)}개 질문 생성")

    return {
        "sub_questions": sub_questions,
        "current_agent": "planner",
        "status": "searching"
    }


def searcher(state: ResearchState) -> ResearchState:
    """2. Searcher: 정보 검색"""
    print("\n[2. Searcher] 정보 검색 중...")

    questions = state.get('sub_questions', [])

    # 검색 시뮬레이션
    results = []
    for i, q in enumerate(questions, 1):
        result = {
            "question": q,
            "answer": f"{q}에 대한 검색 결과 (시뮬레이션)",
            "source": f"source{i}.com"
        }
        results.append(result)
        print(f"   └─ 검색 {i}/{len(questions)}: {q[:30]}...")

    return {
        "search_results": results,
        "current_agent": "searcher",
        "status": "analyzing"
    }


def analyzer(state: ResearchState) -> ResearchState:
    """3. Analyzer: 데이터 분석"""
    print("\n[3. Analyzer] 데이터 분석 중...")

    topic = state['topic']
    search_results = state.get('search_results', [])

    # 분석 생성
    analysis = f"""
[주요 발견사항]
- {topic}에 대한 {len(search_results)}개 소스 분석 완료
- 핵심 개념 및 특징 파악
- 실무 활용 가능성 확인

[인사이트]
- 최근 주목받는 기술
- 다양한 활용 사례 존재
- 학습 곡선은 있으나 실용적
"""

    print("   └─ 분석 완료")

    return {
        "analysis": analysis.strip(),
        "current_agent": "analyzer",
        "status": "writing"
    }


def writer(state: ResearchState) -> ResearchState:
    """4. Writer: 보고서 작성"""
    print("\n[4. Writer] 보고서 작성 중...")

    topic = state['topic']
    sub_questions = state.get('sub_questions', [])
    analysis = state.get('analysis', '')
    search_results = state.get('search_results', [])

    # 보고서 생성
    draft = f"""# {topic} 리서치 보고서

## 1. 개요
본 보고서는 '{topic}'에 대한 종합 리서치 결과입니다.

## 2. 조사 항목
{chr(10).join([f"- {q}" for q in sub_questions])}

## 3. 분석 결과
{analysis}

## 4. 데이터 출처
총 {len(search_results)}개 소스 조사

## 5. 결론
{topic}은(는) 실무에서 충분히 활용 가능한 기술입니다.

---
*AI Research Bot 생성 보고서*
"""

    print("   └─ 초안 작성 완료")

    return {
        "draft_report": draft,
        "current_agent": "writer",
        "status": "reviewing"
    }


def reviewer(state: ResearchState) -> ResearchState:
    """5. Reviewer: 품질 검토"""
    print("\n[5. Reviewer] 품질 검토 중...")

    draft = state.get('draft_report', '')

    # 품질 체크
    has_structure = "##" in draft
    has_conclusion = "결론" in draft
    has_sources = "출처" in draft
    min_length = len(draft) > 300

    all_good = has_structure and has_conclusion and has_sources and min_length

    if all_good:
        feedback = "✅ 보고서 승인: 구조, 내용, 분량 모두 양호"
        status = "completed"
        final = draft
        print("   └─ 승인 완료")
    else:
        feedback = "⚠️ 재작성 필요: 구조 또는 분량 부족"
        status = "writing"
        final = ""
        print("   └─ 재작성 요청")

    return {
        "feedback": [feedback],
        "current_agent": "reviewer",
        "status": status,
        "final_report": final
    }


def route_after_review(state: ResearchState) -> str:
    """리뷰 후 라우팅"""
    if state['status'] == "completed":
        return "end"
    else:
        return "writer"  # 재작성


def main():
    print("="*60)
    print("🤖 자동 리서치 봇 - Multi-Agent System")
    print("="*60)

    # 그래프 구성
    workflow = StateGraph(ResearchState)

    # 에이전트 노드
    workflow.add_node("planner", planner)
    workflow.add_node("searcher", searcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("writer", writer)
    workflow.add_node("reviewer", reviewer)

    # 흐름
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "analyzer")
    workflow.add_edge("analyzer", "writer")
    workflow.add_edge("writer", "reviewer")

    # 리뷰 후 조건부 분기
    workflow.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "writer": "writer",  # 재작성
            "end": END          # 완료
        }
    )

    # 컴파일
    app = workflow.compile()

    # 실행
    print("\n주제: GraphRAG")
    print("-"*60)

    result = app.invoke({
        "topic": "GraphRAG",
        "sub_questions": [],
        "search_results": [],
        "analysis": "",
        "draft_report": "",
        "final_report": "",
        "current_agent": "",
        "status": "planning",
        "feedback": []
    })

    # 결과 출력
    print("\n" + "="*60)
    print("📄 최종 보고서")
    print("="*60)
    print(result['final_report'])

    print("\n" + "="*60)
    print("✅ 리서치 완료!")
    print("="*60)

    print(f"\n📊 통계:")
    print(f"   - 조사 질문: {len(result['sub_questions'])}개")
    print(f"   - 검색 결과: {len(result['search_results'])}개")
    print(f"   - 보고서 길이: {len(result['final_report'])}자")

    print(f"\n💬 피드백:")
    for fb in result['feedback']:
        print(f"   {fb}")

    print("\n🎉 Multi-Agent 튜토리얼 완료!")
    print("\n💡 배운 내용:")
    print("   1. Sequential 패턴 (순차 실행)")
    print("   2. Supervisor 패턴 (작업 분배)")
    print("   3. Collaborative 패턴 (대화형 협업)")
    print("   4. Tool Sharing (도구 공유)")
    print("   5. State Management (상태 관리)")
    print("   6. 실전 프로젝트 (리서치 봇)")

    print("\n🚀 다음 단계:")
    print("   - LangSmith/Langfuse: 디버깅 및 모니터링")
    print("   - Advanced RAG: 정보 검색 품질 향상")
    print("   - Fine-tuning: 특화 모델 학습\n")


if __name__ == "__main__":
    main()
