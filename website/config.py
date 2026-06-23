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

    if os.getenv('CACHE_REDIS_URL'):
        CACHE_TYPE = 'RedisCache'
        CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL')
        CACHE_DEFAULT_TIMEOUT = 300
    else:
        CACHE_TYPE = 'SimpleCache'
        CACHE_DEFAULT_TIMEOUT = 300
