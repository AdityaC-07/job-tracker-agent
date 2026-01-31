"""
Analytics API Routes
Provides dashboard analytics, timeline data, and company insights
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from backend.config.database import (
    get_applications_collection,
    get_jobs_collection,
    get_users_collection,
    get_insights_collection
)
from backend.auth.jwt_handler import get_current_user
from backend.services.matcher import analyze_skill_gap

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


class DashboardStats(BaseModel):
    total_applications: int
    applied: int
    interviews: int
    offers: int
    rejected: int
    success_rate: float
    avg_response_time_days: Optional[float]
    active_applications: int


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_analytics(current_user_id: str = Depends(get_current_user)):
    """
    Get comprehensive dashboard analytics
    """
    try:
        applications_collection = await get_applications_collection()
        
        # Get all applications for user
        cursor = applications_collection.find({"user_id": ObjectId(current_user_id)})
        applications = []
        async for app in cursor:
            applications.append(app)
        
        # Calculate stats
        total_apps = len(applications)
        
        status_counts = defaultdict(int)
        response_times = []
        
        for app in applications:
            status = app.get("status", "saved")
            status_counts[status] += 1
            
            # Calculate response time for applications that progressed
            if app.get("applied_date") and app.get("updated_at"):
                applied_date = app["applied_date"]
                updated_date = app["updated_at"]
                
                if isinstance(applied_date, str):
                    applied_date = datetime.fromisoformat(applied_date.replace("Z", "+00:00"))
                if isinstance(updated_date, str):
                    updated_date = datetime.fromisoformat(updated_date.replace("Z", "+00:00"))
                
                if status not in ["saved", "applied"]:
                    days = (updated_date - applied_date).days
                    if days > 0:
                        response_times.append(days)
        
        # Calculate metrics
        applied_count = status_counts.get("applied", 0) + status_counts.get("interview_scheduled", 0) + \
                       status_counts.get("offer_received", 0) + status_counts.get("rejected", 0)
        interviews = status_counts.get("interview_scheduled", 0)
        offers = status_counts.get("offer_received", 0)
        rejected = status_counts.get("rejected", 0)
        
        success_rate = (offers / applied_count * 100) if applied_count > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        active_apps = status_counts.get("saved", 0) + status_counts.get("applied", 0) + \
                     status_counts.get("interview_scheduled", 0)
        
        return DashboardStats(
            total_applications=total_apps,
            applied=applied_count,
            interviews=interviews,
            offers=offers,
            rejected=rejected,
            success_rate=round(success_rate, 2),
            avg_response_time_days=round(avg_response_time, 1) if avg_response_time else None,
            active_applications=active_apps
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch dashboard analytics"
        )


@router.get("/timeline")
async def get_application_timeline(
    days: int = 30,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get application timeline data grouped by week
    """
    try:
        applications_collection = await get_applications_collection()
        
        # Get applications from last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user_id),
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "week": {"$week": "$created_at"},
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.week": 1}}
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        
        # Organize data by week
        timeline_data = defaultdict(lambda: defaultdict(int))
        
        async for doc in cursor:
            week_key = f"{doc['_id']['year']}-W{doc['_id']['week']:02d}"
            status = doc["_id"]["status"]
            count = doc["count"]
            timeline_data[week_key][status] = count
        
        # Format for frontend
        timeline = []
        for week, statuses in sorted(timeline_data.items()):
            timeline.append({
                "week": week,
                "saved": statuses.get("saved", 0),
                "applied": statuses.get("applied", 0),
                "interviews": statuses.get("interview_scheduled", 0),
                "offers": statuses.get("offer_received", 0),
                "rejected": statuses.get("rejected", 0)
            })
        
        return {"timeline": timeline}
        
    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch timeline data"
        )


