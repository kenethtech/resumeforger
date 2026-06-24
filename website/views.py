from flask import Blueprint, render_template, redirect

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/login')
def login_page():
    return render_template('login.html')

@views.route('/signup')
def signup():
    return render_template('signup.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route("/contact")
def contact():
    return render_template("contact.html")