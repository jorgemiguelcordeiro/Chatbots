from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
from rag import get_response, add_documents, collection
import os

app = FastAPI()

origins = ["http://127.0.0.1:5173", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

class DocItem(BaseModel):
    text: str
    metadata: Optional[dict] = None

class DocsPayload(BaseModel):
    documents: List[Union[str, DocItem]]

@app.on_event("startup")
async def load_seed_docs():
    try:
        stats = collection.count()
        if stats and stats > 0:
            return
    except Exception:
        # Proceed to load if count is unavailable
        pass

    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    docs: List[str] = []

    if os.path.isdir(data_dir):
        for name in os.listdir(data_dir):
            if name.lower().endswith(".txt"):
                path = os.path.join(data_dir, name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            docs.append(content)
                except Exception:
                    continue

    if docs:
        add_documents(docs)

@app.post("/chat")
def chat(msg: ChatMessage):
    reply = get_response(msg.message)
    return {"reply": reply}

@app.post("/docs")
def add_docs(payload: DocsPayload):
    if not payload.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    docs: List[str] = []

    for item in payload.documents:
        if isinstance(item, str):
            docs.append(item)
        else:
            docs.append(item.text)

    add_documents(docs)
    return {"added": len(docs)}
