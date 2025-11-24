# Step 2: 데이터셋 준비

## 목표

- Fine-tuning 데이터셋 형식 이해
- 고품질 데이터 작성 가이드
- 데이터 정제 방법
- 실전 준비 단계

## 데이터셋이 성패를 결정

```
고품질 데이터 1,000개 > 저품질 데이터 100,000개
```

**핵심 원칙:**
- 품질 > 양
- 일관성 > 다양성
- 정확성 > 속도

## 데이터셋 형식

### Instruction 형식 (권장)

```json
{
  "instruction": "작업 설명",
  "input": "입력 (선택사항)",
  "output": "기대 출력"
}
```

### 예시

```json
[
  {
    "instruction": "FastAPI로 Hello World 엔드포인트 만들어줘",
    "input": "",
    "output": "@app.get('/')\ndef hello():\n    return {'message': 'Hello World'}"
  },
  {
    "instruction": "다음 코드를 FastAPI로 변환해줘",
    "input": "def get_user(id): return users[id]",
    "output": "@app.get('/users/{id}')\ndef get_user(id: int):\n    return users[id]"
  },
  {
    "instruction": "Python 리스트 컴프리헨션 설명해줘",
    "input": "",
    "output": "리스트 컴프리헨션은 간결하게 리스트를 생성하는 방법입니다. [x for x in range(10)]"
  }
]
```

### Chat 형식 (대화형)

```json
{
  "messages": [
    {"role": "system", "content": "너는 Python 전문가야"},
    {"role": "user", "content": "FastAPI 설명해줘"},
    {"role": "assistant", "content": "FastAPI는..."}
  ]
}
```

## 데이터 수집 전략

### 1. 직접 작성 (권장)

```python
# 전문 지식을 데이터로
examples = [
    {
        "instruction": "우리 회사 휴가 정책은?",
        "input": "",
        "output": "연차 15일, 병가 10일입니다. 입사 1년 후부터 사용 가능합니다."
    },
    # ... 1,000개
]
```

**장점:**
- 정확도 보장
- 도메인 특화 가능
- 스타일 통일

**단점:**
- 시간 소요
- 전문 지식 필요

### 2. 기존 데이터 변환

```python
# FAQ → Fine-tuning 데이터
faq = [
    ("Q: 배송 기간은?", "A: 2-3일 소요됩니다"),
    ("Q: 반품 가능한가요?", "A: 7일 이내 가능합니다")
]

dataset = [
    {
        "instruction": q.replace("Q: ", ""),
        "input": "",
        "output": a.replace("A: ", "")
    }
    for q, a in faq
]
```

### 3. GPT-4로 생성 (초안)

```python
from openai import OpenAI
client = OpenAI()

def generate_samples(topic, n=10):
    prompt = f"""
    {topic}에 대한 질문-답변 쌍을 {n}개 생성해줘.

    형식:
    Q: 질문
    A: 답변
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # 파싱 및 검증 필요
    return response.choices[0].message.content

# 주의: 반드시 수동 검증 필요!
```

**주의사항:**
- 생성된 데이터는 **반드시 검증**
- 오류, 편향 확인
- 법적 문제 고려 (저작권)

## 데이터 품질 가이드

### 1. 양 (Quantity)

```
최소: 1,000개
권장: 10,000개
이상적: 100,000개+
```

**단, 품질이 우선!**

```python
# 나쁜 예
1,000,000개 (자동 생성, 오류 많음) ❌

# 좋은 예
10,000개 (수동 검증, 정확함) ✅
```

### 2. 품질 (Quality)

```python
# 나쁜 예
{
    "instruction": "코드 짜줘",  # 모호함
    "output": "def f(): pass"    # 불완전
}

# 좋은 예
{
    "instruction": "FastAPI로 사용자 등록 엔드포인트를 만들어줘. Pydantic 모델 포함.",
    "output": "from fastapi import FastAPI\nfrom pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    email: str\n\n@app.post('/users')\ndef create_user(user: User):\n    return user"
}
```

### 3. 일관성 (Consistency)

```python
# 나쁜 예 (스타일 불일치)
[
    {"output": "def hello(): return 'hi'"},     # 한 줄
    {"output": "def world():\n    return 'world'"},  # 여러 줄
]

# 좋은 예 (스타일 통일)
[
    {"output": "def hello():\n    return 'hi'"},
    {"output": "def world():\n    return 'world'"},
]
```

### 4. 다양성 (Diversity)

