"""
Profile and Job Matching Service
Uses sentence-transformers for semantic matching between user profiles and job postings
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# Load model (lightweight and efficient)
model = SentenceTransformer('all-MiniLM-L6-v2')


def create_profile_embedding(user_profile: Dict[str, Any]) -> List[float]:
    """
    Create vector embedding for user profile
    
    Args:
        user_profile: Dictionary containing user's skills, experience, resume text
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Combine all relevant profile information
        profile_parts = []
        
        # Add skills
        if user_profile.get("skills"):
            profile_parts.append("Skills: " + ", ".join(user_profile["skills"]))
        
        # Add experience
        if user_profile.get("experience_years"):
            profile_parts.append(f"Experience: {user_profile['experience_years']} years")
        
        # Add target roles
        if user_profile.get("target_roles"):
            profile_parts.append("Target roles: " + ", ".join(user_profile["target_roles"]))
        
        # Add education
        if user_profile.get("education"):
            edu = user_profile["education"]
            if isinstance(edu, dict):
                edu_text = f"{edu.get('degree', '')} in {edu.get('field', '')}"
                profile_parts.append(f"Education: {edu_text}")
        
        # Add resume text (truncated)
        if user_profile.get("resume_text"):
            resume_snippet = user_profile["resume_text"][:500]  # First 500 chars
            profile_parts.append(resume_snippet)
        
        # Combine all parts
        profile_text = " | ".join(profile_parts)
        
        # Generate embedding
        embedding = model.encode(profile_text, convert_to_numpy=True)
        
        logger.debug(f"Created profile embedding with {len(embedding)} dimensions")
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error creating profile embedding: {e}")
        return []


