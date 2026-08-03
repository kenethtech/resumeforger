
from dotenv import load_dotenv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from .config import Config
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mailman import Mail

load_dotenv()  # Load environment variables from .env file

db = SQLAlchemy()
migrate = Migrate()
cors = CORS(supports_credentials=True)
jwt = JWTManager()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("REDIS_URL")
)
email = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app,db)
    cors.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    email.init_app(app)

    from .views import views
    from .auth import auth
    from .agent import agent
    from .paypal_payments import paypal_payments

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(agent, url_prefix='/')
    app.register_blueprint(paypal_payments, url_prefix='/')


    with app.app_context():
        db.create_all()

    
    #Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'views.login_page' #the redirect for @login_required
    login_manager.init_app(app)

    import website.models as model
    @login_manager.user_loader
    def load_user(user_id):
        return model.User.query.get(int(user_id))

    

    return app
