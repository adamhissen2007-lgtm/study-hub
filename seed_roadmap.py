import json
from app import app, db, CareerTrack, Skill, Project

def seed_roadmap():
    with app.app_context():
        print("🌱 جاري إنشاء المسارات التعليمية...")

        # حذف البيانات القديمة
        try:
            db.session.query(Skill).delete()
            db.session.query(CareerTrack).delete()
            db.session.commit()
            print("🗑️ تم حذف البيانات القديمة")
        except:
            print("⚠️ قاعدة البيانات جديدة")

        # 1. مسارات التخصص
        tracks_data = [
            ('🧑‍💻 هندسة البرمجيات (Software Engineering)', 'fa-code', 'من الصفر لبناء تطبيقات الويب والمحمول والأنظمة الكبيرة'),
            ('🧠 الذكاء الاصطناعي (AI)', 'fa-brain', 'تعلم الآلة وعلوم البيانات وبناء نماذج ذكية'),
            ('🛡️ الأمن السيبراني (Cyber Security)', 'fa-shield-alt', 'حماية الأنظمة والشبكات واكتشاف الثغرات'),
            ('📊 تحليل البيانات (Data Analysis)', 'fa-chart-line', 'اكتشاف الرؤى واتخاذ القرارات من البيانات'),
        ]
        
        tracks = {}
        for name, icon, desc in tracks_data:
            track = CareerTrack(name=name, icon=icon, description=desc)
            db.session.add(track)
            db.session.flush()
            tracks[name] = track.id
        db.session.commit()
        print(f"✅ تم إنشاء {len(tracks)} مسار وظيفي.")

        # 2. المهارات (بصيغة JSON صحيحة)
        skills_data = [
            # مسار هندسة البرمجيات - سنة أولى ترم أول
            ('أساسيات البرمجة (Python)', '🧑‍💻 هندسة البرمجيات (Software Engineering)', 1, 1, 1, 40,
             '[{"title": "Python for Beginners", "url": "https://youtu.be/eWRfhZUzrAc", "type": "video"}]',
             'مشروع: تطبيق آلة حاسبة بسيطة', '[]'),
             
            ('Problem Solving', '🧑‍💻 هندسة البرمجيات (Software Engineering)', 1, 1, 2, 30,
             '[{"title": "Problem Solving Course", "url": "https://youtu.be/coqQwbDezUA", "type": "video"}]',
             'حل 30 مسألة على موقع Codeforces', '[1]'),
             
            ('Git & GitHub', '🧑‍💻 هندسة البرمجيات (Software Engineering)', 1, 1, 3, 15,
             '[{"title": "Git Crash Course", "url": "https://youtu.be/Q6G-J54vgKc", "type": "video"}]',
             'إنشاء أول Repository ورفع مشروع', '[1,2]'),
            
            # مسار الذكاء الاصطناعي - سنة أولى ترم أول
            ('Python for Data Science', '🧠 الذكاء الاصطناعي (AI)', 1, 1, 1, 40,
             '[{"title": "Python for Data Science", "url": "https://youtu.be/xiXk8T_yIX4", "type": "video"}]',
             'تحليل بيانات CSV باستخدام Pandas', '[]'),
            
            ('Mathematics for ML', '🧠 الذكاء الاصطناعي (AI)', 1, 1, 2, 35,
             '[{"title": "Linear Algebra Course", "url": "https://youtu.be/fNk_zzaMoSs", "type": "playlist"}]',
             'تنفيذ Linear Regression من الصفر', '[4]'),
            
            # مسار الأمن السيبراني - سنة أولى ترم أول
            ('Networking Basics', '🛡️ الأمن السيبراني (Cyber Security)', 1, 1, 1, 30,
             '[{"title": "Computer Networks", "url": "https://youtu.be/qiQR5rTS3wQ", "type": "video"}]',
             'تحليل حزم الشبكة باستخدام Wireshark', '[]'),
            
            ('Linux Fundamentals', '🛡️ الأمن السيبراني (Cyber Security)', 1, 1, 2, 25,
             '[{"title": "Linux Basics", "url": "https://youtu.be/ROjZy1WbCIA", "type": "video"}]',
             'تنفيذ الأوامر الأساسية في Linux', '[6]'),
            
            # مسار تحليل البيانات - سنة أولى ترم أول
            ('Excel for Data Analysis', '📊 تحليل البيانات (Data Analysis)', 1, 1, 1, 25,
             '[{"title": "Excel Skills", "url": "https://youtu.be/Vl0H-qTclOg", "type": "video"}]',
             'تحليل مبيعات باستخدام Pivot Tables', '[]'),
            
            ('SQL for Analysis', '📊 تحليل البيانات (Data Analysis)', 1, 1, 2, 30,
             '[{"title": "SQL Course", "url": "https://youtu.be/9Pzj7Aj25lw", "type": "video"}]',
             'استخراج تقارير من قاعدة بيانات', '[8]'),
        ]
        
        for title, track_name, level, sem, order_val, duration, resources_json, project, prereqs in skills_data:
            track_id = tracks.get(track_name)
            if track_id:
                # تحويل الـ prerequisites من string to list
                prereq_list = [int(x) for x in prereqs.strip('[]').split(',') if x.strip()]
                
                skill = Skill(
                    title=title,
                    description=f'مهارة في {track_name}: {title}',
                    track_id=track_id,
                    level=level,
                    semester=sem,
                    order=order_val,
                    duration_hours=duration,
                    resources=resources_json,
                    project_idea=project,
                    prerequisites=json.dumps(prereq_list)
                )
                db.session.add(skill)
        
        db.session.commit()
        print(f"✅ تم إضافة {len(skills_data)} مهارة جديدة.")
        print("\n🎉 تم تجهيز الـ Career Roadmap بنجاح!")

if __name__ == '__main__':
    seed_roadmap()