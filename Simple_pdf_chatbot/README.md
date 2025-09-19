# 📄 Chatbot

An interactive **PDF Document Chatbot** built with Gradio and Hugging Face, which lets you upload a PDF and chat with it using the **GPT-OSS-20B** model.  

---

## 👍 Project Status

- ✅ Available at: [Chatbot on Hugging Face Spaces](https://huggingface.co/spaces/jmcordeiro/Chatbot_2)  
- 🔁 Built using Gradio’s “chatbot” template  
- 📂 Key files in the space:
  - `app.py` — main application logic (PDF processing, embedding, HF inference)  
  - `requirements.txt` — dependencies needed for building and running  
  - `.gitattributes` — version control settings  
  - `README.md` — this file  

---

## 🚀 Features

- Upload a PDF and the app splits it into text chunks  
- Embeddings via `sentence-transformers/all-MiniLM-L6-v2` + Chroma vector store  
- Context-based responses using `openai/gpt-oss-20b` model via Hugging Face Inference API  
- Clean Gradio UI for uploading PDFs and asking questions  

---

## 🛠 How to Use

1. Go to the Space: [Chatbot_2](https://huggingface.co/spaces/jmcordeiro/Chatbot_2)  
2. Upload a PDF using the “Upload PDF” field  
3. Enter your Hugging Face API token in the HF Token field  
4. Ask your question in the “Your question” box  
5. See response from the document via the chatbot  

---

## ⚠️ Setup / Dependencies

In `requirements.txt`, the project includes:

- `gradio`  
- `huggingface-hub`  
- `langchain_community` for document loaders, embeddings, vector stores  
- `sentence-transformers` for embeddings  
- Any other necessary libraries for PDF upload and processing  

Make sure the HF token has **read** permissions (for model inference)  

---

## 💡 Future Ideas

- Support for **multiple PDFs** uploaded in one session, enabling cross-document search  
- Voice or speech input / output  
- More summarization, possibly auto-extracting key points from documents  

---

## ⚙️ Notes & Tips

- As this is on a cloud model setup, performance depends on Hugging Face’s Inference API  
- Token usage may be limited depending on your plan/account  
- Make sure your PDF has extractable text (not just scanned images) for better results  

---



