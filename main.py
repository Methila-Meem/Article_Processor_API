from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import requests
import os
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
async def submit_article(data: ArticleRequest):

    session_id = str(uuid.uuid4())

    payload ={
        "session_id": session_id,
        "email": data.email,
        "article_url": data.article_url
    }

    try:
        response = requests.post(N8N_Webhook_URL, json=payload)
        response.raise_for_status()
    except  requests.RequestException as e:
        print("Error forwarding data to n8n webhook:", e)
        return{"status": "error", "message": "Failed to forward data to n8n webhook."}

    print(f"Received article submission from {data.email} for URL: {data.article_url}") 
    print("Forwarded data to n8n webhook with session_id:", session_id)
    
    return{"status": "ok", "message": "Data received."}