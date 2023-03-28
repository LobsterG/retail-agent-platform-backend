import psycopg2
import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_NAME = os.environ.get('POSTGRES_NAME', 'shop_db')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'my_password')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)

with psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, port=POSTGRES_PORT) as conn:
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute('CREATE DATABASE shop_db')
    cursor.close()
    conn.close()
