import os
import unittest
import click

from flask.cli import FlaskGroup, with_appcontext
from flask_migrate import Migrate
from app import create_app, db
from app.models import Ingredient

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate()

migrate.init_app(app, db)

@cli.command()
def create_tables():
    """Create database tables"""
    db.create_tables([Ingredient])

@cli.command()
def runserver():
    """Run the development server"""
    app.run(host='0.0.0.0', port=5000, debug=True)

@cli.command()
def seed():
    """Seed the database with test data."""
    Ingredient.seed()

if __name__ == '__main__':
    cli()
