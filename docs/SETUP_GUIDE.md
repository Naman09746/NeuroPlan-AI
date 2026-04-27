# NeuroPlan AI: Full Setup & Testing Guide

This guide will walk you through the initialization and testing process for the NeuroPlan AI ecosystem.

---

## 💻 Local Development Setup (SQLite — Zero Install)

> **Prerequisites**: Python 3.12+, Node.js 18+ (via nvm)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (skip if already exists)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (creates neuroplan.db automatically)
PYTHONPATH=. ./venv/bin/alembic upgrade head

# Start server
PYTHONPATH=. ./venv/bin/uvicorn app.main:app --reload
```
Wait for: `Uvicorn running on http://127.0.0.1:8000`

### 2. Frontend Setup (New Terminal Tab)

```bash
cd frontend

# Load nvm (if node/npm are not in PATH)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

# Install dependencies
npm install

# Start dev server
npm run dev
```
Wait for: `Local: http://localhost:5173/`

### 3. Access the Application
- **Dashboard**: http://localhost:5173
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing the Complete Pipeline

To ensure the system is operating at 100% efficiency, follow this test protocol:

### Step 1: Authentication Flow
- Go to `http://localhost:5173/register`.
- Create an account with name, email, and password.
- You should be automatically redirected to the **Empty Dashboard** ("Your Mind is a Blank Slate").

### Step 2: Curriculum Ingestion
- Navigate to the **Curriculum** tab (sidebar).
- Add a subject (e.g., "Deep Learning") with a custom color.
- In the "Quick Add Topics" text area, paste:
    ```text
    Neural Networks
    Backpropagation
    Transformer Architecture
    Attention Mechanisms
    ```
- Click **Bulk Ingest**. Verify the topics appear in the list.

### Step 3: Neural Plan Generation
- Navigate to **Study Plan** (sidebar).
- Enter a title, select a deadline (e.g., 2 weeks from now), and select your subjects.
- Click **Initialize Synthesis**.
- You will be redirected to the Dashboard where "Study" and "Revision" tasks should appear for today.

### Step 4: The Mastery Loop
- On the Dashboard, click the **⚡ Generate Deep Test** button.
- Complete the timed cognitive assessment (answer all questions).
- Click **Finalize Synchronization** to submit results.
- Check the **Analytics** tab. Your "Phase Mastery" and "Neural Efficiency" charts should reflect the new data.

### Step 5: Task Execution
- On the Dashboard, toggle tasks to **done** by clicking the circle icon.
- Verify the progress percentage updates in real-time.

---

## 🛠️ Internal Sanity Checks (CLI)

Check the health of the API:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "app": "NeuroPlan AI"}
```

Verify all API routes are registered:
```bash
curl http://localhost:8000/docs
```

---

## 📦 Docker Launch (Production)

> Requires Docker Desktop installed.

```bash
docker compose up -d
```
- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## ⚙️ Environment Variables Reference

### Backend (`backend/.env`)
| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./neuroplan.db` | Database connection string |
| `SECRET_KEY` | (auto-generated) | JWT signing key |
| `OPENAI_API_KEY` | (optional) | For AI schedule optimization |

### Frontend (`frontend/.env`)
| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |
