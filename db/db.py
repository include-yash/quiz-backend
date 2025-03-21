import sqlite3
from flask import g
import click

DATABASE = 'quiz_app4.db'  # Replace with your database file name

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES,
            timeout=60  # Increase timeout to 60 seconds
        )
        g.db.row_factory = sqlite3.Row
        # Enable WAL mode
        g.db.execute('PRAGMA journal_mode=WAL;')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)