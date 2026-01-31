"""
MongoDB Pydantic Models for Job Tracker Application
Defines User, JobPosting, Application, and CompanyInsights models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"


class Education(BaseModel):
    """Education information"""
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None


class UserPreferences(BaseModel):
    """User job search preferences"""
    job_types: List[str] = Field(default_factory=list)  # ["Full-time", "Remote", "Contract"]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_preference: str = "any"  # "remote_only", "hybrid", "on_site", "any"
    notification_frequency: str = "daily"  # "realtime", "daily", "weekly", "none"


class User(BaseModel):
    """User model with resume data and preferences"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    name: str
    password_hash: str
    resume_text: Optional[str] = None
    resume_embedding: Optional[List[float]] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: Education = Field(default_factory=Education)
    target_roles: List[str] = Field(default_factory=list)
    target_locations: List[str] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "skills": ["Python", "React", "MongoDB"],
                "experience_years": 3.5,
                "target_roles": ["Software Engineer", "Full Stack Developer"]
            }
        }


class JobPosting(BaseModel):
    """Job posting model from various sources"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    external_id: Optional[str] = None  # ID from external API
    source: str  # "adzuna", "jsearch", "themuse", "manual"
    title: str
    company: str
    location: str
    job_type: Optional[str] = None  # "Full-time", "Part-time", "Contract", "Remote"
    description: str
    requirements: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    posted_date: Optional[datetime] = None
    is_active: bool = True
    job_embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "source": "adzuna",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "description": "We are looking for...",
                "skills_required": ["Python", "Django", "PostgreSQL"]
            }
        }


class InterviewRound(BaseModel):
    """Interview round details"""
    round_number: int
    round_type: str  # "phone_screen", "technical", "behavioral", "final"
    scheduled_date: Optional[datetime] = None
    completed: bool = False
    notes: Optional[str] = None
    interviewer: Optional[str] = None


class Application(BaseModel):
    """Job application tracking model"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    job_id: PyObjectId
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_date: Optional[datetime] = None
    match_score: Optional[float] = None  # 0-100
    cover_letter: Optional[str] = None
    interview_rounds: List[InterviewRound] = Field(default_factory=list)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    next_follow_up: Optional[datetime] = None
    follow_up_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('applied_date', always=True)
    def set_applied_date(cls, v, values):
        """Auto-set applied_date when status is APPLIED"""
        if values.get('status') == ApplicationStatus.APPLIED and not v:
            return datetime.utcnow()
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        use_enum_values = True


class CompanyInsights(BaseModel):
    """Aggregated insights about companies from user experiences"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    company_name: str
    average_response_time_days: Optional[float] = None
    common_questions: List[str] = Field(default_factory=list)
    interview_process: List[str] = Field(default_factory=list)  # ["Phone Screen", "Technical", "Final"]
    tips: List[str] = Field(default_factory=list)
    culture_notes: Optional[str] = None
    application_count: int = 0  # Number of applications tracked for this company
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "company_name": "Tech Corp",
                "average_response_time_days": 7.5,
                "common_questions": ["Tell me about yourself", "Why Tech Corp?"],
                "interview_process": ["Phone Screen", "Technical Round", "Manager Round", "HR Round"]
            }
        }
