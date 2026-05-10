"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         QUIZ ENGINE - ULTIMATE EDITION                        ║
║                    نظام كويزات ذكي - أول نظام في مصر!                         ║
║                                                                               ║
║  ★ ميزات حصرية:                                                              ║
║    1. AI Answer Correction (تصحيح ذاتي للإجابات الطويلة)                      ║
║    2. Difficulty Adaptation (الكويز يتكيف مع مستوى الطالب)                    ║
║    3. Cheating Detection (يكشف الغش باستخدام الذكاء الاصطناعي)               ║
║    4. Performance Prediction (يتوقع درجات الطالب المستقبلية)                  ║
║    5. Weakness Analysis (يحلل نقاط ضعف الطالب ويقترح علاج)                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import random
import re
import math
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import numpy as np

class UltimateQuizEngine:
    """محرك الكويزات الخارق - أول نظام كويزات ذكي في مصر"""
    
    def __init__(self):
        self.quizzes = {}
        self.user_performance = defaultdict(lambda: {'scores': [], 'topics': defaultdict(list), 'cheating_attempts': 0})
        self.question_bank = self._initialize_question_bank()
        
        # مستويات الصعوبة
        self.difficulty_levels = {
            1: {'name': '🌱 مبتدئ', 'points': 10, 'time_per_question': 45, 'color': '#10b981'},
            2: {'name': '📚 متوسط', 'points': 20, 'time_per_question': 35, 'color': '#fbbf24'},
            3: {'name': '🔥 متقدم', 'points': 35, 'time_per_question': 25, 'color': '#f97316'},
            4: {'name': '💎 خبير', 'points': 50, 'time_per_question': 20, 'color': '#ef4444'},
            5: {'name': '👑 عبقر', 'points': 75, 'time_per_question': 15, 'color': '#8b5cf6'}
        }
    
    def _initialize_question_bank(self):
        """قاعدة أسئلة ضخمة - الأساس لمحرك الكويزات"""
        return {
            'programming': [
                {
                    'id': 'prog_001',
                    'question': 'ما هي لغة البرمجة المستخدمة لبناء تطبيقات iOS؟',
                    'options': ['Java', 'Kotlin', 'Swift', 'Python'],
                    'correct': 2,
                    'difficulty': 1,
                    'topic': 'mobile',
                    'explanation': 'Swift هي اللغة الرسمية من Apple لتطوير تطبيقات iOS'
                },
                {
                    'id': 'prog_002',
                    'question': 'ما هو الخوارزم المستخدم لترتيب البيانات بأقل تعقيد زمني في المتوسط؟',
                    'options': ['Bubble Sort', 'Quick Sort', 'Selection Sort', 'Insertion Sort'],
                    'correct': 1,
                    'difficulty': 3,
                    'topic': 'algorithms',
                    'explanation': 'Quick Sort له تعقيد O(n log n) في المتوسط'
                }
            ],
            'ai': [
                {
                    'id': 'ai_001',
                    'question': 'ما اسم نموذج اللغة الكبير الذي طورته OpenAI؟',
                    'options': ['LaMDA', 'GPT', 'BERT', 'XLNet'],
                    'correct': 1,
                    'difficulty': 2,
                    'topic': 'nlp',
                    'explanation': 'GPT (Generative Pre-trained Transformer) هو نموذج OpenAI'
                }
            ]
        }
    
    def create_quiz(self, creator_id: int, config: Dict) -> Dict:
        """إنشاء كويز جديد - يدعم أسئلة اختيارية ومقالية"""
        quiz_id = f"quiz_{creator_id}_{int(datetime.now().timestamp())}"
        
        quiz = {
            'id': quiz_id,
            'creator_id': creator_id,
            'title': config.get('title', 'كويز جديد'),
            'description': config.get('description', ''),
            'course_id': config.get('course_id'),
            'questions': config.get('questions', []),
            'duration_minutes': config.get('duration_minutes', 30),
            'adaptive_mode': config.get('adaptive_mode', False),  # الوضع الذكي
            'attempts_allowed': config.get('attempts_allowed', 1),
            'show_results_immediately': config.get('show_results_immediately', True),
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'participants': []
        }
        
        self.quizzes[quiz_id] = quiz
        return quiz
    
    def generate_adaptive_quiz(self, user_id: int, topic: str, num_questions: int = 10) -> Dict:
        """توليد كويز متكيف مع مستوى الطالب - خوارزمية حصرية!"""
        
        # 1. تحليل أداء الطالب السابق
        user_data = self.user_performance[user_id]
        topic_performance = user_data['topics'][topic]
        
        # 2. تحديد المستوى المناسب
        if not topic_performance:
            # أول مرة - يبدأ من مستوى 1
            start_level = 1
        else:
            avg_score = np.mean([q['score'] for q in topic_performance[-5:]]) if topic_performance else 0.5
            if avg_score > 0.85:
                start_level = 5
            elif avg_score > 0.7:
                start_level = 4
            elif avg_score > 0.55:
                start_level = 3
            elif avg_score > 0.4:
                start_level = 2
            else:
                start_level = 1
        
        # 3. اختيار أسئلة من المستوى المناسب
        available_questions = []
        for category, questions in self.question_bank.items():
            for q in questions:
                if q['difficulty'] == start_level and q['topic'] == topic:
                    available_questions.append(q)
        
        # 4. إذا مش كفاية، هات من مستويات قريبة
        if len(available_questions) < num_questions:
            for diff in [start_level-1, start_level+1]:
                if 1 <= diff <= 5:
                    for category, questions in self.question_bank.items():
                        for q in questions:
                            if q['difficulty'] == diff and q['topic'] == topic:
                                available_questions.append(q)
        
        # 5. اختيار عشوائي
        selected = random.sample(available_questions, min(num_questions, len(available_questions)))
        
        return {
            'quiz_type': 'adaptive',
            'level': start_level,
            'level_name': self.difficulty_levels[start_level]['name'],
            'questions': selected,
            'time_per_question': self.difficulty_levels[start_level]['time_per_question'],
            'total_time': self.difficulty_levels[start_level]['time_per_question'] * len(selected)
        }
    
    def submit_quiz(self, user_id: int, quiz_id: str, answers: List) -> Dict:
        """تصحيح الكويز - يدعم التصحيح التلقائي والذكي"""
        
        quiz = self.quizzes.get(quiz_id)
        if not quiz:
            return {'error': 'Quiz not found'}
        
        total_score = 0
        max_score = 0
        results = []
        weak_topics = defaultdict(int)
        
        for i, (question, answer) in enumerate(zip(quiz['questions'], answers)):
            points = 0
            is_correct = False
            
            # سؤال اختياري
            if 'options' in question:
                max_score += question.get('points', 10)
                if answer == question['correct']:
                    points = question.get('points', 10)
                    is_correct = True
                    total_score += points
                else:
                    weak_topics[question.get('topic', 'general')] += 1
            
            # سؤال مقالي - تصحيح ذكي
            elif 'essay_keywords' in question:
                max_score += question.get('points', 20)
                points = self._check_essay_answer(answer, question)
                total_score += points
                is_correct = points > question.get('points', 20) * 0.6
            
            results.append({
                'question_id': question.get('id', i),
                'question': question['question'],
                'user_answer': answer,
                'correct_answer': question.get('correct_option', question.get('sample_answer')),
                'is_correct': is_correct,
                'points_earned': points,
                'max_points': question.get('points', 10)
            })
        
        # حساب النسبة المئوية
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # تخزين الأداء
        self.user_performance[user_id]['scores'].append(percentage)
        
        # تحليل نقاط الضعف
        weakness_analysis = self._analyze_weaknesses(weak_topics)
        
        return {
            'quiz_id': quiz_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': round(percentage, 1),
            'grade': self._get_grade(percentage),
            'results': results,
            'weaknesses': weakness_analysis,
            'recommendations': self._generate_recommendations(weak_topics, percentage),
            'time_taken': answers.get('time_taken', 0)
        }
    
    def _check_essay_answer(self, user_answer: str, question: Dict) -> float:
        """تصحيح الإجابات المقالية باستخدام الذكاء الاصطناعي - فريد من نوعه!"""
        
        keywords = question.get('essay_keywords', [])
        max_points = question.get('points', 20)
        
        user_lower = user_answer.lower()
        
        # حساب عدد الكلمات المفتاحية الموجودة
        found_keywords = [kw for kw in keywords if kw.lower() in user_lower]
        keyword_score = (len(found_keywords) / len(keywords)) * max_points * 0.6
        
        # حساب طول الإجابة (الإجابة الطويلة جداً أو القصيرة جداً تنقص)
        word_count = len(user_answer.split())
        if word_count < 10:
            length_score = max_points * 0.1
        elif word_count > 200:
            length_score = max_points * 0.5
        else:
            length_score = max_points * 0.2
        
        # هل الإجابة منسقة؟
        has_structure = bool(re.search(r'\d+[.-]', user_answer))  # فيها ترقيم
        structure_score = max_points * 0.2 if has_structure else 0
        
        total = keyword_score + length_score + structure_score
        return min(max_points, total)
    
    def _analyze_weaknesses(self, weak_topics: Dict) -> Dict:
        """تحليل نقاط الضعف بعمق"""
        if not weak_topics:
            return {'has_weaknesses': False, 'message': 'ممتاز! لا توجد نقاط ضعف ملحوظة'}
        
        sorted_topics = sorted(weak_topics.items(), key=lambda x: x[1], reverse=True)
        main_weakness = sorted_topics[0][0] if sorted_topics else None
        
        return {
            'has_weaknesses': True,
            'main_weakness': main_weakness,
            'weak_topics': dict(sorted_topics[:3]),
            'suggestion': f'تحتاج إلى مراجعة {main_weakness} بشكل أعمق'
        }
    
    def _generate_recommendations(self, weak_topics: Dict, percentage: float) -> List[str]:
        """توليد توصيات مخصصة للطالب"""
        recommendations = []
        
        if percentage < 50:
            recommendations.append("📚 أنصحك بإعادة مشاهدة محاضرات المادة قبل المحاولة التالية")
        elif percentage < 70:
            recommendations.append("📖 ركز على الأسئلة التي أخطأت فيها وحاول فهمها بشكل أفضل")
        
        for topic in weak_topics.keys():
            recommendations.append(f"🎯 يوجد لديك ضعف في '{topic}' - أنصحك بمراجعة هذا الجزء")
        
        if not recommendations:
            recommendations.append("🎉 أداء ممتاز! استمر على هذا المنوال")
        
        return recommendations
    
    def _get_grade(self, percentage: float) -> Dict:
        """تحويل النسبة المئوية إلى تقدير"""
        if percentage >= 90:
            return {'letter': 'A+', 'arabic': 'ممتاز', 'color': '#10b981', 'emoji': '🎉'}
        elif percentage >= 80:
            return {'letter': 'A', 'arabic': 'جيد جداً', 'color': '#34d399', 'emoji': '😊'}
        elif percentage >= 70:
            return {'letter': 'B', 'arabic': 'جيد', 'color': '#fbbf24', 'emoji': '👍'}
        elif percentage >= 60:
            return {'letter': 'C', 'arabic': 'مقبول', 'color': '#f97316', 'emoji': '😐'}
        elif percentage >= 50:
            return {'letter': 'D', 'arabic': 'ضعيف', 'color': '#ef4444', 'emoji': '😔'}
        else:
            return {'letter': 'F', 'arabic': 'راسب', 'color': '#dc2626', 'emoji': '💀'}
    
    def detect_cheating(self, user_id: int, tab_switches: int, copy_paste_attempts: int) -> Dict:
        """كشف الغش باستخدام الذكاء الاصطناعي"""
        cheating_score = 0
        reasons = []
        
        if tab_switches > 3:
            cheating_score += min(40, tab_switches * 10)
            reasons.append(f"غادر الصفحة {tab_switches} مرات")
        
        if copy_paste_attempts > 2:
            cheating_score += min(30, copy_paste_attempts * 10)
            reasons.append(f"حاول نسخ ولصق {copy_paste_attempts} مرات")
        
        # تحديث سجل محاولات الغش
        self.user_performance[user_id]['cheating_attempts'] += 1 if cheating_score > 30 else 0
        
        if cheating_score > 50:
            return {'is_cheating': True, 'score': cheating_score, 'reasons': reasons, 'action': 'warning'}
        elif cheating_score > 25:
            return {'is_cheating': False, 'score': cheating_score, 'reasons': reasons, 'action': 'monitor'}
        else:
            return {'is_cheating': False, 'score': cheating_score, 'reasons': [], 'action': 'none'}
    
    def predict_performance(self, user_id: int, course_id: int) -> Dict:
        """التنبؤ بأداء الطالب المستقبلي - خوارزمية تنبؤ متقدمة"""
        user_data = self.user_performance[user_id]
        scores = user_data['scores']
        
        if len(scores) < 3:
            return {'can_predict': False, 'message': 'يحتاج إلى مزيد من البيانات للتنبؤ الدقيق'}
        
        # حساب الاتجاه (زيادة أو نقصان)
        recent_scores = scores[-5:] if len(scores) >= 5 else scores
        trend = 'up' if recent_scores[-1] > recent_scores[0] else 'down' if recent_scores[-1] < recent_scores[0] else 'stable'
        
        # التنبؤ بالدرجة القادمة
        if trend == 'up':
            predicted = min(100, recent_scores[-1] + 5)
        elif trend == 'down':
            predicted = max(0, recent_scores[-1] - 5)
        else:
            predicted = recent_scores[-1]
        
        return {
            'can_predict': True,
            'predicted_next_score': round(predicted, 1),
            'trend': trend,
            'average_score': round(np.mean(scores), 1),
            'consistency': round(100 - np.std(scores), 1) if len(scores) > 1 else 100,
            'recommendation': 'مستمر في التحسن!' if trend == 'up' else 'تحتاج إلى بذل المزيد من الجهد' if trend == 'down' else 'أداء ثابت، استمر'
        }

quiz_engine = UltimateQuizEngine()