"""Fine-tuning Step 4: 평가 및 비교"""

def evaluate_model():
    print("=== 모델 평가 ===\n")
    
    # 시뮬레이션
    base_perplexity = 15.2
    finetuned_perplexity = 8.3
    
    print(f"📊 Perplexity:")
    print(f"   베이스 모델: {base_perplexity}")
    print(f"   Fine-tuned: {finetuned_perplexity}")
    print(f"   개선: {(base_perplexity - finetuned_perplexity) / base_perplexity * 100:.1f}%\n")
    
    print("✅ Fine-tuning 성공!")

if __name__ == "__main__":
    evaluate_model()
    print("\n📚 다음: step5.py - 배포\n")
