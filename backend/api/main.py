from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.tutor_engine import tutor_engine
from ai.recommendation_engine import recommendation_engine
from ai.knowledge_tracer import knowledge_tracer
from ai.spaced_repetition import spaced_repetition
from database.models import get_session, User

app = FastAPI(title="Study Hub AI 2.0", version="2.0.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    user_id: int
    question: str

class RateAnswerRequest(BaseModel):
    interaction_id: int
    helpful: bool

class ConceptProgressRequest(BaseModel):
    user_id: int
    concept: str
    correct: bool

class ReviewCompleteRequest(BaseModel):
    review_id: int
    quality: int

@app.get("/")
def root():
    return {"message": "Study Hub AI 2.0 is alive!", "status": "ready"}

@app.post("/api/tutor/ask")
async def ask_tutor(request: AskRequest):
    response = await tutor_engine.ask(request.user_id, request.question)
    return {"question": request.question, "answer": response}

@app.post("/api/tutor/rate")
async def rate_answer(request: RateAnswerRequest):
    session = get_session()
    interaction = session.query(UserInteraction).filter(UserInteraction.id == request.interaction_id).first()
    if interaction:
        interaction.was_helpful = request.helpful
        session.commit()
    return {"success": True}

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: int):
    recs = recommendation_engine.get_personalized_recommendations(user_id)
    return {"recommendations": recs}

@app.get("/api/weaknesses/{user_id}")
async def get_weaknesses(user_id: int):
    weaknesses = knowledge_tracer.get_weaknesses(user_id)
    due = knowledge_tracer.get_due_concepts(user_id)
    return {"weaknesses": weaknesses, "due_reviews": due}

@app.post("/api/knowledge/update")
async def update_knowledge(request: ConceptProgressRequest):
    mastery = knowledge_tracer.update_mastery(request.user_id, request.concept, request.correct)
    return {"mastery": mastery}

@app.get("/api/reviews/today/{user_id}")
async def get_today_reviews(user_id: int):
    reviews = spaced_repetition.get_today_reviews(user_id)
    return {"reviews": reviews}

@app.post("/api/reviews/complete")
async def complete_review(request: ReviewCompleteRequest):
    success = spaced_repetition.complete_review(request.review_id, request.quality)
    return {"success": success}

@app.get("/api/study-plan/{user_id}")
async def get_study_plan(user_id: int):
    plan = knowledge_tracer.generate_study_plan(user_id)
    return {"plan": plan}

@app.get("/api/health")
def health():
    return {"status": "healthy", "services": ["tutor", "recommendations", "knowledge_tracer", "spaced_repetition"]}