import os
import time
import logging
from flask import g
from flask.cli import with_appcontext
import click
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from sqlalchemy import event

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global SQLAlchemy engine variable
_engine = None

def init_connection_pool():
    """
    Initialize the SQLAlchemy connection pool with production-ready settings.
    """
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        try:
            _engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,             # Max persistent connections
                max_overflow=20,          # Extra temporary connections
                pool_timeout=30,          # Wait time before raising timeout error
                pool_recycle=1800,        # Recycle connections every 30 min
                pool_pre_ping=True,       # Validate connection before use
                future=True
            )
            logger.info("✅ SQLAlchemy engine (connection pool) created successfully.")

            @event.listens_for(_engine, "checkout")
            def log_checkout(dbapi_connection, connection_record, connection_proxy):
                logger.info("🔓 Connection checked out from pool.")

            @event.listens_for(_engine, "checkin")
            def log_checkin(dbapi_connection, connection_record):
                logger.info("🔁 Connection returned to pool.")

            # Optional: Warm-up 2 connections
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("🔥 Connection pool warmed up.")

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to create SQLAlchemy engine: {e}")
            raise

def get_db_engine():
    """
    Returns the global SQLAlchemy engine, initializes if necessary.
    """
    global _engine
    if _engine is None:
        init_connection_pool()
    return _engine

def get_db():
    """
    Get a SQLAlchemy Connection from the engine and attach it to Flask's `g` context.
    """
    if 'db_conn' not in g:
        engine = get_db_engine()
        try:
            t0 = time.time()
            conn = engine.connect()  # Use SQLAlchemy connection
            elapsed = time.time() - t0

            if elapsed > 0.1:
                logger.warning(f"⚠️ Slow connection retrieval: {elapsed:.4f}s")
            else:
                logger.info(f"✅ Connection retrieved in {elapsed:.4f}s")

            g.db_conn = conn

        except SQLAlchemyError as e:
            raise RuntimeError(f"❌ Could not retrieve DB connection: {e}")

    return g.db_conn

def close_db(e=None):
    """
    Return the DB connection to the pool.
    """
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        try:
            db_conn.close()  # SQLAlchemy connection object
            logger.info("🔒 Connection returned to pool.")
        except Exception as e:
            logger.error(f"❌ Error closing DB connection: {e}")

def init_db():
    """
    Run schema.sql to initialize the DB (e.g., from CLI).
    """
    conn = get_db()
    try:
        with open('schema.sql', 'r') as f:
            logger.info("🛠️ Initializing database schema...")
            sql = f.read()
            conn.execute(text(sql))
            logger.info("✅ Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Error initializing schema: {e}")
        raise



@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    CLI command to initialize the database.
    """
    try:
        init_db()
        click.echo('✅ Initialized the database.')
    except Exception as e:
        click.echo(f'❌ Error: {e}', err=True)

def init_app(app):
    """
    Register DB functions with Flask app context and CLI.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    init_connection_pool()
