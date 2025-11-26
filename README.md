# LLM API Core

A FastAPI-based REST API service for interacting with Large Language Models (LLMs) using OpenAI. This project provides an API endpoint to send prompts to ChatGPT models and store the conversation history in a PostgreSQL database.

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

## 🎯 About the Project

LLM API Core is a scalable FastAPI application that provides a RESTful API for interacting with OpenAI's ChatGPT models. It stores conversation history in a PostgreSQL database, allowing you to track and manage all interactions with the LLM.

### Key Components

- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI Integration**: Seamless connection to ChatGPT models
- **PostgreSQL**: Persistent storage for conversation history
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management

## ✨ Features

- ✅ Send prompts to ChatGPT models via REST API
- ✅ Automatic conversation history storage
- ✅ PostgreSQL database integration
- ✅ Docker support for easy deployment
- ✅ Environment-based configuration
- ✅ Type-safe API with Pydantic schemas
- ✅ Error handling and validation

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
cd llm-api-core
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
docker run --name llm-postgres \
  -e POSTGRES_DB=llm_api_db \
  -e POSTGRES_USER=llm_user \
  -e POSTGRES_PASSWORD=llm_password_123 \
  -p 5432:5432 \
  -d postgres
```

#### Option B: Local PostgreSQL Installation

1. Install PostgreSQL on your system
2. Create a new database:
```sql
CREATE DATABASE llm_api_db;
CREATE USER llm_user WITH PASSWORD 'llm_password_123';
GRANT ALL PRIVILEGES ON DATABASE llm_api_db TO llm_user;
```

### Step 5: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Database Configuration
DB_NAME=llm_api_db
DB_USERNAME=llm_user
DB_PASSWORD=llm_password_123
DB_HOST=localhost

# Application Configuration
SECRET_KEY=your-secret-key-here-change-in-production
APP_ENV=dev

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
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
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model to use | No | `gpt-4o-mini` |

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

### Customization

You can customize these URLs or disable them:

```python
# Change URLs
app = FastAPI(
    docs_url="/api-docs",           # Custom Swagger URL
    redoc_url="/documentation",      # Custom ReDoc URL
    openapi_url="/api-schema.json",  # Custom schema URL
)

# Disable in production
app = FastAPI(
    docs_url=None,      # Disable Swagger UI
    redoc_url=None,     # Disable ReDoc
    openapi_url=None,   # Disable OpenAPI schema
)
```

**Note**: FastAPI automatically generates this documentation based on your code - no additional libraries needed! It reads your type hints, Pydantic models, and docstrings to create comprehensive API docs.

### Endpoints

#### POST `/api/v1/llm/`

Send a message to the LLM and save the conversation.

**Request Body:**
```json
{
  "prompt": "Hello, how are you?"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt": "Hello, how are you?",
  "response": "Hello! I'm doing well, thank you for asking..."
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8080/api/v1/llm/" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Python?"}'
```

**Example with Python:**
```python
import requests

url = "http://localhost:8080/api/v1/llm/"
data = {"prompt": "What is Python?"}
response = requests.post(url, json=data)
print(response.json())
```

## 📁 Project Structure

```
llm-api-core/
├── app.py                 # FastAPI application entry point
├── config.py              # Application configuration (Settings)
├── database.py            # SQLAlchemy database configuration
├── dependencies.py        # Shared dependencies (get_db)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── local.yml              # Docker Compose configuration
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
│
├── core/                  # Main application modules
│   └── llm/               # LLM module
│       ├── __init__.py
│       ├── models.py      # SQLAlchemy models (LLMMessage)
│       ├── routes.py      # API routes/endpoints
│       ├── schema.py      # Pydantic schemas (LLMRequest, LLMRecord)
│       ├── service.py     # OpenAI service (LLMService)
│       └── dependency.py  # Module-specific dependencies
│
└── test/                  # Test modules
    └── llm/               # Test LLM module
```

## 🐳 Docker Deployment

### Building the Docker Image

```bash
docker build -t llm-api-core .
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

3. **Port Already in Use**
   - Change port in `app.py` or use `--port` flag with uvicorn
   - Stop other services using port 8080

4. **Module Not Found**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## 📧 Contact

For questions, suggestions, or collaboration opportunities, feel free to reach out:

- **LinkedIn**: [Jasiel Salvador Hernandez Gonzalez](https://www.linkedin.com/in/jasiel-salvador-hernandez-gonzalez/)# rag-search-api
# rag-search-api
