import psycopg2
from psycopg2.extras import DictCursor
from flask import g
from flask.cli import with_appcontext
import click
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
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
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with db.cursor() as cursor:
        with open('schema.sql', 'r') as f:
            logger.info("Initializing database schema")
            cursor.execute(f.read())
        logger.info("Database schema initialized successfully")

@click.command('init-db')
@with_appcontext
def init_db_command():
    try:
        init_db()
        click.echo('Initialized the database.')
    except Exception as e:
        click.echo(f'Error: {e}', err=True)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)