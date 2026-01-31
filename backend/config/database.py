"""
MongoDB Database Connection and Configuration
Motor async driver for MongoDB with connection management
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Global MongoDB client
_mongo_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/job_tracker")
MAX_POOL_SIZE = int(os.getenv("MONGO_MAX_POOL_SIZE", "10"))
MIN_POOL_SIZE = int(os.getenv("MONGO_MIN_POOL_SIZE", "1"))


async def connect_db() -> AsyncIOMotorDatabase:
    """
    Establish connection to MongoDB with retry logic
    Returns the database instance
    """
    global _mongo_client, _database
    
    if _database is not None:
        return _database
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB (attempt {attempt + 1}/{max_retries})...")
            
            _mongo_client = AsyncIOMotorClient(
                DATABASE_URL,
                maxPoolSize=MAX_POOL_SIZE,
                minPoolSize=MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            
            # Extract database name from URL or use default
            db_name = DATABASE_URL.split("/")[-1].split("?")[0] or "job_tracker"
            _database = _mongo_client[db_name]
            
            # Verify connection
            await _database.command("ping")
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
            # Create indexes
            await _create_indexes()
            
            return _database
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise Exception(f"Failed to connect to MongoDB after {max_retries} attempts")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise


async def disconnect_db():
    """
    Close MongoDB connection gracefully
    """
    global _mongo_client, _database
    
    if _mongo_client:
        logger.info("Closing MongoDB connection...")
        _mongo_client.close()
        _mongo_client = None
        _database = None
        logger.info("MongoDB connection closed")


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get the current database instance
    Creates new connection if not exists
    """
    global _database
    
    if _database is None:
        _database = await connect_db()
    
    return _database


async def _create_indexes():
    """
    Create database indexes for optimal query performance
    """
    try:
        db = await get_database()
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        
        # Jobs collection indexes
        await db.jobs.create_index([("title", "text"), ("description", "text"), ("company", "text")])
        await db.jobs.create_index("source")
        await db.jobs.create_index("company")
        await db.jobs.create_index("location")
        await db.jobs.create_index("is_active")
        await db.jobs.create_index("created_at")
        await db.jobs.create_index("external_id")
        
        # Applications collection indexes
        await db.applications.create_index("user_id")
        await db.applications.create_index("job_id")
        await db.applications.create_index([("user_id", 1), ("status", 1)])
        await db.applications.create_index("status")
        await db.applications.create_index("next_follow_up")
        await db.applications.create_index("created_at")
        await db.applications.create_index([("user_id", 1), ("job_id", 1)], unique=True)
        
        # Company insights collection indexes
        await db.company_insights.create_index("company_name", unique=True)
        await db.company_insights.create_index("updated_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        # Don't raise - indexes are optimization, not critical


# Collection getters
async def get_users_collection():
    """Get users collection"""
    db = await get_database()
    return db.users


async def get_jobs_collection():
    """Get jobs collection"""
    db = await get_database()
    return db.jobs


async def get_applications_collection():
    """Get applications collection"""
    db = await get_database()
    return db.applications


async def get_insights_collection():
    """Get company insights collection"""
    db = await get_database()
    return db.company_insights


async def health_check() -> dict:
    """
    Perform health check on database connection
    Returns status and connection info
    """
    try:
        db = await get_database()
        
        # Ping database
        result = await db.command("ping")
        
        # Get server info
        server_info = await db.command("serverStatus")
        
        # Get collection stats
        stats = {
            "status": "healthy",
            "database": db.name,
            "collections": {
                "users": await db.users.count_documents({}),
                "jobs": await db.jobs.count_documents({}),
                "applications": await db.applications.count_documents({}),
                "company_insights": await db.company_insights.count_documents({})
            },
            "uptime_seconds": server_info.get("uptime", 0),
            "connections": server_info.get("connections", {}).get("current", 0)
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
