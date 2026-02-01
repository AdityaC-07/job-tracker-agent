"""
Resume Parser Service
Extracts structured data from PDF and DOCX resume files
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)

# Comprehensive skills database (100+ tech skills)
SKILLS_DATABASE = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin",
    "go", "rust", "scala", "r", "matlab", "perl", "shell", "bash", "powershell",
    
    # Web Development
    "react", "angular", "vue", "vue.js", "node.js", "express", "django", "flask", "fastapi",
    "spring", "spring boot", "asp.net", "laravel", "rails", "next.js", "nuxt.js", "svelte",
    "html", "html5", "css", "css3", "sass", "scss", "tailwind", "bootstrap", "jquery",
    
    # Mobile Development
    "react native", "flutter", "android", "ios", "xamarin", "ionic",
    
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
    "oracle", "sql server", "sqlite", "mariadb", "neo4j", "firebase",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "gitlab ci",
    "github actions", "terraform", "ansible", "chef", "puppet", "circleci", "travis ci",
    
    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "data analysis", "nlp",
    "computer vision", "neural networks", "ai", "artificial intelligence",
    
    # Other Technologies
    "git", "linux", "unix", "agile", "scrum", "jira", "rest api", "graphql", "microservices",
    "ci/cd", "testing", "unit testing", "integration testing", "selenium", "jest", "pytest",
    "spark", "hadoop", "kafka", "rabbitmq", "nginx", "apache", "websockets", "grpc"
}

# Education degree patterns
DEGREE_PATTERNS = [
    r"(?:bachelor|b\.?tech|b\.?e\.?|b\.?s\.?|bs|ba|bsc|beng)\s+(?:of\s+)?(?:science|engineering|arts|technology)?",
    r"(?:master|m\.?tech|m\.?e\.?|m\.?s\.?|ms|ma|msc|meng|mba)\s+(?:of\s+)?(?:science|engineering|arts|technology|business)?",
    r"(?:phd|ph\.d|doctorate|doctor\s+of\s+philosophy)",
    r"associate(?:'s)?\s+degree",
    r"diploma"
]


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using PyMuPDF
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    if not FITZ_AVAILABLE:
        raise ValueError("PDF parsing is unavailable. Install PyMuPDF to enable it.")

    try:
        doc = fitz.open(file_path)
        text_parts = []

        for page in doc:
            page_text = page.get_text()
            if not page_text.strip():
                blocks = page.get_text("blocks")
                block_text = " ".join([block[4] for block in blocks if len(block) > 4])
                page_text = block_text
            text_parts.append(page_text)

        doc.close()
        return "\n".join(text_parts)
        
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise ValueError(f"Failed to parse PDF file: {str(e)}")


def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file using python-docx
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text content
    """
    if not DOCX_AVAILABLE:
        raise ValueError("DOCX parsing is unavailable. Install python-docx to enable it.")

    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
        
    except Exception as e:
        logger.error(f"Error parsing DOCX: {e}")
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text using regex
    
    Args:
        text: Resume text
        
    Returns:
        Email address or None
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number from text using regex
    
    Args:
        text: Resume text
        
    Returns:
        Phone number or None
    """
    # Matches various phone formats: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
    phone_patterns = [
        r'\+?1?\s*\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'\b\d{10}\b',
        r'\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}'
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                return f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
            return matches[0]
    
    return None


def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from resume text
    Matches against comprehensive skills database
    
    Args:
        text: Resume text
        
    Returns:
        List of identified skills
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in SKILLS_DATABASE:
        # Use word boundaries for exact matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Return proper casing
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
    
    # Remove duplicates and sort
    return sorted(list(set(found_skills)))


def extract_education(text: str) -> Dict[str, Any]:
    """
    Extract education information from resume
    
    Args:
        text: Resume text
        
    Returns:
        Dictionary with degree, field, institution, graduation year
    """
    education = {
        "degree": None,
        "field": None,
        "institution": None,
        "graduation_year": None
    }
    
    text_lower = text.lower()
    
    # Extract degree
    for pattern in DEGREE_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            education["degree"] = match.group(0).strip().title()
            break
    
    # Extract graduation year (4-digit year between 1980 and 2030)
    year_pattern = r'\b(19[89]\d|20[0-3]\d)\b'
    years = re.findall(year_pattern, text)
    if years:
        # Take the most recent year
        education["graduation_year"] = int(max(years))
    
    # Extract field of study (common patterns)
    field_keywords = [
        "computer science", "software engineering", "information technology",
        "electrical engineering", "mechanical engineering", "business administration",
        "data science", "artificial intelligence", "mathematics", "physics"
    ]
    
    for field in field_keywords:
        if field in text_lower:
            education["field"] = field.title()
            break
    
    # Extract institution (look for "University", "Institute", "College")
    institution_pattern = r'(?:university|institute|college)\s+of\s+[\w\s]+|[\w\s]+\s+(?:university|institute|college)'
    institution_match = re.search(institution_pattern, text, re.IGNORECASE)
    if institution_match:
        education["institution"] = institution_match.group(0).strip().title()
    
    return education


def extract_experience(text: str) -> List[Dict[str, Any]]:
    """
    Extract work experience entries from resume
    
    Args:
        text: Resume text
        
    Returns:
        List of experience dictionaries
    """
    experiences = []
    
    # Look for date patterns indicating work periods
    # Patterns like: Jan 2020 - Dec 2022, 2020-2022, 01/2020 - 12/2022
    date_patterns = [
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*[-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)',
        r'(\d{2}/\d{4})\s*[-–—]\s*(\d{2}/\d{4}|Present|Current)',
        r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)'
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            experiences.append({
                "start_date": match.group(1),
                "end_date": match.group(2),
                "current": match.group(2).lower() in ["present", "current"]
            })
    
    return experiences[:5]  # Return max 5 experiences


def calculate_experience_years(text: str) -> float:
    """
    Calculate total years of experience from resume
    
    Args:
        text: Resume text
        
    Returns:
        Years of experience as float
    """
    # Try explicit mentions first
    explicit_patterns = [
        r'(\d+\.?\d*)\s*\+?\s*years?\s+of\s+experience',
        r'experience\s*:\s*(\d+\.?\d*)\s*\+?\s*years?'
    ]
    
    for pattern in explicit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    # Calculate from work experience dates
    experiences = extract_experience(text)
    
    if not experiences:
        return 0.0
    
    total_months = 0
    current_year = datetime.now().year
    
    for exp in experiences:
        start = exp.get("start_date", "")
        end = exp.get("end_date", "")
        
        # Extract years
        start_year = None
        end_year = current_year if exp.get("current") else None
        
        start_match = re.search(r'\d{4}', start)
        if start_match:
            start_year = int(start_match.group())
        
        if not exp.get("current"):
            end_match = re.search(r'\d{4}', end)
            if end_match:
                end_year = int(end_match.group())
        
        if start_year and end_year:
            years = end_year - start_year
            total_months += max(years * 12, 0)
    
    return round(total_months / 12, 1)


def parse_resume(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Main function to parse resume and extract all information
    
    Args:
        file_path: Path to resume file
        file_type: 'pdf' or 'docx'
        
    Returns:
        Dictionary with all extracted resume data
    """
    try:
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            text = parse_pdf(file_path)
        elif file_type.lower() in ['docx', 'doc']:
            text = parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        text_length = len(text.strip())
        logger.info(f"Extracted resume text length: {text_length}")

        if text_length < 50:
            raise ValueError(
                "No readable text found in the resume. Please upload a text-based PDF or a DOCX file."
            )

        # Extract all information
        result = {
            "resume_text": text,
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": extract_skills(text),
            "education": extract_education(text),
            "experience_years": calculate_experience_years(text),
            "work_experiences": extract_experience(text)
        }
        
        logger.info(f"Successfully parsed resume: {len(result['skills'])} skills found, {result['experience_years']} years experience")
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        raise ValueError(f"Failed to parse resume: {str(e)}")
