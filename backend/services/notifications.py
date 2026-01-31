"""
Notification Service
Sends email notifications for follow-ups, job alerts, and weekly summaries
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Job Tracker")


def send_email(to_email: str, subject: str, html_content: str, plain_text: Optional[str] = None) -> bool:
    """
    Send email via SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        plain_text: Plain text alternative (optional)
        
    Returns:
        True if sent successfully, False otherwise
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add plain text version
        if plain_text:
            message.attach(MIMEText(plain_text, "plain"))
        else:
            # Create plain text from HTML (simple strip)
            plain_text = html_content.replace("<br>", "\n").replace("<p>", "\n")
            message.attach(MIMEText(plain_text, "plain"))
        
        # Add HTML version
        message.attach(MIMEText(html_content, "html"))
        
        # Connect and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def send_follow_up_reminder(application: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """
    Send follow-up reminder email for an application
    
    Args:
        application: Application data with job details
        user: User data with email
        
    Returns:
        True if sent successfully
    """
    try:
        job = application.get("job", {})
        job_title = job.get("title", "Job")
        company = job.get("company", "Company")
        applied_date = application.get("applied_date")
        status = application.get("status", "applied")
        
        days_since_applied = 0
        if applied_date:
            if isinstance(applied_date, str):
                applied_date = datetime.fromisoformat(applied_date.replace("Z", "+00:00"))
            days_since_applied = (datetime.utcnow() - applied_date).days
        
        subject = f"Follow-up Reminder: {job_title} at {company}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .job-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }}
        .action-button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📬 Follow-up Reminder</h1>
        </div>
        <div class="content">
            <p>Hi {user.get('name', 'there')},</p>
            
            <p>It's been <strong>{days_since_applied} days</strong> since you applied for this position:</p>
            
            <div class="job-details">
                <h3>{job_title}</h3>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>Status:</strong> {status.replace('_', ' ').title()}</p>
                <p><strong>Applied:</strong> {applied_date.strftime('%B %d, %Y') if applied_date else 'N/A'}</p>
            </div>
            
            <p><strong>Suggested Actions:</strong></p>
            <ul>
                <li>Send a polite follow-up email to the hiring manager</li>
                <li>Connect with the recruiter on LinkedIn</li>
                <li>Check the company's career page for updates</li>
            </ul>
            
            <p>Stay proactive in your job search!</p>
            
            <a href="{job.get('url', '#')}" class="action-button">View Job Posting</a>
        </div>
        <div class="footer">
            <p>This is an automated reminder from your Job Tracker application.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return send_email(user.get("email"), subject, html_content)
        
    except Exception as e:
        logger.error(f"Error sending follow-up reminder: {e}")
        return False


def send_new_job_alert(user: Dict[str, Any], jobs: List[Dict[str, Any]]) -> bool:
    """
    Send email notification about new matching jobs
    
    Args:
        user: User data
        jobs: List of matching jobs
        
    Returns:
        True if sent successfully
    """
    try:
        if not jobs:
            return False
        
        subject = f"🎯 {len(jobs)} New Matching Jobs Found!"
        
        # Build job cards HTML
        job_cards = ""
        for job in jobs[:5]:  # Limit to 5 jobs in email
            match_score = job.get("match_score", 0)
            job_cards += f"""
            <div class="job-card">
                <h3>{job.get('title', 'Job Title')}</h3>
                <p><strong>{job.get('company', 'Company')}</strong> - {job.get('location', 'Location')}</p>
                <p>Match Score: <span style="color: #10B981; font-weight: bold;">{match_score}%</span></p>
                <p>{job.get('description', '')[:150]}...</p>
                <a href="{job.get('url', '#')}" style="color: #4F46E5;">View Job →</a>
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .job-card {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #10B981; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 New Jobs Matching Your Profile!</h1>
        </div>
        <div class="content">
            <p>Hi {user.get('name', 'there')},</p>
            
            <p>We found <strong>{len(jobs)} new jobs</strong> that match your profile and preferences.</p>
            
            {job_cards}
            
            {'<p><em>And ' + str(len(jobs) - 5) + ' more jobs...</em></p>' if len(jobs) > 5 else ''}
            
            <p style="margin-top: 30px;">
                <a href="http://localhost:3000/jobs" style="display: inline-block; padding: 12px 24px; background-color: #10B981; color: white; text-decoration: none; border-radius: 5px;">View All Jobs</a>
            </p>
        </div>
        <div class="footer">
            <p>This is an automated alert from your Job Tracker application.</p>
            <p>Update your preferences anytime in your profile settings.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return send_email(user.get("email"), subject, html_content)
        
    except Exception as e:
        logger.error(f"Error sending job alert: {e}")
        return False


def send_weekly_summary(user: Dict[str, Any], stats: Dict[str, Any]) -> bool:
    """
    Send weekly summary email with application stats
    
    Args:
        user: User data
        stats: Dictionary with weekly statistics
        
    Returns:
        True if sent successfully
    """
    try:
        subject = f"📊 Your Weekly Job Search Summary"
        
        total_apps = stats.get("total_applications", 0)
        new_apps = stats.get("new_applications", 0)
        interviews = stats.get("interviews_scheduled", 0)
        offers = stats.get("offers_received", 0)
        rejections = stats.get("rejections", 0)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
        .stat-card {{ background-color: #f9f9f9; padding: 20px; text-align: center; border-radius: 5px; }}
        .stat-number {{ font-size: 32px; font-weight: bold; color: #4F46E5; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .insights {{ background-color: #FEF3C7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Summary</h1>
            <p>Your job search at a glance</p>
        </div>
        <div class="content">
            <p>Hi {user.get('name', 'there')},</p>
            
            <p>Here's your job search activity for this week:</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_apps}</div>
                    <div class="stat-label">Total Applications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{new_apps}</div>
                    <div class="stat-label">New This Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{interviews}</div>
                    <div class="stat-label">Interviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{offers}</div>
                    <div class="stat-label">Offers</div>
                </div>
            </div>
            
            <div class="insights">
                <h3>💡 Insights & Recommendations</h3>
                <ul>
                    <li>You're making great progress! Keep up the momentum.</li>
                    <li>Consider following up on applications older than 2 weeks.</li>
                    <li>Update your resume with recent projects and achievements.</li>
                </ul>
            </div>
            
            <p style="margin-top: 30px;">
                <a href="http://localhost:3000/dashboard" style="display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px;">View Dashboard</a>
            </p>
        </div>
        <div class="footer">
            <p>This is your weekly summary from Job Tracker.</p>
            <p>Keep tracking, keep improving!</p>
        </div>
    </div>
</body>
</html>
"""
        
        return send_email(user.get("email"), subject, html_content)
        
    except Exception as e:
        logger.error(f"Error sending weekly summary: {e}")
        return False


def test_email_config() -> bool:
    """
    Test email configuration
    
    Returns:
        True if configuration is valid
    """
    try:
        if not SMTP_USER or not SMTP_PASSWORD:
            return False
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
        
        logger.info("Email configuration test successful")
        return True
        
    except Exception as e:
        logger.error(f"Email configuration test failed: {e}")
        return False
