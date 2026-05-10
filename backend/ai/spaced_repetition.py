from datetime import datetime, timedelta
import math
from database.models import get_session, ReviewSession

class SpacedRepetitionSystem:
    def __init__(self):
        self.session = get_session()
        # SM-2 algorithm parameters
        self.ease_factors = {}
        self.interval_days = {}
    
    def schedule_review(self, user_id, concept, quality_score):
        """
        quality_score: 0-5 (0 = forgot, 5 = perfect)
        """
        session = self.session.query(ReviewSession).filter(
            ReviewSession.user_id == user_id,
            ReviewSession.concept == concept,
            ReviewSession.completed_date.isnot(None)
        ).order_by(ReviewSession.scheduled_date.desc()).first()
        
        if not session:
            # First time studying this concept
            repetitions = 0
            ease_factor = 2.5
            interval = 1
        else:
            repetitions = self._get_repetition_count(user_id, concept)
            ease_factor = self.ease_factors.get(f"{user_id}_{concept}", 2.5)
            
            # Update ease factor based on quality
            ease_factor = ease_factor + (0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02))
            ease_factor = max(1.3, min(2.5, ease_factor))
            self.ease_factors[f"{user_id}_{concept}"] = ease_factor
            
            # Calculate next interval
            if quality_score >= 3:
                if repetitions == 1:
                    interval = 1
                elif repetitions == 2:
                    interval = 6
                else:
                    interval = math.ceil(self.interval_days.get(f"{user_id}_{concept}", 1) * ease_factor)
            else:
                interval = 1
                repetitions = 0
        
        self.interval_days[f"{user_id}_{concept}"] = interval
        
        # Schedule next review
        new_session = ReviewSession(
            user_id=user_id,
            concept=concept,
            scheduled_date=datetime.utcnow() + timedelta(days=interval),
            completed_date=None,
            performance_score=quality_score
        )
        self.session.add(new_session)
        self.session.commit()
        
        return interval
    
    def _get_repetition_count(self, user_id, concept):
        count = self.session.query(ReviewSession).filter(
            ReviewSession.user_id == user_id,
            ReviewSession.concept == concept,
            ReviewSession.completed_date.isnot(None)
        ).count()
        return count
    
    def get_today_reviews(self, user_id):
        reviews = self.session.query(ReviewSession).filter(
            ReviewSession.user_id == user_id,
            ReviewSession.scheduled_date <= datetime.utcnow(),
            ReviewSession.completed_date.is_(None)
        ).all()
        
        return [{
            'id': r.id,
            'concept': r.concept,
            'scheduled_date': r.scheduled_date.strftime('%Y-%m-%d')
        } for r in reviews]
    
    def complete_review(self, review_id, quality_score):
        review = self.session.query(ReviewSession).filter(ReviewSession.id == review_id).first()
        if review:
            review.completed_date = datetime.utcnow()
            review.performance_score = quality_score
            self.session.commit()
            return True
        return False

spaced_repetition = SpacedRepetitionSystem()