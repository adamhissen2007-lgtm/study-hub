from datetime import datetime, timedelta
import json
import random
from flask import session, jsonify, render_template, redirect, request

# هنستخدم db والنماذج من الـ app بعد ما يتعرفوا
# هنستدعيهم من داخل الدوال عشان نتجنب الـ circular import

class FailureTracker:
    """النظام الذكي لتتبع الإخفاقات وإدارة الضغط الأكاديمي"""
    
    def __init__(self, user_id, db, User, Course, StudentPerformance, Notification):
        self.user_id = user_id
        self.db = db
        self.User = User
        self.Course = Course
        self.StudentPerformance = StudentPerformance
        self.Notification = Notification
        self.user = User.query.get(user_id)
    
    def get_endangered_courses(self):
        endangered = []
        performances = self.StudentPerformance.query.filter_by(user_id=self.user_id).order_by(self.StudentPerformance.date.desc()).limit(30).all()
        
        course_scores = {}
        for perf in performances:
            if perf.course_id not in course_scores:
                course_scores[perf.course_id] = []
            course_scores[perf.course_id].append(perf.points_earned)
        
        for course_id, scores in course_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            trend = scores[-1] - scores[0] if len(scores) > 1 else 0
            
            risk_level = 'high' if avg_score < 50 else 'medium' if avg_score < 65 else 'low'
            if risk_level in ['high', 'medium']:
                course = self.Course.query.get(course_id)
                if course:
                    endangered.append({
                        'id': course.id,
                        'name': course.name,
                        'current_score': round(avg_score, 1),
                        'trend': 'down' if trend < 0 else 'up',
                        'risk_level': risk_level,
                        'hours_needed': self.calculate_recovery_hours(avg_score)
                    })
        return endangered
    
    def calculate_recovery_hours(self, current_score):
        if current_score >= 70:
            return 0
        elif current_score >= 50:
            return int((70 - current_score) * 0.5)
        else:
            return int((70 - current_score) * 0.8) + 5
    
    def generate_rescue_plan(self, course_id):
        course = self.Course.query.get(course_id)
        if not course:
            return None
        
        endangered = self.get_endangered_courses()
        course_data = next((c for c in endangered if c['id'] == course_id), None)
        if not course_data:
            return None
        
        total_hours = course_data['hours_needed']
        days_to_deadline = random.randint(7, 21)
        
        plan = {
            'course_name': course.name,
            'current_score': course_data['current_score'],
            'target_score': min(100, course_data['current_score'] + 30),
            'total_hours_needed': total_hours,
            'days_remaining': days_to_deadline,
            'daily_hours_recommended': max(1, round(total_hours / max(1, days_to_deadline), 1)),
            'tasks': self.generate_recovery_tasks(course_id, total_hours, days_to_deadline),
            'priority_topics': ['الأساسيات', 'المسائل المتقدمة', 'النظريات']
        }
        return plan
    
    def generate_recovery_tasks(self, course_id, total_hours, days):
        tasks = []
        hours_per_day = max(1, total_hours // max(1, days))
        
        for i in range(min(7, days)):
            tasks.append({
                'day': i + 1,
                'hours': hours_per_day if i < days - 1 else total_hours - (hours_per_day * (days - 1)),
                'description': f'ذاكرة {hours_per_day} ساعات في المادة',
                'completed': False
            })
        return tasks
    
    def get_recovery_streak(self):
        recent_tasks = self.Notification.query.filter_by(
            user_id=self.user_id
        ).order_by(self.Notification.created_at.desc()).limit(14).all()
        
        streak = 0
        today = datetime.utcnow().date()
        
        for task in recent_tasks:
            task_date = task.created_at.date()
            if (today - task_date).days == streak:
                streak += 1
            else:
                break
        return streak
    
    def update_recovery_streak(self, completed=False):
        streak = self.get_recovery_streak()
        if completed:
            points_earned = 10 + (streak * 2)
            self.user.points += points_earned
            self.db.session.commit()
            return points_earned
        return 0
    
    def calculate_resilience_score(self):
        failures = self.StudentPerformance.query.filter(
            self.StudentPerformance.user_id == self.user_id,
            self.StudentPerformance.points_earned < 50
        ).count()
        
        recoveries = self.Notification.query.filter_by(
            user_id=self.user_id
        ).count()
        
        if failures == 0:
            return 100
        
        resilience = (recoveries / (failures + recoveries)) * 100
        return min(100, int(resilience))
    
    def find_accountability_partner(self, course_id):
        students = self.User.query.filter(
            self.User.id != self.user_id,
            self.User.major == self.user.major,
            self.User.university_year == self.user.university_year
        ).limit(10).all()
        
        for student in students:
            return {
                'id': student.id,
                'name': student.full_name,
                'course_risk': 'medium',
                'current_score': 55,
                'streak': 0
            }
        return None
    
    def get_error_heatmap(self, course_id):
        error_patterns = [
            {'type': 'أخطاء في الحسابات', 'percentage': random.randint(20, 40)},
            {'type': 'أخطاء في النظرية', 'percentage': random.randint(15, 35)},
            {'type': 'أخطاء في المنهجية', 'percentage': random.randint(10, 30)},
            {'type': 'أخطاء الوقت', 'percentage': random.randint(5, 25)}
        ]
        
        total = sum(e['percentage'] for e in error_patterns)
        for e in error_patterns:
            e['percentage'] = round(e['percentage'] / total * 100, 1)
        
        return error_patterns
    
    def analyze_failure_journal(self, entry_text):
        keywords = {
            'صعبة': 'المادة صعبة - حاول تقسمها لأجزاء صغيرة',
            'وقت': 'مشكلة في إدارة الوقت - استخدم تقنية بومودورو',
            'فهمت': 'تحتاج مراجعة أكثر - جرب شرح المعلومة لزميل',
            'نسيت': 'مشكلة في التذكر - استخدم البطاقات التعليمية',
            'تركيز': 'عزز بيئة مذاكرتك - ابعد المشتتات',
            'فشلت': 'الفشل جزء من التعلم - حدد بالضبط أين وقع الخطأ'
        }
        
        insights = []
        for key, advice in keywords.items():
            if key in entry_text.lower():
                insights.append(advice)
        
        if not insights:
            insights = ['استمر في المحاولة! حدد سبب التحدي وضّح أهدافك']
        
        positive_words = ['فهمت', 'عملت', 'نجحت', 'تعلمت', 'تقدمت']
        negative_words = ['صعب', 'فشلت', 'مش قادر', 'تعبت', 'ضغط']
        
        positive_count = sum(1 for w in positive_words if w in entry_text.lower())
        negative_count = sum(1 for w in negative_words if w in entry_text.lower())
        
        if positive_count > negative_count:
            emotion = 'positive'
        elif negative_count > positive_count:
            emotion = 'negative'
        else:
            emotion = 'neutral'
        
        return {
            'insights': insights,
            'emotional_score': emotion,
            'recommended_action': insights[0]
        }
    
    def get_mini_boss(self, course_id):
        bosses = [
            {'name': '🏰 مدير القواعد', 'difficulty': 'medium', 'xp_reward': 30, 'time_limit': 60},
            {'name': '🐉 تنين المسائل', 'difficulty': 'hard', 'xp_reward': 50, 'time_limit': 90},
            {'name': '🧙 ساحر النظريات', 'difficulty': 'easy', 'xp_reward': 15, 'time_limit': 30},
            {'name': '👑 ملك المراجعة', 'difficulty': 'hard', 'xp_reward': 60, 'time_limit': 120}
        ]
        
        course = self.Course.query.get(course_id)
        boss = random.choice(bosses)
        boss['course_name'] = course.name if course else 'المادة'
        return boss
    
    def get_failure_analytics(self):
        """تحليلات متقدمة للإخفاقات"""
        performances = self.StudentPerformance.query.filter_by(user_id=self.user_id).order_by(self.StudentPerformance.date).all()
        
        if len(performances) < 3:
            return None
        
        # حساب معدل التحسن
        recent_scores = [p.points_earned for p in performances[-5:]] if len(performances) >= 5 else [p.points_earned for p in performances]
        improvement_rate = recent_scores[-1] - recent_scores[0] if len(recent_scores) > 1 else 0
        
        # أكثر وقت فشل
        failures = [p for p in performances if p.points_earned < 50]
        failure_hours = {}
        for f in failures:
            hour = f.date.strftime('%A') if hasattr(f.date, 'strftime') else str(f.date)
            failure_hours[hour] = failure_hours.get(hour, 0) + 1
        
        worst_day = max(failure_hours.items(), key=lambda x: x[1])[0] if failure_hours else 'غير محدد'
        
        # المواد الأكثر فشلاً
        course_failures = {}
        for f in failures:
            if f.course_id:
                course_failures[f.course_id] = course_failures.get(f.course_id, 0) + 1
        
        worst_course_id = max(course_failures.items(), key=lambda x: x[1])[0] if course_failures else None
        worst_course = self.Course.query.get(worst_course_id) if worst_course_id else None
        
        return {
            'total_failures': len(failures),
            'improvement_rate': improvement_rate,
            'worst_day': worst_day,
            'worst_course': worst_course.name if worst_course else None,
            'recovery_rate': self.calculate_resilience_score(),
            'recommendation': self._get_recommendation(improvement_rate, len(failures))
        }
    
    def _get_recommendation(self, improvement_rate, failures_count):
        if improvement_rate > 0:
            return "✅ أداءك في تحسن مستمر! استمر على نفس المنهجية."
        elif failures_count > 10:
            return "⚠️ عدد الإخفاقات كبير. استخدم خطة الإنقاذ فوراً!"
        elif improvement_rate < -10:
            return "📉 الأداء في تراجع. حاول تغيير طريقة مذاكرتك."
        else:
            return "💪 أنت في الطريق الصحيح. استمر ولا تيأس!"


def register_failure_tracking_routes(app, db, User, Course, StudentPerformance, Notification, CareerTrack, Skill, UserSkill):
    """تسجيل مسارات نظام تتبع الإخفاق"""
    
    @app.route('/failure-tracker')
    def failure_tracker():
        if 'user_id' not in session:
            return redirect('/login')
        return render_template('failure_tracker.html')
    
    @app.route('/api/failure/endangered-courses')
    def api_endangered_courses():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        courses = tracker.get_endangered_courses()
        return jsonify(courses)
    
    @app.route('/api/failure/rescue-plan/<int:course_id>')
    def api_rescue_plan(course_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        plan = tracker.generate_rescue_plan(course_id)
        return jsonify(plan or {})
    
    @app.route('/api/failure/recovery-streak')
    def api_recovery_streak():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        streak = tracker.get_recovery_streak()
        resilience = tracker.calculate_resilience_score()
        return jsonify({'streak': streak, 'resilience': resilience})
    
    @app.route('/api/failure/accountability-partner/<int:course_id>')
    def api_accountability_partner(course_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        partner = tracker.find_accountability_partner(course_id)
        return jsonify(partner or {})
    
    @app.route('/api/failure/error-heatmap/<int:course_id>')
    def api_error_heatmap(course_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        heatmap = tracker.get_error_heatmap(course_id)
        return jsonify(heatmap)
    
    @app.route('/api/failure/analyze-journal', methods=['POST'])
    def api_analyze_journal():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        entry = data.get('entry', '')
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        analysis = tracker.analyze_failure_journal(entry)
        return jsonify(analysis)
    
    @app.route('/api/failure/mini-boss/<int:course_id>')
    def api_mini_boss(course_id):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        boss = tracker.get_mini_boss(course_id)
        return jsonify(boss)
    
    @app.route('/api/failure/complete-recovery', methods=['POST'])
    def api_complete_recovery():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        points = tracker.update_recovery_streak(completed=True)
        
        msg = Notification(
            user_id=session['user_id'],
            message=f'🎉 أحسنت! أكملت مهمة إنقاذ وحصلت على {points} نقطة! استمر 🔥'
        )
        db.session.add(msg)
        db.session.commit()
        
        return jsonify({'success': True, 'points_earned': points})
    
    @app.route('/api/failure/analytics')
    def api_failure_analytics():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        analytics = tracker.get_failure_analytics()
        return jsonify(analytics or {})
    
    @app.route('/api/failure/trends')
    def api_failure_trends():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        performances = StudentPerformance.query.filter_by(user_id=session['user_id']).order_by(StudentPerformance.date).limit(30).all()
        
        trends = {
            'labels': [],
            'scores': [],
            'moving_average': []
        }
        
        for perf in performances:
            trends['labels'].append(perf.date.strftime('%d/%m') if hasattr(perf.date, 'strftime') else str(perf.date))
            trends['scores'].append(perf.points_earned)
        
        # حساب المتوسط المتحرك
        window = 3
        for i in range(len(trends['scores'])):
            if i < window - 1:
                trends['moving_average'].append(None)
            else:
                avg = sum(trends['scores'][i-window+1:i+1]) / window
                trends['moving_average'].append(round(avg, 1))
        
        return jsonify(trends)
    
    @app.route('/api/failure/predict-risk')
    def api_predict_risk():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        tracker = FailureTracker(session['user_id'], db, User, Course, StudentPerformance, Notification)
        endangered = tracker.get_endangered_courses()
        
        # تحليل المخاطر المستقبلية
        high_risk_count = len([c for c in endangered if c['risk_level'] == 'high'])
        medium_risk_count = len([c for c in endangered if c['risk_level'] == 'medium'])
        
        if high_risk_count >= 2:
            risk_level = 'critical'
            message = '🚨 تحذير! أنت معرض لخطر الرسوب في مادتين أو أكثر. استخدم خطة الإنقاذ فوراً!'
        elif high_risk_count >= 1:
            risk_level = 'high' 
            message = '⚠️ خطر مرتفع! مادة واحدة تحتاج تركيزاً فورياً.'
        elif medium_risk_count >= 2:
            risk_level = 'medium'
            message = '📊 مستوى خطر متوسط. راجع المواد المهددة للإنقراض.'
        else:
            risk_level = 'low'
            message = '✅ مستوى خطر منخفض. استمر في المذاكرة المنتظمة.'
        
        return jsonify({
            'risk_level': risk_level,
            'message': message,
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'total_endangered': len(endangered)
        })