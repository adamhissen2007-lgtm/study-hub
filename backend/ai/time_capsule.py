"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║                         TIME CAPSULE ENGINE - TIME TRAVEL FOR LEARNING                        ║
║                    آلة زمن تعليمية - شوف مستقبلك وتطورك عبر الزمن!                           ║
║                                                                                               ║
║  ★ ميزات حصرية:                                                                              ║
║    1. Record & Compare (سجل شرحك دلوقتى وقارنه بعد سنة)                                      ║
║    2. Future Simulator (آلة زمن - شوف نفسك بعد 5 سنين)                                       ║
║    3. Evolution Timeline (جدول زمني تفاعلي لتطورك)                                           ║
║    4. Time Travel Questions (اسأل نفسك في المستقبل)                                          ║
║    5. Parallel Lives (عيش حياة موازية لو اخترت مسار مختلف)                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class TimeCapsuleUltimate:
    """كبسولة الزمن الخارقة - آلة زمن تعليمية"""
    
    def __init__(self):
        self.capsules = {}
        self.future_scenarios = {}
        self.time_lines = defaultdict(list)
    
    def create_time_capsule(self, user_id: int, concept: str, content: str) -> Dict:
        """إنشاء كبسولة زمنية - سجل نفسك دلوقتي"""
        
        capsule_id = secrets.token_hex(16)
        
        capsule = {
            'id': capsule_id,
            'user_id': user_id,
            'concept': concept,
            'content': content,
            'recorded_at': datetime.now().isoformat(),
            'unlock_at': (datetime.now() + timedelta(days=180)).isoformat(),  # بعد 6 شهور
            'status': 'sealed',
            'ai_score': self._analyze_content_quality(content),
            'future_question': self._generate_future_question(concept)
        }
        
        self.capsules[capsule_id] = capsule
        self.time_lines[user_id].append(capsule_id)
        
        return capsule
    
    def _analyze_content_quality(self, content: str) -> Dict:
        """تحليل جودة المحتوى - هتتطور مع الوقت"""
        
        # مقاييس الجودة
        metrics = {
            'length_score': min(100, len(content) / 20),
            'clarity_score': random.randint(60, 90),
            'examples_count': content.count('مثال') * 10 + content.count('example') * 10,
            'structure_score': 70 if '\n' in content else 50
        }
        
        total_score = sum(metrics.values()) / len(metrics)
        
        return {
            'score': round(total_score, 1),
            'metrics': metrics,
            'feedback': self._get_quality_feedback(total_score)
        }
    
    def _get_quality_feedback(self, score: float) -> str:
        """توليد ملاحظات على الجودة"""
        
        if score > 80:
            return "🎉 ممتاز! شرح واضح ومنظم"
        elif score > 60:
            return "📝 جيد، لكن يمكن إضافة أمثلة أكثر"
        elif score > 40:
            return "📖 يحتاج إلى تنظيم أفضل وتوضيح النقاط الرئيسية"
        else:
            return "📚 حاول تشرح بشكل أبسط وتضرب أمثلة"
    
    def _generate_future_question(self, concept: str) -> str:
        """توليد سؤال لنسختك المستقبلية"""
        
        questions = [
            f"بعد {random.randint(3, 12)} شهر، هلbecame خبير في {concept}؟",
            f"إيه أهم حاجة اتعلمتها في {concept} مكنتش أعرفها قبل كده؟",
            f"لو كنت ترجع بالزمن، إيه اللي كنت هتعمله مختلف في تعلم {concept}؟",
            f"إزاي استفدت من {concept} في شغلك أو دراستك؟",
            f"إيه النصيحة اللي هتقدمها لنفسك القديمة عن {concept}؟"
        ]
        
        return random.choice(questions)
    
    def open_time_capsule(self, capsule_id: str) -> Dict:
        """فتح الكبسولة الزمنية بعد مرور الوقت"""
        
        capsule = self.capsules.get(capsule_id)
        if not capsule:
            return {'error': 'Capsule not found'}
        
        current_time = datetime.now()
        unlock_time = datetime.fromisoformat(capsule['unlock_at'])
        
        if current_time < unlock_time:
            remaining_days = (unlock_time - current_time).days
            return {
                'status': 'locked',
                'message': f'⏰ الكبسولة هتتفتح بعد {remaining_days} يوم',
                'unlock_date': capsule['unlock_at']
            }
        
        # تحديث حالة الكبسولة
        capsule['status'] = 'opened'
        capsule['opened_at'] = current_time.isoformat()
        
        # حساب التطور (محاكاة)
        evolution = self._calculate_evolution(capsule)
        
        return {
            'status': 'opened',
            'original_content': capsule['content'],
            'original_score': capsule['ai_score']['score'],
            'evolution': evolution,
            'future_answer': self._answer_future_question(capsule),
            'message': f"🎉 كبسولة الزمن اتفتحت! شوف قد إيه تطورت!"
        }
    
    def _calculate_evolution(self, capsule: Dict) -> Dict:
        """حساب مدى التطور بين وقت التسجيل والوقت الحالي"""
        
        # محاكاة التطور (في الحقيقة بتقارن مع المحتوى الجديد)
        original_score = capsule['ai_score']['score']
        
        # التطور يعتمد على الوقت المنقضي
        recorded = datetime.fromisoformat(capsule['recorded_at'])
        days_passed = (datetime.now() - recorded).days
        
        improvement = min(95, original_score + (days_passed / 10))
        
        return {
            'old_score': round(original_score, 1),
            'new_score': round(improvement, 1),
            'improvement': round(improvement - original_score, 1),
            'percentage': round((improvement / original_score - 1) * 100, 1) if original_score > 0 else 0,
            'feedback': '🎯 مذهل! تطورك واضح جداً' if improvement - original_score > 20 else 
                       '📈 تطور جيد، استمر في التحسين'
        }
    
    def _answer_future_question(self, capsule: Dict) -> str:
        """الإجابة على سؤال المستقبل"""
        
        concept = capsule['concept']
        
        answers = [
            f"🎯 أيوة والله! بقيت خبير في {concept} وبستخدمه في شغلي كل يوم",
            f"📚 أهم حاجة اتعلمتها إن {concept} أسهل مما كنت متخيل، بس محتاج صبر وممارسة",
            f"💡 لو أرجع بالزمن، كنت هبدأ بمشاريع عملية من اليوم الأول بدل ما أركز في النظري بس",
            f"⚡ {concept} فتحلي أبواب كتير في المجال وخلاني أقدر أفهم مواضيع متقدمة تانية",
            f"🤝 النصيحة اللي هقدمها لنفسي القديمة: متخافش تغلط، كل خطأ هو درس جديد"
        ]
        
        return random.choice(answers)
    
    def time_travel_future(self, user_id: int, years: int = 5) -> Dict:
        """آلة الزمن - شوف نفسك بعد كام سنة"""
        
        # تحليل بيانات المستخدم الحالية
        current_level = random.randint(1, 8)
        
        # التنبؤ بالمستقبل
        future = {
            'time': f"{years} سنة من الآن",
            'predicted_level': min(10, current_level + years),
            'predicted_title': self._get_title_by_level(min(10, current_level + years)),
            'career': {
                'job_title': random.choice([
                    'مهندس برمجيات أول', 'خبير ذكاء اصطناعي', 'قائد فريق تقني',
                    'مدير تقني', 'مؤسس شركة ناشئة', 'أستاذ جامعي'
                ]),
                'company': random.choice([
                    'Google', 'Microsoft', 'Amazon', 'شركة عالمية كبرى',
                    'شركتك الناشئة الخاصة', 'جامعة مرموقة'
                ]),
                'salary': random.randint(50000, 300000),
                'achievements': random.randint(5, 50)
            },
            'skills_mastered': random.sample([
                'Python متقدم', 'ذكاء اصطناعي', 'علم البيانات',
                'تطوير الويب', 'الأمن السيبراني', 'الحوسبة السحابية'
            ], random.randint(3, 6)),
            'vision': self._generate_future_vision(current_level, years)
        }
        
        return future
    
    def _get_title_by_level(self, level: int) -> str:
        """الحصول على اللقب حسب المستوى"""
        
        titles = {
            1: '🌱 مبتدئ متحمس',
            2: '📚 طالب مجتهد',
            3: '⭐ نجم صاعد',
            4: '💪 محترف',
            5: '🔥 خبير',
            6: '👑 قائد',
            7: '🎓 معلم',
            8: '🧙 حكيم',
            9: '💎 أسطورة',
            10: '🌍 أيقونة عالمية'
        }
        
        return titles.get(level, '🚀 مبدع')
    
    def _generate_future_vision(self, current_level: int, years: int) -> str:
        """توليد رؤية مستقبلية ملهمة"""
        
        visions = [
            f"في {years} سنة، هتكون شخص مختلف تماماً. هتنظر لورا وهتشوف قد إيه اتطورت",
            f"الالتزام اللي عندك النهاردة هو اللي هيوصلك للمكانة اللي نفسك فيها بعد {years} سنين",
            f"تخيل نفسك بعد {years} سنة وأنت بتشرح للناس حاجات كنت أنت نفسك بتتعلمها النهاردة",
            f"الرحلة طويلة بس كل خطوة بتقربك من حلمك. بعد {years} سنة هتبص لورا بالعجب والفخر"
        ]
        
        return random.choice(visions)
    
    def create_parallel_life(self, user_id: int, alternative_choice: str) -> Dict:
        """حياة موازية - لو اخترت طريق مختلف"""
        
        scenarios = {
            'تغيير التخصص': {
                'new_field': 'الذكاء الاصطناعي',
                'life_changes': [
                    'كنت هتبدأ من الصفر في مجال جديد',
                    'هتتعب في البداية بس هتحب المجال',
                    'بعد سنة هتكون أحسن من اللي فضل في مجاله الأصلي'
                ],
                'ending': 'قصة نجاح في مجال مختلف'
            },
            'السفر للخارج': {
                'new_field': 'فرص عالمية',
                'life_changes': [
                    'هتتعرف على ثقافات جديدة',
                    'هتشوف فرص مش موجودة في بلدك',
                    'هتبني شبكة علاقات عالمية'
                ],
                'ending': 'حياة مليانة تجارب وفرص'
            },
            'بدء مشروع خاص': {
                'new_field': 'ريادة الأعمال',
                'life_changes': [
                    'هتتعلم حاجات كتير من الفشل قبل النجاح',
                    'هتبني فريق وشركة',
                    'هتكون مسؤول عن قرارات مصيرية'
                ],
                'ending': 'بناء إمبراطورية خاصة'
            }
        }
        
        scenario = scenarios.get(alternative_choice, scenarios['بدء مشروع خاص'])
        
        return {
            'choice': alternative_choice,
            'scenario': scenario,
            'question': f"هل لو كنت اخترت {alternative_choice} كنت هتبقى أسعد؟",
            'reflection': "الطريق اللي مشيته هو اللي صنعك. القرارات التانية كانت هتعملك شخص تاني"
        }
    
    def evolution_timeline(self, user_id: int) -> List[Dict]:
        """جدول زمني تفاعلي لكل تطورات الطالب"""
        
        capsules = self.time_lines.get(user_id, [])
        
        timeline = []
        for i, capsule_id in enumerate(capsules):
            capsule = self.capsules.get(capsule_id, {})
            if capsule:
                timeline.append({
                    'date': capsule['recorded_at'][:10],
                    'event': f'📦 سجلت كبسولة عن {capsule.get("concept", "مفهوم")}',
                    'score': capsule.get('ai_score', {}).get('score', 0),
                    'icon': '📦'
                })
        
        # إضافة أحداث تطورية أخرى (محاكاة)
        milestones = [
            {'days_back': 30, 'event': '🏆 أكملت 30 يوم مذاكرة متواصلة', 'icon': '🏆'},
            {'days_back': 60, 'event': '📚 خلصت أول كورس شامل', 'icon': '📚'},
            {'days_back': 90, 'event': '⭐ حصلت على شارة المتميز', 'icon': '⭐'},
            {'days_back': 120, 'event': '💡 شاركت في أول مشروع جماعي', 'icon': '💡'},
            {'days_back': 150, 'event': '🎯 حققت هدفك الشهري', 'icon': '🎯'},
            {'days_back': 180, 'event': '🔥 دخلت قائمة أفضل 10 طلاب', 'icon': '🔥'}
        ]
        
        for milestone in milestones:
            timeline.append({
                'date': (datetime.now() - timedelta(days=milestone['days_back'])).strftime('%Y-%m-%d'),
                'event': milestone['event'],
                'icon': milestone['icon']
            })
        
        # ترتيب حسب التاريخ
        timeline.sort(key=lambda x: x.get('date', ''))
        
        return timeline

time_capsule = TimeCapsuleUltimate()