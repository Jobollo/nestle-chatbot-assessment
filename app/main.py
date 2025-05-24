from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .vector_search import query_pinecone
from .llm import ask_openai_with_context

app = FastAPI()

# Enable CORS for the React frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_question = req.question
    # Step 1: Query Pinecone for relevant context
    context_chunks = query_pinecone(user_question)
    # Step 2: Pass context and question to OpenAI LLM
    answer = ask_openai_with_context(user_question, context_chunks)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000, reload=True)