```python
# 나쁜 예 (비슷한 예제만)
[
    "GET 엔드포인트 만들어줘",
    "GET 엔드포인트 작성해줘",
    "GET 엔드포인트 생성해줘",
    # ... 100개 전부 GET
]

# 좋은 예 (다양한 케이스)
[
    "GET 엔드포인트 만들어줘",
    "POST로 데이터 저장하는 엔드포인트",
    "PUT으로 업데이트하는 API",
    "DELETE 엔드포인트",
    "쿼리 파라미터 처리",
    "Path 파라미터 검증",
    # ... 다양한 시나리오
]
```

## 품질 체크리스트

실행: `python step2.py` → 체크리스트 출력

```
✓ 모든 답변이 정확한가?
✓ 일관된 스타일인가?
✓ 너무 짧거나 길지 않은가? (50-500자)
✓ 다양한 케이스를 커버하는가?
✓ 중복된 샘플은 없는가?
✓ 편향(bias)은 없는가?
```

### 자동 검증 스크립트

```python
def validate_dataset(data):
    issues = []

    # 중복 체크
    outputs = [d['output'] for d in data]
    if len(outputs) != len(set(outputs)):
        issues.append("중복된 답변 발견")

    # 길이 체크
    for i, d in enumerate(data):
        length = len(d['output'])
        if length < 50:
            issues.append(f"샘플 {i}: 너무 짧음 ({length}자)")
        if length > 2000:
            issues.append(f"샘플 {i}: 너무 김 ({length}자)")

    # 빈 값 체크
    for i, d in enumerate(data):
        if not d['instruction'] or not d['output']:
            issues.append(f"샘플 {i}: 빈 값 존재")

    return issues

# 사용
with open("dataset.json") as f:
    data = json.load(f)

issues = validate_dataset(data)
if issues:
    print("문제 발견:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ 검증 통과")
```

## 데이터 분할

### Train / Validation 분할

```python
import json
import random

with open("dataset.json") as f:
    data = json.load(f)

# 셔플
random.shuffle(data)

# 90% train, 10% validation
split_idx = int(len(data) * 0.9)
train = data[:split_idx]
val = data[split_idx:]

# 저장
with open("train.json", "w") as f:
    json.dump(train, f, ensure_ascii=False, indent=2)

with open("val.json", "w") as f:
    json.dump(val, f, ensure_ascii=False, indent=2)

print(f"Train: {len(train)}개")
print(f"Val: {len(val)}개")
```

## 포맷 변환 (JSONL)

### JSON → JSONL

```python
import json

with open("dataset.json") as f:
    data = json.load(f)

with open("dataset.jsonl", "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
```

**JSONL 형식:** (한 줄에 하나의 JSON)
```jsonl
{"instruction": "...", "output": "..."}
{"instruction": "...", "output": "..."}
{"instruction": "...", "output": "..."}
```

**장점:**
- 대용량 데이터 처리 효율적
- 스트리밍 가능
- 대부분 프레임워크 지원

## 실무 준비 단계

### 1. 목표 정의

```
무엇을 잘하게 만들 것인가?
- FastAPI 코드 생성?
- 고객 상담 답변?
- 번역?
```

### 2. 데이터 수집

```
- 직접 작성: 100개 (고품질)
- 기존 데이터 변환: 900개
- 합계: 1,000개
```

### 3. 데이터 정제

```python
# 중복 제거
# 오류 수정
# 스타일 통일
# 검증
```

### 4. 포맷 변환

```python
# JSON → JSONL
# Train/Val 분할
```

### 5. GPU 환경 준비

```
RTX 3090 (24GB) 이상
또는
Google Colab (무료 T4)
```

## 데이터셋 예시 (실행)

```bash
python step2.py
```

**출력:**
```
=== 데이터셋 형식 ===

샘플 데이터:

1. Instruction: FastAPI로 Hello World 엔드포인트 만들어줘
   Output: @app.get('/')...

✅ dataset.json 생성 (3개 샘플)

=== 데이터셋 작성 가이드 ===

양         | 최소 1,000개, 권장 10,000개
품질       | 고품질 > 대량. 정확한 답변만
...
```

## 다음 단계

**Step 3: Fine-tuning 실행**
- LoRA 적용
- 학습 파라미터 설정
- 모델 학습 및 평가

---

**핵심 요약:**
1. 품질 > 양 (정확한 1,000개 > 부정확한 100,000개)
2. 일관성 유지 (스타일, 포맷)
3. 검증 필수 (자동 + 수동)
4. JSONL 형식 권장

**데이터셋 = Fine-tuning의 90%** ✅
