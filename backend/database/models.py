from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON, Table, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json
import numpy as np

Base = declarative_base()

# ==================== الجداول الأساسية ====================

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(120), unique=True)
    password_hash = Column(String(200))
    level = Column(Integer, default=1)
    points = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    learning_style = Column(String(20), default='visual')
    preferred_difficulty = Column(Integer, default=2)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    learning_path = Column(JSON, default=list)
    
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    knowledge_traces = relationship("KnowledgeTrace", back_populates="user", cascade="all, delete-orphan")
    review_sessions = relationship("ReviewSession", back_populates="user", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    description = Column(Text)
    subject = Column(String(50))
    difficulty = Column(Integer, default=2)
    estimated_hours = Column(Integer, default=10)
    prerequisites = Column(JSON, default=list)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(200))
    content = Column(Text)
    video_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    order = Column(Integer, default=0)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="lessons")
    questions = relationship("Question", back_populates="lesson", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=True)
    text = Column(Text)
    question_type = Column(String(20))
    options = Column(JSON, nullable=True)
    correct_answer = Column(Text)
    explanation = Column(Text, nullable=True)
    difficulty = Column(Integer, default=2)
    subject = Column(String(50))
    intent = Column(String(30))
    embedding = Column(Text, nullable=True)
    times_asked = Column(Integer, default=0)
    times_answered_correctly = Column(Integer, default=0)
    
    lesson = relationship("Lesson", back_populates="questions")

class UserInteraction(Base):
    __tablename__ = 'user_interactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=True)
    question_text = Column(Text)
    user_answer = Column(Text, nullable=True)
    ai_response = Column(Text)
    intent = Column(String(30))
    was_helpful = Column(Boolean, default=True)
    response_time_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interactions")

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    score = Column(Float, default=0)
    max_score = Column(Float, default=100)
    time_spent_seconds = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    answers = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="assessments")
    course = relationship("Course", back_populates="assessments")

class KnowledgeTrace(Base):
    __tablename__ = 'knowledge_traces'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    concept = Column(String(100))
    mastery_level = Column(Float, default=0)
    times_practiced = Column(Integer, default=0)
    last_practiced = Column(DateTime, default=datetime.utcnow)
    next_review_date = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="knowledge_traces")

class Concept(Base):
    __tablename__ = 'concepts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    prerequisites = Column(JSON, default=list)
    dependents = Column(JSON, default=list)
    difficulty = Column(Integer, default=2)

class ReviewSession(Base):
    __tablename__ = 'review_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    concept = Column(String(100))
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime, nullable=True)
    performance_score = Column(Integer, default=0)
    
    user = relationship("User", back_populates="review_sessions")

# ==================== دوال مساعدة ====================

def init_db():
    engine = create_engine('sqlite:///studyhub_ai.db', echo=True)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()