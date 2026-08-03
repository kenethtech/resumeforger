from flask import Blueprint, flash, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user, login_required
from .models import Subscription
import os
from dotenv import load_dotenv

load_dotenv()

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)

@views.route('/login')
def login_page():
    return render_template('login.html', user=current_user)

@views.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    return render_template('signup.html', user=current_user)

@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


@views.route("/contact")
def contact():
    return render_template("contact.html", user=current_user)

@views.route('/subscribe')
@login_required
@jwt_required()
def subscribe():
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    if current_user.subscriptions and subscription.is_active:
        flash("You already have an active subscription.", "info")
        return redirect(url_for('views.home'))
    paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
    return render_template("subscribe.html", user=current_user, paypal_client_id=paypal_client_id)

@views.route('/reset-password')
def reset_password():
    return render_template("reset_password.html", user=current_user)
