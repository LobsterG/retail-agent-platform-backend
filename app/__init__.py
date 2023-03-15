from flask import Flask
from peewee import PostgresqlDatabase
from config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = PostgresqlDatabase(
    'ingredients',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    password='postgres',  # Ditto.
    host='localhost') 
# db = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    csrf.init_app(app)
    
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
    print("DB initalize complete:", type(db))

    with app.app_context():
        # Import models after initializing the database
        from app.models import Ingredient

        from .api.ingredient.views import ingredient_bp
        app.register_blueprint(ingredient_bp, url_prefix='/api/ingredient')
        csrf.exempt(ingredient_bp)

    return app