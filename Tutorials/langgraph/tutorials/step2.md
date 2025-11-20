# Step 2: LangChain 기본 사용

## 개요
LangChain은 LLM 애플리케이션 개발을 쉽게 만들어주는 프레임워크입니다.
Step 1에서 배운 기본 LLM 호출을 더 구조적이고 재사용 가능하게 만드는 방법을 배웁니다.

## 사전 준비

### 필요한 패키지 설치
```bash
pip install langchain langchain-google-genai pydantic
```

### 실행
```bash
python tutorials/step2.py
```

## LangChain이 필요한 이유

Step 1에서 Gemini API를 직접 사용했을 때의 문제점:
- 프롬프트를 재사용하기 어렵다
- 여러 단계의 처리를 연결하기 복잡하다
- 출력을 구조화하려면 직접 파싱 로직을 작성해야 한다
- 대화 이력 관리를 수동으로 해야 한다

LangChain은 이러한 문제들을 해결해줍니다!

## 코드 설명

### 1. 기본 LangChain 호출 (`basic_langchain_call`)

**Step 1과의 차이점:**

**Before (Step 1):**
```python
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("질문")
text = response.text
```

**After (Step 2):**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
response = llm.invoke([HumanMessage(content="질문")])
text = response.content
```

**LangChain의 메시지 타입:**
- `SystemMessage`: 시스템 프롬프트 (LLM의 역할/행동 정의)
- `HumanMessage`: 사용자 메시지
- `AIMessage`: AI의 응답 (대화 이력에 저장할 때 사용)

### 2. 프롬프트 템플릿 (`prompt_template_example`)

**프롬프트 템플릿의 장점:**
- 재사용 가능한 프롬프트 패턴을 만들 수 있습니다
- 변수를 사용하여 동적으로 프롬프트를 생성합니다
- 코드가 깔끔하고 유지보수하기 쉽습니다

**템플릿 정의:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {subject} 전문가입니다."),
    ("user", "{topic}에 대해 설명해주세요.")
])
```

**템플릿 사용:**
```python
messages = prompt.invoke({
    "subject": "Python 프로그래밍",
    "topic": "데코레이터"
})
```

`{subject}`와 `{topic}`이 실제 값으로 치환되어 메시지가 생성됩니다.

### 3. 체인 (Chain) (`chain_example`)

**체인이란?**
여러 컴포넌트를 순차적으로 연결하여 데이터 처리 파이프라인을 만드는 것입니다.

**LCEL (LangChain Expression Language):**
```python
chain = prompt | llm | output_parser
```

`|` 연산자로 컴포넌트를 연결합니다. 왼쪽에서 오른쪽으로 데이터가 흐릅니다.

**체인 실행 흐름:**
1. `prompt`: 입력 딕셔너리를 받아 메시지 생성
2. `llm`: 메시지를 받아 LLM 호출
3. `output_parser`: AI 응답을 원하는 형태로 변환

**장점:**
- 재사용 가능: 같은 체인을 다른 입력으로 여러 번 호출
- 모듈화: 각 단계를 독립적으로 테스트하고 교체 가능
- 가독성: 데이터 흐름이 명확함

### 4. 구조화된 출력 (`json_output_example`)

**문제:** LLM은 자유 형식의 텍스트를 반환합니다. 이를 프로그램에서 사용하려면 구조화가 필요합니다.

**해결책:** JsonOutputParser 사용

**Pydantic 모델 정의:**
```python
class ProgrammingConcept(BaseModel):
    name: str = Field(description="개념의 이름")
    difficulty: str = Field(description="난이도")
    description: str = Field(description="설명")
    example: str = Field(description="코드 예제")
```

**파서 사용:**
```python
parser = JsonOutputParser(pydantic_object=ProgrammingConcept)
chain = prompt | llm | parser
result = chain.invoke({"concept": "제너레이터"})
# result는 딕셔너리로 반환됩니다!
```

