import os
import unittest
import click
import time

from flask.cli import FlaskGroup, with_appcontext
from flask_migrate import Migrate
from app import db_initialize
from app.models import *


@click.group()
def cli():
    pass

@cli.command()
@click.option('--env', default='dev', help='Environment name')
def create_tables(**kwargs):
    """Create database tables"""
    db = db_initialize(kwargs['env'])
    with db.bind_ctx(MODELS):
        from app.models import BaseModel
        BaseModel.update_env(kwargs['env'])
        db.create_tables(MODELS)
    print("Tables created!")

@cli.command()
@click.option('--env', default='dev', help='Environment name')
def drop_tables(**kwargs):
    """Drop database tables"""
    db = db_initialize(kwargs['env'])
    with db.bind_ctx(MODELS):
        from app.models import BaseModel
        BaseModel.update_env(kwargs['env'])
        db.drop_tables(MODELS)
    print("Tables droped!")

@cli.command()
@click.option('--env', default='dev', help='Environment name')
def runserver(**kwargs):
    """Run the development server"""
    from app import create_app
    app = create_app(kwargs['env'])
    cli = FlaskGroup(app)
    app.run(host='0.0.0.0', port=5000, debug=True)


@cli.command()
def migrate_db():
    migrate = Migrate()
    migrate.init_app(app, db)


@cli.command()
@click.option('--count')
@click.option('--env', default='dev', help='Environment name')
def seed(**kwargs):
    """Seed the database with test data."""
    # db = db_initialize(kwargs['env'])
    # with db.bind_ctx(MODELS):
    #     from app.models import BaseModel
    #     BaseModel.update_env(kwargs['env'])
    fake_countries = Country.seed(int(kwargs['count']))
    
    fake_users, fake_merchants, fake_products, fake_orders = [], [], [], []
    for country in fake_countries:
        tmp_user = User.seed(country_code=country)
        fake_users.append(tmp_user)
        fake_merchants.append(Merchant.seed(user_id=tmp_user[0], country_code=country))
    
    for user in fake_users:
        fake_orders.append(Order.seed(user_id=user[0]))

    for i, merchant in enumerate(fake_merchants):
        fake_products.append(Product.seed(merchant_id=merchant[0]))
        tmp_order_item = OrderItem.seed(product_id=fake_products[i][0], order_id=fake_orders[i][0])
        
    print("Database seeded!")


if __name__ == '__main__':
    cli()
