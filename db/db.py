import time
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import pool
from flask import g
from flask.cli import with_appcontext
import click
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool variable
connection_pool = None

def init_connection_pool(minconn=5, maxconn=30):
    """
    Initialize a PostgreSQL connection pool.
    """
    global connection_pool
    if connection_pool is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        try:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn,
                maxconn,
                dsn=db_url,
                cursor_factory=DictCursor
            )
            logger.info(f"✅ Connection pool created successfully with minconn={minconn} and maxconn={maxconn}")
        except Exception as e:
            logger.error(f"❌ Error creating connection pool: {e}")
            raise

def get_db():
    """
    Retrieve a database connection from the pool and attach it to Flask's 'g' object.
    """
    if 'db' not in g:
        if connection_pool is None:
            init_connection_pool()
        
        try:
            t0 = time.time()
            conn = connection_pool.getconn()
            elapsed = time.time() - t0

            if conn is None:
                raise RuntimeError("❌ No available DB connection in the pool")

            g.db = conn
            g.db.autocommit = True

            # Log how fast the connection was retrieved
            if elapsed > 0.1:
                logger.warning(f"⚠️ Slow connection retrieval from pool: {elapsed:.4f} seconds")
            else:
                logger.info(f"✅ Connection retrieved quickly from pool: {elapsed:.4f} seconds")

            # Optional: Show pool status (debug level)
            logger.debug(f"🔍 Pool status: used={len(connection_pool._used)}, available={len(connection_pool._pool)}")

        except psycopg2.OperationalError as e:
            raise RuntimeError(f"❌ Failed to get connection from pool: {e}") from e

    return g.db

def close_db(e=None):
    """
    Return the database connection to the pool at the end of a request.
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            connection_pool.putconn(db)
            logger.debug("🔁 Connection returned to pool")
        except Exception as e:
            logger.error(f"❌ Error returning connection to pool: {e}")

def init_db():
    """
    Initialize the database schema using schema.sql.
    """
    db = get_db()
    with db.cursor() as cursor:
        with open('schema.sql', 'r') as f:
            logger.info("🛠️ Initializing database schema...")
            cursor.execute(f.read())
            logger.info("✅ Database schema initialized successfully")

@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Flask CLI command to initialize the database via `flask init-db`.
    """
    try:
        init_db()
        click.echo('✅ Initialized the database.')
    except Exception as e:
        click.echo(f'❌ Error: {e}', err=True)

def init_app(app):
    """
    Register database functions with Flask app context and CLI.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # Proactively initialize the pool at app startup
    init_connection_pool()
