# NeuroPlan AI: The Intelligence Engine for Study Execution

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

NeuroPlan AI is a production-grade, adaptive study execution agent designed to transform how students and professionals approach learning. By combining **Cognitive Science (1-3-7 Spacing)** with a **Proprietary Fine-Tuned LLaMA-3.1 Model** and **Deep Knowledge Tracing (DKT)**, NeuroPlan optimizes your schedule in real-time based on your actual performance.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=NeuroPlan+AI+Dashboard+Preview)

## 🚀 Key Features

*   **🧠 Proprietary AI Engine**: Powered by a custom-trained GGUF LLaMA-3.1-8B-Instruct model fine-tuned on a massive synthetic dataset for precision educational planning.
*   **📐 1-3-7 Spacing Algorithm**: Automated multi-phase revision scheduling (Study → Day 1 → Day 3 → Day 7) to ensure maximum retention.
*   **📊 Deep Knowledge Tracing (DKT)**: Real-time analysis of your mastery levels, using historical performance to predict future outcomes and adjust dynamically.
*   **📈 Advanced Analytics Engine**: Deep-dive into your study bio-metrics, including Cognitive Load distribution and Neural Efficiency curves.
*   **🧪 Adaptive Test Simulation**: Take AI-powered assessments that dynamically update your knowledge levels and automatically reschedule missed concepts.
*   **⚡ Elastic Rescheduler**: Life happens. Our rescheduler intelligently redistributes missed tasks into future low-density windows without breaking your momentum.
*   **🍦 Glassmorphism UI**: A premium, high-performance interface built with React, Tailwind CSS, Framer Motion, and Recharts.

## 🛠️ Technology Stack

### Backend
*   **FastAPI**: High-performance Python framework for building APIs.
*   **PostgreSQL**: Relational database for persistent neural records.
*   **SQLAlchemy 2.0 / Alembic**: Advanced ORM and migration handling.
*   **Redis**: Caching and background task orchestration.
*   **Pydantic V2**: Strict data validation and settings management.

### ML & AI 
*   **Custom GGUF Model**: LLaMA-3.1-8B fine-tuned locally using QLoRA.
*   **Deep Knowledge Tracing**: PyTorch-based neural networks predicting knowledge state.
*   **Hugging Face Spaces**: Serverless model deployment for cloud inference.

### Frontend
*   **React 18 / Vite**: Modern, fast frontend development environment.
*   **Zustand**: Lightweight, high-performance state management.
*   **Tailwind CSS & Framer Motion**: Professional utility-first styling with smooth micro-animations and custom glassmorphism tokens.
*   **Recharts**: Interactive, data-driven visualizations.

## 🏗️ Getting Started

### Prerequisites
*   [Docker & Docker Compose](https://docs.docker.com/get-docker/)
*   Node.js 18+ (for local frontend dev)
*   Python 3.10+ (for local backend/ML dev)
*   (Optional) Groq API Key or Hugging Face Space URL for the LLM backend

### 1. Environment Setup (Cloud LLM Configuration)

To run the project, you must connect the backend to your deployed AI model. Copy the environment template and configure it to point to your Hugging Face Space.

```bash
cd backend
cp .env.example .env
```

Open `backend/.env` and ensure the AI configuration points to your Hugging Face API:
```env
USE_CUSTOM_AI=true
CUSTOM_AI_URL="https://naman0313-neuroplan-api.hf.space/v1"
CUSTOM_AI_MODEL="neuroplan-model-final.gguf"
```
*(Make sure to update the database credentials and `SECRET_KEY` as well).*

### 2. Direct Launch (Docker - Recommended)

The entire ecosystem (Postgres, Redis, Backend) is containerized for instant deployment. We use a `Makefile` for convenience.

```bash
# Clone the repository
git clone https://github.com/Naman09746/NeuroPlan-AI.git
cd NeuroPlan-AI

# Build and start all services
make build
make up

# Run database migrations
make migrate-run
```

Access the API documentation at `http://localhost:8000/docs`.

### 3. Local Development (Frontend)

The frontend is run separately from Docker in development mode for HMR (Hot Module Replacement).

```bash
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:5173`.

## 📐 System Architecture

NeuroPlan follows a strict **Service Layer Pattern**:
1.  **Models**: Clean SQLAlchemy definitions with PostgreSQL constraints.
2.  **Schemas**: Pydantic models for data validation and API documentation.
3.  **Services**: Decoupled business logic (Scheduler, Generator, Tracker).
4.  **Endpoints**: Thin routers for API delivery.
5.  **ML Pipeline**: Isolated in the `ml/` directory, contains pipelines for synthetic data generation, QLoRA fine-tuning, and Deep Knowledge Tracing evaluation.

## 🤝 Contributing

Contributions are welcome! Please check out our issues to see what we're working on.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Built with Precision by [Naman Joshi](https://github.com/Naman09746) & the NeuroPlan Team.**
