"""
IBM watsonx AI Service
Integration with IBM watsonx for AI-powered features using direct HTTP API calls
"""
import os
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv
import httpx
import json

# Load .env from backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Configuration
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
IBM_IAM_API_KEY = os.getenv("IBM_IAM_API_KEY", "")
MODEL_ID = "ibm/granite-13b-chat-v2"

# Check if credentials are available
WATSONX_AVAILABLE = bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)
if not WATSONX_AVAILABLE:
    logger.warning("Watson credentials not configured. AI features will use fallback templates.")


def _get_iam_token() -> Optional[str]:
    """
    Get IBM Cloud IAM access token
    
    Returns:
        Access token or None if failed
    """
    if not IBM_IAM_API_KEY:
        logger.warning("IBM_IAM_API_KEY not configured")
        return None
    
    try:
        response = httpx.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": IBM_IAM_API_KEY
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logger.error(f"Failed to get IAM token: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting IAM token: {e}")
        return None


def _call_watsonx_api(prompt: str, max_tokens: int = 500) -> Optional[str]:
    """
    Call watsonx API directly using HTTP
    
    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Generated text or None if failed
    """
    if not WATSONX_AVAILABLE:
        return None
    
    try:
        # Get IAM token
        token = _get_iam_token()
        if not token:
            logger.warning("Could not get IAM token, using fallback")
            return None
        
        # Make API call
        url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model_id": MODEL_ID,
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "repetition_penalty": 1.1
                },
                "project_id": WATSONX_PROJECT_ID
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("results", [{}])[0].get("generated_text", "")
            return generated_text.strip()
        else:
            logger.error(f"Watson API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error calling Watson API: {e}")
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

        # Try Watson API first
        generated_text = _call_watsonx_api(prompt, max_tokens=600)
        
        if generated_text:
            return generated_text
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

        # Try Watson API first
        analysis_text = _call_watsonx_api(prompt, max_tokens=400)
        
        if not analysis_text:
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


def generate_interview_prep(company: str, role: str, description: str = "") -> Dict[str, Any]:
    """
    Generate interview preparation materials using multi-agent approach
    
    Args:
        company: Company name
        role: Job role/title
        description: Job description for context
        
    Returns:
        Dictionary with questions, tips, and agent breakdown
    """
    try:
        # AGENT 1: Job Requirements Analyzer - Extract key skills and requirements
        job_requirements = _extract_job_requirements(role, description)
        
        # AGENT 2: Technical Interview Agent - Generate role-specific technical questions
        technical_questions = _generate_technical_questions(role, job_requirements)
        
        # AGENT 3: Behavioral Interview Agent - Generate behavioral questions
        behavioral_questions = _generate_behavioral_questions(company, role)
        
        # AGENT 4: Interview Coaching Agent - Generate tips and strategies
        tips_and_strategies = _generate_interview_tips(company, role, job_requirements)
        
        # AGENT 5: Preparation Agent - Create checklist
        checklist = _generate_preparation_checklist(role)
        
        result = {
            "company": company,
            "role": role,
            "technical_questions": technical_questions,
            "behavioral_questions": behavioral_questions,
            "tips": tips_and_strategies,
            "preparation_checklist": checklist,
            "key_requirements": job_requirements,
            "agents_used": [
                {"name": "Job Requirements Analyzer", "status": "completed"},
                {"name": "Technical Interview Agent", "status": "completed"},
                {"name": "Behavioral Interview Agent", "status": "completed"},
                {"name": "Interview Coaching Agent", "status": "completed"},
                {"name": "Preparation Agent", "status": "completed"}
            ]
        }
        
        logger.info(f"Generated interview prep for {role} at {company} using multi-agent approach")
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


