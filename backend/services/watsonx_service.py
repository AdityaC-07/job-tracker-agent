"""
IBM watsonx AI Service
Integration with IBM watsonx for AI-powered features
"""
import os
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Try to import IBM watsonx AI library
try:
    from ibm_watsonx_ai import Credentials, APIClient
    from ibm_watsonx_ai.foundation_models import ModelInference
    WATSONX_AVAILABLE = True
except ImportError:
    logger.warning("ibm-watsonx-ai not installed. AI features will use fallback.")
    WATSONX_AVAILABLE = False

# Configuration
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
MODEL_ID = "ibm/granite-13b-chat-v2"


def _get_watsonx_client() -> Optional[Any]:
    """
    Initialize and return watsonx AI client
    
    Returns:
        ModelInference client or None if not configured
    """
    if not WATSONX_AVAILABLE:
        return None
    
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        logger.warning("watsonx credentials not configured")
        return None
    
    try:
        credentials = Credentials(
            url=WATSONX_URL,
            api_key=WATSONX_API_KEY
        )
        
        client = ModelInference(
            model_id=MODEL_ID,
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "temperature": 0.7,
                "repetition_penalty": 1.1
            }
        )
        
        return client
        
    except Exception as e:
        logger.error(f"Error initializing watsonx client: {e}")
        return None


def generate_cover_letter(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> str:
    """
    Generate customized cover letter using AI
    
    Args:
        user_profile: User's profile with skills and experience
        job_posting: Job posting details
        
    Returns:
        Generated cover letter text
    """
    try:
        client = _get_watsonx_client()
        
        # Prepare prompt
        skills_str = ", ".join(user_profile.get("skills", [])[:10])
        exp_years = user_profile.get("experience_years", 0)
        
        prompt = f"""Write a professional cover letter for the following job application:

Job Title: {job_posting.get('title', '')}
Company: {job_posting.get('company', '')}
Job Description: {job_posting.get('description', '')[:300]}

Candidate Profile:
- Name: {user_profile.get('name', 'The Applicant')}
- Experience: {exp_years} years
- Key Skills: {skills_str}

Write a concise, professional cover letter (3-4 paragraphs) that:
1. Expresses enthusiasm for the role
2. Highlights relevant skills and experience
3. Explains why they're a great fit
4. Includes a call to action

Cover Letter:"""

        if client:
            response = client.generate_text(prompt=prompt)
            cover_letter = response.strip()
        else:
            # Fallback template if watsonx not available
            cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_posting.get('title', '')} position at {job_posting.get('company', '')}. With {exp_years} years of professional experience and expertise in {skills_str}, I am confident in my ability to contribute effectively to your team.

My background in {skills_str.split(',')[0] if skills_str else 'software development'} has prepared me well for this role. I am particularly drawn to this opportunity because of {job_posting.get('company', 'your company')}'s reputation and the exciting challenges this position offers.

I would welcome the opportunity to discuss how my skills and experience align with your needs. Thank you for considering my application, and I look forward to hearing from you.

Best regards,
{user_profile.get('name', 'The Applicant')}"""
        
        logger.info(f"Generated cover letter for {job_posting.get('title', 'job')}")
        return cover_letter
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return "Error generating cover letter. Please try again."


def analyze_rejection(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze rejected application and provide insights
    
    Args:
        application_data: Application details including job and user profile
        
    Returns:
        Dictionary with analysis and recommendations
    """
    try:
        client = _get_watsonx_client()
        
        job = application_data.get("job", {})
        user = application_data.get("user", {})
        notes = application_data.get("notes", "")
        
        prompt = f"""Analyze this rejected job application and provide insights:

Job: {job.get('title', '')} at {job.get('company', '')}
Candidate Skills: {', '.join(user.get('skills', [])[:8])}
Experience: {user.get('experience_years', 0)} years
Application Notes: {notes}

Provide a brief analysis (3-4 sentences) covering:
1. Possible reasons for rejection
2. Skills that may have been lacking
3. Specific recommendations for improvement

Analysis:"""

        if client:
            response = client.generate_text(prompt=prompt)
            analysis_text = response.strip()
        else:
            # Fallback analysis
            analysis_text = f"""Based on the application for {job.get('title', 'this position')}, here are some possible factors:

1. The role may have required more specialized experience in certain technical areas.
2. Competition was likely strong, with candidates who had more direct experience with the required technologies.
3. Consider strengthening your skills in {job.get('skills_required', ['key technologies'])[0] if job.get('skills_required') else 'relevant technologies'} and gaining hands-on project experience.
4. Tailor your application materials more specifically to highlight relevant achievements."""
        
        # Extract actionable recommendations
        recommendations = [
            "Review the job requirements and identify skill gaps",
            "Build projects showcasing relevant skills",
            "Consider certifications in key technology areas",
            "Network with professionals in similar roles"
        ]
        
        result = {
            "analysis": analysis_text,
            "recommendations": recommendations,
            "skill_focus_areas": job.get("skills_required", [])[:3]
        }
        
        logger.info("Completed rejection analysis")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing rejection: {e}")
        return {
            "analysis": "Unable to complete analysis. Please review the job requirements manually.",
            "recommendations": ["Review application materials", "Strengthen relevant skills"],
            "skill_focus_areas": []
        }


