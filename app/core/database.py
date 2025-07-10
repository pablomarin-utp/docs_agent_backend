from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Environment variables
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT", "5432")
DBNAME = os.getenv("DB_NAME", "postgres")

# Supabase requires SSL
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# OPTIMIZADO: Pool más pequeño para 512MB RAM
engine = create_engine(
    DATABASE_URL,
    pool_size=2,           # Reducido de 10 → 2
    max_overflow=5,        # Reducido de 20 → 5
    pool_pre_ping=True,
    pool_recycle=1800,     # Reducido de 3600 → 1800 (30min)
    connect_args={
        "connect_timeout": 10,
        "application_name": "ai-docs-agent"
    },
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test Supabase connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Supabase connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Error connecting to Supabase: {e}")
        raise

def check_existing_tables():
    """Check if your existing Supabase tables are available."""
    try:
        with engine.connect() as conn:
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('users', 'conversations', 'messages')
            """)
            
            result = conn.execute(tables_query)
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                logger.info(f"✅ Found existing Supabase tables: {existing_tables}")
                return True
            else:
                logger.warning("⚠️ No expected tables found in Supabase")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error checking Supabase tables: {e}")
        raise

def init_db():
    """Check Supabase connection and tables - DON'T create new ones."""
    try:
        test_connection()
        check_existing_tables()
        logger.info("✅ Supabase database check completed")
        return True
    except Exception as e:
        logger.error(f"❌ Error with Supabase database: {e}")
        raise