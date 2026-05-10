import httpx
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from database.models import get_session, User, UserInteraction, Question
from ai.recommendation_engine import recommendation_engine
from ai.knowledge_tracer import knowledge_tracer
from ai.spaced_repetition import spaced_repetition

load_dotenv()

class TutorEngine:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.use_gemini = bool(self.api_key)
        self.session = get_session()
    
    async def ask(self, user_id, question, intent="explain", level=2):
        # Save interaction
        interaction = UserInteraction(
            user_id=user_id,
            question_text=question,
            intent=intent,
            timestamp=datetime.utcnow()
        )
        
        # Get answer
        answer = await self._get_answer(question, intent, level)
        interaction.ai_response = answer
        
        self.session.add(interaction)
        self.session.commit()
        
        # Update knowledge trace
        concept = self._extract_concept(question)
        if concept:
            knowledge_tracer.update_mastery(user_id, concept, True, level)
        
        # Get recommendations and due reviews
        recommendations = recommendation_engine.get_personalized_recommendations(user_id, 3)
        due_reviews = spaced_repetition.get_today_reviews(user_id)
        
        # Add recommendations to response
        if recommendations:
            answer += "\n\n📚 **موصى لك:**\n"
            for rec in recommendations:
                answer += f"• {rec['title']}: {rec['reason']}\n"
        
        if due_reviews:
            answer += f"\n🔄 **لديك {len(due_reviews)} مراجعة اليوم!**"
        
        return answer
    
    async def _get_answer(self, question, intent, level):
        # First, check local knowledge base
        local_answer = self._get_local_answer(question)
        if local_answer:
            return local_answer
        
        # Use Gemini if available
        if self.use_gemini:
            return await self._call_gemini(question, intent, level)
        
        return self._offline_response(question, intent, level)
    
    def _extract_concept(self, question):
        concepts = ['python', 'java', 'binary search', 'recursion', 'oop', 'database', 'flask', 'django', 'html', 'css']
        q_lower = question.lower()
        for concept in concepts:
            if concept in q_lower:
                return concept
        return None
    
    def _get_local_answer(self, question):
        q_lower = question.lower()
        
        knowledge = {
            "binary search": "🔍 **Binary Search**\n\nخوارزمية بحث سريعة تعمل فقط على المصفوفات المرتبة. تعقيدها O(log n).\n\nمثال: البحث عن 7 في [1,3,5,7,9] → تتجه يميناً حتى تجده!",
            "python": "🐍 **Python**\n\nلغة برمجة سهلة وقوية.\n\nمثال: `print('Hello')`",
            "تفاضل": "📐 **التفاضل**\n\nدراسة معدل التغير. مشتقة x^n = n × x^(n-1)",
            "flask": "🌶️ **Flask**\n\nإطار ويب صغير لـ Python",
            "recursion": "🔄 **Recursion**\n\nدالة تستدعي نفسها. مهم: شرط الإيقاف (Base Case)"
        }
        
        for key, answer in knowledge.items():
            if key in q_lower:
                return answer
        return None
    
    async def _call_gemini(self, question, intent, level):
        try:
            async with httpx.AsyncClient() as client:
                prompt = f"أنت معلم خبير. اشرح '{question}' للمستوى {level}/5 بالعربية بشكل مبسط مع أمثلة."
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=30.0
                )
                data = response.json()
                return data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "عذراً، لم أستطع الإجابة")
        except:
            return self._offline_response(question, intent, level)
    
    def _offline_response(self, question, intent, level):
        return f"📚 سؤال: {question}\n\nأنا فهيم، معلمك. جرب تسأل عن: Python، Binary Search، تفاضل، Flask، Recursion"

tutor_engine = TutorEngine()