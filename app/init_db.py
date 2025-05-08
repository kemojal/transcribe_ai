from sqlalchemy import create_engine, text
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    try:
        # Get database URL from environment variable
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            logger.error("DATABASE_URL environment variable is not set")
            return False
            
        logger.info(f"Connecting to database: {database_url.split('@')[0].split(':')[0]}://*****@*****")
        
        # Connect to the database
        engine = create_engine(database_url)
        
        # Create users table if it doesn't exist
        with engine.connect() as connection:
            logger.info("Creating users table if it doesn't exist")
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE
            )
            """))
            connection.commit()
            
            # Check if table was created
            result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
            if result.scalar():
                logger.info("Users table exists or was created successfully")
                return True
            else:
                logger.error("Failed to create users table")
                return False
                
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Initializing database...")
    success = init_database()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed") 