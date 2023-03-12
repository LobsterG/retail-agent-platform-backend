import os
import unittest

from flask.cli import FlaskGroup
from flask_migrate import Migrate
from app import create_app, db
from app.models import User

app = create_app()
cli = FlaskGroup(app)
migrate = Migrate()

migrate.init_app(app, db)

@cli.command()
def create_tables():
    """Create database tables"""
    db.create_tables([User])

@cli.command()
def runserver():
    """Run the development server"""
    app.run(host='0.0.0.0', port=5000, debug=True)


@cli.command()
def seed():
    """Seed the database with test data."""
    user = User(username='test_user', email='test@test.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    cli()