def suggest_resume_updates(
    resume_text: str,
    job_posting: Dict[str, Any],
    resume_skills: List[str],
    job_skills: List[str]
) -> Dict[str, Any]:
    """
    Provide resume improvements tailored to a target job.
    """
    try:
        missing_skills = sorted(list(set(job_skills) - set(resume_skills)))
        matching_skills = sorted(list(set(job_skills) & set(resume_skills)))

        prompt = f"""You are a career coach. Review the resume and job description and suggest improvements.

Job Title: {job_posting.get('title', '')}
Company: {job_posting.get('company', '')}
Job Description: {job_posting.get('description', '')[:600]}

Resume (truncated):
{resume_text[:1200]}

Provide:
1. 5-7 specific resume improvements
2. Key keywords/skills to add
3. A short summary of fit gaps

Resume Suggestions:"""

        suggestions: List[str] = []
        summary = ""

        raw_text = _call_watsonx_api(prompt, max_tokens=700)
        if raw_text:
            summary = raw_text.split("\n")[0] if raw_text else ""
            for line in raw_text.split("\n"):
                clean = line.strip("-• ").strip()
                if len(clean) > 4:
                    suggestions.append(clean)
        else:
            suggestions = [
                "Add a concise summary tailored to the role and company.",
                "Highlight measurable achievements tied to the job requirements.",
                "Emphasize relevant projects and technical stack alignment.",
                "Mirror key job keywords in skills and experience sections.",
                "Include recent, role-relevant certifications or training."
            ]
            summary = "Focus on adding missing skills and measurable impact relevant to the role."

        return {
            "summary": summary,
            "suggestions": suggestions[:8],
            "matching_skills": matching_skills[:12],
            "missing_skills": missing_skills[:12],
            "keywords_to_add": missing_skills[:10],
            "job_requirements": job_skills[:15]
        }
    except Exception as e:
        logger.error(f"Error generating resume suggestions: {e}")
        return {
            "summary": "Unable to generate AI suggestions. Please try again.",
            "suggestions": ["Review the job description and align your resume keywords."],
            "matching_skills": resume_skills[:10],
            "missing_skills": job_skills[:10],
            "keywords_to_add": job_skills[:10],
            "job_requirements": job_skills[:15]
        }


def analyze_job_requirements(job_posting: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze job requirements and compare with user skills
    
    Args:
        job_posting: Job posting details
        user_profile: User's profile with skills
        
    Returns:
        Dictionary with skill gap analysis
    """
    try:
        job_skills = job_posting.get("skills_required", [])
        user_skills = user_profile.get("skills", [])
        
        # Find matching and missing skills
        matching_skills = [s for s in user_skills if any(js.lower() in s.lower() or s.lower() in js.lower() for js in job_skills)]
        missing_skills = [s for s in job_skills if not any(us.lower() in s.lower() or s.lower() in us.lower() for us in user_skills)]
        
        prompt = f"""Analyze this job opportunity for the candidate:

Job Title: {job_posting.get('title', '')}
Company: {job_posting.get('company', '')}
Required Skills: {', '.join(job_skills)}

Candidate Skills: {', '.join(user_skills)}
Experience: {user_profile.get('experience_years', 0)} years

Provide:
1. Skill match percentage
2. Top 3 strengths that align with the role
3. Top 3 skills to improve or learn
4. Overall fit assessment

Analysis:"""

        analysis_text = _call_watsonx_api(prompt, max_tokens=600)
        
        result = {
            "matching_skills": matching_skills[:10],
            "missing_skills": missing_skills[:10],
            "match_percentage": round((len(matching_skills) / len(job_skills) * 100) if job_skills else 0, 1),
            "analysis": analysis_text or f"You match {len(matching_skills)} out of {len(job_skills)} required skills.",
            "recommendations": missing_skills[:5] if missing_skills else ["Continue building on your existing skills"]
        }
        
        logger.info(f"Analyzed job requirements for {job_posting.get('title', 'job')}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing job requirements: {e}")
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "analysis": "Error analyzing job requirements",
            "recommendations": []
        }


def optimize_resume(user_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide resume optimization suggestions based on job posting
    
    Args:
        user_profile: User's profile
        job_posting: Target job posting
        
    Returns:
        Dictionary with optimization suggestions
    """
    try:
        prompt = f"""As a resume expert, analyze this resume for the target job and provide specific improvements:

Target Job: {job_posting.get('title', '')} at {job_posting.get('company', '')}
Job Description: {job_posting.get('description', '')[:400]}

Current Skills: {', '.join(user_profile.get('skills', [])[:15])}
Experience: {user_profile.get('experience_years', 0)} years

Provide 5-7 specific, actionable suggestions to improve the resume for THIS job:
1. Keywords to add
2. Skills to highlight
3. Experience to emphasize
4. Sections to rewrite

Suggestions:"""

        suggestions_text = _call_watsonx_api(prompt, max_tokens=600)
        
        # Parse suggestions
        suggestions = []
        if suggestions_text:
            lines = [l.strip() for l in suggestions_text.split('\n') if l.strip()]
            suggestions = lines[:7]
        else:
            suggestions = [
                f"Emphasize experience with {job_posting.get('skills_required', ['relevant technologies'])[0]}",
                "Add quantifiable achievements with metrics",
                "Tailor your professional summary to match the job description",
                "Include relevant keywords from the job posting",
                "Highlight projects that demonstrate required skills"
            ]
        
        result = {
            "suggestions": suggestions,
            "keywords_to_add": job_posting.get("skills_required", [])[:8],
            "priority": "high" if len(suggestions) > 5 else "medium"
        }
        
        logger.info(f"Generated resume optimization for {job_posting.get('title', 'job')}")
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}")
        return {
            "suggestions": ["Review and tailor your resume to the job description"],
            "keywords_to_add": [],
            "priority": "medium"
        }


