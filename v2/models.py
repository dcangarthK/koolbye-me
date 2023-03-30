from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login_manager

db = SQLAlchemy()

class AdminLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"AdminLogin('{self.username}')"

class UserLogin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<AdminLogin %r>' % self.username
        
class Scam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    location = db.Column(db.String(50))
    tags = db.relationship('Tag', secondary='scam_tag', backref='scams')
    images = db.relationship('Image', backref='scam', lazy=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Scam {self.title}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    scam_id = db.Column(db.Integer, db.ForeignKey('scam.id'), nullable=False)

    def __repr__(self):
        return f'<Image {self.filename}>'

scam_tag = db.Table('scam_tag',
    db.Column('scam_id', db.Integer, db.ForeignKey('scam.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('admin_login.id'), nullable=False)
    author = db.relationship('AdminLogin', backref=db.backref('blogs', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Blog('{self.title}', '{self.created_at}')"