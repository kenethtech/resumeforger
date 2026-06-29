from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from . import db
from flask_login import login_user

auth = Blueprint('auth', __name__)


@auth.route('/token', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()

        if not user or not check_password_hash(user.password, data.get('password')):
            return jsonify({'error': 'Wrong email or password!'}),400
        
        if not user.is_active:
            return jsonify({'error': 'Your account has been suspended, please contact support!'}),401
        
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=5))
        refresh = create_refresh_token(identity=str(user.id), expires_delta=timedelta(days=5))

        login_user(user, remember=True)

        response = jsonify({
            'msg': 'Login Successful'
        })
        set_access_cookies(response, token)
        set_refresh_cookies(response, refresh)

        return response, 200
    
    except Exception as e:
        return jsonify({'error': str(e)}),500

@auth.route('/register', methods=['POST'])
def register():
    try:
        
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided!'}),400
        user = User.query.filter_by(email=data.get('email')).first()

        if user:
            return jsonify({'error': 'The user with the entered email already exist!'}),401
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'email and password are required!'}),402
        if data.get('password') != data.get('confirmPassword'):
            return jsonify({'error': 'password mismatch!'}) ,403
            
        hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')

        new_user = User(email=data.get('email'), password=hashed_password) 
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'msg': 'user successfully registered, login to proceed!'
        }),201
        
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({
            'error': str(e)
        }),500
    
@auth.route('/refresh', methods=['POST'])
def refresh():
    current_user_id = get_jwt_identity()
    token = create_access_token(identity=current_user_id, expires_delta=timedelta(days=7))
    response = {'msg': 'Token refreshed'}
    set_access_cookies(response, token)
    
    return response, 201

@auth.route('/get-user', methods=['GET'])
@jwt_required()
def get_user():
   try:
        current_user_id = int(get_jwt_identity())
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return jsonify({
                'error': 'Unable to fetch user profile'
            }), 404
        return jsonify({
            'email': user.email
        }), 200
   
   except Exception as e:
       return jsonify({
           'error': str(e)
       }), 500

