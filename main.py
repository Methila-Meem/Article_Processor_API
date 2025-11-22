from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ArticleSession API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read once at startup
# N8N_Webhook_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_Webhook_URL = "https://methilameem.app.n8n.cloud/webhook-test/a60f85db-cb61-4006-b291-c8552f4962a8"

if not N8N_Webhook_URL:
    # Fail fast: environment variable must be set
    raise RuntimeError("N8N_WEBHOOK_URL environment variable is not set. Set it to your n8n webhook URL.")

class ArticleRequest(BaseModel):
    email: str
    article_url: str

@app.get("/")
async def root():
    return {"message": "ArticleSession API is running."}

@app.post("/submit-article")
async def receive_from_lovable(data: ArticleRequest):
    session_id = str(uuid.uuid4())

    payload = {
        "session_id": session_id,
        "email": data.email,
        "article_url": data.article_url
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(N8N_Webhook_URL, json=payload)
            resp.raise_for_status()   # raise for non-2xx
        except httpx.HTTPStatusError as exc:
            # n8n responded with non-2xx
            return {"status": "error", "message": f"n8n returned {exc.response.status_code}: {exc.response.text}"}
        except Exception as e:
            # Could be network error, invalid URL (None), etc.
            return {"status": "error", "message": str(e)}

    return {"status": "received", "session_id": session_id}
