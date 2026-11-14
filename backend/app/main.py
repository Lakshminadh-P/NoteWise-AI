from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, documents, flashcards, quizzes, dashboard

app = FastAPI(
    title="NoteWise AI",
    description="Intelligent Learning Platform with AI-powered study material generation and spaced repetition",
    version="0.1.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["Flashcards"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "NoteWise AI"}
