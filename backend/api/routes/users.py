"""
User API Routes
Handles user registration, login, profile management, and resume upload
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
import os
import tempfile
import logging

from models.database import User, Education, UserPreferences
from config.database import get_users_collection
from auth.jwt_handler import (
    create_access_token, 
    hash_password, 
    verify_password, 
    get_current_user
)
from services.resume_parser import parse_resume
from services.matcher import create_profile_embedding

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


# Request/Response Models
class UserRegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[Education] = None
    target_roles: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None


class UserStatsResponse(BaseModel):
    total_applications: int
    active_applications: int
    interviews_scheduled: int
    offers_received: int
    profile_completeness: int


@router.post("/register", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user
    """
    try:
        users_collection = await get_users_collection()
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=hash_password(user_data.password)
        )
        
        # Insert user
        result = await users_collection.insert_one(new_user.dict(by_alias=True, exclude={"id"}))
        user_id = str(result.inserted_id)
        
        # Create access token
        access_token = create_access_token(user_id)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return UserLoginResponse(
            access_token=access_token,
            user={
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login with email and password
    """
    try:
        users_collection = await get_users_collection()
        
        # Find user by email
        user = await users_collection.find_one({"email": form_data.username})
        
        if not user or not verify_password(form_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create access token
        access_token = create_access_token(str(user["_id"]))
        
        logger.info(f"User logged in: {form_data.username}")
        
        return UserLoginResponse(
            access_token=access_token,
            user={
                "id": str(user["_id"]),
                "email": user["email"],
                "name": user["name"],
                "skills": user.get("skills", []),
                "experience_years": user.get("experience_years", 0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me")
async def get_current_user_profile(current_user_id: str = Depends(get_current_user)):
    """
    Get current user's profile
    """
    try:
        users_collection = await get_users_collection()
        
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove sensitive data
        user.pop("password_hash", None)
        user["id"] = str(user.pop("_id"))
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.put("/me")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    try:
        users_collection = await get_users_collection()
        
        # Build update document
        update_data = profile_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # If skills or other profile data changed, regenerate embedding
        if any(key in update_data for key in ["skills", "experience_years", "target_roles", "resume_text"]):
            user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
            if user:
                # Merge with existing data
                profile_for_embedding = {**user, **update_data}
                update_data["resume_embedding"] = create_profile_embedding(profile_for_embedding)
        
        result = await users_collection.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no changes made"
            )
        
        logger.info(f"User profile updated: {current_user_id}")
        
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user)
):
    """
    Upload and parse resume (PDF or DOCX)
    """
    try:
        # Validate file type
        allowed_extensions = [".pdf", ".docx", ".doc"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 5MB limit"
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            # Parse resume
            parsed_data = parse_resume(temp_path, file_ext[1:])  # Remove dot from extension
            
            # Update user profile with parsed data
            users_collection = await get_users_collection()
            
            update_data = {
                "resume_text": parsed_data.get("resume_text", ""),
                "skills": parsed_data.get("skills", []),
                "experience_years": parsed_data.get("experience_years", 0),
                "education": parsed_data.get("education", {}),
                "updated_at": datetime.utcnow()
            }
            
            # Create profile embedding
            user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
            if user:
                profile_for_embedding = {**user, **update_data}
                update_data["resume_embedding"] = create_profile_embedding(profile_for_embedding)
            
            await users_collection.update_one(
                {"_id": ObjectId(current_user_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Resume uploaded and parsed for user: {current_user_id}")
            
            return {
                "message": "Resume uploaded and parsed successfully",
                "parsed_data": {
                    "skills": parsed_data.get("skills", []),
                    "experience_years": parsed_data.get("experience_years", 0),
                    "education": parsed_data.get("education", {}),
                    "email": parsed_data.get("email"),
                    "phone": parsed_data.get("phone")
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user_id: str = Depends(get_current_user)):
    """
    Get user's application statistics
    """
    try:
        from config.database import get_applications_collection
        
        applications_collection = await get_applications_collection()
        users_collection = await get_users_collection()
        
        # Get user
        user = await users_collection.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Count applications by status
        total_apps = await applications_collection.count_documents({"user_id": ObjectId(current_user_id)})
        active_apps = await applications_collection.count_documents({
            "user_id": ObjectId(current_user_id),
            "status": {"$in": ["saved", "applied", "interview_scheduled"]}
        })
        interviews = await applications_collection.count_documents({
            "user_id": ObjectId(current_user_id),
            "status": "interview_scheduled"
        })
        offers = await applications_collection.count_documents({
            "user_id": ObjectId(current_user_id),
            "status": "offer_received"
        })
        
        # Calculate profile completeness
        completeness = 0
        if user.get("name"): completeness += 20
        if user.get("email"): completeness += 20
        if user.get("skills") and len(user["skills"]) > 0: completeness += 20
        if user.get("experience_years") and user["experience_years"] > 0: completeness += 20
        if user.get("resume_text"): completeness += 20
        
        return UserStatsResponse(
            total_applications=total_apps,
            active_applications=active_apps,
            interviews_scheduled=interviews,
            offers_received=offers,
            profile_completeness=completeness
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )
