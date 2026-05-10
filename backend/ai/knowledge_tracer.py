import numpy as np
from datetime import datetime, timedelta
from database.models import get_session, User, KnowledgeTrace, UserInteraction

class KnowledgeTracer:
    def __init__(self):
        self.session = get_session()
    
    def update_mastery(self, user_id, concept, correct, difficulty=2):
        trace = self.session.query(KnowledgeTrace).filter(
            KnowledgeTrace.user_id == user_id,
            KnowledgeTrace.concept == concept
        ).first()
        
        if not trace:
            trace = KnowledgeTrace(
                user_id=user_id,
                concept=concept,
                mastery_level=0,
                times_practiced=0
            )
            self.session.add(trace)
        
        # Bayesian Knowledge Tracing update
        # Simple model: mastery increases with correct answers, decreases slightly with wrong
        if correct:
            trace.mastery_level = min(1.0, trace.mastery_level + 0.1 * (1 - trace.mastery_level))
        else:
            trace.mastery_level = max(0, trace.mastery_level - 0.05)
        
        trace.times_practiced += 1
        trace.last_practiced = datetime.utcnow()
        
        # Spaced repetition: next review based on mastery level
        days_until_review = self._calculate_review_interval(trace.mastery_level)
        trace.next_review_date = datetime.utcnow() + timedelta(days=days_until_review)
        
        self.session.commit()
        return trace.mastery_level
    
    def _calculate_review_interval(self, mastery):
        if mastery < 0.3:
            return 1
        elif mastery < 0.5:
            return 3
        elif mastery < 0.7:
            return 7
        elif mastery < 0.85:
            return 14
        else:
            return 30
    
    def get_due_concepts(self, user_id, limit=5):
        due = self.session.query(KnowledgeTrace).filter(
            KnowledgeTrace.user_id == user_id,
            KnowledgeTrace.next_review_date <= datetime.utcnow(),
            KnowledgeTrace.mastery_level < 0.85
        ).order_by(KnowledgeTrace.next_review_date).limit(limit).all()
        
        return [{'concept': t.concept, 'mastery': t.mastery_level} for t in due]
    
    def get_weaknesses(self, user_id, limit=3):
        traces = self.session.query(KnowledgeTrace).filter(
            KnowledgeTrace.user_id == user_id
        ).order_by(KnowledgeTrace.mastery_level).limit(limit).all()
        
        return [{'concept': t.concept, 'mastery': t.mastery_level} for t in traces]
    
    def generate_study_plan(self, user_id, hours_per_day=2):
        weaknesses = self.get_weaknesses(user_id, limit=3)
        due_concepts = self.get_due_concepts(user_id, limit=3)
        
        plan = []
        
        for w in weaknesses:
            if w['mastery'] < 0.5:
                plan.append({
                    'concept': w['concept'],
                    'action': 'تعلم جديد',
                    'estimated_hours': 2,
                    'priority': 'high'
                })
        
        for d in due_concepts:
            plan.append({
                'concept': d['concept'],
                'action': 'مراجعة',
                'estimated_hours': 1,
                'priority': 'medium'
            })
        
        return plan[:int(hours_per_day)]

knowledge_tracer = KnowledgeTracer()