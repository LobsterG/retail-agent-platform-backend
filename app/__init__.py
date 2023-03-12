from flask import Flask
from peewee import PostgresqlDatabase
from config import DevelopmentConfig

db = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Initialize database connection based on config settings
    global db
    db = PostgresqlDatabase(
        app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        host=app.config['DB_HOST'],
        port=app.config['DB_PORT'],
        autorollback=True,
        autocommit=True
    )

    with app.app_context():
        # Import models after initializing the database
        from app.models import User

    #     from .api import bp as api_bp

    #     app.register_blueprint(api_bp, url_prefix='/api')

    return app