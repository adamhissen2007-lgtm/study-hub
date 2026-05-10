from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import math
import json

class AnalyticsEngine:
    """محرك التحليل المتقدم لتتبع أداء الطالب وسجل الأمان"""
    
    def __init__(self):
        self.sentiment_keywords = {
            'positive': ['ممتاز', 'رائع', 'فهمت', 'حلو', 'شكراً', 'جميل', 'أحسنت', 'great', 'excellent', 'good', 'perfect'],
            'negative': ['صعب', 'مش فاهم', 'صعبة', 'ضغط', 'تعبان', 'زعلان', 'صعوبة', 'hard', 'difficult', 'confused', 'stressed'],
            'neutral': ['ok', 'عادي', 'حسناً', 'تمام', 'fine']
        }
        
        self.anomaly_thresholds = {
            'login_failures': 5,      # أكثر من 5 محاولات فاشلة في الساعة
            'rapid_actions': 30,       # أكثر من 30 إجراء في الدقيقة
            'cheating_score': 85       # أكثر من 85% تشابه في الإجابات
        }
    
    # ==================== 1. خوارزمية تحليل المشاعر ====================
    
    def analyze_sentiment(self, text: str) -> dict:
        """تحليل مشاعر الطالب من النص"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = 'neutral'
            score = 50
        else:
            sentiment = 'positive' if positive_count > negative_count else 'negative'
            score = int((positive_count / total) * 100) if positive_count > negative_count else int((negative_count / total) * 100)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'emoji': '😊' if sentiment == 'positive' else '😞' if sentiment == 'negative' else '😐',
            'advice': self._get_sentiment_advice(sentiment, score)
        }
    
    def _get_sentiment_advice(self, sentiment: str, score: int) -> str:
        if sentiment == 'positive':
            return "🌟 ممتاز! استمر بهذه الطاقة الإيجابية"
        elif sentiment == 'negative':
            if score > 70:
                return "😔 تشعر بضغط؟ خذ استراحة قصيرة وجرب تمارين التنفس"
            return "💪 لا تيأس! كل صعوبة تمر هي خطوة نحو النجاح"
        return "📚 استمر في التعلم، كل يوم هو فرصة جديدة"
    
    # ==================== 2. خوارزمية التنبؤ بالأداء ====================
    
    def predict_performance_trend(self, user_data: list) -> dict:
        """توقع أداء الطالب خلال الأيام القادمة"""
        if len(user_data) < 5:
            return {'can_predict': False, 'message': 'بيانات غير كافية للتوقع'}
        
        # استخراج نقاط الأداء
        points = [d.get('points', 0) for d in user_data]
        days = list(range(len(points)))
        
        # حساب الاتجاه (Simple Linear Regression)
        n = len(points)
        sum_x = sum(days)
        sum_y = sum(points)
        sum_xy = sum(days[i] * points[i] for i in range(n))
        sum_x2 = sum(x**2 for x in days)
        
        if (n * sum_x2 - sum_x**2) != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        else:
            slope = 0
        
        # توقع بعد 7 أيام
        future_day = n + 6
        predicted_points = points[-1] + slope * 7
        
        # حساب الثقة
        confidence = 95 if abs(slope) > 5 else 70 if abs(slope) > 2 else 50
        confidence = min(95, confidence)
        
        trend = 'up' if slope > 2 else 'down' if slope < -2 else 'stable'
        
        return {
            'can_predict': True,
            'predicted_points': max(0, int(predicted_points)),
            'trend': trend,
            'confidence': confidence,
            'slope': round(slope, 2),
            'advice': self._get_performance_advice(trend, predicted_points)
        }
    
    def _get_performance_advice(self, trend: str, predicted: int) -> str:
        if trend == 'up':
            return f"🎉 ممتاز! من المتوقع وصولك لـ {predicted} نقطة خلال أسبوع. استمر!"
        elif trend == 'down':
            return f"⚠️ نلاحظ انخفاضاً في أدائك. خصص وقتاً إضافياً يومياً للمذاكرة"
        return f"📊 أداؤك مستقر. لتحسينه، حاول إضافة ساعة مذاكرة يومياً"
    
    # ==================== 3. كشف الشذوذ الأمني ====================
    
    def detect_anomalies(self, user_id: int, user_logs: list) -> dict:
        """كشف السلوكيات غير الطبيعية في سجل الأمان"""
        anomalies = []
        
        # تحليل محاولات الدخول الفاشلة
        login_failures = [log for log in user_logs if 'LOGIN_FAIL' in log.get('type', '')]
        if len(login_failures) > self.anomaly_thresholds['login_failures']:
            anomalies.append({
                'type': 'suspicious_login',
                'severity': 'high',
                'message': f'⚠️ {len(login_failures)} محاولة دخول فاشلة في الساعة الأخيرة',
                'action': '🔐 يرجى تغيير كلمة المرور'
            })
        
        # تحليل الإجراءات السريعة
        recent_actions = [log for log in user_logs if log.get('created_at', datetime.min) > datetime.now() - timedelta(minutes=1)]
        if len(recent_actions) > self.anomaly_thresholds['rapid_actions']:
            anomalies.append({
                'type': 'rapid_actions',
                'severity': 'medium',
                'message': f'⚡ {len(recent_actions)} إجراء في دقيقة واحدة (غير طبيعي)',
                'action': '🐢 تم تقييد السرعة مؤقتاً'
            })
        
        # تحليل محاولات الغش
        cheating_attempts = [log for log in user_logs if 'CHEATING_ATTEMPT' in log.get('type', '')]
        if cheating_attempts:
            anomalies.append({
                'type': 'cheating_attempt',
                'severity': 'high',
                'message': f'🚫 تم اكتشاف {len(cheating_attempts)} محاولة غش',
                'action': '📚 الإجابة الصحيحة هي من فهمك الشخصي'
            })
        
        return {
            'has_anomalies': len(anomalies) > 0,
            'anomalies': anomalies,
            'risk_score': min(100, len(anomalies) * 30),
            'recommendations': [a['action'] for a in anomalies]
        }
    
    # ==================== 4. لوحة حرارة الأمان ====================
    
    def generate_security_heatmap(self, logs: list) -> dict:
        """توليد بيانات لوحة حرارة الأمان"""
        hourly_data = defaultdict(int)
        type_data = defaultdict(int)
        
        for log in logs:
            hour = log.get('created_at', datetime.now()).hour
            hourly_data[hour] += 1
            type_data[log.get('type', 'other')] += 1
        
        # تحديد أوقات الذروة
        peak_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # تحديد أكثر أنواع الأحداث
        top_events = sorted(type_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'hourly_activity': [{'hour': h, 'count': c} for h, c in hourly_data.items()],
            'peak_hours': [{'hour': h, 'count': c} for h, c in peak_hours],
            'event_distribution': [{'type': t, 'count': c} for t, c in top_events],
            'total_events': len(logs)
        }
    
    # ==================== 5. تحليل نمط التعلم ====================
    
    def analyze_learning_pattern(self, interactions: list) -> dict:
        """تحليل نمط تعلم الطالب (وقت ذروة التركيز، المواد المفضلة)"""
        if not interactions:
            return {'has_data': False, 'message': 'لا توجد بيانات كافية'}
        
        # أفضل وقت للمذاكرة
        hour_success = defaultdict(list)
        for inter in interactions:
            hour = inter.get('created_at', datetime.now()).hour
            success = 1 if inter.get('correct', False) else 0
            hour_success[hour].append(success)
        
        best_hour = max(hour_success.items(), key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)
        
        # المواد الأكثر تفاعلاً
        subject_counts = defaultdict(int)
        for inter in interactions:
            subject_counts[inter.get('subject', 'general')] += 1
        
        top_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # حساب نسبة التركيز
        focus_score = sum(inter.get('focus_score', 50) for inter in interactions) / len(interactions) if interactions else 50
        
        return {
            'has_data': True,
            'best_study_hour': best_hour[0],
            'best_hour_efficiency': round(sum(best_hour[1]) / len(best_hour[1]) * 100, 1) if best_hour[1] else 0,
            'favorite_subjects': [{'subject': s, 'count': c} for s, c in top_subjects],
            'focus_score': round(focus_score, 1),
            'study_streak': self._calculate_streak(interactions),
            'recommended_schedule': self._generate_study_schedule(best_hour[0])
        }
    
    def _calculate_streak(self, interactions: list) -> int:
        """حساب سلسلة الأيام المتتالية"""
        if not interactions:
            return 0
        
        dates = sorted(set(inter.get('created_at', datetime.now()).date() for inter in interactions))
        streak = 1
        current = dates[0]
        
        for date in dates[1:]:
            if (date - current).days == 1:
                streak += 1
            else:
                break
            current = date
        
        return streak
    
    def _generate_study_schedule(self, best_hour: int) -> dict:
        """توليد جدول دراسة مخصص"""
        return {
            'optimal_time': f'{best_hour}:00 - {best_hour+2}:00',
            'sessions': [
                {'time': f'{best_hour}:00', 'activity': '🎯 أفضل وقت للمذاكرة العميقة'},
                {'time': f'{best_hour+2}:00', 'activity': '☕ استراحة قصيرة'},
                {'time': f'{best_hour+3}:00', 'activity': '📝 مراجعة وتمارين'},
                {'time': f'{best_hour+5}:00', 'activity': '🧠 حل اختبارات قصيرة'}
            ]
        }

analytics_engine = AnalyticsEngine()