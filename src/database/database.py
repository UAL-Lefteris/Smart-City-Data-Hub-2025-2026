from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from typing import Generator

from .config import Config
from src.core.models.property import Base


class Database:
    def __init__(self):
        self.postgres_engine = create_engine(
            Config.get_sql_url(),
            echo=True,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.postgres_engine,
        )

        self.mongo_client = MongoClient(Config.get_mongodb_url())
        self.mongo_db = self.mongo_client[Config.MONGODB_NAME]

    def get_postgres_session(self) -> Generator:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_mongo_db(self):
        return self.mongo_db

    def create_postgres_tables(self):
        Base.metadata.create_all(self.postgres_engine)

    def close(self):
        self.postgres_engine.dispose()
        self.mongo_client.close()


database = Database()