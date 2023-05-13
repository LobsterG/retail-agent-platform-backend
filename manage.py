import os
import unittest
import click
import time

from flask.cli import FlaskGroup, with_appcontext
from flask_migrate import Migrate
from app import create_app, db
from app.models.users import User
from app.models.products import Product
from app.models.merchants import Merchant
from app.models.countries import Country
from app.models.orders import Order


app = create_app()
cli = FlaskGroup(app)
migrate = Migrate()

migrate.init_app(app, db)

@cli.command()
def create_tables():
    """Create database tables"""
    db.create_tables([Country])
    db.create_tables([User])
    db.create_tables([Merchant])
    db.create_tables([Product])
    db.create_tables([Order])
    print("Tables created!")

@cli.command()
def drop_tables():
    """Drop database tables"""
    db.drop_tables([Order])
    db.drop_tables([Product])
    db.drop_tables([Merchant])
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
    fake_countries = Country.seed(int(kwargs['count']))
    
    fake_users, fake_merchants, fake_products, fake_orders = [], [], [], []
    for country in fake_countries:
        tmp_user = User.seed(country_code=country)
        fake_users.append(tmp_user)
        fake_merchants.append(Merchant.seed(user_id=tmp_user[0], country_code=country))
    
    for user in fake_users:
        fake_orders.append(Order.seed(user_id=user[0]))

    for merchant in fake_merchants:
        fake_products.append(Product.seed(merchant_id=merchant[0]))
    print("Database seeded!")


if __name__ == '__main__':
    cli()
