# server.py

from fastapi import FastAPI, HTTPException #used to return error messages if something goes wrong.
#from fastapi.middleware.cors import CORSMiddleware - allows requests from a web frontend running on a different server/port. Not necessary in this case
from pydantic import BaseModel #used for structured request parsing and validation.
from typing import List, Union, Optional
from model import get_response, add_documents, collection #everything from model.py
from whatsapp_utils import send_whatsapp_message
import os

app = FastAPI() #starts the web server

# Modelos Pydantic para validação de entrada
#This define the request models
class ChatMessage(BaseModel):
    message: str #Incoming JSON must look like:{ "message": "hello" }

class DocItem(BaseModel):
    text: str
    metadata: Optional[dict] = None #Represents a document with optional metadata. { "text": "some document", "metadata": {"author": "me"} }

class DocsPayload(BaseModel):
    documents: List[Union[str, DocItem]] #payload for adding many documents at once

# Evento startup para carregar documentos iniciais na base

@app.on_event("startup") #  Runs once when the API starts.
async def load_seed_docs():
    try:               #Checks if your collection already has docs → if yes, skip.
        stats = collection.count()
        if stats and stats > 0:
            return
    except Exception:
        pass
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    docs = []
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

# Endpoint para teste local, enviar mensagem e receber resposta do chatbot
@app.post("/chat")
def chat(msg: ChatMessage):
    reply = get_response(msg.message)  #Calls your get_response() (from model.py) to generate chatbot reply.
    return {"reply": reply}

# Endpoint para adicionar documentos novos dinamicamente
@app.post("/docs")
def add_docs(payload: DocsPayload):
    if not payload.documents:
        raise HTTPException(status_code=400, detail="No documents provided") #This ensures the request isn’t empty.
    docs = []
    for item in payload.documents:  #this loops through provided docs
        if isinstance(item, str):
            docs.append(item) #if it is a palin string, we add directly
        else:
            docs.append(item.text) #if it is a docitem, we extract .text
    add_documents(docs) #saves to the database
    return {"added": len(docs)}

# Endpoint webhook para receber mensagens do WhatsApp API
@app.post("/whatsapp_webhook")
async def whatsapp_webhook(request: Request):  #WhatsApp sends POST requests when someone messages your number
    payload = await request.json()
    # Aqui você deve adaptar conforme o formato do webhook WhatsApp API
    try:
        # Exemplo simplificado:
        user_message = payload["messages"][0]["text"]["body"] #extracts the message text 
        sender_id = payload["messages"][0]["from"] #and the sender's ID
    except (KeyError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid WhatsApp webhook payload") #If the format is wrong return 400 Bad Request

    # Obter resposta do chatbot
    reply = get_response(user_message)

    # Aqui você deve enviar a resposta para o WhatsApp via API (código omitido para você implementar)
    success = send_whatsapp_message(sender_id, reply)
    if not success:
        # Handle failure if needed (e.g., log or retry)
        pass

    return {"status": "received"}
