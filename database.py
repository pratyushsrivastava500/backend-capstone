from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database path
DATABASE_URL = "sqlite:///./app.db"

# Database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # SQL queries terminal me show hongi (debugging)
)

# Session maker
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()