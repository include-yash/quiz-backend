import psycopg2
from flask import g
import click
import os

# PostgreSQL Database URL (Replace with Railway's connection string)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(DATABASE_URL)
        g.db.autocommit = True
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open('schema.sql', 'r') as f:
        cursor = db.cursor()
        cursor.execute(f.read())
        db.commit()
        cursor.close()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the PostgreSQL database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)