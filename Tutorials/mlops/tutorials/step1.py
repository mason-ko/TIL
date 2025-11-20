"""
MLOps Step 1: FastAPI 서버

pip install fastapi uvicorn langchain-community
"""

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama

app = FastAPI(title="LLM API")
llm = Ollama(model="llama3")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {"message": "LLM API Server", "status": "running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """채팅 엔드포인트"""
    response = llm.invoke(request.message)
    return ChatResponse(response=response)


@app.get("/health")
def health():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("🚀 LLM API 서버 시작...")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs (Swagger UI)")

    uvicorn.run(app, host="0.0.0.0", port=8000)
