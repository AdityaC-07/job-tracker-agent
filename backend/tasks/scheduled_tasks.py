"""
Celery Scheduled Tasks
Background tasks for follow-ups, job fetching, and notifications
"""
import os
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import asyncio
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "job_tracker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
)


# Helper to run async functions in Celery tasks
def run_async(coro):
    """Run async coroutine in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="check_pending_follow_ups")
def check_pending_follow_ups():
    """
    Check for applications needing follow-up and send reminders
    Runs daily at 9:00 AM
    """
    try:
        logger.info("Checking pending follow-ups...")
        
        async def _check_follow_ups():
            from backend.config.database import get_applications_collection, get_users_collection, get_jobs_collection
            from backend.services.notifications import send_follow_up_reminder
            
            applications_collection = await get_applications_collection()
            users_collection = await get_users_collection()
            jobs_collection = await get_jobs_collection()
            
            # Find applications with follow-up date today or earlier
            today = datetime.utcnow()
            cursor = applications_collection.find({
                "next_follow_up": {"$lte": today},
                "status": {"$in": ["applied", "interview_scheduled"]}
            })
            
            count = 0
            async for app in cursor:
                try:
                    # Get user and job
                    user = await users_collection.find_one({"_id": app["user_id"]})
                    job = await jobs_collection.find_one({"_id": app["job_id"]})
                    
                    if user and job:
                        # Send reminder
                        app["job"] = job
                        success = send_follow_up_reminder(app, user)
                        
                        if success:
                            # Clear follow-up date after sending
                            await applications_collection.update_one(
                                {"_id": app["_id"]},
                                {"$set": {"next_follow_up": None}}
                            )
                            count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending follow-up reminder: {e}")
                    continue
            
            logger.info(f"Sent {count} follow-up reminders")
            return count
        
        return run_async(_check_follow_ups())
        
    except Exception as e:
        logger.error(f"Error in check_pending_follow_ups task: {e}")
        raise


@celery_app.task(name="fetch_new_jobs_daily")
def fetch_new_jobs_daily():
    """
    Fetch new jobs from APIs and notify users of matches
    Runs daily at 8:00 AM
    """
    try:
        logger.info("Fetching new jobs from APIs...")
        
        async def _fetch_jobs():
            from backend.config.database import get_users_collection, get_jobs_collection
            from backend.services.job_api_service import aggregate_from_all_sources
            from backend.services.matcher import find_matching_jobs, batch_create_job_embeddings
            from backend.services.notifications import send_new_job_alert
            from backend.models.database import JobPosting
            
            users_collection = await get_users_collection()
            jobs_collection = await get_jobs_collection()
            
            # Get all active users with target roles
            cursor = users_collection.find({
                "target_roles": {"$exists": True, "$ne": []},
                "preferences.notification_frequency": {"$in": ["daily", "realtime"]}
            })
            
            users = []
            async for user in cursor:
                users.append(user)
            
            if not users:
                logger.info("No users with notification preferences found")
                return 0
            
            total_jobs_found = 0
            total_notifications_sent = 0
            
            # For each user, search for jobs matching their target roles
            for user in users:
                try:
                    target_roles = user.get("target_roles", [])
                    target_locations = user.get("target_locations", [])
                    
                    # Search for each target role
                    all_jobs = []
                    for role in target_roles[:3]:  # Limit to top 3 roles
                        location = target_locations[0] if target_locations else ""
                        jobs = await aggregate_from_all_sources(role, location, max_results=20)
                        all_jobs.extend(jobs)
                    
                    if not all_jobs:
                        continue
                    
                    # Remove duplicates and create embeddings
                    unique_jobs = {(j.get("title"), j.get("company")): j for j in all_jobs}.values()
                    unique_jobs = list(unique_jobs)
                    unique_jobs = batch_create_job_embeddings(unique_jobs)
                    
                    # Save new jobs to database
                    new_jobs = []
                    for job in unique_jobs:
                        existing = await jobs_collection.find_one({
                            "external_id": job.get("external_id"),
                            "source": job.get("source")
                        })
                        
                        if not existing:
                            job_model = JobPosting(**job)
                            result = await jobs_collection.insert_one(
                                job_model.dict(by_alias=True, exclude={"id"})
                            )
                            job["_id"] = result.inserted_id
                            new_jobs.append(job)
                    
                    total_jobs_found += len(new_jobs)
                    
                    if new_jobs:
                        # Find matching jobs
                        matching_jobs = find_matching_jobs(user, new_jobs, min_score=60, top_n=10)
                        
                        if matching_jobs:
                            # Send notification
                            success = send_new_job_alert(user, matching_jobs)
                            if success:
                                total_notifications_sent += 1
                
                except Exception as e:
                    logger.error(f"Error processing jobs for user {user.get('email')}: {e}")
                    continue
            
            logger.info(f"Fetched {total_jobs_found} new jobs, sent {total_notifications_sent} notifications")
            return total_jobs_found
        
        return run_async(_fetch_jobs())
        
    except Exception as e:
        logger.error(f"Error in fetch_new_jobs_daily task: {e}")
        raise


@celery_app.task(name="send_weekly_summary")
def send_weekly_summary():
    """
    Send weekly summary email to all active users
    Runs every Sunday at 6:00 PM
    """
    try:
        logger.info("Sending weekly summaries...")
        
        async def _send_summaries():
            from backend.config.database import get_users_collection, get_applications_collection
            from backend.services.notifications import send_weekly_summary as send_summary_email
            
            users_collection = await get_users_collection()
            applications_collection = await get_applications_collection()
            
            # Get all users with email preferences
            cursor = users_collection.find({
                "preferences.notification_frequency": {"$in": ["weekly", "daily", "realtime"]}
            })
            
            count = 0
            async for user in cursor:
                try:
                    # Calculate weekly stats
                    one_week_ago = datetime.utcnow() - timedelta(days=7)
                    
                    # Total applications
                    total_apps = await applications_collection.count_documents({
                        "user_id": user["_id"]
                    })
                    
                    # New applications this week
                    new_apps = await applications_collection.count_documents({
                        "user_id": user["_id"],
                        "created_at": {"$gte": one_week_ago}
                    })
                    
                    # Interviews this week
                    interviews = await applications_collection.count_documents({
                        "user_id": user["_id"],
                        "status": "interview_scheduled",
                        "updated_at": {"$gte": one_week_ago}
                    })
                    
                    # Offers this week
                    offers = await applications_collection.count_documents({
                        "user_id": user["_id"],
                        "status": "offer_received",
                        "updated_at": {"$gte": one_week_ago}
                    })
                    
                    # Rejections this week
                    rejections = await applications_collection.count_documents({
                        "user_id": user["_id"],
                        "status": "rejected",
                        "updated_at": {"$gte": one_week_ago}
                    })
                    
                    stats = {
                        "total_applications": total_apps,
                        "new_applications": new_apps,
                        "interviews_scheduled": interviews,
                        "offers_received": offers,
                        "rejections": rejections
                    }
                    
                    # Send email
                    success = send_summary_email(user, stats)
                    if success:
                        count += 1
                
                except Exception as e:
                    logger.error(f"Error sending weekly summary to {user.get('email')}: {e}")
                    continue
            
            logger.info(f"Sent {count} weekly summaries")
            return count
        
        return run_async(_send_summaries())
        
    except Exception as e:
        logger.error(f"Error in send_weekly_summary task: {e}")
        raise


# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "check-pending-follow-ups": {
        "task": "check_pending_follow_ups",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    "fetch-new-jobs-daily": {
        "task": "fetch_new_jobs_daily",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    "send-weekly-summary": {
        "task": "send_weekly_summary",
        "schedule": crontab(day_of_week=0, hour=18, minute=0),  # Sunday at 6:00 PM
    },
}


if __name__ == "__main__":
    # For testing tasks
    pass
