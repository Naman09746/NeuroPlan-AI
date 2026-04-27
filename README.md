# NeuroPlan AI: The Intelligence Engine for Study Execution

NeuroPlan AI is a production-grade, adaptive study execution agent designed to transform how students and professionals approach learning. By combining **Cognitive Science (1-3-7 Spacing)** with **Machine Learning patterns**, NeuroPlan optimizes your schedule in real-time based on your actual performance.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=NeuroPlan+AI+Dashboard+Preview)

## 🚀 Key Features

*   **🧠 Neural Mastery Loop**: Define your curriculum nodes (Subjects & Topics) and let our engine calculate the optimal spacing for maximum retention.
*   **📐 1-3-7 Spacing Algorithm**: Automated multi-phase revision scheduling (Study → Day 1 → Day 3 → Day 7).
*   **📈 Advanced Analytics Engine**: Deep-dive into your study bio-metrics, including Cognitive Load distribution and Neural Efficiency curves.
*   **🧪 Adaptive Test Simulation**: Take AI-powered assessments that dynamically update your knowledge levels and automatically reschedule missed concepts.
*   **⚡ Elastic Rescheduler**: Life happens. Our rescheduler intelligently redistributes missed tasks into future low-density windows without breaking your momentum.
*   **🍦 Glassmorphism UI**: A premium, high-performance interface built with React, Tailwind CSS, and Recharts.

## 🛠️ Technology Stack

### Backend
*   **FastAPI**: High-performance Python framework for building APIs.
*   **PostgreSQL**: Relational database for persistent neural records.
*   **SQLAlchemy 2.0 / Alembic**: Advanced ORM and migration handling.
*   **Redis**: Caching and background task orchestration.
*   **Pydantic V2**: Strict data validation and settings management.

### Frontend
*   **React 18 / Vite**: Modern, fast frontend development environment.
*   **Zustand**: Lightweight, high-performance state management.
*   **Tailwind CSS**: Professional utility-first styling with custom glassmorphism tokens.
*   **Recharts**: Interactive, data-driven visualizations.
*   **Axios**: Centralized API client with interceptors for JWT security.

## 🏗️ Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Node.js 18+ (for local frontend dev)
*   Python 3.10+ (for local backend dev)

### Direct Launch (Docker)
The entire ecosystem is containerized for instant deployment.

```bash
# Clone the repository
git clone https://github.com/your-repo/neuroplan-ai.git
cd neuroplan-ai

# Launch the engine
docker compose up -d
```

Access the application at `http://localhost:5173`.

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📐 System Architecture

NeuroPlan follows a strict **Service Layer Pattern**:
1.  **Models**: Clean SQLAlchemy definitions with PostgreSQL constraints.
2.  **Schemas**: Pydantic models for data validation and API documentation.
3.  **Services**: Decoupled business logic (Scheduler, Generator, Tracker).
4.  **Endpoints**: Thin routers for API delivery.

---

**Built with Precision by the NeuroPlan Team.**
