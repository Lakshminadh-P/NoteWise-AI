# NoteWise AI

**Intelligent Learning Platform** — Upload PDFs, auto-generate flashcards & quizzes with AI, track mastery with SM-2 spaced repetition.

## Quick Start

```bash
# 1. Clone & configure
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and a random JWT_SECRET_KEY

# 2. Start services
docker-compose up -d

# 3. Run database migrations
cd backend
pip install -r requirements.txt
alembic upgrade head

# 4. Start backend (dev)
uvicorn app.main:app --reload

# 5. Start frontend (dev)
cd ../frontend
npm install
npm run dev
```

## Architecture

- **Frontend**: React + Vite + React Router
- **Backend**: Python / FastAPI / SQLAlchemy (async)
- **Database**: PostgreSQL
- **AI**: Google Gemini API
- **Algorithm**: SM-2 Spaced Repetition

## API Docs

Once the backend is running: [http://localhost:8000/docs](http://localhost:8000/docs)
