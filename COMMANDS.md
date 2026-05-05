# NeuroPlan AI: Complete Command Reference

This document provides a comprehensive list of all terminal commands needed to build, test, run, and manage the NeuroPlan AI project across all its micro-services. 

Use this file as a **dictionary** to quickly find the exact command you need. You do **not** need to run all of these to start the project.

## 🚀 Quick Start (The Only Commands You Need)

If you just want to start the project and get to work, choose ONE of the following methods:

### Option A: Using Docker (Requires Docker Desktop)
**1. Start the Backend & Database**
```bash
make build
make up
make migrate-run
```

### Option B: Local Setup (No Docker Required)
If you don't have Docker, you can run everything directly on your machine (using SQLite instead of Postgres).

**1. Start the Backend**
The easiest way is to use the provided startup script which handles environment setup, dependencies, and migrations automatically:
```bash
cd backend
./run_local.sh
```

---

### Start the Frontend (Required for both Option A and B)
In a **new terminal window**, start the user interface:
```bash
cd frontend
npm install
npm run dev
```

That's it! Everything below this point is just for your reference when you need to test, debug, or change specific things.

---

## 🛠️ Makefile Commands (Recommended)

The easiest way to interact with the project ecosystem is through the provided `Makefile`. These commands wrap Docker Compose and execute tasks automatically inside the containers.

| Command | Description |
| :--- | :--- |
| `make build` | Builds all Docker images (Backend, DB, Redis). |
| `make up` | Starts the entire application stack in detached mode. |
| `make down` | Stops and removes all containers and networks. |
| `make logs` | Follows the live logs from the backend container. |
| `make migrate-init` | Initializes Alembic for database migrations. |
| `make migrate-generate name="Update"` | Autogenerates a new migration revision based on SQLAlchemy model changes. |
| `make migrate-run` | Applies all pending migrations to the database (`upgrade head`). |
| `make test` | Runs the Pytest test suite inside the backend container. |
| `make clean` | Removes all Python cache files (`__pycache__`, `*.pyc`) from the directory. |

---

## 🐳 Docker Compose (Direct Usage)

If you prefer using Docker Compose directly instead of the Makefile:

```bash
# Build the containers
docker compose build

# Start the containers
docker compose up -d

# Stop the containers
docker compose down

# View logs for a specific service
docker compose logs -f backend
docker compose logs -f db
docker compose logs -f redis
```

---

## ☁️ Hugging Face Space AI Configuration

Since the custom model is hosted on a Hugging Face Space to act as a cloud backend (preventing local Out-Of-Memory errors), you must update your `.env` configuration before running the backend.

```bash
cd backend
cp .env.example .env
```

Open `.env` and set the following variables to point to your Space:
```env
USE_CUSTOM_AI=true
CUSTOM_AI_URL="https://naman0313-neuroplan-api.hf.space/v1"
CUSTOM_AI_MODEL="neuroplan-model-final.gguf"
```

---

## 🐍 Backend (Local Development without Docker)

If you are developing the FastAPI backend locally without Docker containers:

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install backend dependencies
pip install -r requirements.txt

# Run the FastAPI server locally with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run local Pytest suite
pytest test_api.py test_groq.py

# Run Alembic migrations locally
alembic upgrade head
```

---

## ⚛️ Frontend (Local Development)

The frontend is built with React and Vite. It is typically run locally to leverage Vite's fast Hot Module Replacement (HMR).

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server (runs on http://localhost:5173)
npm run dev

# Build the frontend for production
npm run build

# Preview the production build locally
npm run preview

# Run the ESLint linter
npm run lint
```

---

## 🤖 Machine Learning & AI

Commands for interacting with the custom ML pipelines, including Deep Knowledge Tracing and Model Fine-Tuning:

```bash
cd ml

# Install ML-specific dependencies
pip install -r requirements.txt

# Run the dataset upload script (if applicable)
chmod +x training/upload_dataset.sh
./training/upload_dataset.sh
```

---

## 🌐 API Testing (cURL Examples)

Once the backend is running (either via Docker on port `8000` or locally), you can test API connectivity. 

Access the full interactive Swagger UI documentation at: **`http://localhost:8000/docs`**

```bash
# Check if API is running (Healthcheck)
curl http://localhost:8000/

# Test the analytics endpoint (Ensure you have a valid JWT token if required)
curl http://localhost:8000/api/v1/analytics
```
