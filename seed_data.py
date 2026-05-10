import random
import json
from datetime import datetime, timedelta
from app import app, db, User, Course, Material, Discussion, DiscussionReply, Notification, FlashcardSet, Flashcard, ClassroomSession, StudentPerformance

# ==================== إعدادات التغذية ====================
CLEAR_EXISTING = True  # لو True: يمسح البيانات القديمة قبل إضافة الجديدة. لو False: يضيف بدون مسح

def clear_existing_data():
    """مسح البيانات القديمة (اختياري)"""
    if CLEAR_EXISTING:
        print("🗑️ جاري مسح البيانات القديمة...")
        db.session.query(StudentPerformance).delete()
        db.session.query(Flashcard).delete()
        db.session.query(FlashcardSet).delete()
        db.session.query(DiscussionReply).delete()
        db.session.query(Discussion).delete()
        db.session.query(Notification).delete()
        db.session.query(ClassroomSession).delete()
        db.session.query(Material).delete()
        db.session.query(Course).delete()
        db.session.query(User).filter(User.email != 'adamhissen2007@gmail.com').delete()
        db.session.commit()
        print("✅ تم مسح البيانات القديمة")

def seed_database():
    with app.app_context():
        print("🌱 بدء إنشاء البيانات العالمية المتطورة...")
        
        if CLEAR_EXISTING:
            clear_existing_data()
        
        # ==================== 1. المواد الدراسية المتقدمة ====================
        courses = []
        
        # كلية الحاسبات
        cs_courses = [
            ("رياضيات 1", "تفاضل وتكامل - أساسيات الرياضيات للعلوم الهندسية", "أولى", "حاسبات", 2),
            ("فيزياء 1", "ميكانيكا كلاسيكية وخصائص المواد", "أولى", "حاسبات", 2),
            ("برمجة 1", "أساسيات البرمجة بلغة Python", "أولى", "حاسبات", 1),
            ("هياكل بيانات", "Arrays, Linked Lists, Trees, Graphs", "ثانية", "حاسبات", 3),
            ("قواعد بيانات", "SQL, مقدمة في قواعد البيانات العلائقية", "ثانية", "حاسبات", 2),
            ("ذكاء اصطناعي", "مقدمة في AI, Machine Learning", "ثالثة", "حاسبات", 3),
        ]
        
        # كلية العلوم
        science_courses = [
            ("رياضيات 1", "تفاضل وتكامل - علمي", "أولى", "علوم", 2),
            ("فيزياء 1", "قياسات وكهربية", "أولى", "علوم", 2),
            ("كيمياء عامة", "مبادئ الكيمياء والجدول الدوري", "أولى", "علوم", 2),
            ("فيزياء 2", "موجات وبصريات", "ثانية", "علوم", 2),
            ("كيمياء عضوية", "مركبات الكربون والتفاعلات", "ثانية", "علوم", 3),
        ]
        
        # كلية الهندسة
        eng_courses = [
            ("رياضيات هندسية 1", "تفاضل وتكامل للمهندسين", "أولى", "هندسة", 2),
            ("ميكانيكا", "إستاتيكا وديناميكا", "أولى", "هندسة", 2),
            ("رسم هندسي", "AutoCAD وأساسيات الرسم الهندسي", "أولى", "هندسة", 1),
            ("مقاومة مواد", "إجهادات وانفعالات", "ثانية", "هندسة", 3),
        ]
        
        # كلية التجارة
        business_courses = [
            ("محاسبة مالية", "أساسيات المحاسبة والقوائم المالية", "أولى", "تجارة", 1),
            ("اقتصاد كلي", "النظرية الاقتصادية الكلية", "أولى", "تجارة", 2),
            ("إدارة أعمال", "مبادئ الإدارة والتنظيم", "ثانية", "تجارة", 1),
        ]
        
        all_courses_list = cs_courses + science_courses + eng_courses + business_courses
        
        for name, desc, year, major, diff in all_courses_list:
            course = Course(name=name, description=desc, university_year=year, major=major, difficulty=diff, semester=random.choice(['first', 'second']))
            db.session.add(course)
            courses.append(course)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(courses)} مادة دراسية من {len(all_courses_list)} مادة")

        # ==================== 2. المستخدمين المتقدمين ====================
        users = []
        
        # الأدمن الأساسي
        admin = User.query.filter_by(email='adamhissen2007@gmail.com').first()
        if not admin:
            admin = User(full_name="آدم حسين", email="adamhissen2007@gmail.com",
                        password="pbkdf2:sha256:600000$12345", university_year="أولى", major="حاسبات",
                        role="super_admin", points=1450, level=5, streak=45)
            db.session.add(admin)
        users.append(admin)
        
        # أساتذة ومشرفين
        professors = [
            ("د. أحمد خالد", "ahmed@university.edu.eg", "دكتوراه حاسبات", "حاسبات", 0, 0, "admin"),
            ("د. محمد علي", "mohamed@university.edu.eg", "دكتوراه فيزياء", "علوم", 0, 0, "admin"),
            ("د. سارة محمود", "sara@university.edu.eg", "دكتوراه إدارة", "تجارة", 0, 0, "admin"),
        ]
        
        for name, email, major, dept, points, level, role in professors:
            prof = User(full_name=name, email=email, password="pbkdf2:sha256:600000$12345",
                       university_year="دكتوراه", major=dept, role=role, points=points, level=level, streak=0)
            db.session.add(prof)
            users.append(prof)
        
        # طلاب متفوقين ومتوسطين ومبتدئين
        student_data = [
            # متفوقون (نقاط عالية)
            ("ليلى عمرو", "laila@university.edu.eg", "ثالثة", "حاسبات", 850, 4, 30),
            ("زياد طارق", "ziad@university.edu.eg", "ثالثة", "هندسة", 820, 4, 28),
            ("فاطمة الزهراء", "fatma@university.edu.eg", "ثالثة", "علوم", 790, 4, 25),
            
            # مجتهدون (نقاط متوسطة)
            ("محمد علي", "mohamed.ali@university.edu.eg", "ثانية", "حاسبات", 480, 3, 18),
            ("سارة محمود", "sara.mahmoud@university.edu.eg", "ثانية", "هندسة", 450, 3, 15),
            ("عمر خالد", "omar@university.edu.eg", "ثانية", "تجارة", 420, 3, 12),
            ("نورا أحمد", "nora@university.edu.eg", "ثانية", "علوم", 390, 2, 10),
            
            # مبتدئون (نقاط قليلة)
            ("يوسف عادل", "youssef@university.edu.eg", "أولى", "حاسبات", 120, 1, 5),
            ("جنى سامح", "jana@university.edu.eg", "أولى", "هندسة", 95, 1, 3),
            ("خالد وائل", "khaled@university.edu.eg", "أولى", "تجارة", 70, 1, 2),
            ("مريم طارق", "maryam@university.edu.eg", "أولى", "علوم", 50, 1, 1),
            ("أحمد سمير", "ahmed.samir@university.edu.eg", "أولى", "حاسبات", 30, 1, 0),
        ]
        
        for name, email, year, major, points, level, streak in student_data:
            student = User(full_name=name, email=email, password="pbkdf2:sha256:600000$12345",
                          university_year=year, major=major, role="student", points=points, level=level, streak=streak)
            db.session.add(student)
            users.append(student)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(users)} مستخدم (أدمن، أساتذة، طلاب)")

        # ==================== 3. الأداء اليومي الذكي ====================
        for user in users:
            # الأداء مش عشوائي، مرتبط بنقاط المستخدم
            base_points = max(5, min(40, user.points // 30))
            for day in range(30):
                date = datetime.utcnow().date() - timedelta(days=day)
                # الطالب المتفوق نقطة أعلى
                points_factor = 1 + (user.level / 10)
                points_earned = int(random.randint(base_points - 3, base_points + 3) * points_factor)
                points_earned = max(1, min(60, points_earned))
                tasks_completed = random.randint(0, 3) if user.level > 1 else random.randint(0, 1)
                study_hours = random.uniform(0.5, 4.5) if user.level > 2 else random.uniform(0.5, 2.5)
                
                perf = StudentPerformance(user_id=user.id, date=date, points_earned=points_earned,
                                         tasks_completed=tasks_completed, study_hours=study_hours)
                db.session.add(perf)
        
        db.session.commit()
        print(f"✅ تم إنشاء بيانات أداء لـ {len(users)} مستخدم (30 يوم لكل مستخدم)")

        # ==================== 4. المناقشات والردود ====================
        discussion_titles = [
            ("سؤال عن المحاضرة الأولى", "هل يمكن شرح نقطة كذا مرة أخرى؟"),
            ("ملخص رائع", "أريد مشاركة ملخص رائع للمادة"),
            ("استفسار عن الواجب", "موعد تسليم الواجب إمتى؟"),
            ("مصادر إضافية", "في مصادر مفيدة خارجية للمادة؟"),
            ("تجميع أسئلة", "حد عنده أسئلة سنوات سابقة؟"),
        ]
        
        for course in courses[:10]:
            for i in range(random.randint(2, 4)):
                user = random.choice(users)
                title = random.choice(discussion_titles)[0]
                content = random.choice(discussion_titles)[1]
                discussion = Discussion(title=title, content=content, course_id=course.id, user_id=user.id,
                                       created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)))
                db.session.add(discussion)
                db.session.flush()
                
                # إضافة ردود
                for j in range(random.randint(1, 3)):
                    replier = random.choice(users)
                    reply = DiscussionReply(content=f"رد رقم {j+1} على المناقشة: {content[:50]}", 
                                           discussion_id=discussion.id, user_id=replier.id)
                    db.session.add(reply)
        
        db.session.commit()
        print(f"✅ تم إنشاء مناقشات وردود للمواد")

        # ==================== 5. البطاقات التعليمية ====================
        flashcard_sets = []
        for user in users[:10]:
            for i in range(2):
                fset = FlashcardSet(title=f"بطاقات {user.full_name} - المجموعة {i+1}", user_id=user.id)
                db.session.add(fset)
                db.session.flush()
                flashcard_sets.append(fset)
                
                for j in range(5):
                    card = Flashcard(question=f"سؤال {j+1} للمجموعة {i+1}", 
                                    answer=f"إجابة السؤال {j+1} للمجموعة {i+1}", 
                                    set_id=fset.id)
                    db.session.add(card)
        
        db.session.commit()
        print(f"✅ تم إنشاء {len(flashcard_sets)} مجموعة بطاقات تعليمية")

        # ==================== 6. محاضرات سابقة مسجلة ====================
        for i, course in enumerate(courses[:8]):
            room = ClassroomSession(room_name=f"شرح {course.name} - {datetime.now().strftime('%d/%m')}",
                                   teacher_id=users[0].id if i % 2 == 0 else users[1].id, course_id=course.id,
                                   is_active=False, created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15)))
            db.session.add(room)
        
        db.session.commit()
        print(f"✅ تم إنشاء محاضرات سابقة مسجلة")

        # ==================== 7. إشعارات تجريبية ====================
        notifications_text = [
            "مرحباً بك في Study Hub! ابدأ رحلة التعلم الآن 🎉",
            "تم إضافة مادة جديدة: الذكاء الاصطناعي 🤖",
            "لا تنسى تحديث ملفك الشخصي 📝",
            "شارك زملاءك في المناقشات العلمية 💬",
            "يمكنك الآن إنشاء بطاقات تعليمية خاصة بك 🃏",
        ]
        
        for user in users[:15]:
            for note in notifications_text[:3]:
                notif = Notification(user_id=user.id, message=note, link="/dashboard", is_read=False,
                                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)))
                db.session.add(notif)
        
        db.session.commit()
        print(f"✅ تم إنشاء إشعارات تجريبية")

        print("\n" + "="*50)
        print("🎉 تمت تغذية قاعدة البيانات بنجاح!")
        print(f"📊 ملخص:")
        print(f"   - {len(users)} مستخدم")
        print(f"   - {len(courses)} مادة")
        print(f"   - {len(users) * 30} سجل أداء")
        print(f"   - مناقشات متعددة")
        print(f"   - {len(flashcard_sets)} مجموعة بطاقات")
        print("="*50)

if __name__ == "__main__":
    seed_database()