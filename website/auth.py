from flask import Blueprint, redirect, render_template, request, jsonify, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import UTC, datetime, timedelta
from . import db, limiter
from flask_login import login_required, login_user, logout_user, current_user
from .utils import send_reset_password_email


auth = Blueprint('auth', __name__)


@auth.route('/token', methods=['POST'])
@limiter.limit("3 per minute")
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
@limiter.limit("3 per minute")
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
@login_required
def get_user():
   try:
        current_user_id = int(get_jwt_identity())
        user = User.query.filter_by(id=current_user_id).first()

        credits_remaining = user.credits - user.credits_consumed or 0

        if not user:
            return jsonify({
                'error': 'Unable to fetch user profile'
            }), 404
        return jsonify({
            'email': user.email,
            'credits_remaining': credits_remaining,
            'plan': user.tiers
        }), 200
   
   except Exception as e:
       return jsonify({
           'error': str(e)
       }), 500
   
@auth.route('/logout')
@jwt_required()
@login_required
def logout():
    logout_user()
    response = jsonify({
        "msg": "Logout Successful!"
    })
    unset_jwt_cookies(response)
    return response, 200

@auth.route('/forget-password', methods=['POST'])
def forget_password():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('views.home'))
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()

        if not user:
            return jsonify({
                "error":"The user with the email you have entered does not exist!"
            })
        
        send_reset_password_email(user) #method for sending reset password instructions to user email
        
        return jsonify({"msg":"Kindly check your email for the password reset link!"})
    
    except Exception as e:
        return jsonify({'error':'Password reset failed! Try again'})

@auth.route('/request-reset-password/<token>/<int:user_id>', methods=['GET', 'POST']) #function to reset new password
def request_reset_password(token, user_id):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    
    user = User.validate_reset_password_token(token, user_id) # Validate if the token and user id are correct

    if not user:
        flash("The password reset link has expired! Try again!")
        return redirect(url_for('views.reset_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new-password')
        
        user.set_password(new_password)
        db.session.commit()

        flash('Password reset successful. You can now login using your new password!')

        return redirect(url_for('views.login_page'))
    
    

    return render_template('request_reset_password.html', user=current_user, token=token, user_id=user_id)
    

