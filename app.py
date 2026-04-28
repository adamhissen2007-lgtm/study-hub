from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_compress import Compress
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit
from flasgger import Swagger
import bleach
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import os, fitz, ollama, chromadb, json, re, subprocess
import filetype
import eventlet

app = Flask(__name__)
compress = Compress(app)

# ==================== الأمان ====================
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'img-src': ["'self'", "data:"],
    'connect-src': ["'self'", "ws://localhost:5000", "wss://localhost:5000"]
}, force_https=False, session_cookie_secure=False, session_cookie_http_only=True)

CORS(app, resources={r"/api/*": {"origins": "*"}})
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

# ==================== التسجيل ====================
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/studyhub.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# ==================== Swagger & SocketIO ====================
swagger_config = {
    "headers": [],
    "specs": [{"endpoint": 'apispec', "route": '/apispec.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}
Swagger(app, config=swagger_config)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ==================== الإعدادات الأساسية ====================
basedir = os.path.abspath(os.path.dirname(__file__))
LEADER_EMAIL = 'adamhissen2007@gmail.com'

# قاعدة البيانات
if os.environ.get('DATABASE_URL'):
    db_url = os.environ.get('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'studyhub.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'mp3', 'mp4'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# ==================== دوال مساعدة ====================
def sanitize_html(text):
    if not text: return text
    return bleach.clean(text, strip=True)

def is_safe_file(filepath):
    kind = filetype.guess(filepath)
    if kind is None: return False
    return kind.mime in ['application/pdf', 'image/jpeg', 'image/png', 'audio/mpeg']

# ==================== حماية الجلسات ====================
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

@app.before_request
def check_session_security():
    if 'user_id' in session:
        if request.headers.get('X-Forwarded-For'):
            client_ip = request.headers.get('X-Forwarded-For').split(',')[0]
        else:
            client_ip = request.remote_addr
        if 'client_ip' not in session:
            session['client_ip'] = client_ip
        elif session['client_ip'] != client_ip:
            session.clear()
            return redirect('/login')

# ==================== التأكد من وجود Ollama والموديل ====================
def check_ollama_model(model_name='codellama:7b'):
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ Ollama ليس قيد التشغيل")
            return False
        if model_name not in result.stdout:
            print(f"📦 جاري تحميل الموديل {model_name}...")
            subprocess.run(['ollama', 'pull', model_name], check=True)
        return True
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        return False

# ==================== Agent فهيم والذكاء الاصطناعي المحلي ====================
fahim_knowledge_base = {}
knowledge_fast_index = {}
stats = {'total_facts': 0, 'total_categories': 0}
conversation_state = {}

def fast_index_builder():
    global knowledge_fast_index
    knowledge_fast_index = {}
    for cat, facts in fahim_knowledge_base.items():
        for fact in facts:
            for word in set(fact.lower().split()):
                if len(word) >= 3:
                    if word not in knowledge_fast_index:
                        knowledge_fast_index[word] = []
                    if fact not in knowledge_fast_index[word]:
                        knowledge_fast_index[word].append(fact)

def load_knowledge_from_file():
    global stats
    filepath = os.path.join(basedir, 'knowledge.txt')
    if not os.path.exists(filepath):
        print("❌ ملف knowledge.txt غير موجود.")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and ': ' in line:
            parts = line.split(': ', 1)
            if len(parts) == 2:
                teach_fahim(parts[0].strip(), parts[1].strip())
                count += 1
    stats['total_facts'] = count
    stats['total_categories'] = len(fahim_knowledge_base)
    fast_index_builder()
    print(f"✅ تم تحميل {count} حقيقة.")

def teach_fahim(category, fact):
    if category not in fahim_knowledge_base:
        fahim_knowledge_base[category] = []
    if fact not in fahim_knowledge_base[category]:
        fahim_knowledge_base[category].append(fact)
    fast_index_builder()
    return True

def query_fahim(question):
    words = [w for w in question.lower().split() if len(w) >= 3]
    if not words:
        return None
    matches = set()
    for w in words:
        if w in knowledge_fast_index:
            matches.update(knowledge_fast_index[w])
    if matches:
        return "\n\n".join([f"🟢 {fact}" for fact in list(matches)[:10]])
    return None

def ask_ollama(prompt, model='codellama:7b'):
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7, 'num_predict': 1024}
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return None

def analyze_intent(question):
    if any(w in question for w in ['عايز', 'عاوز', 'ابغي', 'أريد']):
        return 'request'
    if any(w in question for w in ['ما', 'ماذا', 'كيف', 'مين', 'ليه']):
        return 'question'
    if any(w in question for w in ['خطة', 'منهج', 'Roadmap']):
        return 'plan_request'
    return 'general'

def generate_follow_up(topic, state):
    if 'subject' not in state:
        return f"📚 **{topic}** - عايز الخطة لمادة معينة ولا عايز خطة عامة؟"
    if 'level' not in state:
        return f"🎯 **{topic}({state['subject']})** - إيه مستواك الحالي؟ (مبتدئ، متوسط، متقدم)"
    if 'duration' not in state:
        return f"⏰ **{topic}({state['subject']})** - عايز الخطة لمدة أد إيه؟ (أسبوع، شهر، 3 شهور)"
    return None

check_ollama_model('codellama:7b')

# ==================== نماذج قاعدة البيانات ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))
    university_year = db.Column(db.String(20))
    major = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    badges = db.Column(db.Text, default='[]')
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='student')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    university_year = db.Column(db.String(20))
    major = db.Column(db.String(50))
    semester = db.Column(db.String(10), default='first')

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    file_type = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class DiscussionReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(500))
    link = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FlashcardSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    source_text = db.Column(db.Text)
    source_pdf = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cards = db.relationship('Flashcard', backref='set', lazy=True, cascade="all, delete-orphan")

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    difficulty = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    repetition_count = db.Column(db.Integer, default=0)
    set_id = db.Column(db.Integer, db.ForeignKey('flashcard_set.id'))

# ==================== نماذج الغرف التعليمية ====================
class ClassroomSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recording_url = db.Column(db.String(500), nullable=True)

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('classroom_session.id'))
    filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class BreakoutRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_room_id = db.Column(db.Integer, db.ForeignKey('classroom_session.id'))
    room_name = db.Column(db.String(100))
    participants = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def update_user_level(user):
    if user.points >= 1000:
        user.level = 5
    elif user.points >= 500:
        user.level = 4
    elif user.points >= 200:
        user.level = 3
    elif user.points >= 50:
        user.level = 2
    else:
        user.level = 1

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ==================== المسارات الأساسية ====================
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = sanitize_html(request.form['full_name'])
        email = sanitize_html(request.form['email'])
        year = sanitize_html(request.form.get('university_year', 'أولى'))
        major = sanitize_html(request.form.get('major', 'عام'))
        u = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(request.form['password']),
            university_year=year,
            major=major,
            role='student'
        )
        db.session.add(u)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = sanitize_html(request.form['email'])
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, request.form['password']):
            session.update({
                'user_id': user.id,
                'user_name': user.full_name,
                'user_email': user.email,
                'user_year': user.university_year,
                'user_major': user.major,
                'user_points': user.points,
                'user_level': user.level,
                'user_streak': user.streak,
                'user_semester': 'first',
                'user_role': user.role
            })
            return redirect('/dashboard')
        return render_template('login.html', error="بيانات خاطئة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    semester = session.get('user_semester', 'first')
    courses = Course.query.filter_by(university_year=session.get('user_year', 'أولى'), semester=semester).all()
    rank = User.query.filter(User.points > (user.points if user else 0)).count() + 1
    unread = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
    student_count = User.query.count()
    material_count = Material.query.count()
    return render_template('dashboard.html',
                         user_name=session['user_name'],
                         courses=courses,
                         user_rank=rank,
                         unread_count=unread,
                         student_count=student_count,
                         material_count=material_count,
                         LEADER_EMAIL=LEADER_EMAIL)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==================== مسارات المواد ====================
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect('/login')
    course = Course.query.get_or_404(course_id)
    materials = Material.query.filter_by(course_id=course_id).all()
    discussions = Discussion.query.filter_by(course_id=course_id).order_by(Discussion.created_at.desc()).all()
    return render_template('course_detail.html',
                         course=course,
                         materials=materials,
                         discussions=discussions,
                         LEADER_EMAIL=LEADER_EMAIL)

@app.route('/course/<int:course_id>/upload', methods=['POST'])
def upload_file(course_id):
    if 'user_id' not in session:
        return redirect('/login')
    if session.get('user_email') != LEADER_EMAIL and session.get('user_role') != 'admin':
        return redirect(url_for('course_detail', course_id=course_id))
    if 'file' not in request.files:
        return redirect(url_for('course_detail', course_id=course_id))
    file = request.files['file']
    if file and allowed_file(file.filename):
        fn = secure_filename(file.filename)
        fp = os.path.join(app.config['UPLOAD_FOLDER'], fn)
        file.save(fp)
        if not is_safe_file(fp):
            os.remove(fp)
            return redirect(url_for('course_detail', course_id=course_id))
        mat = Material(filename=fn, file_type=request.form['file_type'], course_id=course_id, uploader_id=session['user_id'])
        db.session.add(mat)
        db.session.commit()
        notify_students(course_id, f"📄 تم رفع ملف جديد في مادة: {Course.query.get(course_id).name}")
    return redirect(url_for('course_detail', course_id=course_id))

def notify_students(course_id, message):
    users = User.query.all()
    for u in users:
        db.session.add(Notification(user_id=u.id, message=message, link=f"/course/{course_id}"))
    db.session.commit()

@app.route('/course/<int:course_id>/discussion/new', methods=['POST'])
def new_discussion(course_id):
    if 'user_id' not in session:
        return redirect('/login')
    if request.form['title'] and request.form['content']:
        db.session.add(Discussion(
            title=sanitize_html(request.form['title']),
            content=sanitize_html(request.form['content']),
            course_id=course_id,
            user_id=session['user_id']
        ))
        db.session.commit()
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/discussion/<int:did>/reply', methods=['POST'])
def reply_discussion(did):
    if 'user_id' not in session:
        return redirect(request.referrer)
    if request.form['content']:
        db.session.add(DiscussionReply(
            content=sanitize_html(request.form['content']),
            discussion_id=did,
            user_id=session['user_id']
        ))
        db.session.commit()
    return redirect(request.referrer)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('leaderboard.html', top_users=User.query.order_by(User.points.desc()).limit(10).all())

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    badges = eval(user.badges) if user.badges else []
    return render_template('profile.html', user=user, badges=badges, user_rank=User.query.filter(User.points > user.points).count()+1)

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect('/login')
    user_notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/api/update-semester', methods=['POST'])
def update_semester():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    semester = request.json.get('semester')
    if semester in ['first', 'second']:
        session['user_semester'] = semester
        return jsonify({'success': True})
    return jsonify({'success': False})

# ==================== المسارات الإضافية ====================
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('chat.html')

@app.route('/video-chat')
def video_chat():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('video_chat.html')

@app.route('/smart-create')
def smart_create():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('smart_create.html')

@app.route('/flashcards')
def flashcards_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('flashcards.html')

@app.route('/roadmap')
def roadmap():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('roadmap.html', courses=Course.query.all())

@app.route('/whiteboard')
def whiteboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('whiteboard.html')

@app.route('/code-mentor')
def code_mentor():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('code_mentor.html', LEADER_EMAIL=LEADER_EMAIL)

@app.route('/api/docs')
def api_docs():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('api_docs.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# ==================== مسارات الغرف التعليمية ====================
@app.route('/live-class/<int:room_id>')
def live_classroom(room_id):
    if 'user_id' not in session:
        return redirect('/login')
    room = ClassroomSession.query.get(room_id)
    if not room:
        room = ClassroomSession(room_name=f"غرفة {room_id}", teacher_id=session['user_id'])
        db.session.add(room)
        db.session.commit()
    user_role = session.get('user_role', 'student')
    return render_template('live_classroom.html', room_id=room.id, username=session['user_name'], user_role=user_role, room_name=room.room_name)

@app.route('/create-live-room')
def create_live_room():
    if 'user_id' not in session:
        return redirect('/login')
    room = ClassroomSession(room_name=f"شرح {datetime.now().strftime('%H:%M')}", teacher_id=session['user_id'])
    db.session.add(room)
    db.session.commit()
    
    # إرسال إشعار لجميع الطلاب ببدء المحاضرة
    all_users = User.query.all()
    for user in all_users:
        if user.id != session['user_id']:  # مش عايز يبعت لنفسه
            notif = Notification(
                user_id=user.id,
                message=f"🎥 {session['user_name']} بدأ محاضرة جديدة: {room.room_name}",
                link=f"/live-class/{room.id}"
            )
            db.session.add(notif)
    db.session.commit()
    
    return redirect(f'/live-class/{room.id}')

@app.route('/api/recordings/<int:room_id>')
def get_recordings(room_id):
    if 'user_id' not in session:
        return jsonify([])
    recordings = Recording.query.filter_by(room_id=room_id).all()
    return jsonify([{'id': r.id, 'filename': r.filename, 'created_at': r.created_at.isoformat()} for r in recordings])

@app.route('/api/active-rooms')
def get_active_rooms():
    rooms = ClassroomSession.query.filter_by(is_active=True).order_by(ClassroomSession.created_at.desc()).limit(10).all()
    result = []
    for room in rooms:
        teacher = User.query.get(room.teacher_id)
        result.append({
            'id': room.id,
            'room_name': room.room_name,
            'teacher_name': teacher.full_name if teacher else 'معلم',
            'created_at': room.created_at.isoformat()
        })
    return jsonify(result)

# ==================== مسارات رفع الملفات المؤقتة للشرح على السبورة ====================
@app.route('/api/upload-temp-file', methods=['POST'])
def upload_temp_file():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({'url': url_for('uploaded_file', filename=filename)})

# ==================== WebSockets ====================
chat_messages = {}
active_participants = {}
active_breakout_rooms = {}

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    if room not in chat_messages:
        chat_messages[room] = []
    emit('previous_messages', {'messages': chat_messages[room][-50:]}, to=request.sid)
    emit('user_joined', {'username': username}, room=room)

@socketio.on('chat_message')
def handle_chat_message(data):
    room = data['room']
    username = data['username']
    message = sanitize_html(data['message'])
    timestamp = datetime.utcnow().isoformat()
    if room not in chat_messages:
        chat_messages[room] = []
    chat_messages[room].append({'username': username, 'message': message, 'timestamp': timestamp})
    emit('chat_message', {'username': username, 'message': message, 'timestamp': timestamp}, room=room)

@socketio.on('leave')
def handle_leave(data):
    leave_room(data['room'])

# ==================== WebRTC ====================
active_video_rooms = {}

@socketio.on('join_video_room')
def handle_join_video_room(data):
    room = data['room']
    username = data['username']
    join_room(room)
    if room not in active_video_rooms:
        active_video_rooms[room] = []
    active_video_rooms[room].append({'id': request.sid, 'username': username})
    emit('user_joined_video', {'userId': request.sid, 'username': username}, room=room)

@socketio.on('video_offer')
def handle_video_offer(data):
    emit('video_offer', {'offer': data['offer'], 'userId': request.sid}, room=data['room'], include_self=False)

@socketio.on('video_answer')
def handle_video_answer(data):
    emit('video_answer', {'answer': data['answer'], 'userId': request.sid}, room=data['room'], include_self=False)

@socketio.on('video_ice_candidate')
def handle_video_ice_candidate(data):
    emit('video_ice_candidate', {'candidate': data['candidate'], 'userId': request.sid}, room=data['room'], include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    for room, users in active_video_rooms.items():
        for user in users:
            if user['id'] == request.sid:
                users.remove(user)
                emit('user_left_video', {'userId': request.sid}, room=room)
                break
    for room, participants in active_participants.items():
        if request.sid in participants:
            participants.remove(request.sid)
            emit('participants_update', {'count': len(participants), 'participants': list(participants)}, room=room)
            break

# ==================== أحداث الغرفة التعليمية ====================
@socketio.on('join_classroom')
def handle_join_classroom(data):
    room = str(data['room'])
    username = data['username']
    join_room(room)
    if room not in active_participants:
        active_participants[room] = set()
    active_participants[room].add(username)
    emit('participants_update', {'count': len(active_participants[room]), 'participants': list(active_participants[room])}, room=room)

@socketio.on('drawing_update')
def handle_drawing_update(data):
    emit('drawing_update', {'drawing': data['drawing']}, room=str(data['room']), include_self=False)

@socketio.on('clear_board')
def handle_clear_board(data):
    emit('clear_board', room=str(data['room']), include_self=False)

@socketio.on('start_video')
def handle_start_video(data):
    emit('teacher_video_started', room=str(data['room']))

@socketio.on('stop_video')
def handle_stop_video(data):
    emit('teacher_video_stopped', room=str(data['room']))

# ==================== أحداث الغرف الفرعية ====================
@socketio.on('create_breakout')
def handle_create_breakout(data):
    parent_room = str(data['parent_room'])
    breakout_name = data['name']
    breakout_id = f"{parent_room}_breakout_{len(active_breakout_rooms)}"
    active_breakout_rooms[breakout_id] = {'name': breakout_name, 'participants': set(), 'parent': parent_room}
    emit('breakout_created', {'id': breakout_id, 'name': breakout_name}, room=parent_room)

@socketio.on('join_breakout')
def handle_join_breakout(data):
    breakout_id = data['breakout_id']
    username = data['username']
    if breakout_id in active_breakout_rooms:
        active_breakout_rooms[breakout_id]['participants'].add(username)
        join_room(breakout_id)
        emit('breakout_joined', {'room': breakout_id, 'username': username}, room=breakout_id)

# ==================== دوال البطاقات التعليمية ====================
def extract_json_from_response(raw_response):
    match = re.search(r'\[\s*\{.*?\}\s*\]', raw_response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    lines = raw_response.strip().split('\n')
    cards = []
    current_q = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[\d\-\*•]+\s*[سس]ؤال', line) or '?' in line[:50]:
            if current_q and current_q['question']:
                cards.append(current_q)
            current_q = {'question': line, 'answer': ''}
        elif current_q:
            current_q['answer'] += line + ' '
        else:
            if len(line) > 10 and ':' in line:
                parts = line.split(':', 1)
                cards.append({'question': parts[0].strip(), 'answer': parts[1].strip()})
    if current_q and current_q['question']:
        cards.append(current_q)
    return [c for c in cards if len(c['question']) > 5 and len(c.get('answer', '')) > 3]

def generate_flashcards_locally(text, max_cards=5):
    sentences = [s.strip() for s in re.split(r'[.!?؛\n]', text) if len(s.strip()) > 20]
    cards = []
    for sent in sentences[:max_cards*2]:
        if len(cards) >= max_cards:
            break
        if any(w in sent for w in ['هو', 'تعتبر', 'تعني', 'تعد']):
            parts = re.split(r'(هو|هي|تعتبر|تعني|تعد)', sent, 1)
            if len(parts) >= 2:
                if parts[1] in ['هو', 'هي']:
                    q = f"ما {parts[1]} {parts[0].strip()}؟"
                else:
                    q = f"ماذا تعني {parts[0].strip()}؟"
                cards.append({'question': q[:100], 'answer': sent[:200]})
        elif len(sent) > 30:
            words = re.findall(r'[\u0600-\u06FF]{4,}', sent)
            if words:
                cards.append({'question': f"ماذا تعرف عن {words[0]}؟", 'answer': sent[:200]})
    if not cards and sentences:
        for i, sent in enumerate(sentences[:max_cards]):
            cards.append({'question': f"معلومة {i+1}", 'answer': sent[:200]})
    return cards

# ==================== مسارات البطاقات التعليمية ====================
@app.route('/api/generate-flashcards', methods=['POST'])
def generate_flashcards_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    text = data.get('text', '')
    if not text or len(text.strip()) < 10:
        return jsonify({'error': 'النص قصير جدا'}), 400
    try:
        prompt = f"""أنت خبير تعليمي. أنشئ {min(5, max(3, len(text)//200))} بطاقات تعليمية (سؤال وجواب) من المحتوى.
المحتوى: {text[:2000]}
اخرج JSON array فقط: [{{"question": "...", "answer": "..."}}, ...]"""
        raw = ask_ollama(prompt)
        cards = extract_json_from_response(raw) if raw else None
        if not cards:
            cards = generate_flashcards_locally(text)
        return jsonify({'cards': cards[:8]})
    except Exception:
        return jsonify({'cards': generate_flashcards_locally(text)})

@app.route('/api/upload-pdf-flashcards', methods=['POST'])
@limiter.limit("10 per hour")
def upload_pdf_flashcards():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    if not is_safe_file(filepath):
        os.remove(filepath)
        return jsonify({'error': 'Invalid file type'}), 400
    try:
        doc = fitz.open(filepath)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'PDF لا يحتوي على نص كافٍ'}), 400
        cards = generate_flashcards_locally(text, 6)
        flashcard_set = FlashcardSet(
            title=f"PDF: {filename}",
            source_text=text[:500],
            source_pdf=filename,
            user_id=session['user_id']
        )
        db.session.add(flashcard_set)
        db.session.commit()
        for card in cards[:10]:
            db.session.add(Flashcard(
                question=card['question'][:500],
                answer=card['answer'][:500],
                set_id=flashcard_set.id
            ))
        db.session.commit()
        return jsonify({'success': True, 'set_id': flashcard_set.id, 'cards': cards[:10]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-flashcards', methods=['POST'])
def save_flashcards():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    title = data.get('title', 'بطاقات جديدة')
    cards = data.get('cards', [])
    if not cards:
        return jsonify({'error': 'No cards'}), 400
    flashcard_set = FlashcardSet(title=title, user_id=session['user_id'])
    db.session.add(flashcard_set)
    db.session.commit()
    for card in cards:
        db.session.add(Flashcard(
            question=card['question'][:500],
            answer=card['answer'][:500],
            set_id=flashcard_set.id
        ))
    db.session.commit()
    return jsonify({'success': True, 'set_id': flashcard_set.id})

@app.route('/api/my-flashcard-sets')
def my_flashcard_sets():
    if 'user_id' not in session:
        return jsonify([])
    sets = FlashcardSet.query.filter_by(user_id=session['user_id']).order_by(FlashcardSet.created_at.desc()).all()
    return jsonify([{'id': s.id, 'title': s.title, 'cards_count': len(s.cards), 'created_at': s.created_at.isoformat()} for s in sets])

@app.route('/api/flashcard-set/<int:set_id>')
def get_flashcard_set(set_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    fset = FlashcardSet.query.get_or_404(set_id)
    if fset.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify([{'id': c.id, 'question': c.question, 'answer': c.answer} for c in fset.cards])

@app.route('/api/review-flashcard/<int:card_id>', methods=['POST'])
def review_flashcard(card_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    card = Flashcard.query.get_or_404(card_id)
    if card.set.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    difficulty = request.json.get('difficulty', 1)
    if difficulty == 0:
        card.repetition_count = 0
        next_days = 1
    elif difficulty == 1:
        card.repetition_count += 1
        next_days = 2 ** card.repetition_count
    else:
        card.repetition_count += 2
        next_days = 2 ** card.repetition_count
    card.next_review = datetime.utcnow() + timedelta(days=min(next_days, 30))
    card.difficulty = difficulty
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/due-flashcards')
def due_flashcards():
    if 'user_id' not in session:
        return jsonify([])
    due_cards = db.session.query(Flashcard).join(FlashcardSet).filter(
        FlashcardSet.user_id == session['user_id'],
        Flashcard.next_review <= datetime.utcnow()
    ).limit(20).all()
    return jsonify([{'id': c.id, 'question': c.question, 'answer': c.answer} for c in due_cards])

# ==================== مسارات الذكاء الاصطناعي ====================
@app.route('/api/generate-ui', methods=['POST'])
def generate_ui():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    user_request = data.get('request', '')
    if not user_request:
        return jsonify({'error': 'Empty request'}), 400
    prompt = f"""المستخدم طلب: {user_request}
قم بتوليد HTML/CSS كامل (بدون body/head مكررة) لواجهة تعليمية متجاوبة. اخرج الكود فقط."""
    html = ask_ollama(prompt)
    if not html:
        html = f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 24px; color: white; text-align: center;">
            <h2 style="color: #fbbf24;">✨ واجهتك الذكية</h2>
            <p>طلبك: {user_request[:100]}</p>
            <div style="margin-top: 20px; padding: 20px; background: #1e293b; border-radius: 16px;">
                <p>⭐ واجهة تجريبية - تأكد من تشغيل Ollama للحصول على نتائج أفضل</p>
                <button onclick="alert('Study Hub AI')" style="background: #4f46e5; border: none; padding: 10px 20px; border-radius: 30px; color: white; cursor: pointer;">
                    جرب الزر
                </button>
            </div>
        </div>
        """
    return jsonify({'html': html})

@app.route('/api/generate-study-plan', methods=['POST'])
def generate_study_plan():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    subject = data.get('subject', '')
    duration = data.get('duration', 'شهر')
    level = data.get('level', 'متوسط')
    if not subject:
        return jsonify({'error': 'Subject required'}), 400
    prompt = f"""ضع خطة دراسية لمادة {subject} لمدة {duration} للمستوى {level}.
اكتبها بشكل واضح ومنظم مع نصائح يومية."""
    plan = ask_ollama(prompt)
    if not plan:
        plan = f"""📚 خطة دراسية لمادة {subject}

المدة: {duration}
المستوى: {level}

✅ الأسبوع الأول: أساسيات المادة
✅ الأسبوع الثاني: مراجعة وتطبيق
✅ الأسبوع الثالث: حل مسائل واسئلة
✅ الأسبوع الرابع: اختبارات ومراجعة نهائية

💡 نصيحة: خصص ساعة يوميا للمذاكرة وراجع ما تعلمته كل اسبوع
🎯 ركز على فهم المفاهيم الأساسية اولا
📝 حل أكبر عدد ممكن من الأسئلة"""
    return jsonify({'plan': plan})

@app.route('/api/recommendations')
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user = User.query.get(session['user_id'])
    my_courses = Course.query.filter_by(university_year=user.university_year, major=user.major).all()
    my_names = [c.name for c in my_courses]
    all_courses = Course.query.all()
    recommendations = []
    for course in all_courses:
        if course.name not in my_names:
            recommendations.append({
                'id': course.id,
                'title': course.name,
                'type': 'course',
                'reason': 'قد تهمك هذه المادة بناءً على تخصصك'
            })
    flashcard_sets = FlashcardSet.query.filter_by(user_id=session['user_id']).limit(5).all()
    for fs in flashcard_sets:
        recommendations.append({
            'id': fs.id,
            'title': fs.title,
            'type': 'flashcard',
            'reason': f'يحتوي على {len(fs.cards)} بطاقة تعليمية'
        })
    return jsonify(recommendations[:10])

@app.route('/recommendation/<string:rec_type>/<int:rec_id>')
def view_recommendation(rec_type, rec_id):
    if 'user_id' not in session:
        return redirect('/login')
    if rec_type == 'course':
        return redirect(f'/course/{rec_id}')
    elif rec_type == 'flashcard':
        return redirect('/flashcards')
    return redirect('/dashboard')

# ==================== مسارات API اضافية ====================
@app.route('/api/code-mentor', methods=['POST'])
def api_code_mentor():
    data = request.json
    question = data.get('question', '')
    mode = data.get('mode', 'chat')
    session_id = data.get('session_id', 'default')
    if not question:
        return jsonify({'error': 'No question'}), 400
    if mode == 'code_explain':
        return jsonify({'answer': ask_ollama(f"اشرح الكود التالي:\n{question}") or 'فشل.'})
    if mode == 'generate':
        return jsonify({'answer': ask_ollama(f"اكتب كود يلبي: {question}") or 'فشل.'})
    if mode == 'review':
        return jsonify({'answer': ask_ollama(f"راجع الكود: {question}") or 'فشل.'})
    if mode == 'design':
        return jsonify({'answer': ask_ollama(f"صمم HTML/CSS/JS لـ: {question}") or 'فشل.'})
    intent = analyze_intent(question)
    if intent == 'plan_request':
        topic = question.replace('خطة', '').strip()
        if session_id not in conversation_state:
            conversation_state[session_id] = {'topic': topic}
        follow_up = generate_follow_up(topic, conversation_state[session_id])
        if follow_up:
            return jsonify({'answer': follow_up})
    ans = query_fahim(question)
    if ans:
        return jsonify({'answer': ans})
    ai_answer = ask_ollama(question)
    if ai_answer:
        return jsonify({'answer': ai_answer})
    return jsonify({'answer': '🧠 ليس لدي معلومات عن هذا. علمني من لوحة "علم فهيم".'})

@app.route('/api/teach-fahim', methods=['POST'])
def api_teach_fahim():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session.get('user_email') != LEADER_EMAIL and session.get('user_role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.json
    category = data.get('category', 'عام')
    fact = data.get('fact', '')
    if fact and category:
        teach_fahim(category, fact)
        stats['total_facts'] += 1
        stats['total_categories'] = len(fahim_knowledge_base)
        return jsonify({'success': True, 'message': f'✅ تم تعليمي! ({category})'})
    return jsonify({'success': False})

@app.route('/api/knowledge-stats')
def knowledge_stats_api():
    return jsonify(stats)

# ==================== تشغيل السيرفر ====================
def init_db():
    with app.app_context():
        db.create_all()
        if Course.query.count() == 0:
            courses_data = [
                ('رياضيات 1', 'تفاضل وتكامل', 'أولى', 'عام', 'first'),
                ('فيزياء 1', 'ميكانيكا', 'أولى', 'عام', 'first'),
                ('كمبيوتر ساينس', 'اساسيات الحاسوب', 'أولى', 'عام', 'first'),
                ('Linear Algebra', 'جبر خطي', 'أولى', 'عام', 'second'),
                ('انجليزي 1', 'English Language', 'أولى', 'عام', 'second'),
                ('برمجة 1', 'Python', 'ثانية', 'عام', 'first'),
                ('تحليل عددي', 'Numerical Analysis', 'ثانية', 'عام', 'first'),
                ('قواعد بيانات', 'Database Systems', 'ثانية', 'عام', 'second'),
                ('هياكل بيانات', 'Data Structures', 'ثانية', 'عام', 'second'),
            ]
            for n, d, y, m, s in courses_data:
                db.session.add(Course(name=n, description=d, university_year=y, major=m, semester=s))
            db.session.commit()
            app.logger.info("Database initialized with sample courses")
        
        admin_user = User.query.filter_by(email=LEADER_EMAIL).first()
        if admin_user:
            admin_user.role = 'super_admin'
            db.session.commit()
            print(f"✅ تم ترقية {admin_user.full_name} إلى super_admin")

if __name__ == '__main__':
    init_db()
    load_knowledge_from_file()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
else:
    with app.app_context():
        db.create_all()