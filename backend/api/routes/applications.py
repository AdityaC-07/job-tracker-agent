"""
Application API Routes
Handles job application tracking and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timedelta
import logging

from backend.models.database import Application, ApplicationStatus, InterviewRound
from backend.config.database import get_applications_collection, get_jobs_collection, get_users_collection
from backend.auth.jwt_handler import get_current_user
from backend.services.watsonx_service import generate_cover_letter, suggest_next_actions
from backend.services.matcher import calculate_match_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["Applications"])


# Request/Response Models
class ApplicationCreate(BaseModel):
    job_id: str
    status: ApplicationStatus = ApplicationStatus.SAVED
    notes: Optional[str] = None
    tags: List[str] = []


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    interview_rounds: Optional[List[InterviewRound]] = None
    next_follow_up: Optional[datetime] = None


class FollowUpRequest(BaseModel):
    days_from_now: int = 7


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: ApplicationCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new job application
    """
    try:
        if not ObjectId.is_valid(app_data.job_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job ID format"
            )
        
        applications_collection = await get_applications_collection()
        jobs_collection = await get_jobs_collection()
        users_collection = await get_users_collection()
        
        # Check if job exists
        job = await jobs_collection.find_one({"_id": ObjectId(app_data.job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if application already exists
        existing = await applications_collection.find_one({
            "user_id": ObjectId(current_user_id),
            "job_id": ObjectId(app_data.job_id)
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application already exists for this job"
            )
        
        # Get user for match score calculation
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        
        # Calculate match score
        match_score = None
        if user and user.get("resume_embedding") and job.get("job_embedding"):
            match_score = calculate_match_score(
                user["resume_embedding"],
                job["job_embedding"]
            )
        
        # Create application
        application = Application(
            user_id=ObjectId(current_user_id),
            job_id=ObjectId(app_data.job_id),
            status=app_data.status,
            notes=app_data.notes,
            tags=app_data.tags,
            match_score=match_score,
            applied_date=datetime.utcnow() if app_data.status == ApplicationStatus.APPLIED else None
        )
        
        # Insert application
        result = await applications_collection.insert_one(
            application.dict(by_alias=True, exclude={"id"})
        )
        
        logger.info(f"Application created: user={current_user_id}, job={app_data.job_id}")
        
        return {
            "id": str(result.inserted_id),
            "message": "Application created successfully",
            "match_score": match_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )


@router.get("")
async def get_applications(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all applications for current user with job details
    """
    try:
        applications_collection = await get_applications_collection()
        
        # Build filter
        filter_query = {"user_id": ObjectId(current_user_id)}
        if status_filter:
            filter_query["status"] = status_filter
        
        # Get total count
        total = await applications_collection.count_documents(filter_query)
        
        # Get paginated applications with job details (aggregation)
        skip = (page - 1) * limit
        
        pipeline = [
            {"$match": filter_query},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": {"path": "$job", "preserveNullAndEmptyArrays": True}}
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        applications = []
        
        async for app in cursor:
            app["id"] = str(app.pop("_id"))
            app["user_id"] = str(app["user_id"])
            app["job_id"] = str(app["job_id"])
            
            if app.get("job"):
                app["job"]["id"] = str(app["job"].pop("_id", ""))
            
            applications.append(app)
        
        return {
            "applications": applications,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )


@router.get("/{application_id}")
async def get_application_by_id(
    application_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get single application by ID
    """
    try:
        if not ObjectId.is_valid(application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format"
            )
        
        applications_collection = await get_applications_collection()
        jobs_collection = await get_jobs_collection()
        
        # Get application
        app = await applications_collection.find_one({
            "_id": ObjectId(application_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Get job details
        job = await jobs_collection.find_one({"_id": app["job_id"]})
        
        # Convert ObjectIds to strings
        app["id"] = str(app.pop("_id"))
        app["user_id"] = str(app["user_id"])
        app["job_id"] = str(app["job_id"])
        
        if job:
            job["id"] = str(job.pop("_id"))
            app["job"] = job
        
        return app
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application"
        )


@router.put("/{application_id}")
async def update_application(
    application_id: str,
    app_update: ApplicationUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update application
    """
    try:
        if not ObjectId.is_valid(application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format"
            )
        
        applications_collection = await get_applications_collection()
        
        # Build update document
        update_data = app_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # If status changed to APPLIED, set applied_date
        if app_update.status == ApplicationStatus.APPLIED:
            update_data["applied_date"] = datetime.utcnow()
        
        result = await applications_collection.update_one(
            {
                "_id": ObjectId(application_id),
                "user_id": ObjectId(current_user_id)
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        logger.info(f"Application updated: {application_id}")
        
        return {"message": "Application updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application"
        )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete application
    """
    try:
        if not ObjectId.is_valid(application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format"
            )
        
        applications_collection = await get_applications_collection()
        
        result = await applications_collection.delete_one({
            "_id": ObjectId(application_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        logger.info(f"Application deleted: {application_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        )


@router.post("/{application_id}/cover-letter")
async def generate_cover_letter_for_application(
    application_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Generate AI cover letter for application
    """
    try:
        if not ObjectId.is_valid(application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format"
            )
        
        applications_collection = await get_applications_collection()
        jobs_collection = await get_jobs_collection()
        users_collection = await get_users_collection()
        
        # Get application
        app = await applications_collection.find_one({
            "_id": ObjectId(application_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Get job and user
        job = await jobs_collection.find_one({"_id": app["job_id"]})
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        
        if not job or not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job or user not found"
            )
        
        # Generate cover letter
        cover_letter = generate_cover_letter(user, job)
        
        # Save to application
        await applications_collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": {"cover_letter": cover_letter, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Cover letter generated for application {application_id}")
        
        return {
            "cover_letter": cover_letter
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cover letter"
        )


@router.post("/{application_id}/follow-up")
async def schedule_follow_up(
    application_id: str,
    follow_up_request: FollowUpRequest,
    current_user_id: str = Depends(get_current_user)
):
    """
    Schedule follow-up reminder for application
    """
    try:
        if not ObjectId.is_valid(application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format"
            )
        
        applications_collection = await get_applications_collection()
        
        # Calculate follow-up date
        follow_up_date = datetime.utcnow() + timedelta(days=follow_up_request.days_from_now)
        
        # Update application
        result = await applications_collection.update_one(
            {
                "_id": ObjectId(application_id),
                "user_id": ObjectId(current_user_id)
            },
            {
                "$set": {
                    "next_follow_up": follow_up_date,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"follow_up_count": 1}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        logger.info(f"Follow-up scheduled for application {application_id}")
        
        return {
            "message": "Follow-up scheduled successfully",
            "next_follow_up": follow_up_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling follow-up: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule follow-up"
        )


@router.get("/analytics/overview")
async def get_applications_analytics(
    current_user_id: str = Depends(get_current_user)
):
    """
    Get analytics overview for user's applications
    """
    try:
        applications_collection = await get_applications_collection()
        
        # Aggregate statistics
        pipeline = [
            {"$match": {"user_id": ObjectId(current_user_id)}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        status_counts = {}
        
        async for doc in cursor:
            status_counts[doc["_id"]] = doc["count"]
        
        # Calculate success rate
        total_apps = sum(status_counts.values())
        offers = status_counts.get("offer_received", 0)
        success_rate = (offers / total_apps * 100) if total_apps > 0 else 0
        
        return {
            "total_applications": total_apps,
            "by_status": status_counts,
            "success_rate": round(success_rate, 2)
        }
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics"
        )
