import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
    
    POSTGRES_NAME = os.environ.get('POSTGRES_NAME', 'shop_db')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    
    LOGGER_NAME = 'app_logger'
    LOGGER_PATH = 'app/logs'

class DevelopmentConfig(Config):
    DEBUG = True
    POSTGRES_NAME = os.environ.get('POSTGRES_NAME', 'shop_db') + '_dev'

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    POSTGRES_NAME = os.environ.get('POSTGRES_NAME', 'shop_db') + '_test'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
