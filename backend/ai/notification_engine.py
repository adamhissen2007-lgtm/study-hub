from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class NotificationEngine:
    """نظام الإشعارات الذكي مع تجميع وتوقيت ذكي"""
    
    def __init__(self):
        self.notification_queue = defaultdict(list)
        self.user_preferences = {}
        self.notification_templates = {
            'security_alert': {
                'icon': '⚠️',
                'title': 'تنبيه أمني',
                'color': '#ef4444'
            },
            'achievement': {
                'icon': '🏆',
                'title': 'إنجاز جديد',
                'color': '#fbbf24'
            },
            'reminder': {
                'icon': '🔔',
                'title': 'تذكير',
                'color': '#10b981'
            },
            'milestone': {
                'icon': '🎯',
                'title': 'هدف محقق',
                'color': '#8b5cf6'
            },
            'warning': {
                'icon': '⚡',
                'title': 'تحذير',
                'color': '#f59e0b'
            }
        }
    
    def queue_notification(self, user_id: int, type: str, message: str, data: dict = None):
        """إضافة إشعار إلى قائمة الانتظار مع تجميع ذكي"""
        now = datetime.utcnow()
        
        # التحقق من وجود إشعار مشابه في آخر 5 دقائق
        for existing in self.notification_queue[user_id]:
            if existing['type'] == type and (now - existing['created_at']).seconds < 300:
                existing['count'] = existing.get('count', 1) + 1
                existing['last_message'] = message
                return
        
        self.notification_queue[user_id].append({
            'id': len(self.notification_queue[user_id]) + 1,
            'type': type,
            'message': message,
            'data': data or {},
            'created_at': now,
            'is_read': False,
            'count': 1
        })
        
        # إزالة الإشعارات القديمة (أكثر من 7 أيام)
        self.notification_queue[user_id] = [
            n for n in self.notification_queue[user_id] 
            if (now - n['created_at']).days < 7
        ]
    
    def get_user_notifications(self, user_id: int, limit: int = 20) -> list:
        """الحصول على إشعارات المستخدم مع تجميع المجموعات"""
        notifications = self.notification_queue.get(user_id, [])
        
        # تجميع الإشعارات المتشابهة
        grouped = []
        for n in notifications:
            template = self.notification_templates.get(n['type'], {})
            display_message = n['message']
            if n.get('count', 1) > 1:
                display_message = f"{n['message']} (+{n['count']-1} إشعارات مشابهة)"
            
            grouped.append({
                'id': n['id'],
                'icon': template.get('icon', '📢'),
                'title': template.get('title', 'إشعار'),
                'color': template.get('color', '#6366f1'),
                'message': display_message,
                'created_at': n['created_at'].isoformat(),
                'is_read': n['is_read'],
                'data': n['data']
            })
        
        return grouped[:limit]
    
    def mark_as_read(self, user_id: int, notification_id: int):
        """تحديد إشعار كمقروء"""
        for n in self.notification_queue.get(user_id, []):
            if n['id'] == notification_id:
                n['is_read'] = True
                return True
        return False
    
    def mark_all_read(self, user_id: int):
        """تحديد كل الإشعارات كمقروءة"""
        for n in self.notification_queue.get(user_id, []):
            n['is_read'] = True
    
    def get_unread_count(self, user_id: int) -> int:
        """عدد الإشعارات غير المقروءة"""
        return sum(1 for n in self.notification_queue.get(user_id, []) if not n['is_read'])
    
    def send_security_alert(self, user_id: int, severity: str, message: str, details: dict = None):
        """إرسال تنبيه أمني"""
        type = 'security_alert'
        icon = '🔴' if severity == 'high' else '🟡' if severity == 'medium' else '🔵'
        full_message = f"{icon} [{severity.upper()}] {message}"
        self.queue_notification(user_id, type, full_message, details)
    
    def send_achievement(self, user_id: int, achievement_name: str, points: int):
        """إرسال إشعار إنجاز جديد"""
        message = f"🎉 أنجزت '{achievement_name}' وحصلت على {points} نقطة!"
        self.queue_notification(user_id, 'achievement', message)
    
    def send_milestone(self, user_id: int, milestone: str, progress: int):
        """إرسال إشعار بإنجاز هدف"""
        message = f"🎯 حققت {progress}% من '{milestone}'! استمر 🔥"
        self.queue_notification(user_id, 'milestone', message)
    
    def send_study_reminder(self, user_id: int, subject: str):
        """إرسال تذكير للمذاكرة"""
        message = f"📚 حان وقت مذاكرة {subject}! خصص 30 دقيقة الآن"
        self.queue_notification(user_id, 'reminder', message)

notification_engine = NotificationEngine()