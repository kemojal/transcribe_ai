from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

# Load database URL from environment variable
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345@localhost/transcribe_ai"
# SQLALCHEMY_DATABASE_URL = "postgresql://ditally-db_owner:uJfZYwcIz6d5@ep-royal-wood-a1on9e6p.ap-southeast-1.aws.neon.tech/editube_db?sslmode=require"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

def get_db():
    db = None
    retries = 5
    while retries > 0:
        try:
            db = SessionLocal()
            yield db
            db.close()
            break
        except OperationalError:
            retries -= 1
            time.sleep(5)  # Wait before retrying
    if db is None:
        raise RuntimeError("Could not connect to the database after several attempts.")