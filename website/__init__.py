
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from .config import Config


db = SQLAlchemy()
migrate = Migrate()
cors = CORS(supports_credentials=True)
jwt = JWTManager()
cache = Cache()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app,db)
    cors.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')


    with app.app_context():
        db.create_all()
    

    return app
