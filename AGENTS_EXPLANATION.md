# Multi-Agent System Architecture - Job Tracker Agent

## Overview
The Job Tracker Application uses a **multi-agent AI system** to personalize interview preparation for each job application. This document explains what each agent does and how they work together.

---

## Interview Preparation Multi-Agent System

When you generate interview prep for a specific job, **5 specialized AI agents** work together in parallel to create customized, job-specific content. Here's what each agent does:

### 1. **Job Requirements Analyzer Agent**
**Purpose:** Extracts and identifies key skills, technologies, and requirements from the job posting.

**What it does:**
- Scans the job title and description for technical keywords (Python, React, AWS, Docker, etc.)
- Identifies role level (Senior, Lead, Principal) and specialization (Frontend, Backend, Full Stack)
- Creates a list of 3-5 key requirements specific to that position
- Determines if the role is leadership-focused, UI/UX-focused, or architecture-focused

**Example Output:**
- For a "Senior React Developer" role → ["React frontend framework", "JavaScript/Node.js", "Leadership and mentoring", "UI/UX principles"]
- For a "Backend Engineer" role → ["Backend architecture", "API REST design", "Python programming", "Kubernetes orchestration"]

**Why it matters:** This ensures all other agents understand the specific context of the job.

---

### 2. **Technical Interview Agent**
**Purpose:** Generates role-specific technical questions that candidates will actually face.

**What it does:**
- Creates 5 different technical questions based on the job role
- Tailors questions to the specific technologies and frameworks required
- For Frontend roles: Asks about React lifecycle, state management, component optimization
- For Backend roles: Asks about API design, database optimization, caching strategies
- For Full-Stack roles: Asks about tech stack decisions, deployment pipelines, full-stack testing

**Example Questions:**
- Frontend Role: "Explain the component lifecycle in React and how hooks changed it"
- Backend Role: "Design a scalable API for this role - walk us through your approach"
- Full-Stack Role: "Walk us through your tech stack and why you chose it for this position"

**Why it matters:** Candidates get relevant technical questions specific to the job, not generic questions.

---

### 3. **Behavioral Interview Agent**
**Purpose:** Generates behavioral and cultural fit questions customized to the company.

**What it does:**
- Creates 5 behavioral questions tailored to the company and role
- Customizes the first question based on company type (Tech, Finance, Startup, AI/ML)
- Generates STAR-method-friendly questions (Situation, Task, Action, Result)
- Focuses on company culture alignment, teamwork, and growth mindset

**Example Questions:**
- "Why are you interested in the Senior React Developer position at Google?"
- "Tell us about a time you had to collaborate with a difficult team member"
- "Describe a situation where you had to meet a tight deadline"
- "What attracted you to this company's mission and culture?"

**Why it matters:** Candidates understand what the company values and can prepare relevant stories.

---

### 4. **Interview Coaching Agent**
**Purpose:** Provides personalized coaching tips and success strategies.

**What it does:**
- Generates 7 interview tips customized to the role and company
- Provides research guidance specific to the company
- Suggests STAR method examples to prepare
- For Senior roles: Emphasizes leadership and mentoring examples
- For different specializations: Provides specific preparation advice
- Includes universal success strategies (eye contact, listening, note-taking)

**Example Tips:**
- "Research Google's recent products, initiatives, and company culture before the interview"
- "Highlight your experience with React frontend framework"
- "Emphasize leadership, mentoring, and strategic thinking examples" (for senior roles)
- "Be ready to discuss system design and scalability concepts" (for backend roles)

**Why it matters:** Candidates get actionable, specific advice on how to succeed.

---

### 5. **Preparation Agent**
**Purpose:** Creates a comprehensive, role-specific preparation checklist.

**What it does:**
- Generates a 12-item preparation checklist
- Covers resume review, company research, example preparation, practice, and logistics
- Includes pre-interview setup and wellness tips
- Provides a structured roadmap to interview readiness

