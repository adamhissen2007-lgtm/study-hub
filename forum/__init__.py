from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# إنشاء تطبيق منفصل للمنتدى
forum_app = Flask(__name__, template_folder='templates', static_folder='static')

# تحميل الإعدادات من ملف flaskbb.cfg
forum_app.config.from_pyfile('flaskbb.cfg')

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy(forum_app)

# استيراد النماذج
from forum import models

# دالة لإنشاء الجداول
def init_forum_db():
    with forum_app.app_context():
        db.create_all()
        print("✅ تم إنشاء جداول المنتدى!")
        
        from forum.models import ForumCategory
        if ForumCategory.query.count() == 0:
            categories = [
                ForumCategory(name='📚 مناقشات المواد', description='ناقش المواد الدراسية واستفسر عن أي شيء', order=1),
                ForumCategory(name='💬 المجتمع الطلابي', description='تعارف، نصائح، وتجارب دراسية', order=2),
                ForumCategory(name='📢 الإعلانات', description='إعلانات هامة من إدارة Study Hub', order=3),
                ForumCategory(name='❓ الأسئلة المتكررة', description='أسئلة وإجابات عن المنصة', order=4),
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            print("✅ تم إضافة الأقسام الافتراضية!")

# الصفحة الرئيسية للمنتدى
@forum_app.route('/')
def forum_index():
    from forum.models import ForumCategory
    categories = ForumCategory.query.order_by(ForumCategory.order).all()
    return render_template('forum_index.html', categories=categories)