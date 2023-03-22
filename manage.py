import os
import unittest
import click

from flask.cli import FlaskGroup, with_appcontext
from flask_migrate import Migrate
from app import create_app, db
from app.models.users import User
from app.models.countries import Country
from scripts.seed import UserFactory

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate()

migrate.init_app(app, db)

@cli.command()
def create_tables():
    """Create database tables"""
    db.create_tables([Country])
    db.create_tables([User])
    print("Tables created!")

@cli.command()
def drop_tables():
    """Drop database tables"""
    db.drop_tables([User])
    db.drop_tables([Country])
    print("Tables droped!")

@cli.command()
def runserver():
    """Run the development server"""
    app.run(host='0.0.0.0', port=5000, debug=True)

@cli.command()
@click.option('--count')
def seed(**kwargs):
    """Seed the database with test data."""
    # Country.seed()
    User.seed(int(kwargs['count']))
    print("Database seeded!")


if __name__ == '__main__':
    cli()
