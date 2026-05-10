"""
Event-Driven Architecture Engine - النسخة الجبارة
نظام الأحداث الذكي الذي يجعل المنصة تتفاعل تلقائياً مع كل تصرفات الطالب
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import asyncio
import json
from collections import defaultdict
import threading
import queue

# ==================== أنواع الأحداث الجبارة ====================

class EventType(Enum):
    """أنواع الأحداث في المنصة"""
    # أحداث المستخدم
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_BANNED = "user_banned"
    
    # أحداث التعلم
    COURSE_STARTED = "course_started"
    COURSE_COMPLETED = "course_completed"
    LESSON_COMPLETED = "lesson_completed"
    QUIZ_PASSED = "quiz_passed"
    QUIZ_FAILED = "quiz_failed"
    EXERCISE_SOLVED = "exercise_solved"
    
    # أحداث الأداء
    LOW_SCORE_DETECTED = "low_score_detected"
    HIGH_SCORE_ACHIEVED = "high_score_achieved"
    STREAK_MILESTONE = "streak_milestone"
    POINTS_EARNED = "points_earned"
    LEVEL_UP = "level_up"
    
    # أحداث التفاعل
    POST_CREATED = "post_created"
    REPLY_POSTED = "reply_posted"
    LIKE_RECEIVED = "like_received"
    CONTENT_REPORTED = "content_reported"
    
    # أحداث الأمان
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    CHEATING_ATTEMPT = "cheating_attempt"
    ACCOUNT_COMPROMISED = "account_compromised"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # أحداث ذكية
    KNOWLEDGE_GAP_DETECTED = "knowledge_gap_detected"
    RECOMMENDATION_READY = "recommendation_ready"
    REVIEW_DUE = "review_due"
    STUDY_REMINDER = "study_reminder"

@dataclass
class Event:
    """كيان الحدث - يحمل كل المعلومات"""
    type: EventType
    user_id: int
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=عادي, 2=هام, 3=عاجل
    source: str = "system"
    event_id: str = None
    
    def __post_init__(self):
        if not self.event_id:
            import hashlib
            import time
            self.event_id = hashlib.md5(f"{self.user_id}{self.type.value}{time.time()}".encode()).hexdigest()[:16]

# ==================== معالج الأحداث (Event Handlers) ====================

class EventHandler:
    """معالج واحد لحدث محدد"""
    
    def __init__(self, name: str, handler_func: Callable, event_type: EventType, priority: int = 1):
        self.name = name
        self.handler_func = handler_func
        self.event_type = event_type
        self.priority = priority
        self.execution_count = 0
        self.last_execution = None
        self.avg_execution_time = 0
    
    async def execute(self, event: Event) -> Any:
        """تنفيذ المعالج"""
        start = datetime.utcnow()
        try:
            result = await self.handler_func(event)
            self.execution_count += 1
            self.last_execution = datetime.utcnow()
            execution_time = (datetime.utcnow() - start).total_seconds()
            self.avg_execution_time = (self.avg_execution_time * (self.execution_count - 1) + execution_time) / self.execution_count
            return result
        except Exception as e:
            print(f"❌ خطأ في المعالج {self.name}: {e}")
            return None

# ==================== Event Bus (العمود الفقري) ====================

class EventBus:
    """ناقل الأحداث المركزي - قلب النظام"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.event_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.event_history = []  # آخر 1000 حدث
        self.stats = {
            'total_events': 0,
            'processed_events': 0,
            'failed_events': 0,
            'avg_latency': 0
        }
        
        # تسجيل المعالجات الأساسية
        self._register_default_handlers()
    
    def register(self, event_type: EventType, handler_func: Callable, name: str = None, priority: int = 1):
        """تسجيل معالج جديد لحدث معين"""
        handler = EventHandler(
            name=name or handler_func.__name__,
            handler_func=handler_func,
            event_type=event_type,
            priority=priority
        )
        self.handlers[event_type].append(handler)
        # ترتيب حسب الأولوية
        self.handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        print(f"✅ تم تسجيل معالج {handler.name} للحدث {event_type.value}")
    
    def emit(self, event: Event):
        """إصدار حدث (غير متزامن)"""
        self.event_queue.put(event)
        self.stats['total_events'] += 1
        
        # حفظ في السجل
        self.event_history.append({
            'event_id': event.event_id,
            'type': event.type.value,
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'priority': event.priority
        })
        
        # الحفاظ على آخر 1000 حدث فقط
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
    
    async def emit_async(self, event: Event):
        """إصدار حدث مع انتظار المعالجة"""
        await self._process_event(event)
    
    async def _process_event(self, event: Event):
        """معالجة حدث واحد"""
        start_time = datetime.utcnow()
        
        handlers = self.handlers.get(event.type, [])
        if not handlers:
            return
        
        for handler in handlers:
            result = await handler.execute(event)
            if result == False:  # إذا أراد المعالج إيقاف السلسلة
                break
        
        latency = (datetime.utcnow() - start_time).total_seconds()
        self.stats['avg_latency'] = (self.stats['avg_latency'] * self.stats['processed_events'] + latency) / (self.stats['processed_events'] + 1)
        self.stats['processed_events'] += 1
    
    def _worker(self):
        """العامل الخلفي الذي يعالج الأحداث باستمرار"""
        while self.is_running:
            try:
                event = self.event_queue.get(timeout=1)
                asyncio.run(self._process_event(event))
            except queue.Empty:
                continue
            except Exception as e:
                self.stats['failed_events'] += 1
                print(f"❌ خطأ في معالجة الحدث: {e}")
    
    def start(self):
        """تشغيل ناقل الأحداث"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            print("🚀 Event Bus started successfully")
    
    def stop(self):
        """إيقاف ناقل الأحداث"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("🛑 Event Bus stopped")
    
    def get_stats(self) -> Dict:
        """إحصائيات أداء ناقل الأحداث"""
        return {
            'total_events': self.stats['total_events'],
            'processed_events': self.stats['processed_events'],
            'failed_events': self.stats['failed_events'],
            'avg_latency_ms': round(self.stats['avg_latency'] * 1000, 2),
            'active_handlers': sum(len(h) for h in self.handlers.values()),
            'queue_size': self.event_queue.qsize(),
            'recent_events': self.event_history[-10:]
        }
    
    def _register_default_handlers(self):
        """تسجيل المعالجات الافتراضية"""
        
        # 1. معالج مستوى المستخدم
        async def handle_level_up(event: Event):
            from database.models import User, Notification
            from app import db
            
            user = User.query.get(event.user_id)
            if user:
                # إضافة إشعار
                notif = Notification(
                    user_id=event.user_id,
                    message=f"🎉 مبروك! وصلت للمستوى {user.level}! استمر 🔥",
                    is_read=False
                )
                db.session.add(notif)
                db.session.commit()
                
                # إضافة شارة لو وصل لمستوى معين
                if user.level == 5:
                    await self.emit_async(Event(
                        type=EventType.POINTS_EARNED,
                        user_id=event.user_id,
                        data={'points': 100, 'reason': 'وصول للمستوى 5'},
                        timestamp=datetime.utcnow(),
                        priority=2
                    ))
        
        async def handle_streak_milestone(event: Event):
            from database.models import Notification
            from app import db
            
            streak = event.data.get('streak', 0)
            milestones = {7: 'أسبوع', 30: 'شهر', 100: 'مئة يوم'}
            
            if streak in milestones:
                notif = Notification(
                    user_id=event.user_id,
                    message=f"🔥 أسطورة! أكملت {milestones[streak]} من المذاكرة المتواصلة!",
                    is_read=False
                )
                db.session.add(notif)
                db.session.commit()
        
        async def handle_low_score(event: Event):
            from database.models import Notification
            from app import db
            
            score = event.data.get('score', 0)
            course = event.data.get('course_name', 'المادة')
            
            notif = Notification(
                user_id=event.user_id,
                message=f"⚠️ نلاحظ أن درجاتك في {course} منخفضة ({score}%). هل تحتاج مساعدة؟",
                is_read=False,
                link=f"/course/{event.data.get('course_id', '')}"
            )
            db.session.add(notif)
            db.session.commit()
        
        async def handle_suspicious_activity(event: Event):
            from database.models import SecurityLog
            from app import db
            
            log = SecurityLog(
                user_id=event.user_id,
                event_type='SUSPICIOUS_ACTIVITY',
                details=json.dumps(event.data),
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        
        async def handle_course_completed(event: Event):
            from database.models import Notification
            from app import db
            
            course_name = event.data.get('course_name', 'الكورس')
            
            notif = Notification(
                user_id=event.user_id,
                message=f"🏆 مبروك! أكملت {course_name} بنجاح! حصلت على 100 نقطة إضافية!",
                is_read=False
            )
            db.session.add(notif)
            db.session.commit()
        
        # تسجيل المعالجات
        self.register(EventType.LEVEL_UP, handle_level_up, "LevelUpHandler", priority=1)
        self.register(EventType.STREAK_MILESTONE, handle_streak_milestone, "StreakMilestoneHandler", priority=1)
        self.register(EventType.LOW_SCORE_DETECTED, handle_low_score, "LowScoreHandler", priority=2)
        self.register(EventType.SUSPICIOUS_ACTIVITY, handle_suspicious_activity, "SecurityHandler", priority=3)
        self.register(EventType.COURSE_COMPLETED, handle_course_completed, "CourseCompletionHandler", priority=1)

# ==================== كشف المعرفة الذكي ====================

class KnowledgeGapDetector:
    """يكشف الفجوات المعرفية قبل أن تصبح مشكلة"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.user_performance = defaultdict(lambda: {'correct': 0, 'total': 0, 'recent_scores': []})
    
    def record_answer(self, user_id: int, topic: str, correct: bool, score: int = None):
        """تسجيل إجابة الطالب"""
        key = f"{user_id}_{topic}"
        self.user_performance[key]['total'] += 1
        if correct:
            self.user_performance[key]['correct'] += 1
        
        if score:
            self.user_performance[key]['recent_scores'].append(score)
            if len(self.user_performance[key]['recent_scores']) > 10:
                self.user_performance[key]['recent_scores'] = self.user_performance[key]['recent_scores'][-10:]
        
        # التحقق من الفجوة المعرفية
        success_rate = self.user_performance[key]['correct'] / max(1, self.user_performance[key]['total'])
        if success_rate < 0.4 and self.user_performance[key]['total'] >= 5:
            self._emit_knowledge_gap(user_id, topic, success_rate)
    
    def _emit_knowledge_gap(self, user_id: int, topic: str, success_rate: float):
        """إصدار حدث بوجود فجوة معرفية"""
        event = Event(
            type=EventType.KNOWLEDGE_GAP_DETECTED,
            user_id=user_id,
            data={
                'topic': topic,
                'success_rate': success_rate,
                'recommended_resources': self._get_resources(topic)
            },
            timestamp=datetime.utcnow(),
            priority=2
        )
        self.event_bus.emit(event)
    
    def _get_resources(self, topic: str) -> List[str]:
        """الحصول على مصادر مقترحة للموضوع"""
        resources = {
            'binary_search': ['فيديو شرح Binary Search', 'تمارين تفاعلية', 'محاكاة مرئية'],
            'recursion': ['شرح العودية خطوة بخطوة', 'أمثلة عملية', 'تحديات عودية'],
            'oop': ['مقدمة في البرمجة الكائنية', 'مشروع صغير', 'أمثلة من الحياة الواقعية']
        }
        return resources.get(topic, ['مراجعة الأساسيات', 'تمارين إضافية'])

# ==================== محرك التوصيات ====================

class RecommendationEngine:
    """محرك التوصيات الذكي"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.user_interests = defaultdict(list)
    
    def track_interest(self, user_id: int, topic: str, interaction_type: str):
        """تتبع اهتمامات المستخدم"""
        self.user_interests[user_id].append({
            'topic': topic,
            'type': interaction_type,
            'timestamp': datetime.utcnow()
        })
        
        # إذا كان الاهتمام متكرراً، اصدر توصية
        topic_count = sum(1 for i in self.user_interests[user_id] if i['topic'] == topic and i['type'] == 'view')
        if topic_count >= 3:
            self._emit_recommendation(user_id, topic)
    
    def _emit_recommendation(self, user_id: int, topic: str):
        """إصدار توصية"""
        event = Event(
            type=EventType.RECOMMENDATION_READY,
            user_id=user_id,
            data={
                'topic': topic,
                'suggested_courses': [f'دورة متقدمة في {topic}', f'تمارين تدريبية في {topic}']
            },
            timestamp=datetime.utcnow(),
            priority=1
        )
        self.event_bus.emit(event)

# ==================== إدارة الأحداث ====================

event_bus = EventBus()
knowledge_gap_detector = KnowledgeGapDetector(event_bus)
recommendation_engine = RecommendationEngine(event_bus)

# بدء تشغيل الناقل
event_bus.start()