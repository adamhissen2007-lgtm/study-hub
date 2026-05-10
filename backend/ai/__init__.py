# backend/ai/__init__.py

"""
Study Hub AI Engine - Ultimate Collection
أقوى محرك ذكاء اصطناعي متكامل
"""

from .analytics_engine import AnalyticsEngine
from .concept_graph import ConceptGraph
from .event_engine import EventEngine
from .intent_model import IntentModel
from .knowledge_tracer import KnowledgeTracer
from .notification_engine import NotificationEngine
from .recommendation_engine import RecommendationEngine
from .spaced_repetition import SpacedRepetition
from .tutor_engine import TutorEngine
from .vector_search_engine import VectorSearchEngine

# الملفات الجديدة
from .chatbot_engine import ChatbotEngine
from .nlp_processor import NLPProcessor
from .model_trainer import ModelTrainer
from .project_generator import ProjectGenerator

__all__ = [
    'AnalyticsEngine',
    'ConceptGraph', 
    'EventEngine',
    'IntentModel',
    'KnowledgeTracer',
    'NotificationEngine',
    'RecommendationEngine',
    'SpacedRepetition',
    'TutorEngine',
    'VectorSearchEngine',
    'ChatbotEngine',
    'NLPProcessor',
    'ModelTrainer',
    'ProjectGenerator'
]