@router.get("/skill-gap")
async def get_skill_gap_analysis(current_user_id: str = Depends(get_current_user)):
    """
    Analyze skill gaps across all applications
    """
    try:
        applications_collection = await get_applications_collection()
        jobs_collection = await get_jobs_collection()
        users_collection = await get_users_collection()
        
        # Get user
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all applications with job details
        pipeline = [
            {"$match": {"user_id": ObjectId(current_user_id)}},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": "$job"}
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        
        # Aggregate all missing skills
        all_missing_skills = defaultdict(int)
        all_matching_skills = defaultdict(int)
        total_jobs = 0
        
        async for app in cursor:
            job = app.get("job", {})
            if not job:
                continue
            
            total_jobs += 1
            
            # Analyze skill gap
            gap_analysis = analyze_skill_gap(user, job)
            
            for skill in gap_analysis.get("missing_skills", []):
                all_missing_skills[skill] += 1
            
            for skill in gap_analysis.get("matching_skills", []):
                all_matching_skills[skill] += 1
        
        # Sort skills by frequency
        top_missing = sorted(
            [{"skill": k, "count": v, "percentage": round(v/total_jobs*100, 1)} 
             for k, v in all_missing_skills.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        top_matching = sorted(
            [{"skill": k, "count": v} 
             for k, v in all_matching_skills.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        # Generate recommendations
        recommendations = []
        if top_missing:
            recommendations.append(f"Focus on learning: {', '.join([s['skill'] for s in top_missing[:3]])}")
        if user.get("experience_years", 0) < 2:
            recommendations.append("Build more hands-on project experience")
        recommendations.append("Consider obtaining relevant certifications")
        recommendations.append("Contribute to open-source projects to demonstrate skills")
        
        return {
            "top_missing_skills": top_missing,
            "top_matching_skills": top_matching,
            "recommendations": recommendations,
            "total_jobs_analyzed": total_jobs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze skill gap"
        )


@router.get("/company-insights/{company_name}")
async def get_company_insights(
    company_name: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get insights about a specific company
    """
    try:
        insights_collection = await get_insights_collection()
        applications_collection = await get_applications_collection()
        
        # Get or create company insights
        insights = await insights_collection.find_one({"company_name": company_name})
        
        if not insights:
            # Create default insights
            insights = {
                "company_name": company_name,
                "average_response_time_days": None,
                "common_questions": [],
                "interview_process": [],
                "tips": [],
                "application_count": 0,
                "updated_at": datetime.utcnow()
            }
            
            await insights_collection.insert_one(insights)
        
        # Get user's applications for this company
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(current_user_id)
                }
            },
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": "$job"},
            {
                "$match": {
                    "job.company": company_name
                }
            }
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        user_applications = []
        async for app in cursor:
            user_applications.append(app)
        
        # Convert ObjectId to string
        if insights.get("_id"):
            insights["id"] = str(insights.pop("_id"))
        
        insights["user_application_count"] = len(user_applications)
        
        return insights
        
    except Exception as e:
        logger.error(f"Error fetching company insights: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch company insights"
        )


@router.get("/success-by-company")
async def get_success_rate_by_company(current_user_id: str = Depends(get_current_user)):
    """
    Get success rate grouped by company
    """
    try:
        applications_collection = await get_applications_collection()
        
        pipeline = [
            {"$match": {"user_id": ObjectId(current_user_id)}},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": "$job"},
            {
                "$group": {
                    "_id": "$job.company",
                    "total": {"$sum": 1},
                    "offers": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "offer_received"]}, 1, 0]
                        }
                    },
                    "interviews": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "interview_scheduled"]}, 1, 0]
                        }
                    }
                }
            },
            {"$match": {"total": {"$gte": 1}}},  # At least 1 application
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]
        
        cursor = applications_collection.aggregate(pipeline)
        
        companies = []
        async for doc in cursor:
            success_rate = (doc["offers"] / doc["total"] * 100) if doc["total"] > 0 else 0
            interview_rate = (doc["interviews"] / doc["total"] * 100) if doc["total"] > 0 else 0
            
            companies.append({
                "company": doc["_id"],
                "total_applications": doc["total"],
                "offers": doc["offers"],
                "interviews": doc["interviews"],
                "success_rate": round(success_rate, 1),
                "interview_rate": round(interview_rate, 1)
            })
        
        return {"companies": companies}
        
    except Exception as e:
        logger.error(f"Error fetching success by company: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch success data"
        )
