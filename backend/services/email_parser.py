"""
Email Parser Service
Parses job alert emails from LinkedIn, Naukri, Indeed, etc.
"""
import os
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("SMTP_USER", "")
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Job alert email addresses
JOB_ALERT_SENDERS = [
    "linkedin.com",
    "naukri.com",
    "indeed.com",
    "jobalerts@",
    "jobs@",
    "careers@"
]


def connect_to_email() -> Optional[imaplib.IMAP4_SSL]:
    """
    Connect to email server via IMAP
    
    Returns:
        IMAP connection object or None
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.warning("Email credentials not configured")
        return None
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        logger.info("Successfully connected to email server")
        return mail
        
    except Exception as e:
        logger.error(f"Error connecting to email: {e}")
        return None


def fetch_job_alerts(days: int = 7, max_emails: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch job alert emails from inbox
    
    Args:
        days: Number of days to look back
        max_emails: Maximum emails to fetch
        
    Returns:
        List of parsed job dictionaries
    """
    mail = connect_to_email()
    if not mail:
        return []
    
    try:
        # Select inbox
        mail.select("inbox")
        
        # Build search criteria for job alerts
        search_criteria = []
        for sender in JOB_ALERT_SENDERS:
            search_criteria.append(f'FROM "{sender}"')
        
        # Search for recent emails
        search_query = f'(OR {" ".join(search_criteria)}) SINCE {days}-days-ago'
        
        # Fallback to simpler search if complex query fails
        try:
            status, messages = mail.search(None, search_query)
        except:
            # Try simpler search
            status, messages = mail.search(None, 'ALL')
        
        if status != "OK":
            logger.error("Failed to search emails")
            return []
        
        email_ids = messages[0].split()
        email_ids = email_ids[-max_emails:]  # Limit number of emails
        
        all_jobs = []
        
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract jobs from email
                jobs = parse_email(email_message)
                all_jobs.extend(jobs)
                
            except Exception as e:
                logger.error(f"Error processing email {email_id}: {e}")
                continue
        
        mail.close()
        mail.logout()
        
        logger.info(f"Fetched {len(all_jobs)} jobs from {len(email_ids)} emails")
        return all_jobs
        
    except Exception as e:
        logger.error(f"Error fetching job alerts: {e}")
        return []


def parse_email(email_message: email.message.Message) -> List[Dict[str, Any]]:
    """
    Parse job information from email message
    
    Args:
        email_message: Email message object
        
    Returns:
        List of job dictionaries extracted from email
    """
    try:
        # Get email subject
        subject = ""
        if email_message["Subject"]:
            subject_parts = decode_header(email_message["Subject"])
            subject = "".join([
                part[0].decode(part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0]
                for part in subject_parts
            ])
        
        # Get email sender
        sender = email_message["From"]
        
        # Determine source
        source = "email"
        if "linkedin" in sender.lower():
            source = "linkedin_email"
        elif "indeed" in sender.lower():
            source = "indeed_email"
        elif "naukri" in sender.lower():
            source = "naukri_email"
        
        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif content_type == "text/plain" and not body:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Extract jobs from HTML body
        if body:
            jobs = extract_jobs_from_html(body, source)
            return jobs
        
        return []
        
    except Exception as e:
        logger.error(f"Error parsing email: {e}")
        return []


def extract_jobs_from_html(html_content: str, source: str) -> List[Dict[str, Any]]:
    """
    Extract job postings from HTML email content
    
    Args:
        html_content: HTML email body
        source: Email source identifier
        
    Returns:
        List of job dictionaries
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # Find job links (common patterns)
        job_links = []
        
        # LinkedIn pattern
        linkedin_links = soup.find_all('a', href=re.compile(r'linkedin\.com/jobs/view'))
        for link in linkedin_links:
            job_links.append({
                "url": link.get('href'),
                "title": link.get_text(strip=True),
                "source": "linkedin_email"
            })
        
        # Indeed pattern
        indeed_links = soup.find_all('a', href=re.compile(r'indeed\.com/.*jk='))
        for link in indeed_links:
            job_links.append({
                "url": link.get('href'),
                "title": link.get_text(strip=True),
                "source": "indeed_email"
            })
        
        # Generic job links
        generic_links = soup.find_all('a', href=re.compile(r'job|career|apply', re.IGNORECASE))
        for link in generic_links:
            href = link.get('href', '')
            if href and 'unsubscribe' not in href.lower() and 'linkedin.com' not in href and 'indeed.com' not in href:
                job_links.append({
                    "url": href,
                    "title": link.get_text(strip=True),
                    "source": source
                })
        
        # Extract job information
        for job_link in job_links[:20]:  # Limit to 20 jobs per email
            title = job_link.get("title", "")
            url = job_link.get("url", "")
            
            if not title or len(title) < 5 or len(title) > 200:
                continue
            
            # Try to extract company and location from nearby text
            company = "Unknown"
            location = ""
            
            # Clean title
            title = re.sub(r'\s+', ' ', title).strip()
            
            job = {
                "external_id": None,
                "source": job_link.get("source", source),
                "title": title,
                "company": company,
                "location": location,
                "job_type": None,
                "description": "",
                "requirements": None,
                "skills_required": [],
                "experience_min": None,
                "experience_max": None,
                "salary_min": None,
                "salary_max": None,
                "url": url,
                "posted_date": datetime.utcnow(),
                "is_active": True
            }
            
            jobs.append(job)
        
        logger.debug(f"Extracted {len(jobs)} jobs from HTML")
        return jobs
        
    except Exception as e:
        logger.error(f"Error extracting jobs from HTML: {e}")
        return []


def parse_job_details_from_text(text: str) -> Dict[str, Any]:
    """
    Extract structured job details from text
    
    Args:
        text: Job description text
        
    Returns:
        Dictionary with extracted job details
    """
    details = {
        "company": None,
        "location": None,
        "salary": None,
        "experience": None
    }
    
    try:
        # Extract company (look for "at Company" or "Company Name")
        company_match = re.search(r'at\s+([A-Z][A-Za-z\s&]+?)(?:\s+in|\s+\||$)', text)
        if company_match:
            details["company"] = company_match.group(1).strip()
        
        # Extract location
        location_match = re.search(r'(?:in|location:)\s*([A-Z][A-Za-z\s,]+?)(?:\s+\||$)', text, re.IGNORECASE)
        if location_match:
            details["location"] = location_match.group(1).strip()
        
        # Extract salary
        salary_match = re.search(r'\$\s*(\d+[,\d]*)\s*-\s*\$\s*(\d+[,\d]*)', text)
        if salary_match:
            details["salary"] = f"${salary_match.group(1)}-${salary_match.group(2)}"
        
        # Extract experience
        exp_match = re.search(r'(\d+)\+?\s*years?', text, re.IGNORECASE)
        if exp_match:
            details["experience"] = f"{exp_match.group(1)}+ years"
        
        return details
        
    except Exception as e:
        logger.error(f"Error parsing job details: {e}")
        return details


def test_email_connection() -> bool:
    """
    Test email connection
    
    Returns:
        True if connection successful, False otherwise
    """
    mail = connect_to_email()
    if mail:
        try:
            mail.close()
            mail.logout()
        except:
            pass
        return True
    return False
