from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import requests
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ArticleSession API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all for testing. Replace with frontend domain later.
    allow_credentials=True,
    allow_methods=["*"],   # Allow POST + OPTIONS
    allow_headers=["*"],   # Allow JSON headers
)

N8N_Webhook_URL = os.getenv("N8N_WEBHOOK_URL")

@app.get("/")
async def root():
    return {"message": "ArticleSession API is running."}

class ArticleRequest(BaseModel):
    email: str
    article_url: str

@app.post("/submit-article")
async def receive_from_lovable(data: ArticleRequest):
    # Generate session ID
    session_id = str(uuid.uuid4())

    # Prepare payload for n8n
    payload = {
        "session_id": session_id,
        "email": data.email,
        "article_url": data.article_url
    }

    # Send to n8n webhook
    async with httpx.AsyncClient() as client:
        try:
            await client.post(N8N_Webhook_URL, json=payload)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {
        "status": "received",
        "session_id": session_id
    }