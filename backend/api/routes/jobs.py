"""
Job API Routes
Handles job search, retrieval, and manual entry
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
import logging

from backend.models.database import JobPosting
from backend.config.database import get_jobs_collection
from backend.auth.jwt_handler import get_current_user, get_current_user_optional
from backend.services.job_api_service import aggregate_from_all_sources
from backend.services.matcher import (
    create_job_embedding, 
    find_matching_jobs,
    batch_create_job_embeddings
)
from backend.config.database import get_users_collection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])


# Request/Response Models
class JobSearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = ""
    job_type: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class ManualJobEntry(BaseModel):
    title: str
    company: str
    location: str
    job_type: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    skills_required: List[str] = []
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None


@router.post("/search")
async def search_jobs(
    search_request: JobSearchRequest,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """
    Search for jobs across all integrated APIs
    """
    try:
        logger.info(f"Searching jobs: keywords='{search_request.keywords}', location='{search_request.location}'")
        
        # Fetch jobs from all sources
        jobs = await aggregate_from_all_sources(
            keywords=search_request.keywords,
            location=search_request.location,
            max_results=50
        )
        
        if not jobs:
            return {"jobs": [], "count": 0, "message": "No jobs found"}
        
        # Create embeddings for all jobs
        jobs = batch_create_job_embeddings(jobs)
        
        # Save jobs to database (upsert to avoid duplicates)
        jobs_collection = await get_jobs_collection()
        
        saved_jobs = []
        for job in jobs:
            # Check if job already exists
            existing = await jobs_collection.find_one({
                "external_id": job.get("external_id"),
                "source": job.get("source")
            })
            
            if existing:
                job["_id"] = existing["_id"]
                saved_jobs.append(job)
            else:
                # Insert new job
                job_model = JobPosting(**job)
                result = await jobs_collection.insert_one(
                    job_model.dict(by_alias=True, exclude={"id"})
                )
                job["_id"] = result.inserted_id
                saved_jobs.append(job)
        
        # If user is authenticated, calculate match scores
        if current_user_id:
            users_collection = await get_users_collection()
            user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
            
            if user:
                saved_jobs = find_matching_jobs(user, saved_jobs, min_score=0, top_n=50)
        
        # Convert ObjectId to string for JSON serialization
        for job in saved_jobs:
            if "_id" in job:
                job["id"] = str(job["_id"])
                del job["_id"]
        
        logger.info(f"Found and saved {len(saved_jobs)} jobs")
        
        return {
            "jobs": saved_jobs,
            "count": len(saved_jobs)
        }
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search jobs: {str(e)}"
        )


@router.get("")
async def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """
    Get jobs with pagination and filters
    """
    try:
        jobs_collection = await get_jobs_collection()
        
        # Build filter
        filter_query = {"is_active": True}
        
        if source:
            filter_query["source"] = source
        if job_type:
            filter_query["job_type"] = job_type
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
        if company:
            filter_query["company"] = {"$regex": company, "$options": "i"}
        
        # Get total count
        total = await jobs_collection.count_documents(filter_query)
        
        # Get paginated jobs
        skip = (page - 1) * limit
        cursor = jobs_collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        
        jobs = []
        async for job in cursor:
            job["id"] = str(job.pop("_id"))
            jobs.append(job)
        
        return {
            "jobs": jobs,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch jobs"
        )


@router.get("/{job_id}")
async def get_job_by_id(job_id: str):
    """
    Get single job by ID
    """
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job ID format"
            )
        
        jobs_collection = await get_jobs_collection()
        job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job["id"] = str(job.pop("_id"))
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch job"
        )


@router.post("/manual", status_code=status.HTTP_201_CREATED)
async def create_manual_job(
    job_data: ManualJobEntry,
    current_user_id: str = Depends(get_current_user)
):
    """
    Manually add a job posting
    """
    try:
        jobs_collection = await get_jobs_collection()
        
        # Create job posting
        job = JobPosting(
            source="manual",
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            job_type=job_data.job_type,
            description=job_data.description,
            requirements=job_data.requirements,
            skills_required=job_data.skills_required,
            experience_min=job_data.experience_min,
            experience_max=job_data.experience_max,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            url=job_data.url,
            is_active=True
        )
        
        # Create embedding
        job_dict = job.dict(by_alias=True, exclude={"id"})
        job_dict["job_embedding"] = create_job_embedding(job_dict)
        
        # Insert job
        result = await jobs_collection.insert_one(job_dict)
        
        logger.info(f"Manual job created by user {current_user_id}: {job_data.title}")
        
        return {
            "id": str(result.inserted_id),
            "message": "Job created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating manual job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )


@router.get("/matches/me")
async def get_matching_jobs_for_user(
    min_score: float = Query(50.0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user)
):
    """
    Get jobs matching current user's profile
    """
    try:
        users_collection = await get_users_collection()
        jobs_collection = await get_jobs_collection()
        
        # Get user profile
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get active jobs
        cursor = jobs_collection.find({"is_active": True}).limit(200)  # Limit for performance
        jobs = []
        async for job in cursor:
            job["id"] = str(job.pop("_id"))
            jobs.append(job)
        
        # Find matching jobs
        matching_jobs = find_matching_jobs(
            user_profile=user,
            job_postings=jobs,
            min_score=min_score,
            top_n=limit
        )
        
        logger.info(f"Found {len(matching_jobs)} matching jobs for user {current_user_id}")
        
        return {
            "jobs": matching_jobs,
            "count": len(matching_jobs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding matching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find matching jobs"
        )
