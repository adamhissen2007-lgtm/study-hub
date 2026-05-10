"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║                         GAMIFIED UNIVERSE - LEARN LIKE A GAME                                 ║
║                    كون ألعاب تعليمي - أول منصة تخلي التعلم زي اللعبة بالضبط!                  ║
║                                                                                               ║
║  ★ ميزات حصرية:                                                                              ║
║    1. Interactive Worlds (عوالم تفاعلية - كل مادة عالم مستقل)                                 ║
║    2. Boss Battles (معارك مع زعماء - لازم تجاوب صح عشان تهزمهم)                               ║
║    3. Guilds & Teams (نقابات وفِرق - اتحاد مع طلاب تانيين)                                   ║
║    4. Real Rewards (جوائز حقيقية - فلوس - لابتوبات - منح)                                     ║
║    5. Season Pass (موسم جديد كل شهر - تحديات ومكافآت خاصة)                                    ║
║    6. Leaderboards Global (لوحات متصدرين عالمية - تنافس مع العالم)                            ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class GamifiedUniverse:
    """الكون الجيمفاي - التعلم بالطريقة الأكثر متعة في العالم"""
    
    def __init__(self):
        self.players = {}
        self.guilds = {}
        self.active_battles = {}
        self.seasons = {
            'current': 1,
            'name': '⚔️ موسم الأبطال',
            'end_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # عوالم اللعبة
        self.worlds = {
            'programming_land': {
                'name': '🏰 أرض البرمجة',
                'description': 'عالم مليء بالتحديات البرمجية',
                'bosses': [
                    {'name': '🐉 تنين الـ Bug', 'health': 1000, 'rewards': ['شفرة ذهبية', 'عباءة المبرمج']},
                    {'name': '🧙 ساحر الـ Algorithm', 'health': 1500, 'rewards': ['خاتم الخوارزميات', 'عصا الحلول']},
                    {'name': '👑 ملك الـ Python', 'health': 2000, 'rewards': ['تاج بايثون', 'عرش المطورين']}
                ],
                'unlock_level': 1
            },
            'ai_mountain': {
                'name': '🏔️ جبل الذكاء الاصطناعي',
                'description': 'تحديات في عالم AI و Machine Learning',
                'bosses': [
                    {'name': '🤖 Netron العملاق', 'health': 2000, 'rewards': ['قلادة الـ TensorFlow', 'خاتم الـ PyTorch']},
                    {'name': '🧠 Master Mind', 'health': 3000, 'rewards': ['تاج الذكاء', 'عباءة العبقري']}
                ],
                'unlock_level': 3
            },
            'cyber_security': {
                'name': '🛡️ قلعة الأمن السيبراني',
                'description': 'حماية المملكة من الهجمات',
                'bosses': [
                    {'name': '💀 هكر الظلام', 'health': 2500, 'rewards': ['درع الحماية', 'سيف التشفير']}
                ],
                'unlock_level': 5
            }
        }
        
        # الجوائز الحقيقية
        self.real_rewards = [
            {'name': '💰 1000 جنيه', 'points': 5000, 'available': 10},
            {'name': '🎧 سماعات لاسلكية', 'points': 10000, 'available': 5},
            {'name': '⌚ ساعة ذكية', 'points': 20000, 'available': 3},
            {'name': '💻 لابتوب', 'points': 50000, 'available': 1},
            {'name': '🎓 منحة دراسية', 'points': 100000, 'available': 1}
        ]
    
    def create_player(self, user_id: int, username: str) -> Dict:
        """إنشاء لاعب جديد"""
        
        player = {
            'user_id': user_id,
            'username': username,
            'level': 1,
            'experience': 0,
            'points': 0,
            'gems': 0,  # عملات خاصة للعبة
            'streak': 0,
            'world': 'programming_land',
            'unlocked_worlds': ['programming_land'],
            'defeated_bosses': [],
            'equipped_items': [],
            'guild_id': None,
            'season_points': 0,
            'last_active': datetime.now().isoformat()
        }
        
        self.players[user_id] = player
        return player
    
    def start_boss_battle(self, user_id: int, boss_name: str) -> Dict:
        """بدء معركة مع زعيم"""
        
        player = self.players.get(user_id)
        if not player:
            return {'error': 'Player not found'}
        
        world = self.worlds[player['world']]
        
        # إيجاد الزعيم المطلوب
        boss = None
        for b in world['bosses']:
            if b['name'] == boss_name or boss_name in b['name']:
                boss = b
                break
        
        if not boss:
            return {'error': 'Boss not found in current world'}
        
        # توليد أسئلة للمعركة
        questions = self._generate_battle_questions(boss)
        
        battle_id = secrets.token_hex(8)
        self.active_battles[battle_id] = {
            'user_id': user_id,
            'boss': boss,
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'started_at': datetime.now().isoformat()
        }
        
        return {
            'battle_id': battle_id,
            'boss': boss['name'],
            'boss_health': boss['health'],
            'boss_icon': self._get_boss_icon(boss['name']),
            'question': questions[0],
            'rewards': boss['rewards']
        }
    
    def _generate_battle_questions(self, boss: Dict) -> List[Dict]:
        """توليد أسئلة للمعركة حسب نوع الزعيم"""
        
        questions = []
        
        # محاكاة أسئلة مختلفة لكل زعيم
        topics = {
            'Bug': ['for loop', 'function', 'variable', 'debugging'],
            'Algorithm': ['sorting', 'searching', 'recursion', 'time complexity'],
            'Python': ['lists', 'dictionaries', 'classes', 'decorators'],
            'TensorFlow': ['neural networks', 'activation functions', 'loss functions'],
            'PyTorch': ['tensors', 'gradients', 'backpropagation'],
            'Master Mind': ['entropy', 'information gain', 'decision trees']
        }
        
        # اختيار موضوع مناسب
        for keyword, topic_list in topics.items():
            if keyword in boss['name']:
                selected_topic = random.choice(topic_list)
                break
        else:
            selected_topic = 'general programming concepts'
        
        for i in range(5):  # 5 أسئلة لكل معركة
            questions.append({
                'id': i,
                'question': fما هو المفهوم الصحيح لـ {selected_topic}?',
                'options': [
                    'الخيار الأول',
                    'الخيار الثاني',
                    'الخيار الثالث',
                    'الخيار الرابع'
                ],
                'correct': random.randint(0, 3),
                'points': 100
            })
        
        return questions
    
    def _get_boss_icon(self, boss_name: str) -> str:
        """الحصول على أيقونة الزعيم"""
        
        icons = {
            'Bug': '🐛',
            'Algorithm': '📊',
            'Python': '🐍',
            'TensorFlow': '🔷',
            'PyTorch': '🔥',
            'Master Mind': '🧠',
            'Netron': '🤖',
            'هكر': '💀'
        }
        
        for key, icon in icons.items():
            if key in boss_name:
                return icon
        
        return '👾'
    
    def answer_question(self, battle_id: str, answer: int) -> Dict:
        """الإجابة على سؤال في المعركة"""
        
        battle = self.active_battles.get(battle_id)
        if not battle:
            return {'error': 'Battle not found'}
        
        current_q = battle['current_question']
        question = battle['questions'][current_q]
        
        is_correct = (answer == question['correct'])
        
        result = {
            'is_correct': is_correct,
            'correct_answer': question['options'][question['correct']],
            'points_earned': question['points'] if is_correct else 0
        }
        
        if is_correct:
            battle['score'] += question['points']
            result['feedback'] = '✅ إجابة صحيحة! أضعفت الزعيم'
        else:
            result['feedback'] = f'❌ خطأ... الإجابة الصحيحة: {question["options"][question["correct"]]}'
        
        # الانتقال للسؤال التالي أو إنهاء المعركة
        if current_q + 1 >= len(battle['questions']):
            # انتهت المعركة
            total_score = battle['score']
            max_score = len(battle['questions']) * 100
            damage_percentage = total_score / max_score
            
            if damage_percentage > 0.7:
                # هزم الزعيم
                player = self.players.get(battle['user_id'])
                if player:
                    player['experience'] += battle['boss']['health'] // 10
                    player['points'] += total_score
                    player['defeated_bosses'].append(battle['boss']['name'])
                    
                    # ترقية المستوى
                    player['level'] = 1 + player['experience'] // 1000
                    
                    # فتح عوالم جديدة
                    self._unlock_worlds(player)
                
                result['battle_ended'] = True
                result['victory'] = True
                result['rewards'] = battle['boss']['rewards']
                result['experience_gained'] = battle['boss']['health'] // 10
                result['message'] = f'🎉 تهانينا! لقد هزمت {battle["boss"]["name"]} وحصلت على {battle["boss"]["rewards"][0]}!'
            else:
                result['battle_ended'] = True
                result['victory'] = False
                result['message'] = f'💀 هزمك {battle["boss"]["name"]}... حاول مرة أخرى'
            
            # حذف المعركة
            del self.active_battles[battle_id]
        else:
            # سؤال جديد
            battle['current_question'] += 1
            next_q = battle['questions'][battle['current_question']]
            result['next_question'] = next_q
        
        return result
    
    def _unlock_worlds(self, player: Dict):
        """فتح عوالم جديدة حسب مستوى اللاعب"""
        
        for world_id, world in self.worlds.items():
            if world['unlock_level'] <= player['level'] and world_id not in player['unlocked_worlds']:
                player['unlocked_worlds'].append(world_id)
    
    def create_guild(self, creator_id: int, guild_name: str) -> Dict:
        """إنشاء نقابة جديدة"""
        
        guild_id = secrets.token_hex(8)
        
        guild = {
            'id': guild_id,
            'name': guild_name,
            'leader_id': creator_id,
            'members': [creator_id],
            'level': 1,
            'points': 0,
            'member_count': 1,
            'created_at': datetime.now().isoformat()
        }
        
        self.guilds[guild_id] = guild
        
        # إضافة اللاعب للنقابة
        if creator_id in self.players:
            self.players[creator_id]['guild_id'] = guild_id
        
        return guild
    
    def join_guild(self, user_id: int, guild_id: str) -> Dict:
        """الانضمام إلى نقابة"""
        
        guild = self.guilds.get(guild_id)
        if not guild:
            return {'error': 'Guild not found'}
        
        if user_id in guild['members']:
            return {'error': 'Already in guild'}
        
        guild['members'].append(user_id)
        guild['member_count'] += 1
        
        if user_id in self.players:
            self.players[user_id]['guild_id'] = guild_id
        
        return {'success': True, 'guild_name': guild['name']}
    
    def get_leaderboard(self, world: str = None, limit: int = 50) -> List[Dict]:
        """الحصول على لوحة المتصدرين"""
        
        players_list = []
        for user_id, player in self.players.items():
            if world and player.get('world') != world:
                continue
            
            players_list.append({
                'username': player['username'],
                'level': player['level'],
                'points': player['points'],
                'world': player['world'],
                'bosses_defeated': len(player['defeated_bosses'])
            })
        
        # ترتيب حسب النقاط
        players_list.sort(key=lambda x: x['points'], reverse=True)
        
        # إضافة الترتيب
        for i, player in enumerate(players_list[:limit]):
            player['rank'] = i + 1
            player['avatar'] = self._get_rank_avatar(i + 1)
        
        return players_list[:limit]
    
    def _get_rank_avatar(self, rank: int) -> str:
        """الحصول على رمز حسب الترتيب"""
        
        if rank == 1:
            return '👑'
        elif rank == 2:
            return '🥈'
        elif rank == 3:
            return '🥉'
        elif rank <= 10:
            return '⭐'
        else:
            return '🎯'
    
    def claim_reward(self, user_id: int, reward_name: str) -> Dict:
        """استلام جائزة حقيقية"""
        
        player = self.players.get(user_id)
        if not player:
            return {'error': 'Player not found'}
        
        # البحث عن الجائزة
        reward = None
        for r in self.real_rewards:
            if r['name'] == reward_name:
                reward = r
                break
        
        if not reward:
            return {'error': 'Reward not found'}
        
        if reward['available'] <= 0:
            return {'error': 'Reward out of stock'}
        
        if player['points'] < reward['points']:
            return {'error': 'Not enough points'}
        
        # خصم النقاط
        player['points'] -= reward['points']
        reward['available'] -= 1
        
        return {
            'success': True,
            'reward': reward['name'],
            'remaining_points': player['points'],
            'message': f'🎉 تهانينا! تم إرسال {reward["name"]} إليك. سيتم التواصل معك قريباً'
        }

gamified = GamifiedUniverse()