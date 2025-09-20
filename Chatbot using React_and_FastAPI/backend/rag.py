import os
import logging
import requests
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List

# Logger setup
logger = logging.getLogger("ingestion")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Load Hugging Face API key
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "openai/gpt-oss-20b:groq"  # Your current choice

# Headers for Hugging Face API
HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

# Initialize embedding model (local, free)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB client and collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="company_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)

# ---- Chunking ----
def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """Split a long string into overlapping character chunks."""
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

# ---- Document Management ----
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


# ---- RAG Pipeline ----
def retrieve_context(query: str, k: int = 3):
    """
    Retrieve top-k most relevant docs for a query.
    """
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results["documents"][0] if results["documents"] else []


def build_prompt(user_query: str, context_docs: list) -> str:
    """
    Build a structured prompt for the chatbot using retrieved context.
    """
    context_text = "\n".join(context_docs)
    system_message = (
        """You are Aurora, a helpful and knowledgeable AI representative for StellarSoft, 
            a leading SaaS and enterprise solutions company. 

            Your job is to:
            - Always respond in a friendly, confident, and professional tone, as if you are a real StellarSoft team member.
            - Only use company-approved knowledge from provided context documents (FAQs, policies, service guides).
            - If something is outside StellarSoft’s expertise, politely say you’re not sure and guide the user to StellarSoft Support.
            - Keep responses short, clear, and easy to read.
            - Add a warm, customer-first tone. Example: “Happy to help!” or “Great question!”
            """
        f"Context:\n{context_text}\n\n"
    )
    return system_message + f"User question: {user_query}"


def get_response(user_query: str) -> str:
    """
    Full RAG pipeline: retrieve context, build prompt, and query HF API.
    """
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
