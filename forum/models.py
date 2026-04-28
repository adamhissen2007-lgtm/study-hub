from forum import db
from datetime import datetime

class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    topics = db.relationship('ForumTopic', backref='category', lazy='dynamic')

class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'))
    
    posts = db.relationship('ForumPost', backref='topic', lazy='dynamic', cascade='all, delete-orphan')

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_answer = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'))