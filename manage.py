import os
import unittest

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def create_tables():
    """Create database tables"""
    db.create_tables([User])

@manager.command
def runserver():
    """Run the development server"""
    app.run(host='0.0.0.0', port=5000, debug=True)


@manager.command
def seed():
    """Seed the database with test data."""
    user = User(username='test_user', email='test@test.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    manager.run()