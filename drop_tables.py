import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Create engine using the URL from alembic.ini
engine = create_engine("postgresql://postgres:12345@localhost/editube")

# Drop tables
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS projectanalytics CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS notifications CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS comments CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS activity_feed CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS project_collaborators CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS videos CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.commit() 