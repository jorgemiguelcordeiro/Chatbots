# Customer Support ChatBot

A full-stack RAG (Retrieval-Augmented Generation) chatbot with a modern React frontend and a FastAPI backend powered by ChromaDB vector search and the Hugging Face Inference Router.

![ViteReact-GoogleChrome2025-09-1018-03-37-ezgif com-crop](https://github.com/user-attachments/assets/7321ba7c-8c5a-4250-b72b-d568826007e4)

## Tech Stack

- Frontend: React + Vite
  - Rich message rendering (minimal Markdown: headings, lists, bold/italics, code blocks, tables)
  - Chat-style UI (bot left, user right), welcome/empty state, pinned input
  - Optional fast typing effect for bot responses
- Backend: FastAPI (Python)
  - Endpoints: `/chat`, `/docs`
  - ChromaDB for vector storage and retrieval
  - Sentence-Transformers for embeddings (all-MiniLM-L6-v2)
  - Hugging Face Inference Router for LLM completions
- Vector DB: Chroma (in-process by default)

## Project Structure

```
Customer_Support_ChatBot/
  backend/
    model.py           # RAG logic, embeddings, retrieval, prompt, ingestion
    server.py          # FastAPI app: /chat and /docs endpoints, startup seeding
    requirements.txt   # Python dependencies
  data/
    policy.txt         # Seed policy (plain text)
    faqs.txt           # Seed FAQs (plain text)
  frontend/
    src/               # React app (App.jsx, index.css, main.jsx)
    index.html         # Vite entry page
    package.json       # Frontend dependencies & scripts
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- Windows PowerShell (your environment) or any shell
- A Hugging Face access token with inference access

## Quick Start

### 1) Backend setup

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set the Hugging Face API Key in your environment:

```powershell
$env:HUGGINGFACE_API_KEY = "hf_xxx_your_token_here"
```

4. Run the server (dev):

```powershell
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

The server starts on `http://127.0.0.1:8000`.

On startup, it loads `.txt` files from the `data/` folder into Chroma if the collection is empty.

### 2) Frontend setup

1. Install dependencies:

```powershell
cd ../frontend
npm install
```

2. Start the dev server:

```powershell
npm run dev
```

The app runs on `http://127.0.0.1:5173` (Vite default).

3. (Optional) Configure a custom backend URL by creating `.env` in `frontend/`:

```
VITE_API_URL=http://127.0.0.1:8000
```

## Application Flow

### High level

1. User asks a question in the frontend chat.
2. Frontend calls `POST /chat` on the backend.
3. Backend retrieves relevant context from ChromaDB (RAG), builds a prompt, and calls the Hugging Face Router for a response.
4. Frontend displays the bot response (optionally streamed as a fast typing effect) with rich formatting.

### RAG pipeline (backend)

- Ingestion (startup and `/docs`):
  - Plain text documents from `data/` or the request body are ingested.
  - Each document is chunked (overlapping chars) and added to Chroma with generated chunk IDs.
- Retrieval:
  - `retrieve_context(query)` queries Chroma for the top-k similar chunks.
- Prompt building:
  - The system message + joined context chunks + user question.
- Generation:
  - Sent to the HF Router (`https://router.huggingface.co/v1/chat/completions`) with the configured model.

### Endpoints

- `POST /chat`
  - Body: `{ "message": "<user question>" }`
  - Returns: `{ "reply": "<model reply>" }`
- `POST /docs`
  - Body: `{ "documents": ["text doc 1", {"text": "doc 2"}] }`
  - Ingests texts into Chroma.



## Configuration

- Backend env var: `HUGGINGFACE_API_KEY` (required)
- Frontend env var: `VITE_API_URL` (optional) to point to a non-default backend URL

## Seeding Knowledge

- Put plain `.txt` files in `data/` (e.g., `policy.txt`, `faqs.txt`).
- Restart the backend. If the collection is empty, the files are loaded and embedded.
- You can also add docs at runtime via `POST /docs`.

## Troubleshooting

- Frontend stuck on "Sending":
  - Ensure the backend is running on `http://127.0.0.1:8000` and reachable.
  - Verify `HUGGINGFACE_API_KEY` is set and valid.
  - Check backend console for network errors from the HF Router.
- CORS issues:
  - `server.py` allows `http://127.0.0.1:5173` and `http://localhost:5173` by default.
- No answers / irrelevant answers:
  - Ensure `data/` has meaningful `.txt` content, then restart the backend to seed.
  - Confirm Chroma has vectors (check logs on startup or after `/docs`).
- Ports in use:
  - Change frontend port with `--port` when running Vite, and/or backend port with `uvicorn --port`.

## Scripts

Frontend:
- `npm run dev` — start Vite dev server
- `npm run build` — build for production
- `npm run preview` — preview production build

Backend:
- `uvicorn server:app --reload` — start FastAPI in dev mode

## Notes

- This project uses an in-process Chroma client for simplicity. For persistence across restarts or multi-process deployments, configure a persistent Chroma server or a backed store.
- The minimal Markdown renderer in the frontend is dependency-free and conservative. If you need full Markdown + sanitization, switch to `marked` + `DOMPurify` on the client.