def generate_email_template(template_type: str, context: Dict[str, Any]) -> str:
    """
    Generate email templates (follow-up, thank you, negotiation)
    
    Args:
        template_type: Type of email (follow_up, thank_you, negotiation)
        context: Context with job, company, user info
        
    Returns:
        Generated email text
    """
    try:
        company = context.get("company", "the company")
        role = context.get("role", "the position")
        user_name = context.get("user_name", "Your Name")
        
        prompts = {
            "follow_up": f"""Write a professional follow-up email for a job application:

Company: {company}
Position: {role}
Applicant: {user_name}
Days since application: {context.get('days_since_application', 7)}

Write a polite, concise follow-up email that:
1. References the application
2. Reiterates interest
3. Asks about timeline
4. Remains professional

Email:""",
            
            "thank_you": f"""Write a professional thank-you email after a job interview:

Company: {company}
Position: {role}
Applicant: {user_name}
Interview Date: {context.get('interview_date', 'recent')}

Write a sincere thank-you email that:
1. Thanks the interviewer
2. Reaffirms interest
3. Mentions a specific discussion point
4. Includes next steps

Email:""",
            
            "negotiation": f"""Write a professional salary negotiation email:

Company: {company}
Position: {role}
Applicant: {user_name}
Current Offer: ${context.get('current_offer', 'X')}
Desired Salary: ${context.get('desired_salary', 'Y')}

Write a tactful negotiation email that:
1. Expresses gratitude for the offer
2. Presents counter-offer with justification
3. Remains positive and collaborative
4. Invites discussion

Email:"""
        }
        
        prompt = prompts.get(template_type, prompts["follow_up"])
        
        email = _call_watsonx_api(prompt, max_tokens=500)
        
        if not email:
            # Fallback templates
            templates = {
                "follow_up": f"""Subject: Following Up on {role} Application

Dear Hiring Manager,

I hope this email finds you well. I recently applied for the {role} position at {company} and wanted to follow up on the status of my application.

I remain very interested in this opportunity and believe my skills and experience would be a great fit for your team. I would appreciate any update you can provide regarding the timeline for next steps.

Thank you for your consideration, and I look forward to hearing from you.

Best regards,
{user_name}""",
                
                "thank_you": f"""Subject: Thank You - {role} Interview

Dear Hiring Manager,

Thank you for taking the time to meet with me regarding the {role} position at {company}. I enjoyed our conversation and learning more about the team and company culture.

Our discussion about [specific topic] further confirmed my enthusiasm for this role. I believe my experience aligns well with your needs, and I'm excited about the possibility of contributing to your team.

Please let me know if you need any additional information. I look forward to hearing about the next steps.

Best regards,
{user_name}""",
                
                "negotiation": f"""Subject: {role} Offer Discussion

Dear Hiring Manager,

Thank you for extending the offer for the {role} position at {company}. I'm excited about the opportunity and appreciate your confidence in me.

After careful consideration of the role's responsibilities and market rates for similar positions, I was hoping we could discuss a salary of ${context.get('desired_salary', 'X')}. This reflects my [years of experience/specialized skills/market research].

I'm confident we can find a number that works for both of us. I'm very enthusiastic about joining the team and contributing to {company}'s success.

I'd welcome the opportunity to discuss this further. Thank you for your understanding.

Best regards,
{user_name}"""
            }
            email = templates.get(template_type, templates["follow_up"])
        
        logger.info(f"Generated {template_type} email template")
        return email
        
    except Exception as e:
        logger.error(f"Error generating email template: {e}")
        return "Error generating email template. Please try again."


