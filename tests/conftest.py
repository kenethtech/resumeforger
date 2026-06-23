import pytest
from website import create_app
from website import db
from website.models import User

@pytest.fixture
def app():
    app = create_app()

    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": False,
    })


    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_user(app):
    user = User(email="test@example.com", password="password")
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        
        db.session.refresh(user)

        return {
            "id": user.id,
            "email": user.email,
        }
