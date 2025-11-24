# Step 4: 평가 및 비교

## 목표

- Fine-tuned 모델 평가
- 베이스 모델과 비교
- 성능 메트릭

## 평가 메트릭

### 1. Perplexity (혼란도)

```python
낮을수록 좋음
베이스 모델: 15.2
Fine-tuned: 8.3 ✅
```

### 2. BLEU Score

```python
# 번역, 생성 품질
0~100, 높을수록 좋음
```

### 3. Human Evaluation

```python
실제 사용자 평가
가장 신뢰할 수 있음
```

## 실무 평가

```python
# 테스트 세트
test_cases = [
    {"input": "...", "expected": "..."},
    # 100개
]

# 평가
correct = 0
for case in test_cases:
    output = model.generate(case["input"])
    if is_correct(output, case["expected"]):
        correct += 1

accuracy = correct / len(test_cases) * 100
print(f"정확도: {accuracy}%")
```

---

**핵심**: 정량적 + 정성적 평가
