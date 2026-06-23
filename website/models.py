from . import db
from datetime import datetime, UTC



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active_flag = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    generations = db.relationship('Generation', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_active(self):
        return self.is_active_flag

class Generation(db.Model):
    __tablename__ = 'generations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_title = db.Column(db.String(50))
    document_type = db.Column(db.String(50))
    template_style = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    ats_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
