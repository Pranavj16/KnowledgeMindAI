# KnowledgeMind AI · Enterprise RAG Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.7-092E20?style=for-the-badge&logo=django&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Neon](https://img.shields.io/badge/Neon-PostgreSQL-00E599?style=for-the-badge&logo=postgresql&logoColor=black)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?style=for-the-badge&logo=googlecloud&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6600?style=for-the-badge&logo=databricks&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

🌐 **Live Demo:** [https://knowledge-mind-ai-jmeu.vercel.app/](https://knowledge-mind-ai-jmeu.vercel.app/)

**KnowledgeMind AI** is an end-to-end Retrieval-Augmented Generation (RAG) platform built with **Django**, **Neon PostgreSQL**, **ChromaDB**, **Sentence Transformers**, and **Google Gemini 2.5 Flash**. It allows users to create workspaces, upload PDF documents, extract knowledge chunks, store embeddings in a vector database, and perform context-aware AI conversations with citation tracking and query history analytics.

---

## 🏛️ System Architecture Diagram

```mermaid
graph TD
    subgraph Client ["Client Interface"]
        UI["Web UI / Workspace Dashboard<br>(Django Templates + TailwindCSS)"]
    end

    subgraph ServerlessBackend ["Vercel Serverless Platform"]
        WSGI["WSGI Handler (api/index.py)"]
        Router["URL Routing & Middleware"]
        Auth["User Auth & Session Control"]
        KBEngine["Knowledge Base Controller"]
        ChatEngine["RAG Retrieval & Chat Engine"]
    end

    subgraph DataPipeline ["Ingestion & Embeddings"]
        PyPDF["PyPDF Parser"]
        Chunker["Semantic Text Chunker"]
        Embedder["Google Gemini / Sentence Transformers"]
    end

    subgraph ExternalServices ["External Cloud Services"]
        NeonDB[("Neon Serverless PostgreSQL<br>(Users, Sessions, Docs, Chat)")]
        GeminiAPI["Google Gemini 2.5 Flash API<br>(Context Generation)"]
        ChromaStore[("ChromaDB Vector Store<br>(Embeddings & Semantic Search)")]
    end

    UI --> WSGI
    WSGI --> Router
    Router --> Auth
    Router --> KBEngine
    Router --> ChatEngine

    Auth -->|Persistent State| NeonDB
    KBEngine -->|Ingest PDF| PyPDF
    PyPDF --> Chunker
    Chunker --> Embedder
    Embedder -->|Store Vectors| ChromaStore
    KBEngine -->|Save Metadata| NeonDB

    ChatEngine -->|Similarity Search| ChromaStore
    ChromaStore -->|Top Relevant Chunks| ChatEngine
    ChatEngine -->|Prompt + Evidence Context| GeminiAPI
    GeminiAPI -->|Grounded Answer| ChatEngine
    ChatEngine -->|Save History| NeonDB
    ChatEngine -->|Stream Response + Citations| UI
```

### High-Level Flow

```
[ User Uploads PDF ] ──► [ PyPDF Text Extraction ] ──► [ Semantic Chunking ]
                                                               │
                                                               ▼
[ Grounded Answer ] ◄── [ Gemini 2.5 Flash ] ◄── [ Vector Retrieval ] ◄── [ Embeddings ]
```

1. **Document Ingestion**: PDF files uploaded by authenticated users are parsed using `PyPDF` and split into semantically coherent context chunks.
2. **Vector Indexing**: Chunks are processed via embeddings into a persistent `ChromaDB` collection with cosine similarity indexing.
3. **Retrieval-Augmented Generation**: User queries are embedded, matched against relevant vector chunks in `ChromaDB`, and passed with source evidence to **Google Gemini 2.5 Flash**.
4. **Relational Management**: User authentication, account sessions, uploaded document metadata, and conversation logs are persisted in **Neon Serverless PostgreSQL**.

---

## ✨ Key Features

- 🔐 **Multi-User Authentication**: Secure sign up, login, case-insensitive email matching, session handling, and protected workspaces.
- 📄 **PDF Document Processing**: Automatic text extraction, chunking, and chunk exploration.
- 🎯 **Semantic Vector Search**: High-performance semantic similarity retrieval powered by ChromaDB.
- 🤖 **Context-Aware AI Chatbot**: Grounded Gemini 2.5 Flash responses accompanied by exact source snippet references and citations.
- 📊 **Workspace Dashboard & Analytics**: Track uploaded knowledge bases, total chunks, queries, and conversation history.
- ⚡ **Vercel Serverless Ready**: Optimized WSGI serverless lambda entrypoint with instant cold-start handling.
- 🐘 **Neon Serverless PostgreSQL**: Centralized, scalable cloud database with connection pooling and SSL encryption.

---

## 🔒 Security & Environment Configuration

> [!IMPORTANT]
> - Never commit `.env` or sensitive API keys to GitHub.
> - `.env` is locked and protected inside `.gitignore`.
> - Always use a safe template like `.env.example` when sharing or configuring new environments.

---

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Pranavj16/KnowledgeMindAI.git
cd KnowledgeMindAI
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Inside `.env`:
```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Django Secret Key
SECRET_KEY=django-insecure-local-dev-key

# Debug Mode (True for development)
DEBUG=True
ALLOWED_HOSTS=*

# Optional: Neon PostgreSQL Connection String (uses SQLite fallback if left empty)
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Run the Test Suite
```bash
python manage.py test accounts
```

### 7. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## ⚡ Deployment on Vercel (with Neon PostgreSQL)

KnowledgeMind AI is pre-configured for deployment on **Vercel Serverless Functions** (`vercel.json` & `api/index.py`) backed by **Neon PostgreSQL**.

### Step 1: Create a Database on Neon
1. Go to [Neon.tech](https://neon.tech) and create a free project.
2. Copy your **PostgreSQL Connection String**:
   ```text
   postgresql://neondb_owner:YOUR_PASSWORD@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Deploy to Vercel
1. Push your repository to [GitHub](https://github.com/Pranavj16/KnowledgeMindAI).
2. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** ──► **Project**.
3. Import the `KnowledgeMindAI` repository.
4. Under **Settings** ──► **Environment Variables**, add:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `DATABASE_URL` | `postgresql://neondb_owner:...@ep-...neon.tech/neondb?sslmode=require` | Neon PostgreSQL connection string |
   | `GEMINI_API_KEY` | `AIzaSy...` | Your Google Gemini API Key |
   | `SECRET_KEY` | *(A random secure 50+ character string)* | Django cryptographic signing key |
   | `DEBUG` | `False` | Disables debug mode in production |
5. Click **Deploy**. Vercel will build and launch your application globally!

---

## 🛠️ Tech Stack

- **Web Framework**: [Django 6.0.7](https://www.djangoproject.com/)
- **Hosting Platform**: [Vercel Serverless Functions](https://vercel.com/)
- **Relational Database**: [Neon Serverless PostgreSQL](https://neon.tech/) (`dj-database-url`, `psycopg2-binary`)
- **LLM Engine**: [Google Gemini 2.5 Flash](https://ai.google.dev/) (`google-genai` SDK)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Document Processing**: [PyPDF](https://pypdf.readthedocs.io/)
- **Styling**: [TailwindCSS](https://tailwindcss.com/)

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
