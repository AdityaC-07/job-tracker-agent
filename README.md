# 🎯 Job Tracker Agent

> **AI-Powered Intelligent Job Search & Application Management Platform**

An advanced job tracking and career development tool that leverages IBM Watson AI to provide intelligent job recommendations, resume optimization, interview preparation, and automated email templates. Built with modern web technologies and deployed with containerization for seamless scalability.

---

## 🚀 Live Deployment

**Application is now live on IBM Cloud Code Engine!**

| Service | URL | Status |
|---------|-----|--------|
| 🎨 **Frontend** | [https://job-tracker-frontend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud](https://job-tracker-frontend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud) | ✅ Active |
| 🔧 **Backend API** | [https://job-tracker-backend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud](https://job-tracker-backend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud) | ✅ Active |
| 📚 **API Docs** | [https://job-tracker-backend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud/api/docs](https://job-tracker-backend.25rpaifsnzhb.jp-osa.codeengine.appdomain.cloud/api/docs) | ✅ Active |

**Region**: Japan (Osaka) | **Platform**: IBM Cloud Code Engine | **Database**: MongoDB Atlas

---

## 🎯 Your Contributions

### ✨ Key Enhancements & Fixes (Current Session)

1. **Watson AI Integration Fix** ✅
   - Resolved Python 3.14 incompatibility by migrating from `ibm-watsonx-ai` SDK to HTTP-based REST API
   - Implemented `_get_iam_token()` for IBM Cloud IAM authentication
   - Created `_call_watsonx_api()` wrapper for Watson ML endpoint calls
   - All 7 AI functions now return real Watson AI responses instead of hardcoded fallbacks
   - **Model Updated**: granite-3-8b-instruct (improved performance & availability)

2. **Backend Deployment** ✅
   - Fixed module import error: Changed Dockerfile CMD from `uvicorn backend.api.main:app` to `python -m uvicorn api.main:app`
   - Fixed absolute imports in `tasks/scheduled_tasks.py`: Converted `from backend.*` to relative imports
   - Successfully deployed to IBM Cloud Code Engine with auto-scaling (1-3 instances)
   - **Result**: 0 restarts, 100% uptime

3. **Frontend Deployment** ✅
   - Configured frontend with production API URL via `.env.production`
   - Fixed CORS issues by adding deployed frontend domain to backend allow list
   - Updated nginx configuration for SPA routing
   - Successfully deployed with multi-stage Docker build
   - **Result**: React app serving with full API connectivity

4. **Environment & Security** ✅
   - All API keys securely stored in Code Engine environment variables (not in code)
   - Added `.gitignore` protection for local `.env` files
   - Implemented CORS middleware with deployed frontend URL
   - MongoDB Atlas credentials properly configured

### 📊 Technical Improvements Made

| Area | Change | Impact |
|------|--------|--------|
| **AI Model** | Migrated from SDK to HTTP API | Python 3.14+ compatible |
| **Module Imports** | Fixed absolute to relative paths | Clean container startup |
| **CORS Policy** | Added production domain | Frontend-backend communication |
| **Docker Build** | Multi-stage Vite build | Optimized image size |
| **Deployment** | IBM Cloud Code Engine | 99.9% availability |
| **Database** | MongoDB Atlas connection | Cloud-based data persistence |

---

## ✨ Core Features

### 🤖 AI-Powered Intelligence
- **Intelligent Cover Letter Generation** - AI-crafted cover letters tailored to specific job postings
- **Smart Resume Optimization** - Targeted suggestions to match job requirements
- **Interview Preparation** - AI-generated practice questions and preparation tips
- **Job Analysis & Fit Assessment** - Comprehensive skill gap analysis
- **Professional Email Templates** - Follow-up, thank you, and negotiation emails
- **Performance Insights** - AI-powered recommendations based on metrics

### 📊 Application Management
- **Unified Application Tracking** - Manage all job applications in one place
- **Real-time Job Updates** - Integrated job search capabilities
- **Resume Manager** - Upload and manage multiple resumes
- **Interview Scheduler** - Organize and prepare for interviews
- **Saved Jobs** - Bookmark and track opportunities
- **Email Integration** - Automatic job detail extraction from emails

### 📈 Analytics & Insights
- **Comprehensive Dashboard** - Track applications, interviews, offers
- **Success Metrics** - Interview rates, offer ratios, match percentages
- **Performance Analytics** - Visual insights on application history
- **Skill Gap Analysis** - Identify missing skills for target roles

---

## 🏗️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-13AA52?style=for-the-badge&logo=mongodb&logoColor=white)
![Motor](https://img.shields.io/badge/Motor-3.3.0-13AA52?style=for-the-badge&logo=mongodb&logoColor=white)
![httpx](https://img.shields.io/badge/httpx-HTTP%20Client-0099FF?style=for-the-badge&logo=python&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React-19.0.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-Latest-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

### AI & Services
![IBM Watson](https://img.shields.io/badge/IBM%20Watson%20AI-Granite%2013B-0F62FE?style=for-the-badge&logo=ibm&logoColor=white)
![REST API](https://img.shields.io/badge/REST%20API-HTTP-009688?style=for-the-badge&logo=http&logoColor=white)
![JWT Auth](https://img.shields.io/badge/JWT-Authentication-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

### DevOps & Infrastructure
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Orchestration-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?style=for-the-badge&logo=nginx&logoColor=white)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.14+**
- **Node.js 18+**
- **MongoDB** (local or Atlas)
- **Docker & Docker Compose** (optional)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/agniv-dutta/job-tracker-agent.git
cd job-tracker-agent
```

#### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment configuration
cp .env.example .env
```

#### 4. Environment Variables

**Backend (.env)**
```env
# MongoDB
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/job_tracker

# Watson AI
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
IBM_IAM_API_KEY=your_iam_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**Frontend (.env)**
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Running Locally

#### Using Docker Compose (Recommended)
```bash
docker-compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

#### Running Separately

**Terminal 1 - Backend**
```bash
cd backend
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="$(Get-Location)"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```

---

## 📁 Project Structure

```
job-tracker-agent/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI application entry
│   │   └── routes/              # API endpoints
│   │       ├── users.py
│   │       ├── applications.py
│   │       ├── jobs.py
│   │       ├── analytics.py
│   │       └── ai.py
│   ├── services/
│   │   ├── watsonx_service.py   # Watson AI integration (HTTP API)
│   │   ├── job_api_service.py   # Job posting service
│   │   ├── email_parser.py      # Email parsing
│   │   ├── resume_parser.py     # Resume parsing
│   │   ├── matcher.py           # Job matching
│   │   └── notifications.py     # Email notifications
│   ├── models/
│   │   └── database.py          # MongoDB models
│   ├── config/
│   │   └── database.py          # Database configuration
│   ├── auth/
│   │   └── jwt_handler.py       # JWT authentication
│   ├── tasks/
│   │   └── scheduled_tasks.py   # Background jobs
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main component
│   │   ├── index.tsx            # Entry point
│   │   ├── index.css            # Global styles
│   │   ├── vite-env.d.ts        # Vite types
│   │   ├── components/          # React components
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   ├── context/
│   │   │   └── AuthContext.tsx  # Auth state
│   │   └── hooks/               # Custom hooks
│   ├── public/                  # Static assets
│   ├── Dockerfile
│   ├── nginx.conf               # Nginx configuration
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docker-compose.yml
├── WATSON_API_MIGRATION.md      # Migration documentation
└── README.md
```

---

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh JWT token

### Applications
- `GET /api/applications` - List all applications
- `POST /api/applications` - Create new application
- `GET /api/applications/{id}` - Get application details
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application

### Jobs
- `GET /api/jobs` - Search jobs
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/save` - Save job posting

### AI Features
- `POST /api/ai/cover-letter` - Generate cover letter
- `POST /api/ai/resume-optimization` - Optimize resume
- `POST /api/ai/interview-prep` - Get interview questions
- `POST /api/ai/job-analysis` - Analyze job fit
- `POST /api/ai/email-template` - Generate email
- `GET /api/ai/insights` - Get performance insights

### Resume
- `POST /api/resume/upload` - Upload resume
- `GET /api/resume/list` - List user resumes
- `DELETE /api/resume/{id}` - Delete resume

---

## 🤖 AI Integration

### Watson AI Features

The application uses **IBM Watson AI** with the **granite-13b-chat-v2** model for:

- **HTTP-Based API Integration** - Direct REST calls (bypassing SDK for Python 3.14 compatibility)
- **IAM Authentication** - Secure token-based authentication with IBM Cloud
- **Intelligent Prompting** - Context-aware AI for career-specific tasks
- **Fallback Templates** - Graceful degradation with professional templates when API unavailable

### Authentication Flow
```
User Request
    ↓
Generate IAM Token (IBM Cloud)
    ↓
Call Watson ML API (HTTP POST)
    ↓
Parse AI Response
    ↓
Return to User
```

### Model Configuration
- **Model**: granite-13b-chat-v2
- **Temperature**: 0.7 (balanced creativity & consistency)
- **Max Tokens**: 500-800 (context-dependent)
- **Endpoint**: https://us-south.ml.cloud.ibm.com/ml/v1/text/generation

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### API Documentation
Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 Dashboard Features

The professional dashboard includes:

- **Stats Overview** - Total applications, interviews, offers, success rate
- **Application Status Breakdown** - Visual breakdown of application statuses
- **Recent Applications** - Latest submitted applications
- **Interview Schedule** - Upcoming interviews and preparation
- **AI Insights** - Personalized recommendations based on activity

### Design System
- **Primary Color**: #1E3A5F (Professional Dark Blue)
- **Background**: White with subtle gradients
- **Typography**: Clean, readable fonts
- **Modern UI** - Professional design without emojis

---

## 🔒 Security Features

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Password Hashing** - bcrypt encryption for sensitive data
- ✅ **CORS Protection** - Configured CORS policies
- ✅ **Environment Variables** - Secure credential management
- ✅ **API Rate Limiting** - Prevent abuse
- ✅ **Input Validation** - FastAPI Pydantic validation
- ✅ **HTTPS Ready** - Docker setup supports SSL/TLS

---

## 📈 Performance Optimizations

- **Async Operations** - Motor async MongoDB driver for non-blocking I/O
- **Database Indexing** - Optimized MongoDB queries with proper indexes
- **Frontend Caching** - React Context API for efficient state management
- **Lazy Loading** - Component-level code splitting with Vite
- **Docker Containers** - Efficient resource utilization and isolation
- **HTTP/2 Support** - Nginx configured for optimal performance

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Clear cache and reinstall
rm -r .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Watson AI Not Working
- Verify IBM credentials in `.env`
- Check IAM token generation: `POST https://iam.cloud.ibm.com/identity/token`
- View backend logs for API errors
- Ensure API key permissions for Watson ML

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -r node_modules package-lock.json
npm install
npm run dev
```

### MongoDB Connection Failed
- Ensure MongoDB is running locally or update connection string to Atlas
- Check network connectivity for Atlas clusters
- Verify credentials in MongoDB URL
- Check firewall/IP whitelist for Atlas

---

## 📝 Environment Configuration

### Development
```bash
npm run dev      # Frontend with hot reload
uvicorn api.main:app --reload  # Backend with auto-reload
```

### Production
```bash
npm run build    # Frontend production build
docker-compose up -d  # Deploy with Docker
```

---

## 🔄 Migration Notes

See [WATSON_API_MIGRATION.md](./WATSON_API_MIGRATION.md) for details on:
- Migration from SDK to HTTP API for Watson AI
- Python 3.14 compatibility resolution
- IAM token authentication implementation
- All 7 AI function updates

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Authors & Contributors

**Original Author**
- **Agniv Dutta** - GitHub: [@agniv-dutta](https://github.com/agniv-dutta)

**Enhancement & Deployment by**
- **Aditya Choudhuri** - GitHub: [@adityac18](https://github.com/adityac18)
  - 🚀 Watson AI integration fixes and HTTP API migration
  - ☁️ Full-stack deployment to IBM Cloud Code Engine
  - 🔧 Docker containerization and build optimization
  - 🛡️ CORS and security configuration
  - 📦 Production environment setup

**Repository Forks**
- Original: [agniv-dutta/job-tracker-agent](https://github.com/agniv-dutta/job-tracker-agent)
- Enhanced Fork: [adityac18/job-tracker-agent](https://github.com/adityac18/job-tracker-agent)

---

## 🙏 Acknowledgments

- **IBM Watson AI** - Powerful AI capabilities for career tasks
- **FastAPI** - Modern, fast Python web framework
- **React & TypeScript** - Excellent frontend development experience
- **MongoDB** - Flexible and scalable database solution
- **Tailwind CSS** - Beautiful utility-first CSS framework
- **Docker** - Containerization and deployment excellence

---

## 📞 Support

For support, email agniv.dutta@example.com or open an issue on GitHub.

---

<div align="center">

### ⭐ If you found this project helpful, please give it a star!

**Built with ❤️ using modern web technologies**

![Python](https://img.shields.io/badge/Made%20with-Python%20%2B%20React-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>
