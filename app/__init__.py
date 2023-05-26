import logging
import os

from flask import Flask
from peewee import PostgresqlDatabase
from config import Config, DevelopmentConfig, ProductionConfig, TestConfig
from flask_wtf.csrf import CSRFProtect
from playhouse.flask_utils import FlaskDB

csrf = CSRFProtect()

def db_initialize(environment='dev'):
    app = Flask(__name__)
    if 'prod' == environment:
        app.config.from_object(ProductionConfig)
    elif 'test' == environment:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    database = PostgresqlDatabase(
        app.config['POSTGRES_NAME'],
        user=app.config['POSTGRES_USER'],
        password=app.config['POSTGRES_PASSWORD'],
        host=app.config['POSTGRES_HOST'],
        port=app.config['POSTGRES_PORT'],
    )
    logger = logging.getLogger(Config.LOGGER_NAME)
    logger.debug(f"DB initalize complete: {app.config['POSTGRES_NAME']}.")
    return database


def create_app(environment):
    app = Flask(__name__)
    if 'prod' == environment:
        app.config.from_object(ProductionConfig)
    elif 'test' == environment:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    csrf.init_app(app)

    # Create a custom logger for the Flask app
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] - %(message)s")
    rootLogger = logging.getLogger(DevelopmentConfig.LOGGER_NAME)
    rootLogger.setLevel(logging.DEBUG)

    # Add a handler to log to a file
    logPath = DevelopmentConfig.LOGGER_PATH
    fileName = os.path.basename(__file__)
    fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName), "w")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    # Stream the logs to std out too
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    with app.app_context():
        # Note: import * is only allowed at module level
        from .api import user_bp
        from .api import merchant_bp
        from .api import order_bp
        api_version = "v1"
        app.register_blueprint(user_bp, url_prefix=f'/api/{api_version}/user')
        app.register_blueprint(merchant_bp, url_prefix=f'/api/{api_version}/merchant')
        app.register_blueprint(order_bp, url_prefix=f'/api/{api_version}/order')
        csrf.exempt(user_bp)    
        csrf.exempt(merchant_bp)   
        csrf.exempt(order_bp) 
        rootLogger.debug("API blueprints added.")
        
    return app