def create_job_embedding(job_posting: Dict[str, Any]) -> List[float]:
    """
    Create vector embedding for job posting
    
    Args:
        job_posting: Dictionary containing job title, description, requirements
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Combine job information
        job_parts = []
        
        # Add title (weighted more heavily)
        if job_posting.get("title"):
            job_parts.append(f"Title: {job_posting['title']}")
        
        # Add company
        if job_posting.get("company"):
            job_parts.append(f"Company: {job_posting['company']}")
        
        # Add location
        if job_posting.get("location"):
            job_parts.append(f"Location: {job_posting['location']}")
        
        # Add required skills
        if job_posting.get("skills_required"):
            job_parts.append("Required skills: " + ", ".join(job_posting["skills_required"]))
        
        # Add experience requirements
        if job_posting.get("experience_min") or job_posting.get("experience_max"):
            exp_min = job_posting.get("experience_min", 0)
            exp_max = job_posting.get("experience_max", "")
            job_parts.append(f"Experience: {exp_min}-{exp_max} years")
        
        # Add description (truncated)
        if job_posting.get("description"):
            desc_snippet = job_posting["description"][:500]  # First 500 chars
            job_parts.append(desc_snippet)
        
        # Add requirements (truncated)
        if job_posting.get("requirements"):
            req_snippet = job_posting["requirements"][:300]
            job_parts.append(req_snippet)
        
        # Combine all parts
        job_text = " | ".join(job_parts)
        
        # Generate embedding
        embedding = model.encode(job_text, convert_to_numpy=True)
        
        logger.debug(f"Created job embedding with {len(embedding)} dimensions")
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error creating job embedding: {e}")
        return []


def calculate_match_score(profile_embedding: List[float], job_embedding: List[float]) -> float:
    """
    Calculate match score between profile and job using cosine similarity
    
    Args:
        profile_embedding: User profile embedding vector
        job_embedding: Job posting embedding vector
        
    Returns:
        Match score between 0 and 100
    """
    try:
        if not profile_embedding or not job_embedding:
            return 0.0
        
        # Convert to numpy arrays
        profile_vec = np.array(profile_embedding).reshape(1, -1)
        job_vec = np.array(job_embedding).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(profile_vec, job_vec)[0][0]
        
        # Convert to 0-100 scale
        # Cosine similarity is between -1 and 1, but typically 0 to 1 for our use case
        score = max(0, min(100, similarity * 100))
        
        return round(score, 2)
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return 0.0


def find_matching_jobs(
    user_profile: Dict[str, Any],
    job_postings: List[Dict[str, Any]],
    min_score: float = 40.0,
    top_n: int = 50
) -> List[Dict[str, Any]]:
    """
    Find and rank jobs matching user profile
    
    Args:
        user_profile: User profile with embedding
        job_postings: List of job postings with embeddings
        min_score: Minimum match score threshold
        top_n: Maximum number of jobs to return
        
    Returns:
        List of jobs with match scores, sorted by score descending
    """
    try:
        # Get or create profile embedding
        profile_embedding = user_profile.get("resume_embedding")
        if not profile_embedding:
            profile_embedding = create_profile_embedding(user_profile)
        
        matching_jobs = []
        
        for job in job_postings:
            # Get or create job embedding
            job_embedding = job.get("job_embedding")
            if not job_embedding:
                job_embedding = create_job_embedding(job)
            
            # Calculate match score
            score = calculate_match_score(profile_embedding, job_embedding)
            
            if score >= min_score:
                job_with_score = job.copy()
                job_with_score["match_score"] = score
                matching_jobs.append(job_with_score)
        
        # Sort by score descending
        matching_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Return top N
        result = matching_jobs[:top_n]
        
        logger.info(f"Found {len(result)} matching jobs (min_score={min_score})")
        return result
        
    except Exception as e:
        logger.error(f"Error finding matching jobs: {e}")
        return []


def analyze_skill_gap(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze skill gap between user profile and job requirements
    
    Args:
        user_profile: User profile with skills
        job_posting: Job posting with required skills
        
    Returns:
        Dictionary with matching_skills, missing_skills, and recommendations
    """
    try:
        user_skills = set([s.lower() for s in user_profile.get("skills", [])])
        required_skills = set([s.lower() for s in job_posting.get("skills_required", [])])
        
        # Find matching and missing skills
        matching_skills = user_skills.intersection(required_skills)
        missing_skills = required_skills.difference(user_skills)
        
        # Calculate match percentage
        if required_skills:
            match_percentage = (len(matching_skills) / len(required_skills)) * 100
        else:
            match_percentage = 100.0  # No specific skills required
        
        # Generate recommendations
        recommendations = []
        
        if missing_skills:
            recommendations.append(f"Consider learning: {', '.join(list(missing_skills)[:5])}")
        
        if match_percentage < 70:
            recommendations.append("Build more experience in the required skill areas")
            recommendations.append("Consider taking online courses or certifications")
        
        # Experience gap
        user_exp = user_profile.get("experience_years", 0)
        required_exp_min = job_posting.get("experience_min", 0)
        
        if required_exp_min and user_exp < required_exp_min:
            exp_gap = required_exp_min - user_exp
            recommendations.append(f"Gain {exp_gap:.1f} more years of relevant experience")
        
        result = {
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "match_percentage": round(match_percentage, 1),
            "experience_gap_years": max(0, required_exp_min - user_exp) if required_exp_min else 0,
            "recommendations": recommendations
        }
        
        logger.debug(f"Skill gap analysis: {match_percentage:.1f}% match, {len(missing_skills)} missing skills")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {e}")
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percentage": 0.0,
            "experience_gap_years": 0,
            "recommendations": ["Unable to analyze skill gap"]
        }


def batch_create_job_embeddings(job_postings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create embeddings for multiple job postings in batch
    More efficient for processing many jobs
    
    Args:
        job_postings: List of job posting dictionaries
        
    Returns:
        List of job postings with embeddings added
    """
    try:
        logger.info(f"Creating embeddings for {len(job_postings)} jobs...")
        
        for job in job_postings:
            if not job.get("job_embedding"):
                job["job_embedding"] = create_job_embedding(job)
        
        logger.info("Batch embedding creation completed")
        return job_postings
        
    except Exception as e:
        logger.error(f"Error in batch embedding creation: {e}")
        return job_postings
