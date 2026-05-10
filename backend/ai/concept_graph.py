"""
Concept Graph - النسخة الجبارة
خريطة المعرفة الذكية التي تربط المفاهيم ببعضها
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import json
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# ==================== أنواع العلاقات ====================

class RelationType(Enum):
    """أنواع العلاقات بين المفاهيم"""
    PREREQUISITE = "prerequisite"  # X مطلوب قبل Y
    RELATED = "related"           # X مرتبط بـ Y
    SIMILAR = "similar"           # X يشبه Y
    OPPOSITE = "opposite"         # X عكس Y
    EXAMPLE = "example"           # X مثال على Y
    PART_OF = "part_of"          # X جزء من Y

@dataclass
class Concept:
    """كيان المفهوم"""
    id: str
    name: str
    description: str
    difficulty: int  # 1-5
    category: str
    prerequisites: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    mastery_threshold: float = 0.7  # نسبة الإتقان المطلوبة

@dataclass
class Relation:
    """العلاقة بين مفهومين"""
    source: str
    target: str
    type: RelationType
    weight: float = 1.0
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()

# ==================== خوارزميات اكتشاف المعرفة ====================

class ConceptGraph:
    """خريطة المعرفة الذكية"""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.relations: List[Relation] = []
        self.graph = nx.DiGraph()  # رسم بياني موجه
        self.user_mastery: Dict[int, Dict[str, float]] = defaultdict(dict)  # user_id -> {concept_id: mastery}
        
        # بناء الخريطة الأساسية
        self._build_default_graph()
    
    def _build_default_graph(self):
        """بناء الخريطة الأساسية للمفاهيم"""
        
        # مفاهيم البرمجة الأساسية
        concepts_data = [
            Concept(id="var", name="المتغيرات", description="تخزين البيانات في الذاكرة", difficulty=1, category="programming"),
            Concept(id="data_types", name="أنواع البيانات", description="أعداد، نصوص، قوائم", difficulty=1, category="programming"),
            Concept(id="conditionals", name="الجمل الشرطية", description="if/else لاتخاذ القرارات", difficulty=2, category="programming"),
            Concept(id="loops", name="الحلقات", description="تكرار الأوامر", difficulty=2, category="programming"),
            Concept(id="functions", name="الدوال", description="تجميع الأوامر لإعادة الاستخدام", difficulty=3, category="programming"),
            Concept(id="arrays", name="المصفوفات", description="تخزين مجموعات من البيانات", difficulty=2, category="programming"),
            Concept(id="recursion", name="العودية", description="دالة تستدعي نفسها", difficulty=4, category="programming"),
            Concept(id="oop", name="البرمجة الكائنية", description="كلاسات وكائنات", difficulty=4, category="programming"),
        ]
        
        for concept in concepts_data:
            self.add_concept(concept)
        
        # إضافة العلاقات
        relations_data = [
            ("var", "data_types", RelationType.RELATED),
            ("var", "conditionals", RelationType.PREREQUISITE),
            ("var", "loops", RelationType.PREREQUISITE),
            ("conditionals", "functions", RelationType.PREREQUISITE),
            ("loops", "functions", RelationType.PREREQUISITE),
            ("functions", "recursion", RelationType.PREREQUISITE),
            ("arrays", "loops", RelationType.RELATED),
            ("functions", "oop", RelationType.RELATED),
        ]
        
        for source, target, rel_type in relations_data:
            self.add_relation(source, target, rel_type)
    
    def add_concept(self, concept: Concept):
        """إضافة مفهوم جديد إلى الخريطة"""
        self.concepts[concept.id] = concept
        self.graph.add_node(concept.id, 
                           name=concept.name,
                           difficulty=concept.difficulty,
                           category=concept.category)
    
    def add_relation(self, source_id: str, target_id: str, rel_type: RelationType, weight: float = 1.0):
        """إضافة علاقة بين مفهومين"""
        if source_id not in self.concepts or target_id not in self.concepts:
            raise ValueError("أحد المفاهيم غير موجود")
        
        relation = Relation(source=source_id, target=target_id, type=rel_type, weight=weight)
        self.relations.append(relation)
        self.graph.add_edge(source_id, target_id, type=rel_type.value, weight=weight)
    
    def get_prerequisites(self, concept_id: str) -> List[Concept]:
        """الحصول على المتطلبات السابقة لمفهوم معين"""
        prerequisites = []
        for rel in self.relations:
            if rel.target == concept_id and rel.type == RelationType.PREREQUISITE:
                if rel.source in self.concepts:
                    prerequisites.append(self.concepts[rel.source])
        return prerequisites
    
    def get_learning_path(self, target_concept: str, user_id: Optional[int] = None) -> List[Concept]:
        """توليد مسار تعلم ذكي للوصول إلى مفهوم معين"""
        if target_concept not in self.concepts:
            return []
        
        # BFS لاكتشاف المسار
        try:
            path_ids = nx.shortest_path(self.graph, source="var", target=target_concept)
            path = [self.concepts[pid] for pid in path_ids if pid in self.concepts]
        except nx.NetworkXNoPath:
            path = []
        
        # تخصيص المسار حسب مستوى المستخدم
        if user_id and user_id in self.user_mastery:
            mastered = self.user_mastery[user_id]
            path = [c for c in path if mastered.get(c.id, 0) < c.mastery_threshold]
        
        return path
    
    def update_user_mastery(self, user_id: int, concept_id: str, score: float):
        """تحديث مستوى إتقان المستخدم لمفهوم معين"""
        if concept_id not in self.concepts:
            return
        
        self.user_mastery[user_id][concept_id] = min(1.0, score / 100)
        
        # إذا أكمل المفهوم، تحقق من المفاهيم المتقدمة
        if self.user_mastery[user_id][concept_id] >= self.concepts[concept_id].mastery_threshold:
            self._check_advanced_concepts(user_id, concept_id)
    
    def _check_advanced_concepts(self, user_id: int, completed_concept: str):
        """فحص المفاهيم المتقدمة التي أصبحت متاحة"""
        for concept_id, concept in self.concepts.items():
            if concept_id == completed_concept:
                continue
            
            prerequisites = self.get_prerequisites(concept_id)
            all_prereqs_met = True
            for prereq in prerequisites:
                if self.user_mastery[user_id].get(prereq.id, 0) < prereq.mastery_threshold:
                    all_prereqs_met = False
                    break
            
            if all_prereqs_met and len(prerequisites) > 0:
                # إصدار حدث (سيتم ربطه بـ event_bus)
                self._emit_concept_unlocked(user_id, concept_id)
    
    def _emit_concept_unlocked(self, user_id: int, concept_id: str):
        """إصدار حدث بفتح مفهوم جديد"""
        concept = self.concepts.get(concept_id)
        if concept:
            print(f"🎉 المستخدم {user_id} فتح المفهوم: {concept.name}")
            # هنا سيتم ربط الـ event bus لاحقاً
    
    def get_knowledge_gaps(self, user_id: int) -> List[Dict]:
        """تحديد الفجوات المعرفية للمستخدم"""
        gaps = []
        mastered = self.user_mastery.get(user_id, {})
        
        for concept_id, concept in self.concepts.items():
            mastery = mastered.get(concept_id, 0)
            if mastery < concept.mastery_threshold:
                prerequisites = self.get_prerequisites(concept_id)
                prereq_mastery = [mastered.get(p.id, 0) for p in prerequisites]
                
                gaps.append({
                    'concept': concept.name,
                    'current_mastery': round(mastery * 100),
                    'required_mastery': concept.mastery_threshold * 100,
                    'missing_prerequisites': [p.name for p, m in zip(prerequisites, prereq_mastery) if m < p.mastery_threshold],
                    'difficulty': concept.difficulty
                })
        
        return sorted(gaps, key=lambda x: x['difficulty'], reverse=True)
    
    def recommend_next_concepts(self, user_id: int, limit: int = 3) -> List[Concept]:
        """توصية بأفضل المفاهيم التالية للدراسة"""
        mastered = self.user_mastery.get(user_id, {})
        candidates = []
        
        for concept_id, concept in self.concepts.items():
            if mastered.get(concept_id, 0) >= concept.mastery_threshold:
                continue
            
            prerequisites = self.get_prerequisites(concept_id)
            prereq_mastered = all(mastered.get(p.id, 0) >= p.mastery_threshold for p in prerequisites)
            
            if prereq_mastered:
                candidates.append(concept)
        
        # ترتيب حسب الأولوية (الصعوبة الأقل أولاً)
        candidates.sort(key=lambda x: x.difficulty)
        return candidates[:limit]
    
    def get_concept_impact(self, concept_id: str) -> Dict:
        """تحليل تأثير مفهوم معين على باقي الخريطة"""
        if concept_id not in self.graph:
            return {'affected_concepts': [], 'importance_score': 0}
        
        # عدد المفاهيم التي تعتمد على هذا المفهوم
        dependents = list(self.graph.successors(concept_id)) if concept_id in self.graph else []
        
        # حساب درجة الأهمية
        importance = len(dependents) * 10 + self.concepts[concept_id].difficulty * 5
        
        return {
            'affected_concepts': [self.concepts.get(d, {}).name for d in dependents if d in self.concepts],
            'importance_score': importance,
            'total_dependents': len(dependents)
        }
    
    def visualize(self, output_path: str = None):
        """تصدير خريطة المعرفة كصورة"""
        if not output_path:
            output_path = 'concept_graph.png'
        
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # رسم العقد
        nx.draw_networkx_nodes(self.graph, pos, node_size=2000, node_color='lightblue')
        nx.draw_networkx_labels(self.graph, pos, 
                                labels={n: self.concepts[n].name[:15] for n in self.graph.nodes() if n in self.concepts},
                                font_size=8, font_family='Arial')
        
        # رسم الحواف
        edge_colors = []
        for u, v, data in self.graph.edges(data=True):
            edge_colors.append('red' if data.get('type') == 'prerequisite' else 'gray')
        
        nx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors, width=1.5, arrows=True)
        
        plt.title("خريطة المعرفة - Study Hub AI", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
    
    def get_stats(self) -> Dict:
        """إحصائيات خريطة المعرفة"""
        return {
            'total_concepts': len(self.concepts),
            'total_relations': len(self.relations),
            'prerequisite_relations': sum(1 for r in self.relations if r.type == RelationType.PREREQUISITE),
            'avg_difficulty': sum(c.difficulty for c in self.concepts.values()) / max(1, len(self.concepts)),
            'categories': list(set(c.category for c in self.concepts.values())),
            'total_users_tracked': len(self.user_mastery)
        }

# ==================== خوارزمية التوصيات الذكية ====================

class SmartRecommender:
    """نظام التوصيات الذكي المعتمد على خريطة المعرفة"""
    
    def __init__(self, concept_graph: ConceptGraph):
        self.graph = concept_graph
        self.recommendation_cache = {}
    
    def recommend_study_plan(self, user_id: int, hours_per_day: float = 2) -> List[Dict]:
        """توليد خطة دراسة مخصصة"""
        next_concepts = self.graph.recommend_next_concepts(user_id, 5)
        knowledge_gaps = self.graph.get_knowledge_gaps(user_id)
        
        plan = []
        for concept in next_concepts:
            hours_needed = concept.difficulty * 2
            days_needed = max(1, int(hours_needed / hours_per_day))
            
            plan.append({
                'concept': concept.name,
                'description': concept.description,
                'difficulty': concept.difficulty,
                'estimated_hours': hours_needed,
                'estimated_days': days_needed,
                'resources': concept.resources[:3],
                'priority': 'high' if concept.id in [g['concept'] for g in knowledge_gaps[:2]] else 'normal'
            })
        
        return plan
    
    def find_similar_concepts(self, concept_name: str, limit: int = 3) -> List[Concept]:
        """البحث عن مفاهيم مشابهة"""
        # استخدام البحث الدلالي (سيتم ربطه بـ vector search)
        # مؤقتاً نرجع مفاهيم ذات صلة
        results = []
        for concept in self.graph.concepts.values():
            if concept_name.lower() in concept.name.lower() and concept.name != concept_name:
                results.append(concept)
                if len(results) >= limit:
                    break
        return results

# ==================== تهيئة النظام ====================

concept_graph = ConceptGraph()
smart_recommender = SmartRecommender(concept_graph)