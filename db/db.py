import psycopg2
from psycopg2.extras import DictCursor
from flask import g
from flask.cli import with_appcontext
import click
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db():
    """Get database connection"""
    if 'db' not in g:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        try:
            g.db = psycopg2.connect(
                db_url,
                cursor_factory=DictCursor
            )
            g.db.autocommit = True
        except psycopg2.OperationalError as e:
            raise RuntimeError(f"Failed to connect to database: {e}") from e
    
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with schema"""
    db = get_db()
    with db.cursor() as cursor:
        with open('schema.sql', 'r') as f:
            cursor.execute(f.read())

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database"""
    try:
        init_db()
        click.echo('Initialized the database.')
    except Exception as e:
        click.echo(f'Error: {e}', err=True)

def init_app(app):
    """Register with the Flask application"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)