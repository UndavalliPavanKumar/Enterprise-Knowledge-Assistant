"""Database connection and session management"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging
from app.config import get_settings
from app.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connection and session creation"""

    def __init__(self):
        """Initialize database manager"""
        self.settings = get_settings()
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        """Get or create database engine"""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.settings.database_url,
                    echo=self.settings.sqlalchemy_echo,
                    poolclass=NullPool,  # Required for pgvector
                    pool_pre_ping=True,
                )
                logger.info("Database engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise

        return self._engine

    @property
    def session_factory(self):
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
        return self._session_factory

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database connection closed")


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = get_db_manager().get_session()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database on application startup"""
    db_manager = get_db_manager()
    db_manager.init_db()
    logger.info("Database initialization completed")
