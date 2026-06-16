# 📚 College Notes RAG Assistant

An AI-powered College Notes Assistant that helps students get instant answers from their study notes using Retrieval-Augmented Generation (RAG).

Users can ask questions in natural language, and the system retrieves the most relevant information from stored notes before generating an accurate answer.

---

## 🚀 Features

- 📄 PDF Notes Ingestion
- ✂️ Automatic Text Chunking
- 🧠 Embedding Generation using Sentence Transformers
- 🗄️ Vector Storage using Qdrant
- 🔍 Semantic Search
- 🤖 LLM-powered Answer Generation
- ⚡ FastAPI Backend
- 🌐 HTML, CSS & JavaScript Frontend
- 📚 Context-Aware Question Answering

---

## 🏗️ Project Architecture

```text
User Question
      │
      ▼
Frontend (HTML/CSS/JS)
      │
      ▼
FastAPI Backend
      │
      ▼
Generate Query Embedding
      │
      ▼
Qdrant Vector Database
      │
      ▼
Retrieve Relevant Notes
      │
      ▼
Build Context
      │
      ▼
Groq LLM
      │
      ▼
Generate Final Answer
      │
      ▼
Return Response to User