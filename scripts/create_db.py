import psycopg2
import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME', 'my_database')
DB_USER = os.environ.get('DB_USER', 'my_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'my_password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 5432)

with psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT) as conn:
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute('CREATE DATABASE Ingredients')
    cursor.close()
    conn.close()
