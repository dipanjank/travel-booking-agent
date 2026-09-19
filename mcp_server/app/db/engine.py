import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=5)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
