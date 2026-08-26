import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import PORT
from app.routes import chat, cart, payment

app = FastAPI(
    title="RazorFlow AI — Intelligent Agentic Commerce Platform",
    description="Agentic E-Commerce Platform built with LangGraph, FastAPI, and Razorpay",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat.router)
app.include_router(cart.router)
app.include_router(payment.router)

@app.get("/")
async def root():
    return {
        "platform": "RazorFlow AI — Intelligent Agentic Commerce Platform",
        "status": "online",
        "track": "Track 1: AI Growth & Agentic Commerce (Razorpay AI Buildathon)"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