def suggest_next_actions(status: str, days_since_applied: int) -> List[str]:
    """
    Suggest next actions based on application status
    
    Args:
        status: Application status
        days_since_applied: Days since application was submitted
        
    Returns:
        List of 3 actionable next steps
    """
    try:
        suggestions = []
        
        if status == "saved":
            suggestions = [
                "Review the job description thoroughly and tailor your resume",
                "Research the company culture and recent news",
                "Prepare a customized cover letter highlighting relevant experience"
            ]
        elif status == "applied":
            if days_since_applied < 7:
                suggestions = [
                    "Wait for initial response (typically takes 7-10 days)",
                    "Prepare for potential technical screening questions",
                    "Continue applying to similar roles"
                ]
            elif days_since_applied < 14:
                suggestions = [
                    "Consider sending a polite follow-up email to the recruiter",
                    "Connect with current employees on LinkedIn for insights",
                    "Review and strengthen interview preparation"
                ]
            else:
                suggestions = [
                    "Send a professional follow-up email expressing continued interest",
                    "Reach out to the hiring manager if contact information is available",
                    "Consider this application inactive and focus on new opportunities"
                ]
        elif status == "interview_scheduled":
            suggestions = [
                "Research common interview questions for this role and company",
                "Prepare STAR method examples showcasing relevant achievements",
                "Review the job description and prepare questions for the interviewer"
            ]
        elif status == "offer_received":
            suggestions = [
                "Evaluate the offer against your requirements and market rates",
                "Negotiate salary and benefits if appropriate",
                "Request time to make a decision if needed (typically 3-7 days)"
            ]
        elif status == "rejected":
            suggestions = [
                "Request feedback on your application or interview performance",
                "Analyze what could be improved for future applications",
                "Stay positive and continue applying to other opportunities"
            ]
        
        logger.info(f"Generated action suggestions for status: {status}")
        return suggestions
        
    except Exception as e:
        logger.error(f"Error suggesting next actions: {e}")
        return ["Review your application", "Continue job search", "Network with professionals"]


def generate_interview_prep(company: str, role: str) -> Dict[str, Any]:
    """
    Generate interview preparation materials
    
    Args:
        company: Company name
        role: Job role/title
        
    Returns:
        Dictionary with questions and tips
    """
    try:
        client = _get_watsonx_client()
        
        prompt = f"""Generate interview preparation guide for:
Company: {company}
Role: {role}

Provide:
1. 5 common technical questions
2. 5 behavioral questions
3. 3 key tips for success

Format as structured text.

Interview Prep:"""

        if client:
            response = client.generate_text(prompt=prompt)
            prep_text = response.strip()
            
            # Parse response (simple parsing)
            questions = []
            tips = []
            
            lines = prep_text.split('\n')
            for line in lines:
                if '?' in line:
                    questions.append(line.strip())
                elif any(word in line.lower() for word in ['tip', 'remember', 'important', 'key']):
                    tips.append(line.strip())
        else:
            # Fallback questions and tips
            questions = [
                f"What interests you about the {role} position?",
                "Describe your experience with relevant technologies",
                "Tell me about a challenging project you worked on",
                "How do you handle tight deadlines and pressure?",
                "Why do you want to work at this company?",
                "Describe a time you worked in a team",
                "What are your greatest strengths?",
                "Where do you see yourself in 5 years?",
                "Tell me about a time you solved a difficult problem",
                "Do you have any questions for us?"
            ]
            
            tips = [
                "Research the company's products, culture, and recent news",
                "Prepare specific examples using the STAR method",
                "Ask thoughtful questions about the role and team"
            ]
        
        result = {
            "company": company,
            "role": role,
            "common_questions": questions[:10],
            "tips": tips[:5],
            "preparation_checklist": [
                "Review your resume and be ready to discuss each point",
                "Prepare questions to ask the interviewer",
                "Test your tech setup if it's a virtual interview",
                "Plan your outfit and arrival time",
                "Bring copies of your resume and notepad"
            ]
        }
        
        logger.info(f"Generated interview prep for {role} at {company}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating interview prep: {e}")
        return {
            "company": company,
            "role": role,
            "common_questions": ["Tell me about yourself", "Why this role?"],
            "tips": ["Be prepared", "Ask questions", "Follow up"],
            "preparation_checklist": ["Review resume", "Research company"]
        }
