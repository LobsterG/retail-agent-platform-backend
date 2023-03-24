import logging
import os

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

    # Create a custom logger for the Flask app
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] - %(message)s")
    rootLogger = logging.getLogger(DevelopmentConfig.LOGGER_NAME)
    rootLogger.setLevel(logging.DEBUG)

    # Add a handler to log to a file
    logPath = DevelopmentConfig.LOGGER_PATH
    fileName = os.path.basename(__file__)
    fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    # Stream the logs to std out too
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    
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
        from app.models.users import User

        from .api import user_bp
        app.register_blueprint(user_bp, url_prefix='/api/user')
        csrf.exempt(user_bp)
        rootLogger.info("API blueprints added.")

    return app