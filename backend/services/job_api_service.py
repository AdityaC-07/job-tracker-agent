"""
Job API Service
Integrates with multiple job search APIs: Adzuna, JSearch (RapidAPI), The Muse
"""
import os
from typing import List, Dict, Optional, Any
import httpx
import asyncio
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# API Configuration
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")
THEMUSE_API_KEY = os.getenv("THEMUSE_API_KEY", "")

# API Endpoints
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"
JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/search"
THEMUSE_BASE_URL = "https://www.themuse.com/api/public/jobs"

# Request timeout
TIMEOUT = 10.0


async def search_adzuna(keywords: str, location: str = "", page: int = 1, results_per_page: int = 20) -> List[Dict[str, Any]]:
    """
    Search jobs using Adzuna API
    
    Args:
        keywords: Job search keywords
        location: Location filter
        page: Page number
        results_per_page: Number of results per page
        
    Returns:
        List of normalized job dictionaries
    """
    if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
        logger.warning("Adzuna API credentials not configured")
        return []
    
    try:
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "what": keywords,
            "where": location,
            "results_per_page": results_per_page,
            "page": page,
            "content-type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{ADZUNA_BASE_URL}/1", params=params)
            response.raise_for_status()
            data = response.json()
        
        jobs = []
        for item in data.get("results", []):
            job = {
                "external_id": item.get("id"),
                "source": "adzuna",
                "title": item.get("title", ""),
                "company": item.get("company", {}).get("display_name", "Unknown"),
                "location": item.get("location", {}).get("display_name", location),
                "job_type": item.get("contract_time", ""),
                "description": item.get("description", ""),
                "requirements": "",
                "skills_required": [],
                "salary_min": item.get("salary_min"),
                "salary_max": item.get("salary_max"),
                "url": item.get("redirect_url", ""),
                "posted_date": datetime.fromisoformat(item["created"].replace("Z", "+00:00")) if item.get("created") else None,
                "is_active": True
            }
            jobs.append(job)
        
        logger.info(f"Adzuna: Found {len(jobs)} jobs for '{keywords}'")
        return jobs
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Adzuna API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching Adzuna: {e}")
        return []


