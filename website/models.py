from email.policy import default
from time import timezone

from sqlalchemy import Index, PrimaryKeyConstraint
from werkzeug.security import generate_password_hash
from . import db
from datetime import datetime, UTC
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature,SignatureExpired
from flask import current_app



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active_flag = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(UTC))

    tiers = db.Column(db.String(50), default='free') #free or premium tier
    credits = db.Column(db.Integer, default=100) #free users are given 100 credits
    credits_consumed = db.Column(db.Integer, default=0)
    last_reset_credit = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(UTC))

    generations = db.relationship('Generation', backref='user', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')

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

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tier = db.Column(db.String(50)) #free or premium tier
    plan = db.Column(db.String(50)) # 1000 AI Credits /5000 /10000
    remaining_credits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(UTC))

    def is_active(self):
        if not self.remaining_credits:
            return False # free users return false
        return self.remaining_credits >= 100 #Only return true  the users with more than 100 remaining credits

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(UTC))