**Example Checklist:**
- ✓ Review your resume and be ready to discuss each point in detail
- ✓ Research the company: mission, products, recent news, and company culture
- ✓ Study the React Developer role requirements and prepare relevant examples
- ✓ Prepare 5-7 specific STAR method examples from your experience
- ✓ Prepare thoughtful questions to ask the interviewer (at least 5)
- ✓ Test your tech setup if it's a virtual interview
- ✓ Plan your outfit - dress professionally
- ✓ Practice your answers with a friend or mentor

**Why it matters:** Candidates have a clear roadmap to prepare thoroughly for their specific interview.

---

## How Agents Work Together

### Data Flow:
1. **User selects a job application**
2. **Job Requirements Analyzer** extracts requirements from that specific job posting
3. **Technical, Behavioral, and Coaching Agents** all use those requirements to generate targeted content
4. **Preparation Agent** creates a final checklist
5. **All outputs are combined** and displayed to the user

### Key Insight:
Each job generates **different** interview prep because each agent reads the specific job posting and generates content based on:
- The exact job title
- The actual job description
- The company name and type
- The technologies and skills required

---

## Example: Different Prep for Different Roles

### Scenario 1: React Frontend Developer at Airbnb
- **Technical Agent** generates: React-specific questions about hooks, state management, performance
- **Behavioral Agent** generates: Questions about Airbnb's travel mission and culture
- **Coaching Agent** emphasizes: "Be ready to discuss UI/UX principles" and "User experience optimization"

### Scenario 2: Backend Engineer at Amazon
- **Technical Agent** generates: AWS, API design, and system scalability questions
- **Behavioral Agent** generates: Questions about Amazon's leadership principles and innovation
- **Coaching Agent** emphasizes: "Be ready to discuss system design" and "Scalability concepts"

Both candidates see completely different interview prep because the agents customize based on the **specific job posting**.

---

## What This Means for Your Hackathon Demo

✅ **Show Different Agents Working:** Generate prep for 2-3 different job applications and show how the questions/tips are completely different

✅ **Highlight the "Agents Used" Section:** The UI displays which agents completed work and their status - this visually demonstrates multi-agent orchestration

✅ **Explain the Customization:** Point out that:
- Technical questions are specific to the role (Frontend vs Backend)
- Behavioral questions reference the actual company
- Tips are tailored to the job requirements
- Each job generates unique prep

✅ **Demonstrate Agent Specialization:**
- Show how the same interview question template generates different questions for different roles
- Explain that each agent has a specific expertise and they work in parallel

---

## Implementation Details

**Backend:** `backend/services/watsonx_service.py`
- `generate_interview_prep()` - Main orchestration function
- `_extract_job_requirements()` - Agent 1
- `_generate_technical_questions()` - Agent 2
- `_generate_behavioral_questions()` - Agent 3
- `_generate_interview_tips()` - Agent 4
- `_generate_preparation_checklist()` - Agent 5

**Frontend:** `frontend/src/pages/InterviewPrep.tsx`
- Displays "AI Agents Working For You" section showing agent names and status
- Shows job-specific: Technical questions, Behavioral questions, Tips, Checklist, Key requirements

---

## Why This Architecture?

1. **Modularity:** Each agent is independent and can be improved separately
2. **Specialization:** Each agent focuses on one type of content
3. **Scalability:** Easy to add new agents (e.g., Salary Negotiation Agent, Equity Evaluation Agent)
4. **Customization:** Agents adapt based on job posting, creating unique prep for each application
5. **Transparency:** Users see which agents worked on their prep

---

## Future Agent Ideas

- **Resume Optimization Agent** - Optimize resume for each specific job
- **Salary Negotiation Agent** - Prep for salary discussions
- **Technical Test Prep Agent** - Prepare for coding challenges
- **Equity Analysis Agent** - Evaluate stock options and compensation
- **Company Culture Agent** - Deep dive into company culture and fit
- **Network Agent** - Find connections at the company