def generate_ai_insights(applications: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered insights and recommendations
    
    Args:
        applications: List of all user applications
        user_profile: User profile data
        
    Returns:
        Dictionary with insights and recommendations
    """
    try:
        total = len(applications)
        applied = len([a for a in applications if a.get("status") == "applied"])
        interviews = len([a for a in applications if a.get("status") == "interview_scheduled"])
        offers = len([a for a in applications if a.get("status") == "offer_received"])
        rejected = len([a for a in applications if a.get("status") == "rejected"])
        
        prompt = f"""Analyze this job search performance and provide insights:

Total Applications: {total}
Applied: {applied}
Interviews: {interviews}
Offers: {offers}
Rejected: {rejected}

User Skills: {', '.join(user_profile.get('skills', [])[:10])}
Experience: {user_profile.get('experience_years', 0)} years

Provide:
1. Performance assessment
2. Three specific recommendations to improve success rate
3. Skills to focus on based on application results
4. Application strategy suggestions

Insights:"""

        insights_text = _call_watsonx_api(prompt, max_tokens=700)
        
        success_rate = round((offers / total * 100) if total > 0 else 0, 1)
        interview_rate = round((interviews / total * 100) if total > 0 else 0, 1)
        
        result = {
            "success_rate": success_rate,
            "interview_rate": interview_rate,
            "summary": insights_text or f"You've applied to {total} jobs with a {success_rate}% offer rate.",
            "recommendations": [
                "Tailor your resume to each job posting",
                "Follow up on applications after 5-7 days",
                "Practice interview skills for common questions"
            ],
            "trending_companies": list(set([a.get("job", {}).get("company", "") for a in applications[:10]])),
            "top_skills_needed": list(set([skill for a in applications for skill in a.get("job", {}).get("skills_required", [])[:3]]))[:10]
        }
        
        logger.info("Generated AI insights for user applications")
        return result
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return {
            "success_rate": 0,
            "interview_rate": 0,
            "summary": "Keep applying and stay positive!",
            "recommendations": ["Continue your job search"],
            "trending_companies": [],
            "top_skills_needed": []
        }


# ============================================================================
# INTERVIEW PREP AGENTS - Multi-Agent System for Interview Preparation
# ============================================================================

def _extract_job_requirements(role: str, description: str) -> List[str]:
    """
    AGENT 1: Job Requirements Analyzer
    Extracts key skills and requirements from job description
    """
    try:
        # Parse description for common technical keywords
        tech_keywords = {
            'python': 'Python programming',
            'java': 'Java development',
            'javascript': 'JavaScript/Node.js',
            'react': 'React frontend framework',
            'aws': 'AWS cloud services',
            'azure': 'Azure cloud platform',
            'docker': 'Docker containerization',
            'kubernetes': 'Kubernetes orchestration',
            'sql': 'SQL databases',
            'api': 'REST API design',
            'agile': 'Agile methodology',
            'git': 'Git version control',
            'ci/cd': 'CI/CD pipelines',
            'machine learning': 'Machine learning',
            'data': 'Data analysis',
            'cloud': 'Cloud computing'
        }
        
        description_lower = description.lower()
        role_lower = role.lower()
        
        requirements = []
        for keyword, full_name in tech_keywords.items():
            if keyword in description_lower or keyword in role_lower:
                requirements.append(full_name)
        
        # Add generic requirements based on role
        if any(x in role_lower for x in ['senior', 'lead', 'principal']):
            requirements.insert(0, "Leadership and mentoring")
        if any(x in role_lower for x in ['frontend', 'ui', 'ux']):
            requirements.append("UI/UX principles")
        if any(x in role_lower for x in ['backend', 'server']):
            requirements.append("Backend architecture")
        
        return requirements[:5] or ["Problem solving", "Communication", "Technical depth"]
        
    except Exception as e:
        logger.error(f"Error in Job Requirements Analyzer: {e}")
        return ["Problem solving", "Communication", "Teamwork"]


def _generate_technical_questions(role: str, requirements: List[str]) -> List[str]:
    """
    AGENT 2: Technical Interview Agent
    Generates role-specific technical questions based on job requirements
    """
    try:
        role_lower = role.lower()
        questions = []
        
        # Role-specific technical questions
        if 'frontend' in role_lower or 'react' in role_lower:
            questions.extend([
                "Explain the component lifecycle in React and how hooks changed it",
                f"How would you optimize performance in a large {role} application?",
                "Describe your approach to state management - Redux vs Context API",
                "What's the difference between controlled and uncontrolled components?",
                "How do you handle complex form validation in React?"
            ])
        elif 'backend' in role_lower or 'api' in role_lower:
            questions.extend([
                f"Design a scalable API for a {role} role - walk us through your approach",
                "How do you handle database optimization and query performance?",
                "Explain your approach to API versioning and backward compatibility",
                "How do you implement authentication and authorization?",
                "Describe your caching strategy for high-traffic applications"
            ])
        elif 'full stack' in role_lower:
            questions.extend([
                f"Walk us through your tech stack and why you chose it for {role}",
                "How do you ensure consistency between frontend and backend?",
                "Describe your deployment pipeline and monitoring strategy",
                "How do you approach database design in a full-stack project?",
                "Explain your approach to testing across the full stack"
            ])
        else:
            # Generic technical questions
            questions.extend([
                f"Tell us about a complex technical challenge you solved for a {role} position",
                f"How do you stay updated with new technologies relevant to {role}?",
                "Describe your approach to code review and quality assurance",
                "What's your experience with version control and collaboration?",
                f"How do you approach debugging in {role}?"
            ])
        
        # Add requirement-specific questions
        for req in requirements[:2]:
            if 'kubernetes' in req.lower():
                questions.append("Explain Kubernetes architecture and container orchestration benefits")
            elif 'ci/cd' in req.lower():
                questions.append("How would you design a CI/CD pipeline for this role?")
            elif 'cloud' in req.lower():
                questions.append(f"What's your experience with cloud services in {role}?")
        
        return questions[:5]
        
    except Exception as e:
        logger.error(f"Error in Technical Interview Agent: {e}")
        return [
            "Tell us about a complex technical challenge you've solved",
            "How do you approach system design?",
            "Describe your experience with relevant technologies"
        ]


def _generate_behavioral_questions(company: str, role: str) -> List[str]:
    """
    AGENT 3: Behavioral Interview Agent
    Generates behavioral questions customized to company culture
    """
    try:
        questions = [
            f"Why are you interested in the {role} position at {company}?",
            "Tell us about a time you had to collaborate with a difficult team member",
            "Describe a situation where you had to meet a tight deadline - how did you handle it?",
            f"What attracted you to {company}'s mission and culture?",
            "Tell us about a time you failed - what did you learn?",
            "Describe a time you took initiative and went above and beyond",
            "How do you handle constructive criticism and feedback?",
            "Tell us about a time you improved a process or suggested innovation",
            f"Why do you think you're a good fit for {company}?",
            "Describe your approach to continuous learning and professional development"
        ]
        
        # Customize first question based on company
        company_lower = company.lower()
        if 'tech' in company_lower or 'software' in company_lower:
            questions[0] = f"What excites you about working on {role} challenges at {company}?"
        elif 'finance' in company_lower:
            questions[0] = f"How do your analytical skills apply to the {role} position at {company}?"
        elif 'startup' in company_lower or 'ai' in company_lower or 'ml' in company_lower:
            questions[0] = f"What draws you to the fast-paced environment of {company} for this {role}?"
        
        return questions[:5]
        
    except Exception as e:
        logger.error(f"Error in Behavioral Interview Agent: {e}")
        return [
            "Why are you interested in this role?",
            "Tell us about a time you faced a challenge",
            "How do you handle teamwork?"
        ]


def _generate_interview_tips(company: str, role: str, requirements: List[str]) -> List[str]:
    """
    AGENT 4: Interview Coaching Agent
    Generates customized interview tips and success strategies
    """
    try:
        tips = [
            f"Research {company}'s recent products, initiatives, and company culture before the interview",
            "Use the STAR method (Situation, Task, Action, Result) for behavioral questions",
            "Prepare 3-5 specific examples from your experience that highlight relevant achievements",
            "Ask thoughtful questions about the team structure and success metrics for the role",
            f"Highlight your experience with {requirements[0] if requirements else 'relevant technologies'}"
        ]
        
        # Add role-specific tips
        role_lower = role.lower()
        if 'senior' in role_lower or 'lead' in role_lower:
            tips.append("Emphasize leadership, mentoring, and strategic thinking examples")
            tips.append("Be prepared to discuss architectural decisions and technical trade-offs")
        if 'backend' in role_lower:
            tips.append("Be ready to discuss system design and scalability concepts")
        if 'frontend' in role_lower:
            tips.append("Prepare to discuss user experience and performance optimization")
        
        # Generic success tips
        tips.extend([
            "Maintain eye contact and use confident body language",
            "Listen carefully and take notes during the interview"
        ])
        
        return tips[:7]
        
    except Exception as e:
        logger.error(f"Error in Interview Coaching Agent: {e}")
        return [
            "Research the company thoroughly",
            "Prepare specific examples",
            "Ask thoughtful questions"
        ]


def _generate_preparation_checklist(role: str) -> List[str]:
    """
    AGENT 5: Preparation Agent
    Creates a comprehensive preparation checklist
    """
    try:
        checklist = [
            "✓ Review your resume and be ready to discuss each point in detail",
            "✓ Research the company: mission, products, recent news, and company culture",
            f"✓ Study the {role} role requirements and prepare relevant examples",
            "✓ Prepare 5-7 specific STAR method examples from your experience",
            "✓ Prepare thoughtful questions to ask the interviewer (at least 5)",
            "✓ Test your tech setup if it's a virtual interview (camera, mic, lighting)",
            "✓ Plan your outfit - dress professionally and appropriately for the company",
            "✓ Plan your travel/setup - arrive 10-15 minutes early for in-person interviews",
            "✓ Bring printed copies of your resume and cover letter",
            "✓ Practice your answers and mock interview with a friend or mentor",
            "✓ Get a good night's sleep the day before",
            "✓ Eat a healthy meal before the interview"
        ]
        
        return checklist
        
    except Exception as e:
        logger.error(f"Error in Preparation Agent: {e}")
        return [
            "Review your resume",
            "Research the company",
            "Prepare examples",
            "Practice your answers"
        ]
