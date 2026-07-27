import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY',SECRET_KEY)
    JWT_TOKEN_LOCATION=['cookies']
    JWT_COOKIE_SECURE=True
    JWT_REFRESH_COOKIE_PATH='/refresh'
    JWT_COOKIE_CSRF_PROTECT=True
    JWT_COOKIE_HTTPONLY=True
    JWT_COOKIE_SAMESITE='Lax'
    JWT_ACCESS_CSRF_HEADER_NAME='X-CSRF-TOKEN'
    JWT_REFRESH_CSRF_HEADER_NAME='X-CSRF-TOKEN'
    GROQ_API_KEY=os.getenv('GROQ_API_KEY')
    RESET_TOKEN_MAX_AGE=int(os.getenv("RESET_TOKEN_MAX_AGE", 900))
    MAIL_SERVER=os.getenv("MAIL_SERVER")
    MAIL_PORT=int(os.getenv("MAIL_PORT") or 25)
    MAIL_USE_TLS=bool(os.getenv("MAIL_USE_TLS"))
    MAIL_USE_SSL=False
    MAIL_USERNAME=os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER") or "do-not-reply@pass-reset-resumeforger.com"
    )

    if os.getenv('CACHE_REDIS_URL'):
        CACHE_TYPE = 'RedisCache'
        CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL')
        CACHE_DEFAULT_TIMEOUT = 300
    else:
        CACHE_TYPE = 'SimpleCache'
        CACHE_DEFAULT_TIMEOUT = 300
