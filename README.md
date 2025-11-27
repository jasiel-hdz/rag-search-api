# RAG Search API

A FastAPI-based REST API service for Retrieval Augmented Generation (RAG) using OpenAI, ChromaDB, and PostgreSQL. This project allows you to upload documents, generate embeddings, and perform semantic search with AI-powered responses.

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🎯 About the Project

RAG Search API is a scalable FastAPI application that implements Retrieval Augmented Generation (RAG) for semantic document search. It allows users to:

- Upload documents (.txt, .pdf)
- Automatically chunk and generate embeddings
- Perform semantic search using vector similarity
- Generate AI-powered responses based on document context

### Key Components

- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI Integration**: For generating embeddings and LLM responses
- **ChromaDB**: Vector database for storing and searching embeddings
- **PostgreSQL**: Persistent storage for documents and metadata
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management

## ✨ Features

- ✅ Upload and process documents (.txt, .pdf)
- ✅ Automatic text chunking and embedding generation
- ✅ Vector-based semantic search using ChromaDB
- ✅ RAG (Retrieval Augmented Generation) with OpenAI
- ✅ PostgreSQL database integration for metadata
- ✅ File validation and error handling
- ✅ Docker support for easy deployment
- ✅ Environment-based configuration
- ✅ Type-safe API with Pydantic schemas
- ✅ Automatic API documentation with Swagger UI

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** (Python 3.12 recommended)
- **PostgreSQL 12+** (or use Docker)
- **Docker** and **Docker Compose** (optional, for containerized deployment)
- **Git** (for cloning the repository)
- **OpenAI API Key** (get it from [OpenAI Platform](https://platform.openai.com/api-keys))

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd rag-search-api
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

#### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL container
docker run --name rag-postgres \
  -e POSTGRES_DB=rag_search_db \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=rag_password_123 \
  -p 5432:5432 \
  -d postgres
```

#### Option B: Local PostgreSQL Installation

1. Install PostgreSQL on your system
2. Create a new database:
```sql
CREATE DATABASE rag_search_db;
CREATE USER rag_user WITH PASSWORD 'rag_password_123';
GRANT ALL PRIVILEGES ON DATABASE rag_search_db TO rag_user;
```

### Step 5: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Database Configuration
DB_NAME=rag_search_db
DB_USERNAME=rag_user
DB_PASSWORD=rag_password_123
DB_HOST=localhost

# Application Configuration
SECRET_KEY=your-secret-key-here-change-in-production
APP_ENV=dev

# Media and Data Directories
MEDIA_ROOT=media
UPLOAD_DIR=media/raw
DATA_ROOT=data
CHROMA_DB_PATH=data/chroma_db

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB Configuration
CHROMA_COLLECTION_NAME=documents

# RAG Configuration
RAG_N_RESULTS=5
```

**Important**: 
- Replace `your-secret-key-here-change-in-production` with a secure random string
- Replace `sk-your-openai-api-key-here` with your actual OpenAI API key
- If using Docker for PostgreSQL, set `DB_HOST=postgres` (service name)

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_NAME` | PostgreSQL database name | Yes | - |
| `DB_USERNAME` | PostgreSQL username | Yes | - |
| `DB_PASSWORD` | PostgreSQL password | Yes | - |
| `DB_HOST` | PostgreSQL host | Yes | - |
| `SECRET_KEY` | Secret key for application | Yes | - |
| `APP_ENV` | Environment (dev/prod) | No | `dev` |
| `MEDIA_ROOT` | Root directory for media files | No | `media` |
| `UPLOAD_DIR` | Directory for uploaded files | No | `media/raw` |
| `DATA_ROOT` | Root directory for data files | No | `data` |
| `CHROMA_DB_PATH` | Path to ChromaDB database | No | `data/chroma_db` |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model for LLM | No | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | OpenAI model for embeddings | No | `text-embedding-3-small` |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name | No | `documents` |
| `RAG_N_RESULTS` | Number of chunks to retrieve in RAG search | No | `5` |

### Environment Files

- `.env` - Development environment (default)
- `.env.prod` - Production environment (when `APP_ENV=prod`)

## 🏃 Running the Project

### Option 1: Run Locally (Development)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python3 app.py
```

The API will be available at: `http://localhost:8080`

### Option 2: Run with Docker Compose

```bash
# Build and start all services
docker-compose -f local.yml up --build

# Run in detached mode (background)
docker-compose -f local.yml up -d --build

# View logs
docker-compose -f local.yml logs -f

# Stop services
docker-compose -f local.yml down

# Stop and remove volumes
docker-compose -f local.yml down -v
```

### Option 3: Run with Uvicorn Directly

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

## 📚 API Documentation

FastAPI **automatically generates interactive API documentation** - you don't need to install anything extra! This is similar to Django REST Framework's browsable API, but even better.

### Documentation URLs Explained

In `app.py`, we configure three documentation endpoints:

```python
app = FastAPI(
    docs_url="/docs",           # Swagger UI - Interactive API documentation
    redoc_url="/redoc",         # ReDoc - Alternative API documentation
    openapi_url="/openapi.json", # OpenAPI schema JSON
)
```

**Line-by-line explanation:**

1. **`docs_url="/docs"`** - Defines the URL where Swagger UI will be available
   - Default: `/docs`
   - Set to `None` to disable Swagger UI
   - This is the interactive documentation where you can test endpoints directly

2. **`redoc_url="/redoc"`** - Defines the URL where ReDoc will be available
   - Default: `/redoc`
   - Set to `None` to disable ReDoc
   - Alternative documentation interface with a cleaner, more readable design

3. **`openapi_url="/openapi.json"`** - Defines the URL for the OpenAPI schema JSON
   - Default: `/openapi.json`
   - Set to `None` to disable the OpenAPI schema
   - Machine-readable API specification that can be imported into Postman, Insomnia, etc.

### Accessing the Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI)**: `http://localhost:8080/docs`
  - Try out endpoints directly in the browser
  - See request/response schemas
  - Test API calls without writing code
  - Similar to Django REST Framework's browsable API
  
- **Alternative API Docs (ReDoc)**: `http://localhost:8080/redoc`
  - Beautiful, clean documentation interface
  - Great for sharing with team members
  - More readable for non-technical users
  
- **OpenAPI Schema (JSON)**: `http://localhost:8080/openapi.json`
  - Machine-readable API specification
  - Can be imported into Postman, Insomnia, or other API tools
  - Used by code generators and API testing tools

### Visual Structure

```
http://localhost:8080/
├── /docs          ← Swagger UI (interactive, test endpoints here)
├── /redoc         ← ReDoc (clean, beautiful documentation)
└── /openapi.json  ← OpenAPI JSON schema (for external tools)
```

**Note**: FastAPI automatically generates this documentation based on your code - no additional libraries needed! It reads your type hints, Pydantic models, and docstrings to create comprehensive API docs.

### Endpoints

#### POST `/api/v1/documents/upload`

Upload a document (.txt or .pdf) for processing and embedding generation.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload (form field name: `file`)

**Response (201 Created):**
```json
{
  "message": "Document 'example.txt' uploaded successfully",
  "document_id": 1,
  "filename": "example.txt",
  "chunks": 5
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8080/api/v1/documents/upload" \
  -F "file=@example.txt"
```

**Example with Python:**
```python
import requests

url = "http://localhost:8080/api/v1/documents/upload"
with open("example.txt", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

#### POST `/api/v1/rag/search`

Perform RAG (Retrieval Augmented Generation) search on uploaded documents.

**Request Body:**
```json
{
  "query": "What are the main advantages of FastAPI?",
  "document_id": null
}
```

**Response (200 OK):**
```json
{
  "query": "What are the main advantages of FastAPI?",
  "chunks_found": 5,
  "chunks": [
    {
      "chunk_id": 1,
      "document_id": 1,
      "text": "FastAPI is a modern framework...",
      "score": 0.95,
      "metadata": {
        "chunk_id": 1,
        "document_id": 1,
        "text": "FastAPI is a modern..."
      }
    }
  ],
  "response": "Based on the documents, FastAPI's main advantages include...",
  "context_used": "[Chunk 1 - Document 1]:\n..."
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8080/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FastAPI?"}'
```

**Example with Python:**
```python
import requests

url = "http://localhost:8080/api/v1/rag/search"
data = {
    "query": "What are the main advantages of FastAPI?",
    "document_id": None  # Optional: filter by document ID
}
response = requests.post(url, json=data)
print(response.json())
```

## 📁 Project Structure

```
rag-search-api/
├── app.py                 # FastAPI application entry point
├── config.py              # Application configuration (Settings)
├── database.py            # SQLAlchemy database configuration
├── dependencies.py        # Shared dependencies (get_db, get_services)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── local.yml              # Docker Compose configuration
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
│
├── core/                  # Main application modules
│   ├── documents/         # Document management module
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models (Document, Chunk)
│   │   ├── routes.py      # API routes for document upload
│   │   ├── services.py    # Document processing service
│   │   └── schema.py      # Pydantic schemas
│   │
│   ├── rag/               # RAG search module
│   │   ├── __init__.py
│   │   ├── routes.py      # API routes for RAG search
│   │   ├── services.py    # RAG service (search + generation)
│   │   └── schema.py      # Pydantic schemas (RAGQueryRequest, etc.)
│   │
│   ├── vector/            # Vector search module
│   │   ├── __init__.py
│   │   └── service.py     # ChromaDB vector service
│   │
│   ├── llm/               # LLM module
│   │   ├── __init__.py
│   │   └── services.py    # OpenAI LLM service
│   │
│   └── utils.py           # Utility functions (file validators)
│
├── data/                  # Data directory (not in git)
│   └── chroma_db/         # ChromaDB vector database
│
├── media/                  # Media directory (not in git)
│   └── raw/                # Uploaded documents
│
└── test/                  # Test modules
    └── ...
```

## 🐳 Docker Deployment

### Building the Docker Image

```bash
docker build -t rag-search-api .
```

### Running with Docker Compose

The `local.yml` file defines two services:

1. **app**: The FastAPI application
2. **postgres**: PostgreSQL database

To start both services:

```bash
docker-compose -f local.yml up --build
```

### Environment Variables in Docker

Docker Compose reads environment variables from:
1. `.env` file in the project root
2. System environment variables

Make sure your `.env` file contains all required variables before running Docker Compose.

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **OpenAI API Key Error**
   - Verify `OPENAI_API_KEY` is set in `.env`
   - Check API key is valid and has credits

3. **ChromaDB Initialization Error**
   - Ensure `CHROMA_DB_PATH` directory exists or can be created
   - Check write permissions for the data directory

4. **File Upload Error**
   - Verify `UPLOAD_DIR` exists and is writable
   - Check file size limits
   - Ensure file extension is .txt or .pdf

5. **Port Already in Use**
   - Change port in `app.py` or use `--port` flag with uvicorn
   - Stop other services using port 8080

6. **Module Not Found**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

7. **python-multipart Error**
   - Install python-multipart: `pip install python-multipart`
   - Required for file uploads in FastAPI

## 📖 How RAG Works

### Overview

RAG (Retrieval Augmented Generation) combines vector search with LLM generation:

1. **Document Upload**: User uploads a document (.txt or .pdf)
2. **Chunking**: Document is split into smaller chunks (500 characters each)
3. **Embedding Generation**: Each chunk is converted to a vector embedding using OpenAI
4. **Storage**: Embeddings are stored in ChromaDB, metadata in PostgreSQL
5. **Search**: User queries are converted to embeddings and matched against stored chunks
6. **Generation**: Most relevant chunks are sent to OpenAI LLM as context
7. **Response**: LLM generates a response based on the retrieved context

### Flow Diagram

```
User Query
    ↓
Convert to Embedding (OpenAI)
    ↓
Search Similar Chunks (ChromaDB)
    ↓
Retrieve Top N Chunks
    ↓
Build Context from Chunks
    ↓
Send Context + Query to LLM (OpenAI)
    ↓
Generate Response
    ↓
Return Response + Chunks
```

## 📧 Contact

For questions, suggestions, or collaboration opportunities, feel free to reach out:

- **LinkedIn**: [Jasiel Salvador Hernandez Gonzalez](https://www.linkedin.com/in/jasiel-salvador-hernandez-gonzalez/)

## 📄 License

This project is open source and available under the MIT License.
