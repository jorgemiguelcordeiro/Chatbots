# 1 - Imports and Basic Setup

import os  #systems operations, like env variables and paths
import logging #lets the app output info on what is happening - helpful for debugging
import requests # - for http requests
import chromadb #vector database for storing and search embedding vectors from documents
from chromadb.utils import embedding_functions #tools for embedding text
from sentence_transformers import SentenceTransformer #embedding model for searching similarity
from typing import List #Typing help for Python, defines that certain variables are lists.

# Logger setup

logger = logging.getLogger("ingestion") #Sets up logging so you get timestamped messages, showing what the program’s doing (like adding docs, warnings).
if not logger.handlers: #Only creates a handler if it doesn’t exist already.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# API Key and Models
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") #We have put this in secrets of github
HF_API_URL = "https://router.huggingface.co/v1/chat/completions" #This is the OpenAI-compatible chat endpoint for Hugging Face. It’s used with models that support chat-completions like "openai/gpt-oss-20b:groq".
MODEL = "openai/gpt-oss-20b:groq"
HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}", #The word "Bearer " before the key is part of the OAuth 2.0 standard. OAuth 2.0 is a standard protocol for authorization.
    "Content-Type": "application/json"
}

# Embedding Model and Chroma Database

embedding_model = SentenceTransformer("all-MiniLM-L6-v2") # loads a local HF model to create vector embeddings
chroma_client = chromadb.Client() #initializes Chroma DB
collection = chroma_client.get_or_create_collection(
    name="company_docs",  #creates or gets a collection called company_docs
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)

#chunking long texts

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    chunks: List[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + max_chars, length)
        chunk = cleaned[start:end]
        chunks.append(chunk)
        if end == length:
            break
        start = max(0, end - overlap)
    return chunks

# Adding Documents to the Vector Database
'''
1st - Break docs into chunks.

2nd - Embed each chunk into a vector.

3rd - Store chunks with an ID for each in the vector database.

4th - Log the number of items added.
'''
def add_documents(docs):
    """
    Add a list of documents to the vector database with chunking and logs.
    docs: List of strings (your company knowledge base)
    """
    if not docs:
        logger.info("No documents provided for ingestion.")
        return

    logger.info("Starting ingestion of %d document(s).", len(docs))

    all_chunks: List[str] = []
    all_ids: List[str] = []

    total_chunks = 0
    for i, doc in enumerate(docs):
        chunks = chunk_text(doc)
        logger.info("Doc %d: produced %d chunk(s).", i + 1, len(chunks))
        total_chunks += len(chunks)
        for j, ch in enumerate(chunks):
            all_chunks.append(ch)
            all_ids.append(f"doc{i+1}_chunk{j+1}")

    if not all_chunks:
        logger.warning("No chunks generated; nothing to embed.")
        return

    logger.info("Embedding and adding %d chunk(s) to Chroma...", len(all_chunks))
    collection.add(documents=all_chunks, ids=all_ids)

    try:
        count = collection.count()
        logger.info("Chroma collection status: %d vectors stored.", count)
    except Exception:
        logger.info("Chroma collection status: count unavailable.")

    logger.info("Ingestion complete. %d chunk(s) added.", total_chunks)

#Retrieving Relevant Context

def retrieve_context(query: str, k: int = 3):  #Takes a user’s query, turns it into a vector, finds top k most similar chunks in the database.
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results["documents"][0] if results["documents"] else []

#Building the prompt for the AI model

def build_prompt(user_query: str, context_docs: list) -> str: # Assembles the retrieved document text and the user’s question into a prompt for the chatbot model.
    context_text = "\n".join(context_docs)
    system_message = (
        """You are Aurora, a helpful ..."""
        f"Context:\n{context_text}\n\n"
    )
    return system_message + f"User question: {user_query}"

# Getting the Chatbot’s Response

def get_response(user_query: str) -> str:
    # Retrieve relevant docs
    docs = retrieve_context(user_query)
    # Build enhanced prompt
    prompt = build_prompt(user_query, docs)
    # Send to Hugging Face Router API
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return str(data)

