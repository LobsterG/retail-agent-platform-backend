from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from peewee import PostgresqlDatabase
from config import config

db = None

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)

    # Initialize database connection based on config settings
    global db
    db = PostgresqlDatabase(
        app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASSWORD'],
        host=app.config['DATABASE_HOST'],
        port=app.config['DATABASE_PORT'],
        autorollback=True,
        autocommit=True
    )

    with app.app_context():
        from .api import bp as api_bp

        app.register_blueprint(api_bp, url_prefix='/api')

        return app