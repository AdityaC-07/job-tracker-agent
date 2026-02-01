"""
AI Orchestration Routes
Triggers watsonx Orchestrate workflows
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict, Optional
import logging
from bson import ObjectId

from auth.jwt_handler import get_current_user
from services.orchestrate_service import run_workflow, get_run_status
from services import watsonx_service
from services.resume_parser import extract_skills
from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


class OrchestrateRunRequest(BaseModel):
    variables: Dict[str, Any] = {}
    project_id: Optional[str] = None
    workflow_id: Optional[str] = None


@router.post("/orchestrate/run", status_code=status.HTTP_202_ACCEPTED)
async def orchestrate_run(
    payload: OrchestrateRunRequest,
    current_user_id: str = Depends(get_current_user)
):
    try:
        result = await run_workflow(
            variables=payload.variables,
            project_id=payload.project_id,
            workflow_id=payload.workflow_id
        )
        return {"run": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running Orchestrate workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to run workflow")


@router.get("/orchestrate/runs/{run_id}")
async def orchestrate_status(
    run_id: str,
    project_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    current_user_id: str = Depends(get_current_user)
):
    try:
        result = await get_run_status(
            run_id=run_id,
            project_id=project_id,
            workflow_id=workflow_id
        )
        return {"run": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching Orchestrate run status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch run status")


@router.post("/analyze-job/{job_id}")
async def analyze_job(
    job_id: str,
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Analyze job requirements and provide skill gap analysis
    """
    try:
        # Get user profile
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get job posting (try applications first, then job postings)
        job = await db.applications.find_one({
            "_id": ObjectId(job_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if job:
            job_data = job.get("job", {})
        else:
            # Try job postings collection
            job_data = await db.job_postings.find_one({"_id": ObjectId(job_id)})
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
        
        # Prepare data for analysis
        user_profile = {
            "skills": user.get("skills", []),
            "experience_years": user.get("experience_years", 0)
        }
        
        job_posting = {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "description": job_data.get("description", ""),
            "skills_required": job_data.get("skills_required", [])
        }
        
        # Generate analysis
        analysis = watsonx_service.analyze_job_requirements(job_posting, user_profile)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-resume")
async def optimize_resume(
    job_id: str,
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get resume optimization suggestions for a specific job
    """
    try:
        # Get user profile
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get job posting
        job = await db.applications.find_one({
            "_id": ObjectId(job_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if job:
            job_data = job.get("job", {})
        else:
            job_data = await db.job_postings.find_one({"_id": ObjectId(job_id)})
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")
        
        # Prepare data
        user_profile = {
            "skills": user.get("skills", []),
            "experience_years": user.get("experience_years", 0)
        }
        
        job_posting = {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "description": job_data.get("description", ""),
            "skills_required": job_data.get("skills_required", [])
        }
        
        # Generate suggestions
        suggestions = watsonx_service.optimize_resume(user_profile, job_posting)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume-suggestions")
async def resume_suggestions(
    job_id: str,
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Provide resume improvement suggestions for a specific job
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        resume_text = user.get("resume_text", "")
        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume not found. Upload a resume first.")

        job = await db.applications.find_one({
            "_id": ObjectId(job_id),
            "user_id": ObjectId(current_user_id)
        })

        if job:
            job_data = job.get("job", {})
        else:
            job_data = await db.job_postings.find_one({"_id": ObjectId(job_id)})
            if not job_data:
                raise HTTPException(status_code=404, detail="Job not found")

        job_posting = {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "description": job_data.get("description", ""),
            "skills_required": job_data.get("skills_required", [])
        }

        resume_skills = extract_skills(resume_text)
        job_skills = job_posting["skills_required"] or extract_skills(job_posting["description"])

        suggestions = watsonx_service.suggest_resume_updates(
            resume_text=resume_text,
            job_posting=job_posting,
            resume_skills=resume_skills,
            job_skills=job_skills
        )

        return {
            "success": True,
            "suggestions": suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating resume suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email-template")
async def generate_email(
    template_type: str,
    application_id: str,
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate email template (follow_up, thank_you, negotiation)
    """
    try:
        if template_type not in ["follow_up", "thank_you", "negotiation"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid template type. Must be: follow_up, thank_you, or negotiation"
            )
        
        # Get user
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get application
        application = await db.applications.find_one({
            "_id": ObjectId(application_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        job = application.get("job", {})
        
        # Calculate days since application
        from datetime import datetime
        applied_date = application.get("applied_date", datetime.now())
        days_since = (datetime.now() - applied_date).days if isinstance(applied_date, datetime) else 7
        
        # Prepare context
        context = {
            "company": job.get("company", "the company"),
            "role": job.get("title", "the position"),
            "user_name": user.get("full_name", user.get("email", "").split("@")[0]),
            "days_since_application": days_since,
            "interview_date": application.get("interview_date", "recent"),
            "current_offer": application.get("offer_amount", "X"),
            "desired_salary": user.get("desired_salary", "Y")
        }
        
        # Generate email
        email = watsonx_service.generate_email_template(template_type, context)
        
        return {
            "success": True,
            "email": email,
            "template_type": template_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_ai_insights(
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get AI-powered insights about job search performance
    """
    try:
        # Get user
        user = await db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all applications
        applications_cursor = db.applications.find({
            "user_id": ObjectId(current_user_id)
        })
        applications = []
        async for app in applications_cursor:
            applications.append(app)
        
        # Prepare data
        user_profile = {
            "skills": user.get("skills", []),
            "experience_years": user.get("experience_years", 0)
        }
        
        # Generate insights
        insights = watsonx_service.generate_ai_insights(applications, user_profile)
        
        return {
            "success": True,
            "insights": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


@router.post("/interview-prep/{application_id}")
async def get_interview_prep(
    application_id: str,
    current_user_id: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get AI-generated interview preparation materials
    """
    try:
        # Get application
        application = await db.applications.find_one({
            "_id": ObjectId(application_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        job = application.get("job", {})
        
        # Generate interview prep
        prep = watsonx_service.generate_interview_prep(
            company=job.get("company", "the company"),
            role=job.get("title", "the position"),
            description=job.get("description", "")
        )
        
        return {
            "success": True,
            "prep": prep
        }
        
    except Exception as e:
        logger.error(f"Error generating interview prep: {e}")
        raise HTTPException(status_code=500, detail=str(e))
