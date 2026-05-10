"""
Study Hub Intelligence & Safety Engine
النسخة 1.0 - نظام متكامل للذكاء والأمان
"""

import re
import hashlib
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any

class IntelligenceEngine:
    """
    محرك الذكاء والأمان المتكامل للمنصة
    يقدم 5 أنظمة رئيسية:
    1. Content Intelligence - تحليل المحتوى (سبام، سمية، جودة)
    2. Behavior Intelligence - تحليل سلوك المستخدم
    3. Dynamic Trust Score - درجة الثقة المتغيرة
    4. Academic Integrity - كشف الغش والتشابه
    5. Learning Intelligence - تحليل نمط التعلم
    """
    
    def __init__(self):
        # سجلات الطلبات والسلوك
        self.user_requests = defaultdict(list)
        self.user_messages = defaultdict(list)
        self.rate_limits = defaultdict(list)
        self.last_typing = {}
        self.content_cache = {}
        
        # قوائم الكلمات الممنوعة والمشبوهة
        self.banned_keywords = {
            'cheating': [
                'حل كامل', 'solve for me', 'write my code', 'حل الواجب',
                'homework help', 'do my homework', 'اجابة نموذجية', 'answer key',
                'cheat', 'غش', 'اجابة جاهزة', 'حل الاختبار', 'exam solution'
            ],
            'toxic': [
                'كلب', 'حمار', 'غبي', 'stupid', 'idiot', 'kill', 'موت',
                'اخرس', 'يلعن', 'وسخ', 'قذر', 'عاهر', 'منافق'
            ],
            'spam': [
                'اشتراك', 'متابعة', 'بيع حسابات', 'شراء متابعين', 'ربح من الانترنت',
                'وظيفة من المنزل', 'ثروة', 'دولارات', 'bitcoin', 'عملات رقمية'
            ]
        }
        
        # الأنماط المنتظمة (Regex)
        self.spam_patterns = [
            r'https?://\S+',           # روابط
            r'www\.\S+\.com',           # روابط .com
            r'\S+@\S+\.\S+',            # إيميلات
            r'\+\d{10,}',               # أرقام هواتف
            r'(\S+\s+){10,}\S+',        # نصوص طويلة جداً
            r'([A-Za-z]+)\1{3,}'        # تكرار أحرف (spspspsp)
        ]
        
        # معاملات الوزن
        self.weights = {
            'content': {
                'spam': 0.4,
                'toxic': 0.3,
                'quality': 0.3
            },
            'behavior': {
                'rate': 0.5,
                'patterns': 0.3,
                'history': 0.2
            }
        }
    
    # ==================== القسم 1: Content Intelligence ====================
    
    def analyze_content(self, text: str, context: str = 'general') -> Dict[str, Any]:
        """
        تحليل المحتوى بشكل شامل
        
        المعطيات:
            text: النص المراد تحليله
            context: سياق المحتوى (discussion, reply, message, question)
        
        المخرجات:
            spam_score: درجة السبام (0-100)
            toxic_score: درجة السمية (0-100)
            quality_score: درجة الجودة الأكاديمية (0-100)
            intent: نية المستخدم
            is_safe: هل المحتوى آمن
            requires_review: هل يحتاج مراجعة بشرية
            suggestions: اقتراحات للتحسين
        """
        text_lower = text.lower()
        text_len = len(text)
        word_count = len(text.split())
        
        # 1. Spam Score (0-100)
        spam_score = self._calculate_spam_score(text_lower, text_len)
        
        # 2. Toxic Score (0-100)
        toxic_score = self._calculate_toxic_score(text_lower)
        
        # 3. Quality Score (0-100)
        quality_score = self._calculate_quality_score(text, word_count, context)
        
        # 4. Intent Detection
        intent = self._detect_intent(text_lower)
        
        # 5. Cheating Detection
        cheating_risk = self._detect_cheating_intent(text_lower)
        
        # تجميع النتيجة
        is_safe = spam_score < 70 and toxic_score < 50 and cheating_risk < 50
        requires_review = spam_score >= 70 or toxic_score >= 50 or cheating_risk >= 70
        
        # اقتراحات للتحسين
        suggestions = []
        if word_count < 5:
            suggestions.append("📝 أضف تفاصيل أكثر لتحصل على إجابة أفضل")
        if '?' not in text and context != 'reply':
            suggestions.append("❓ اسأل سؤالاً محدداً للحصول على إجابة دقيقة")
        if spam_score > 50:
            suggestions.append("⚠️ تجنب إضافة روابط أو إعلانات في مشاركاتك")
        if toxic_score > 30:
            suggestions.append("🤝 كن محترماً في تعاملك مع الآخرين")
        
        return {
            'spam_score': spam_score,
            'toxic_score': toxic_score,
            'quality_score': quality_score,
            'cheating_risk': cheating_risk,
            'intent': intent,
            'is_safe': is_safe,
            'requires_review': requires_review,
            'suggestions': suggestions[:3],
            'overall_score': int((100 - spam_score) * 0.4 + (100 - toxic_score) * 0.3 + quality_score * 0.3)
        }
    
    def _calculate_spam_score(self, text: str, length: int) -> int:
        """حساب درجة السبام"""
        score = 0
        
        # كلمات السبام
        for keyword in self.banned_keywords['spam']:
            if keyword in text:
                score += 35
                break
        
        # أنماط السبام
        for pattern in self.spam_patterns:
            if re.search(pattern, text):
                score += 25
        
        # تكرار علامات التعجب والاستفهام
        if text.count('!') > 3:
            score += 10
        if text.count('?') > 5:
            score += 10
        
        # كتابة بأحرف كبيرة
        if len(text) > 20 and text.isupper():
            score += 15
        
        return min(100, score)
    
    def _calculate_toxic_score(self, text: str) -> int:
        """حساب درجة السمية"""
        score = 0
        
        for keyword in self.banned_keywords['toxic']:
            if keyword in text:
                score += 20
                if score >= 60:
                    break
        
        return min(100, score)
    
    def _calculate_quality_score(self, text: str, word_count: int, context: str) -> int:
        """حساب درجة الجودة الأكاديمية"""
        score = 50  # درجة أساسية
        
        # طول مناسب
        if 20 <= len(text) <= 500:
            score += 15
        elif len(text) > 500:
            score -= 10
        
        # وجود علامات ترقيم
        if '.' in text or '?' in text or '!' in text:
            score += 10
        
        # وجود كلمات أكاديمية
        academic_words = ['ماذا', 'كيف', 'لماذا', 'اشرح', 'وضح', 'حلل', 'قارن', 'استنتج']
        for word in academic_words:
            if word in text:
                score += 5
                break
        
        return min(100, max(0, score))
    
    def _detect_intent(self, text: str) -> str:
        """كشف نية المستخدم"""
        if '?' in text:
            if 'ما هو' in text or 'what is' in text:
                return 'definition'
            elif 'كيف' in text or 'how' in text:
                return 'explanation'
            elif 'هل' in text or 'do/does' in text:
                return 'verification'
            return 'question'
        
        if any(word in text for word in ['شكراً', 'جزاك', 'ممتاز', 'thanks']):
            return 'gratitude'
        
        if any(word in text for word in self.banned_keywords['cheating']):
            return 'cheating_attempt'
        
        if any(word in text for word in ['اتفق', 'أوافق', 'agree']):
            return 'agreement'
        
        return 'statement'
    
    def _detect_cheating_intent(self, text: str) -> int:
        """كشف نية الغش"""
        score = 0
        
        for keyword in self.banned_keywords['cheating']:
            if keyword in text:
                score += 30
        
        # أنماط إضافية
        if re.search(r'حل\s+السؤال\s+\d+', text):
            score += 20
        if re.search(r'أريد\s+الإجابة\s+الكاملة', text):
            score += 25
        
        return min(100, score)
    
    # ==================== القسم 2: Behavior Intelligence ====================
    
    def analyze_behavior(self, user_id: int, action: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        تحليل سلوك المستخدم
        
        المعطيات:
            user_id: معرف المستخدم
            action: نوع الإجراء (post, reply, like, typing, login)
            metadata: بيانات إضافية
        
        المخرجات:
            risk_level: مستوى الخطورة (low, medium, high)
            is_bot: هل هو بوت
            unusual_patterns: أنماط غير طبيعية
            recommendations: توصيات
        """
        now = datetime.utcnow()
        key = f"{user_id}_{action}"
        
        # تسجيل الطلب
        self.user_requests[key].append(now)
        self.user_requests[key] = [t for t in self.user_requests[key] 
                                   if (now - t).seconds < 60]
        
        request_rate = len(self.user_requests[key])
        
        # 1. كشف البوت
        is_bot = self._detect_bot(user_id, action, request_rate)
        
        # 2. كشف الأنماط غير الطبيعية
        unusual_patterns = self._detect_unusual_patterns(user_id, action, request_rate, metadata)
        
        # 3. حساب مستوى الخطورة
        risk_level = self._calculate_risk_level(is_bot, unusual_patterns, request_rate)
        
        # 4. توصيات
        recommendations = []
        if is_bot:
            recommendations.append("🚫 تم اكتشاف سلوك آلي. يرجى التحقق من هويتك")
        if request_rate > 20:
            recommendations.append("⚠️ نشاط مكثف. يرجى التوقف قليلاً")
        if 'cheating' in unusual_patterns:
            recommendations.append("📚 التركيز على الفهم وليس الحلول الجاهزة يساعدك في التعلم")
        
        return {
            'risk_level': risk_level,
            'is_bot': is_bot,
            'request_rate': request_rate,
            'unusual_patterns': unusual_patterns,
            'recommendations': recommendations,
            'should_block': risk_level == 'high' and request_rate > 50
        }
    
    def _detect_bot(self, user_id: int, action: str, rate: int) -> bool:
        """كشف البوتات"""
        # سرعة طلبات غير طبيعية
        if rate > 30:
            return True
        
        # تكرار نفس الإجراء
        key = f"{user_id}_{action}"
        if len(self.user_requests[key]) > 50:
            return True
        
        return False
    
    def _detect_unusual_patterns(self, user_id: int, action: str, rate: int, metadata: Dict) -> List[str]:
        """كشف الأنماط غير الطبيعية"""
        patterns = []
        
        # تكرار نفس الرسالة
        if action == 'post':
            recent = self.user_messages.get(user_id, [])[-5:] if user_id in self.user_messages else []
            if len(recent) >= 3 and all(msg == recent[0] for msg in recent[-3:]):
                patterns.append('repetitive_content')
        
        # سرعة كتابة غير طبيعية
        if action == 'typing' and metadata:
            typing_speed = metadata.get('speed', 0)
            if typing_speed > 15:
                patterns.append('unnatural_typing_speed')
        
        # عدد كبير من الإعجابات في وقت قصير
        if action == 'like' and rate > 20:
            patterns.append('like_spam')
        
        return patterns
    
    def _calculate_risk_level(self, is_bot: bool, patterns: List, rate: int) -> str:
        """حساب مستوى الخطورة"""
        if is_bot:
            return 'high'
        if len(patterns) >= 2 or rate > 20:
            return 'medium'
        if rate > 10:
            return 'medium'
        return 'low'
    
    def check_rate_limit(self, user_id: int, action: str, limit: int = 10, window: int = 60) -> Tuple[bool, int]:
        """
        التحقق من عدم تجاوز الحد المسموح
        
        المخرجات:
            (is_allowed, remaining_requests)
        """
        key = f"rate_{user_id}_{action}"
        now = datetime.utcnow().timestamp()
        
        # تنظيف الطلبات القديمة
        self.rate_limits[key] = [t for t in self.rate_limits[key] if now - t < window]
        
        remaining = max(0, limit - len(self.rate_limits[key]))
        
        if len(self.rate_limits[key]) >= limit:
            return False, remaining
        
        self.rate_limits[key].append(now)
        return True, remaining - 1
    
    # ==================== القسم 3: Dynamic Trust Score ====================
    
    def calculate_trust_score(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        حساب درجة الثقة المتقدمة للمستخدم
        
        المعطيات (user_data):
            account_age_days: عمر الحساب بالأيام
            total_posts: عدد المشاركات
            helpful_replies: عدد الردود المفيدة
            reports_received: عدد البلاغات ضده
            helpful_votes: عدد التصويتات الإيجابية
            flags_received: عدد العلامات السلبية
            verified_email: هل البريد مؤكد
            completed_profile: هل الملف مكتمل
        
        المخرجات:
            score: درجة الثقة (0-100)
            level: المستوى (low, medium, high, trusted)
            badge: الشارة المناسبة
            factors: العوامل المؤثرة
        """
        score = 30  # درجة ابتدائية
        factors = []
        
        # 1. عمر الحساب (0-15 نقطة)
        days = user_data.get('account_age_days', 0)
        if days > 180:
            score += 15
            factors.append({'factor': 'account_age', 'contribution': 15, 'description': 'حساب قديم +6 أشهر'})
        elif days > 60:
            score += 10
            factors.append({'factor': 'account_age', 'contribution': 10, 'description': 'حساب قديم +2 شهر'})
        elif days > 14:
            score += 5
            factors.append({'factor': 'account_age', 'contribution': 5, 'description': 'حساب عمره أكثر من أسبوعين'})
        
        # 2. المشاركات المفيدة (0-25 نقطة)
        helpful = user_data.get('helpful_replies', 0)
        if helpful > 50:
            score += 25
            factors.append({'factor': 'helpful', 'contribution': 25, 'description': f'{helpful} رد مفيد'})
        elif helpful > 20:
            score += 20
            factors.append({'factor': 'helpful', 'contribution': 20, 'description': f'{helpful} رد مفيد'})
        elif helpful > 5:
            score += 10
            factors.append({'factor': 'helpful', 'contribution': 10, 'description': f'{helpful} رد مفيد'})
        
        # 3. البلاغات ضده (0- -30 نقطة)
        reports = user_data.get('reports_received', 0)
        if reports > 10:
            score -= 30
            factors.append({'factor': 'reports', 'contribution': -30, 'description': f'{reports} بلاغ ضدك'})
        elif reports > 5:
            score -= 20
            factors.append({'factor': 'reports', 'contribution': -20, 'description': f'{reports} بلاغ ضدك'})
        elif reports > 1:
            score -= 10
            factors.append({'factor': 'reports', 'contribution': -10, 'description': f'{reports} بلاغ ضدك'})
        
        # 4. التصويتات الإيجابية (0-10 نقطة)
        helpful_votes = user_data.get('helpful_votes', 0)
        if helpful_votes > 100:
            score += 10
            factors.append({'factor': 'helpful_votes', 'contribution': 10, 'description': f'{helpful_votes} تقييم إيجابي'})
        elif helpful_votes > 30:
            score += 5
            factors.append({'factor': 'helpful_votes', 'contribution': 5, 'description': f'{helpful_votes} تقييم إيجابي'})
        
        # 5. التحقق من البريد (0-10 نقطة)
        if user_data.get('verified_email', False):
            score += 10
            factors.append({'factor': 'verified', 'contribution': 10, 'description': 'بريد إلكتروني مؤكد'})
        
        # 6. اكتمال الملف الشخصي (0-5 نقطة)
        if user_data.get('completed_profile', False):
            score += 5
            factors.append({'factor': 'profile_complete', 'contribution': 5, 'description': 'ملف شخصي مكتمل'})
        
        # 7. محاولات الغش (0- -40 نقطة)
        cheating_attempts = user_data.get('cheating_attempts', 0)
        if cheating_attempts > 5:
            score -= 40
            factors.append({'factor': 'cheating', 'contribution': -40, 'description': 'محاولات غش متكررة'})
        elif cheating_attempts > 2:
            score -= 20
            factors.append({'factor': 'cheating', 'contribution': -20, 'description': 'محاولات غش'})
        
        # تحديد المستوى والشارة
        score = max(0, min(100, score))
        level, badge = self._get_trust_level_and_badge(score)
        
        return {
            'score': score,
            'level': level,
            'badge': badge,
            'factors': factors[:5],
            'recommendation': self._get_trust_recommendation(score, factors)
        }
    
    def _get_trust_level_and_badge(self, score: int) -> Tuple[str, Dict]:
        """تحديد مستوى الثقة والشارة"""
        if score >= 85:
            return 'trusted', {'icon': '👑', 'name': 'أسطورة موثوق', 'color': '#fbbf24', 'description': 'عضو مميز وموثوق'}
        elif score >= 70:
            return 'high', {'icon': '⭐', 'name': 'عضو موثوق', 'color': '#10b981', 'description': 'سجل ممتاز من المساهمات المفيدة'}
        elif score >= 50:
            return 'medium', {'icon': '✅', 'name': 'عضو نشط', 'color': '#6366f1', 'description': 'عضو إيجابي في المجتمع'}
        elif score >= 30:
            return 'low', {'icon': '🔄', 'name': 'عضو جديد', 'color': '#f59e0b', 'description': 'مازلت تكتشف المنصة'}
        else:
            return 'restricted', {'icon': '⚠️', 'name': 'تحت المراجعة', 'color': '#ef4444', 'description': 'ننصحك بمراجعة قوانين المنصة'}
    
    def _get_trust_recommendation(self, score: int, factors: List) -> str:
        """توليد توصية لرفع درجة الثقة"""
        if score < 30:
            return "شارك في المناقشات المفيدة وتجنب السلوكيات السلبية لرفع درجتك"
        elif score < 50:
            return "استمر في المساهمات المفيدة، وتجنب الشكاوي لتصبح عضواً موثوقاً"
        elif score < 70:
            return "🎉 أنت في الطريق الصحيح! استمر في مساعدة الآخرين"
        else:
            return "🏆 أنت نموذج يُحتذى به! شكراً لمساهماتك القيمة"
    
    # ==================== القسم 4: Academic Integrity ====================
    
    def check_academic_integrity(self, answer: str, question_id: int, all_answers: List[Dict]) -> Dict[str, Any]:
        """
        كشف الغش والتشابه بين الإجابات
        
        المعطيات:
            answer: إجابة الطالب
            question_id: معرف السؤال
            all_answers: قائمة بجميع الإجابات {'user_id': x, 'answer': y, 'timestamp': z}
        
        المخرجات:
            similarity_score: نسبة التشابه (0-1)
            is_plagiarized: هل هو منقول
            is_suspicious: هل هو مشبوه
            matched_with: مع من تشابهت الإجابة
            suggestion: اقتراح للطالب
        """
        if not all_answers:
            return {
                'similarity_score': 0,
                'is_plagiarized': False,
                'is_suspicious': False,
                'matched_with': None,
                'suggestion': ''
            }
        
        # حساب التشابه مع الإجابات الأخرى
        similarities = []
        for other in all_answers:
            if other.get('answer'):
                sim = self._calculate_similarity(answer, other['answer'])
                similarities.append({
                    'user_id': other.get('user_id'),
                    'similarity': sim,
                    'timestamp': other.get('timestamp')
                })
        
        if not similarities:
            return {
                'similarity_score': 0,
                'is_plagiarized': False,
                'is_suspicious': False,
                'matched_with': None,
                'suggestion': ''
            }
        
        max_sim = max(similarities, key=lambda x: x['similarity'])
        
        # الكشف عن التشابه
        is_plagiarized = max_sim['similarity'] > 0.9
        is_suspicious = max_sim['similarity'] > 0.75
        
        # توليد اقتراح
        suggestion = ''
        if is_plagiarized:
            suggestion = "📚 حاول صياغة الإجابة بكلماتك الخاصة لفهم أفضل للمادة"
        elif is_suspicious:
            suggestion = "💡 الإجابة تشبه إجابة أخرى. حاول إضافة وجهة نظرك الشخصية"
        
        return {
            'similarity_score': round(max_sim['similarity'], 2),
            'is_plagiarized': is_plagiarized,
            'is_suspicious': is_suspicious,
            'matched_with': max_sim['user_id'] if is_suspicious else None,
            'suggestion': suggestion
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """حساب نسبة التشابه بين نصين"""
        if not text1 or not text2:
            return 0
        
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        # طريقة shingling بسيطة
        def get_shingles(text: str, k: int = 3):
            words = text.split()
            if len(words) < k:
                return {text}
            return {' '.join(words[i:i+k]) for i in range(len(words) - k + 1)}
        
        shingles1 = get_shingles(text1)
        shingles2 = get_shingles(text2)
        
        if not shingles1 or not shingles2:
            return 0
        
        intersection = shingles1.intersection(shingles2)
        union = shingles1.union(shingles2)
        
        return len(intersection) / len(union) if union else 0
    
    # ==================== القسم 5: Learning Intelligence ====================
    
    def analyze_learning_pattern(self, user_id: int, interactions: List[Dict]) -> Dict[str, Any]:
        """
        تحليل نمط تعلم الطالب
        
        المعطيات:
            user_id: معرف الطالب
            interactions: سجل تفاعلات الطالب
        
        المخرجات:
            weaknesses: نقاط الضعف
            strengths: نقاط القوة
            engagement_score: درجة التفاعل
            learning_speed: سرعة التعلم
            recommended_focus: المواضيع المقترحة للتركيز
        """
        weak_topics = defaultdict(int)
        strong_topics = defaultdict(int)
        topic_attempts = defaultdict(list)
        
        for interaction in interactions:
            topic = interaction.get('topic', 'general')
            correct = interaction.get('correct', False)
            time_taken = interaction.get('time_taken', 0)
            
            topic_attempts[topic].append({
                'correct': correct,
                'time': time_taken
            })
            
            if correct:
                strong_topics[topic] += 1
            else:
                weak_topics[topic] += 1
        
        # تحليل نقاط القوة والضعف
        weaknesses = []
        for topic, count in weak_topics.items():
            total = weak_topics[topic] + strong_topics.get(topic, 0)
            if total > 2:
                success_rate = strong_topics.get(topic, 0) / total
                if success_rate < 0.5:
                    weaknesses.append({
                        'topic': topic,
                        'error_count': count,
                        'success_rate': round(success_rate * 100)
                    })
        
        strengths = []
        for topic, count in strong_topics.items():
            total = weak_topics.get(topic, 0) + count
            if total > 2:
                success_rate = count / total
                if success_rate > 0.7:
                    strengths.append({
                        'topic': topic,
                        'correct_count': count,
                        'success_rate': round(success_rate * 100)
                    })
        
        # حساب درجة التفاعل
        engagement_score = min(100, len(interactions) * 2)
        
        # حساب سرعة التعلم
        avg_time = np.mean([i.get('time_taken', 60) for i in interactions]) if interactions else 60
        learning_speed = 'سريع' if avg_time < 30 else 'متوسط' if avg_time < 90 else 'بطيء'
        
        # المواضيع الموصى بالتركيز عليها
        recommended_focus = [w['topic'] for w in weaknesses[:3]]
        
        # توليد رؤى تعليمية
        insights = self._generate_learning_insights(weaknesses, strengths, engagement_score)
        
        return {
            'weaknesses': weaknesses[:5],
            'strengths': strengths[:5],
            'engagement_score': engagement_score,
            'learning_speed': learning_speed,
            'recommended_focus': recommended_focus,
            'insights': insights,
            'total_interactions': len(interactions)
        }
    
    def _generate_learning_insights(self, weaknesses: List, strengths: List, engagement: int) -> List[str]:
        """توليد رؤى تعليمية مخصصة"""
        insights = []
        
        if weaknesses:
            topics = ', '.join([w['topic'] for w in weaknesses[:2]])
            insights.append(f"📚 ركز على فهم {topics} - هذه المواضيع تحتاج مزيداً من الممارسة")
        
        if strengths:
            insights.append(f"💪 ممتاز في {strengths[0]['topic']}! استفد من قوتك لمساعدة الآخرين")
        
        if engagement < 30:
            insights.append("🌟 شارك أكثر في المنصة لتحسين مستواك التعليمي")
        elif engagement > 70:
            insights.append("🎉 تفاعلك ممتاز! استمر بهذا المستوى")
        
        return insights
    
    # ==================== القسم 6: APIs للاستخدام الخارجي ====================
    
    def get_user_safety_status(self, user_id: int, user_data: Dict) -> Dict:
        """الحصول على حالة الأمان الشاملة للمستخدم"""
        
        # تحليل السلوك
        behavior = self.analyze_behavior(user_id, 'general', {})
        
        # حساب درجة الثقة
        trust = self.calculate_trust_score(user_data)
        
        # تجميع النتيجة
        if trust['score'] < 30 or behavior['risk_level'] == 'high':
            status = 'restricted'
            actions = ['limit_posting', 'require_verification']
        elif trust['score'] < 50 or behavior['risk_level'] == 'medium':
            status = 'monitored'
            actions = ['moderate_content']
        else:
            status = 'normal'
            actions = []
        
        return {
            'status': status,
            'trust_score': trust['score'],
            'trust_level': trust['level'],
            'badge': trust['badge'],
            'risk_level': behavior['risk_level'],
            'actions': actions
        }
    
    def moderate_content(self, content: str, author_id: int, context: str = 'general') -> Dict:
        """مراجعة المحتوى قبل النشر"""
        
        # تحليل المحتوى
        analysis = self.analyze_content(content, context)
        
        # قرارات التعديل
        if not analysis['is_safe']:
            return {
                'allowed': False,
                'reason': 'المحتوى غير مناسب',
                'suggestions': analysis['suggestions'],
                'requires_review': analysis['requires_review']
            }
        
        return {
            'allowed': True,
            'suggestions': analysis['suggestions'],
            'requires_review': False
        }

# ==================== نسخة واحدة جاهزة للاستخدام ====================
intelligence_engine = IntelligenceEngine()