async def search_jsearch(query: str, location: str = "", page: int = 1, num_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Search jobs using JSearch API (RapidAPI)
    
    Args:
        query: Job search query
        location: Location filter
        page: Page number
        num_pages: Number of pages to fetch
        
    Returns:
        List of normalized job dictionaries
    """
    if not JSEARCH_API_KEY:
        logger.warning("JSearch API key not configured")
        return []
    
    try:
        params = {
            "query": f"{query} {location}".strip(),
            "page": page,
            "num_pages": num_pages
        }
        
        headers = {
            "X-RapidAPI-Key": JSEARCH_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(JSEARCH_BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        jobs = []
        for item in data.get("data", []):
            job = {
                "external_id": item.get("job_id"),
                "source": "jsearch",
                "title": item.get("job_title", ""),
                "company": item.get("employer_name", "Unknown"),
                "location": item.get("job_city", "") + ", " + item.get("job_state", "") if item.get("job_city") else location,
                "job_type": item.get("job_employment_type", ""),
                "description": item.get("job_description", ""),
                "requirements": item.get("job_required_experience", {}).get("required_experience_in_months", ""),
                "skills_required": item.get("job_required_skills", []) or [],
                "salary_min": item.get("job_min_salary"),
                "salary_max": item.get("job_max_salary"),
                "url": item.get("job_apply_link", ""),
                "posted_date": datetime.fromisoformat(item["job_posted_at_datetime_utc"].replace("Z", "+00:00")) if item.get("job_posted_at_datetime_utc") else None,
                "is_active": item.get("job_is_remote", False) or True
            }
            jobs.append(job)
        
        logger.info(f"JSearch: Found {len(jobs)} jobs for '{query}'")
        return jobs
        
    except httpx.HTTPStatusError as e:
        logger.error(f"JSearch API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching JSearch: {e}")
        return []


async def search_themuse(category: str = "", location: str = "", page: int = 0, page_size: int = 20) -> List[Dict[str, Any]]:
    """
    Search jobs using The Muse API
    
    Args:
        category: Job category
        location: Location filter
        page: Page number
        page_size: Number of results per page
        
    Returns:
        List of normalized job dictionaries
    """
    try:
        params = {
            "category": category,
            "location": location,
            "page": page,
            "descending": "true"
        }
        
        # Remove empty params
        params = {k: v for k, v in params.items() if v}
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(THEMUSE_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        jobs = []
        for item in data.get("results", []):
            # Extract location
            locations = item.get("locations", [])
            location_str = locations[0].get("name", location) if locations else location
            
            # Extract job type
            job_type = ""
            if item.get("levels"):
                job_type = item["levels"][0].get("name", "")
            
            job = {
                "external_id": str(item.get("id")),
                "source": "themuse",
                "title": item.get("name", ""),
                "company": item.get("company", {}).get("name", "Unknown"),
                "location": location_str,
                "job_type": job_type,
                "description": item.get("contents", ""),
                "requirements": "",
                "skills_required": [],
                "salary_min": None,
                "salary_max": None,
                "url": item.get("refs", {}).get("landing_page", ""),
                "posted_date": datetime.fromisoformat(item["publication_date"].replace("Z", "+00:00")) if item.get("publication_date") else None,
                "is_active": True
            }
            jobs.append(job)
        
        logger.info(f"The Muse: Found {len(jobs)} jobs for category '{category}'")
        return jobs
        
    except httpx.HTTPStatusError as e:
        logger.error(f"The Muse API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching The Muse: {e}")
        return []


async def aggregate_from_all_sources(keywords: str, location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Aggregate job postings from all available sources in parallel
    
    Args:
        keywords: Job search keywords
        location: Location filter
        max_results: Maximum total results to return
        
    Returns:
        Combined list of jobs from all sources
    """
    logger.info(f"Aggregating jobs from all sources: keywords='{keywords}', location='{location}'")
    
    # Create tasks for parallel API calls
    tasks = []
    
    if ADZUNA_APP_ID and ADZUNA_API_KEY:
        tasks.append(search_adzuna(keywords, location, results_per_page=20))
    
    if JSEARCH_API_KEY:
        tasks.append(search_jsearch(keywords, location, num_pages=1))
    
    # The Muse doesn't require API key
    tasks.append(search_themuse(keywords, location, page_size=20))
    
    # Execute all searches in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results and handle exceptions
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"API call failed: {result}")
    
    # Remove duplicates based on title and company
    seen = set()
    unique_jobs = []
    
    for job in all_jobs:
        key = (job.get("title", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Limit results
    unique_jobs = unique_jobs[:max_results]
    
    logger.info(f"Aggregated {len(unique_jobs)} unique jobs from {len(tasks)} sources")
    return unique_jobs


def normalize_job_data(raw_job: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Normalize job data from different sources to common schema
    
    Args:
        raw_job: Raw job data from API
        source: Source identifier
        
    Returns:
        Normalized job dictionary
    """
    return {
        "external_id": str(raw_job.get("id", "")),
        "source": source,
        "title": raw_job.get("title", ""),
        "company": raw_job.get("company", "Unknown"),
        "location": raw_job.get("location", ""),
        "job_type": raw_job.get("job_type", ""),
        "description": raw_job.get("description", ""),
        "requirements": raw_job.get("requirements", ""),
        "skills_required": raw_job.get("skills_required", []),
        "experience_min": raw_job.get("experience_min"),
        "experience_max": raw_job.get("experience_max"),
        "salary_min": raw_job.get("salary_min"),
        "salary_max": raw_job.get("salary_max"),
        "url": raw_job.get("url", ""),
        "posted_date": raw_job.get("posted_date"),
        "is_active": True
    }
