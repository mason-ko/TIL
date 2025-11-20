"""
MLOps Step 2: Docker 컨테이너화

실행: docker build -t llm-api .
"""


def create_dockerfile():
    """Dockerfile 생성"""
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

    print("=== Dockerfile ===\n")
    print(dockerfile_content)

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    print("✅ Dockerfile 생성 완료\n")


def create_requirements():
    """requirements.txt 생성"""
    requirements = '''fastapi==0.109.0
uvicorn==0.27.0
langchain-community==0.0.38
python-dotenv==1.0.0
'''

    print("=== requirements.txt ===\n")
    print(requirements)

    with open("requirements.txt", "w") as f:
        f.write(requirements)

    print("✅ requirements.txt 생성 완료\n")


def create_main_app():
    """main.py 생성"""
    main_content = '''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LLM API")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def root():
    return {"message": "LLM API Server", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Ollama는 Docker 외부에서 실행 중이라고 가정
    return ChatResponse(response=f"Echo: {request.message}")

@app.get("/health")
def health():
    return {"status": "healthy"}
'''

    print("=== main.py ===\n")
    print(main_content)

    with open("main.py", "w") as f:
        f.write(main_content)

    print("✅ main.py 생성 완료\n")


def docker_commands():
    """Docker 명령어 가이드"""
    print("=== Docker 빌드 및 실행 ===\n")

    commands = [
        ("빌드", "docker build -t llm-api ."),
        ("실행", "docker run -p 8000:8000 llm-api"),
        ("백그라운드", "docker run -d -p 8000:8000 llm-api"),
        ("로그 확인", "docker logs <container_id>"),
        ("중지", "docker stop <container_id>"),
        ("이미지 목록", "docker images"),
        ("컨테이너 목록", "docker ps"),
    ]

    for desc, cmd in commands:
        print(f"{desc:15} | {cmd}")

    print("\n테스트:")
    print("  curl http://localhost:8000")
    print('  curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d \'{"message":"Hello"}\'')
    print()


if __name__ == "__main__":
    print("🚀 Docker 컨테이너화\n")
    print("=" * 60)

    create_dockerfile()
    print("-" * 60)
    create_requirements()
    print("-" * 60)
    create_main_app()
    print("-" * 60)
    docker_commands()

    print("=" * 60)
    print("\n✅ Docker 설정 완료!")
    print("\n📦 생성된 파일:")
    print("  - Dockerfile")
    print("  - requirements.txt")
    print("  - main.py")
    print("\n🚀 실행:")
    print("  docker build -t llm-api .")
    print("  docker run -p 8000:8000 llm-api")
    print()
