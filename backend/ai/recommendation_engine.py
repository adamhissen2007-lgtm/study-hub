import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func
from database.models import get_session, User, Course, Concept, KnowledgeTrace, UserInteraction

class RecommendationEngine:
    def __init__(self):
        self.session = get_session()
    
    def get_personalized_recommendations(self, user_id, limit=5):
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        recommendations = []
        
        # 1. بناءً على نقاط الضعف
        for weakness in user.weaknesses:
            courses = self.session.query(Course).filter(
                Course.subject == weakness,
                Course.difficulty <= user.preferred_difficulty + 1
            ).limit(2).all()
            for course in courses:
                recommendations.append({
                    'type': 'course',
                    'id': course.id,
                    'title': course.title,
                    'reason': f'لتحسين مستواك في {weakness}',
                    'confidence': 0.85
                })
        
        # 2. بناءً على المفاهيم التي حان وقت مراجعتها
        old_concepts = self.session.query(KnowledgeTrace).filter(
            KnowledgeTrace.user_id == user_id,
            KnowledgeTrace.next_review_date <= datetime.utcnow(),
            KnowledgeTrace.mastery_level < 0.8
        ).limit(3).all()
        
        for trace in old_concepts:
            recommendations.append({
                'type': 'review',
                'concept': trace.concept,
                'reason': f'حان وقت مراجعة {trace.concept} (الإتقان: {trace.mastery_level*100:.0f}%)',
                'confidence': 0.9
            })
        
        # 3. بناءً على مواضيع رائجة بين الطلاب المتميزين
        top_students = self.session.query(User).filter(User.level >= 5).limit(10).all()
        top_student_ids = [s.id for s in top_students]
        
        popular_courses = self.session.query(Course).join(Assessment).filter(
            Assessment.user_id.in_(top_student_ids),
            Assessment.score >= 80
        ).group_by(Course.id).order_by(func.count(Course.id).desc()).limit(3).all()
        
        for course in popular_courses:
            if course.id not in [r.get('id') for r in recommendations if r.get('type') == 'course']:
                recommendations.append({
                    'type': 'course',
                    'id': course.id,
                    'title': course.title,
                    'reason': f'موصى به من قبل الطلاب المتميزين',
                    'confidence': 0.75
                })
        
        return recommendations[:limit]
    
    def get_similar_questions(self, question_text, limit=3):
        # Simple keyword-based similarity (will upgrade to embeddings later)
        keywords = question_text.lower().split()
        all_questions = self.session.query(Question).all()
        
        scored = []
        for q in all_questions:
            score = sum(1 for kw in keywords if kw in q.text.lower())
            if score > 0:
                scored.append((q, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [q for q, _ in scored[:limit]]

recommendation_engine = RecommendationEngine()