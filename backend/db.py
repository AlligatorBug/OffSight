import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class CachedFixture(Base):
    __tablename__ = "cached_fixtures"

    fixture_id = Column(Integer, primary_key=True)
    data       = Column(JSON, nullable=False)
    synced_at  = Column(DateTime(timezone=True), nullable=False)


class CachedSquad(Base):
    __tablename__ = "cached_squads"

    fixture_id = Column(Integer, primary_key=True)
    data       = Column(JSON, nullable=False)
    synced_at  = Column(DateTime(timezone=True), nullable=False)


def create_tables():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