**내부 동작:**
1. `parser.get_format_instructions()`가 JSON 형식 지시사항 생성
2. 이 지시사항을 프롬프트에 포함
3. LLM이 지시에 따라 JSON 형식으로 응답
4. 파서가 JSON 문자열을 파싱하여 딕셔너리로 변환

### 5. 스트리밍 체인 (`streaming_chain_example`)

체인에서도 스트리밍을 사용할 수 있습니다:

```python
chain = prompt | llm | output_parser

for chunk in chain.stream({"question": "질문"}):
    print(chunk, end="", flush=True)
```

- `invoke()`: 전체 응답을 한 번에 반환
- `stream()`: 응답을 청크 단위로 생성

### 6. 대화 이력 관리 (`conversation_with_memory`)

**MessagesPlaceholder 사용:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "시스템 메시지"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])
```

`MessagesPlaceholder`는 런타임에 여러 메시지를 동적으로 삽입할 수 있는 자리 표시자입니다.

**대화 이력 관리:**
```python
chat_history = []

# 첫 번째 대화
response = chain.invoke({
    "chat_history": chat_history,
    "input": "안녕하세요!"
})

# 이력에 추가
chat_history.append(HumanMessage(content="안녕하세요!"))
chat_history.append(AIMessage(content=response))

# 두 번째 대화 (이전 내용을 기억함)
response = chain.invoke({
    "chat_history": chat_history,
    "input": "방금 뭐라고 했죠?"
})
```

## 핵심 개념 정리

### 1. LangChain의 주요 컴포넌트

**Models (모델):**
- `ChatGoogleGenerativeAI`: Google Gemini의 채팅 모델 래퍼
- 환경변수에서 API 키 자동 로드
- 일관된 인터페이스 제공

**Prompts (프롬프트):**
- `ChatPromptTemplate`: 재사용 가능한 프롬프트 템플릿
- 변수를 사용한 동적 프롬프트 생성
- 메시지 역할 관리

**Output Parsers (출력 파서):**
- `StrOutputParser`: 문자열로 변환
- `JsonOutputParser`: JSON으로 파싱
- 커스텀 파서 작성 가능

**Chains (체인):**
- LCEL (`|` 연산자)로 컴포넌트 연결
- 재사용 가능한 파이프라인
- `invoke()`, `stream()` 메서드 제공

### 2. LCEL의 장점

**조합성 (Composability):**
```python
chain1 = prompt1 | llm
chain2 = prompt2 | llm | parser
chain3 = chain1 | parser  # 체인을 조합 가능
```

**일관된 인터페이스:**
- 모든 체인이 `invoke()`, `stream()`, `batch()` 지원
- 컴포넌트를 쉽게 교체 가능

**병렬 처리:**
```python
from langchain_core.runnables import RunnableParallel

combined = RunnableParallel(
    summary=summary_chain,
    translation=translation_chain
)
```

### 3. Step 1과의 비교

| 측면 | Step 1 (Gemini 직접) | Step 2 (LangChain) |
|------|---------------------|-------------------|
| **간결성** | 상대적으로 많은 코드 | 간결한 코드 |
| **재사용성** | 프롬프트 하드코딩 | 템플릿으로 재사용 |
| **구조화** | 수동 파싱 필요 | 자동 파싱 지원 |
| **체인 구성** | 수동으로 연결 | LCEL로 쉽게 연결 |
| **학습 곡선** | 쉬움 | 중간 |
| **유연성** | 높음 | 높음 |

## 다음 단계

LangChain의 기본을 이해했습니다!

다음 단계(Step 3)에서는 드디어 **LangGraph**를 배웁니다.
LangGraph는 복잡한 에이전트 워크플로우를 그래프 구조로 표현할 수 있게 해줍니다.

**Step 3에서 배울 내용:**
- LangGraph의 기본 개념 (노드, 엣지, 그래프)
- 상태 기반 워크플로우
- 순환 흐름 (사이클)
- 간단한 에이전트 구축
