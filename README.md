# 🎯 Smart Job Application Tracker

A comprehensive full-stack application for tracking job applications with AI-powered matching, resume parsing, and analytics.

## ✨ Features

- 🔐 **User Authentication** - Secure JWT-based authentication
- 📄 **Resume Parser** - Automatic extraction of skills, experience, and education from PDF/DOCX files
- 🔍 **Multi-Source Job Search** - Aggregates jobs from Adzuna, JSearch, and The Muse APIs
- 🤖 **AI-Powered Matching** - Semantic matching between user profiles and job postings using sentence-transformers
- ✍️ **AI Cover Letter Generation** - Automated cover letter creation with IBM watsonx
- 📊 **Application Tracking** - Kanban board and list view for managing applications
- 📈 **Analytics Dashboard** - Comprehensive insights and statistics
- 📧 **Email Notifications** - Follow-up reminders, job alerts, and weekly summaries
- 🏢 **Company Insights** - Aggregated data about companies and interview processes
- 📱 **Responsive UI** - Modern React interface with TailwindCSS

## 🏗️ Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Vite + TS)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend │
│   (Python 3.11) │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐
│MongoDB │ │ Redis  │ │Celery  │
│        │ │        │ │Workers │
└────────┘ └────────┘ └────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with Motor async driver
- **Celery** - Distributed task queue for background jobs
- **Redis** - Message broker and caching
- **Sentence Transformers** - Semantic text embeddings
- **IBM watsonx AI** - AI-powered content generation
- **PyMuPDF & python-docx** - Resume parsing
- **BeautifulSoup** - Email parsing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Build tool and dev server
- **TanStack Query** - Server state management
- **Axios** - HTTP client
- **TailwindCSS** - Utility-first styling
- **Recharts** - Data visualization
- **DND Kit** - Drag and drop functionality

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **MongoDB 6.0+**
- **Redis 7.0+**

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd job-tracker-agent
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### 4. Stop the Application

```bash
docker-compose down
```

## 🔧 Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if any)
# Start development server
uvicorn backend.api.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A backend.tasks.scheduled_tasks worker --loglevel=info

# Run Celery beat (separate terminal)
celery -A backend.tasks.scheduled_tasks beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update profile
- `POST /api/users/resume` - Upload resume

### Jobs
- `POST /api/jobs/search` - Search jobs from APIs
- `GET /api/jobs` - Get jobs with filters
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/manual` - Add manual job entry
- `GET /api/jobs/matches/me` - Get matching jobs

### Applications
- `POST /api/applications` - Create application
- `GET /api/applications` - List applications
- `GET /api/applications/{id}` - Get application details
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application
- `POST /api/applications/{id}/cover-letter` - Generate cover letter
- `POST /api/applications/{id}/follow-up` - Schedule follow-up

### Analytics
- `GET /api/analytics/dashboard` - Dashboard stats
- `GET /api/analytics/timeline` - Application timeline
- `GET /api/analytics/skill-gap` - Skill gap analysis
- `GET /api/analytics/company-insights/{company}` - Company insights

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | MongoDB connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `WATSONX_API_KEY` | IBM watsonx API key | Optional |
| `ADZUNA_APP_ID` | Adzuna API app ID | Optional |
| `ADZUNA_API_KEY` | Adzuna API key | Optional |
| `JSEARCH_API_KEY` | JSearch RapidAPI key | Optional |
| `SMTP_USER` | Email address for notifications | Optional |
| `SMTP_PASSWORD` | Email password/app password | Optional |

## 📂 Project Structure

```
job-tracker-agent/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── users.py
│   │   │   ├── jobs.py
│   │   │   ├── applications.py
│   │   │   └── analytics.py
│   │   └── main.py
│   ├── auth/
│   │   └── jwt_handler.py
│   ├── config/
│   │   └── database.py
│   ├── models/
│   │   └── database.py
│   ├── services/
│   │   ├── resume_parser.py
│   │   ├── job_api_service.py
│   │   ├── matcher.py
│   │   ├── watsonx_service.py
│   │   ├── email_parser.py
│   │   └── notifications.py
│   ├── tasks/
│   │   └── scheduled_tasks.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   └── index.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔄 Background Tasks

Celery handles scheduled tasks:

- **Daily (9:00 AM)** - Check pending follow-ups and send reminders
- **Daily (8:00 AM)** - Fetch new jobs and send alerts to users
- **Weekly (Sunday 6:00 PM)** - Send weekly summary emails

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Adzuna API for job listings
- JSearch RapidAPI for job data
- The Muse for career opportunities
- IBM watsonx for AI capabilities
- Sentence Transformers for semantic matching

## 📧 Support

For support, email support@jobtracker.com or open an issue in the repository.

---

Built with ❤️ by the Job Tracker Team
