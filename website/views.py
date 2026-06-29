from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required
from flask_login import current_user, login_required

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