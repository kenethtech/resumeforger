from sqlalchemy import Index
from werkzeug.security import generate_password_hash
from . import db
from datetime import datetime, UTC
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature,SignatureExpired
from flask import current_app



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active_flag = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    generations = db.relationship('Generation', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_active(self):
        return self.is_active_flag

    def set_password(self, new_pass:str): #A method for updating/setting new passwords
        self.password = generate_password_hash(new_pass, method='pbkdf2:sha256')
        return self.password
    
    def generate_reset_password_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt=self.password)
    
    @staticmethod
    def validate_reset_password_token(token:str, user_id:int):

        user = db.session.get(User, user_id)
        if user is None:
            return None
        
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

        try:
            token_user_email = serializer.loads(
                token,
                max_age=current_app.config['RESET_TOKEN_MAX_AGE'],
                salt=user.password
            )
        
        except(BadSignature, SignatureExpired):
            return None
        
        if token_user_email != user.email:
            return None
        
        return user



class Generation(db.Model):
    __tablename__ = 'generations'

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_title = db.Column(db.String(50))
    document_type = db.Column(db.String(50))
    template_style = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    ats_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
