from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/token', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()

        if not user or not check_password_hash(data.get('password'), user.password) :
            return jsonify({'error': 'Wrong email or password!'})
        
        if not user.is_active:
            return jsonify({'error': 'Your account has been suspended, please contact support!'})
        
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=5))
        refresh = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=5))

        response = jsonify({
            'msg': 'Login Successful'
        })
        set_access_cookies(response, token)
        set_refresh_cookies(response, refresh)

        return response, 200
    
    except Exception as e:
        return jsonify({'error': str(e)})

@auth.route('/register', methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided!'})
            user = User.query.filter_by(email=data.get('email')).first()
            if user:
                return jsonify({'error': 'The user with the entered email already exist!'})
            if not data.get('email') and not data.get('password'):
                return jsonify({'error': 'email and password are required!'}) 
            if data.get('password') != data.get('confirmed'):
                return jsonify({'error': 'password mismatch!'}) 

            new_user = User(email=data.get('email'), password=generate_password_hash(data.get('password'))) 
            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'msg': 'user successfully registered, login to proceed!'
            })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        })

