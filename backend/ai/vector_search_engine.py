"""
Vector Search Engine - النسخة الجبارة
نظام البحث الذكي باستخدام المتجهات والدلالات
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import pickle
import os

# استخدام FAISS للبحث السريع
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS غير متوفر، سيتم استخدام بحث أبطأ")

from sentence_transformers import SentenceTransformer

# ==================== هيكل البيانات ====================

@dataclass
class SearchDocument:
    """وثيقة قابلة للبحث"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()

@dataclass
class SearchResult:
    """نتيجة البحث"""
    document: SearchDocument
    score: float
    highlighted_content: str

# ==================== محرك البحث المتجهي الجبار ====================

class VectorSearchEngine:
    """محرك البحث المتجهي المتقدم"""
    
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-large'):
        """
        استخدام نموذج متعدد اللغات (يدعم العربية والإنجليزية)
        """
        # تحميل نموذج التضمين (Embedding Model)
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.dimension = 768  # بعد المتجه
        
        # إنشاء فهرس FAISS إذا كان متاحاً
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (مشابهة Cosine)
        else:
            self.index = None
        
        self.documents: List[SearchDocument] = []
        self.doc_index = {}  # id -> index position
        self.cache = {}  # cache للاستعلامات المتكررة
        
        # إحصائيات
        self.stats = {
            'total_documents': 0,
            'total_searches': 0,
            'avg_search_time': 0,
            'cache_hits': 0
        }
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """إضافة وثيقة إلى الفهرس"""
        doc_id = hashlib.md5(f"{content}{datetime.utcnow()}".encode()).hexdigest()[:16]
        
        # توليد embedding
        embedding = self.model.encode(content)
        
        # إنشاء الوثيقة
        doc = SearchDocument(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )
        
        # إضافة إلى القائمة والفهرس
        position = len(self.documents)
        self.documents.append(doc)
        self.doc_index[doc_id] = position
        
        # إضافة إلى FAISS
        if self.index is not None:
            # تطبيع المتجه (لجعل التشابه = cos similarity)
            normalized_embedding = embedding / np.linalg.norm(embedding)
            self.index.add(normalized_embedding.reshape(1, -1))
        
        self.stats['total_documents'] += 1
        return doc_id
    
    def add_batch(self, documents: List[Dict]) -> List[str]:
        """إضافة مجموعة من الوثائق دفعة واحدة"""
        ids = []
        for doc in documents:
            doc_id = self.add_document(doc.get('content', ''), doc.get('metadata', {}))
            ids.append(doc_id)
        return ids
    
    def search(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[SearchResult]:
        """
        بحث دلالي متقدم
        
        query: نص السؤال
        limit: عدد النتائج المطلوبة
        threshold: الحد الأدنى للثقة
        """
        import time
        start_time = time.time()
        
        # التحقق من cache أولاً
        cache_key = hashlib.md5(f"{query}{limit}".encode()).hexdigest()
        if cache_key in self.cache:
            self.stats['cache_hits'] += 1
            self.stats['total_searches'] += 1
            return self.cache[cache_key]
        
        # توليد embedding للاستعلام
        query_embedding = self.model.encode(query)
        normalized_query = query_embedding / np.linalg.norm(query_embedding)
        
        results = []
        
        if self.index is not None and len(self.documents) > 0:
            # بحث باستخدام FAISS (سريع جداً)
            scores, indices = self.index.search(normalized_query.reshape(1, -1), min(limit * 2, len(self.documents)))
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    similarity = float(score)  # FAISS أفضلية
                    if similarity >= threshold:
                        doc = self.documents[idx]
                        results.append(SearchResult(
                            document=doc,
                            score=similarity,
                            highlighted_content=self._highlight_content(doc.content, query)
                        ))
        else:
            # بحث خطي (أبطأ ولكن لا يحتاج FAISS)
            for doc in self.documents:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                if similarity >= threshold:
                    results.append(SearchResult(
                        document=doc,
                        score=similarity,
                        highlighted_content=self._highlight_content(doc.content, query)
                    ))
            
            # ترتيب حسب التشابه
            results.sort(key=lambda x: x.score, reverse=True)
        
        # تجميع النتائج حسب النوع والموضوع (تحسين الجودة)
        results = self._rerank_results(results, query)
        
        # حفظ في cache
        self.cache[cache_key] = results[:limit]
        
        # تحديث الإحصائيات
        search_time = time.time() - start_time
        self.stats['total_searches'] += 1
        self.stats['avg_search_time'] = (self.stats['avg_search_time'] * (self.stats['total_searches'] - 1) + search_time) / self.stats['total_searches']
        
        return results[:limit]
    
    def search_by_metadata(self, metadata_filter: Dict, limit: int = 20) -> List[SearchDocument]:
        """بحث بتصفية حسب البيانات الوصفية"""
        results = []
        for doc in self.documents:
            match = True
            for key, value in metadata_filter.items():
                if doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                results.append(doc)
        
        return results[:limit]
    
    def semantic_search_with_context(self, query: str, context: str, limit: int = 5) -> List[SearchResult]:
        """بحث دلالي مع سياق إضافي"""
        enhanced_query = f"{context}. سؤال المستخدم: {query}"
        return self.search(enhanced_query, limit)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """حساب التشابه بين متجهين"""
        if vec1 is None or vec2 is None:
            return 0
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)
    
    def _highlight_content(self, content: str, query: str) -> str:
        """تظليل الكلمات المفتاحية في النتيجة"""
        words = query.lower().split()
        highlighted = content
        for word in words[:3]:  # أهم 3 كلمات فقط
            if len(word) > 2:
                highlighted = highlighted.replace(word, f"**{word}**")
        return highlighted
    
    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """إعادة ترتيب النتائج باستخدام عوامل إضافية"""
        # إضافة نقاط إضافية للمحتوى الحديث
        for result in results:
            doc_age = (datetime.utcnow() - result.document.created_at).days
            if doc_age < 7:
                result.score += 0.05
            
            # نقاط إضافية للوثائق ذات الصلة بالموضوع
            topic_match = result.document.metadata.get('topic', '')
            if topic_match and topic_match in query:
                result.score += 0.1
        
        # إعادة الترتيب
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def get_stats(self) -> Dict:
        """إحصائيات محرك البحث"""
        return {
            'total_documents': self.stats['total_documents'],
            'total_searches': self.stats['total_searches'],
            'avg_search_time_ms': round(self.stats['avg_search_time'] * 1000, 2),
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': round(self.stats['cache_hits'] / max(1, self.stats['total_searches']) * 100, 1),
            'faiss_available': FAISS_AVAILABLE
        }
    
    def save_index(self, path: str):
        """حفظ الفهرس على القرص"""
        data = {
            'documents': [(d.id, d.content, d.metadata, d.created_at.isoformat()) for d in self.documents],
            'stats': self.stats
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        if self.index is not None:
            faiss.write_index(self.index, f"{path}.faiss")
    
    def load_index(self, path: str):
        """تحميل الفهرس من القرص"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = []
            for doc_id, content, metadata, created_at in data['documents']:
                embedding = self.model.encode(content)
                doc = SearchDocument(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    embedding=embedding,
                    created_at=datetime.fromisoformat(created_at)
                )
                self.documents.append(doc)
                self.doc_index[doc_id] = len(self.documents) - 1
            
            self.stats = data['stats']
            
            # إعادة بناء FAISS index
            if FAISS_AVAILABLE and os.path.exists(f"{path}.faiss"):
                self.index = faiss.read_index(f"{path}.faiss")

# ==================== البحث في مصادر متعددة ====================

class MultiSourceSearchEngine:
    """محرك بحث متعدد المصادر (كورسات، أسئلة، إجابات)"""
    
    def __init__(self):
        self.engines = {
            'courses': VectorSearchEngine(),
            'questions': VectorSearchEngine(),
            'answers': VectorSearchEngine(),
            'documents': VectorSearchEngine()
        }
    
    def index_course(self, course_data: Dict):
        """فهرسة كورس في محرك البحث"""
        self.engines['courses'].add_document(
            content=course_data.get('description', ''),
            metadata={
                'type': 'course',
                'id': course_data.get('id'),
                'title': course_data.get('title'),
                'difficulty': course_data.get('difficulty', 'beginner')
            }
        )
    
    def index_question(self, question_data: Dict):
        """فهرسة سؤال مع إجاباته"""
        content = f"{question_data.get('title', '')}\n{question_data.get('content', '')}"
        self.engines['questions'].add_document(
            content=content,
            metadata={
                'type': 'question',
                'id': question_data.get('id'),
                'author': question_data.get('user_id')
            }
        )
    
    def search_all(self, query: str, limit_per_source: int = 3) -> Dict:
        """البحث في جميع المصادر"""
        results = {}
        for source, engine in self.engines.items():
            results[source] = engine.search(query, limit_per_source)
        return results
    
    def smart_search(self, query: str, user_level: int = 1) -> List[SearchResult]:
        """بحث ذكي يتكيف مع مستوى المستخدم"""
        all_results = []
        
        for source, engine in self.engines.items():
            results = engine.search(query, 5)
            for result in results:
                # تعديل النتيجة حسب مستوى المستخدم
                doc_level = result.document.metadata.get('difficulty', 1)
                if isinstance(doc_level, int):
                    level_diff = abs(user_level - doc_level)
                    if level_diff > 2:
                        result.score *= 0.7  # تقليل النتيجة إذا كان المستوى غير مناسب
                all_results.append(result)
        
        # ترتيب واختيار أفضل النتائج
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:10]

# ==================== التكامل مع المنصة ====================

vector_search = VectorSearchEngine()
multi_search = MultiSourceSearchEngine()