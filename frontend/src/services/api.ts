/**
 * API Client Service
 * Axios-based HTTP client for backend API communication
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import toast from 'react-hot-toast';

// TypeScript interfaces
export interface User {
  id: string;
  email: string;
  name: string;
  skills: string[];
  experience_years: number;
  education?: Education;
  target_roles?: string[];
  target_locations?: string[];
  preferences?: UserPreferences;
  created_at: string;
  updated_at: string;
}

export interface Education {
  degree?: string;
  field?: string;
  institution?: string;
  graduation_year?: number;
}

export interface UserPreferences {
  job_types: string[];
  salary_min?: number;
  salary_max?: number;
  remote_preference: string;
  notification_frequency: string;
}

export interface Job {
  id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  job_type?: string;
  description: string;
  requirements?: string;
  skills_required: string[];
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  salary_max?: number;
  url?: string;
  posted_date?: string;
  match_score?: number;
}

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  job?: Job;
  status: 'saved' | 'applied' | 'interview_scheduled' | 'offer_received' | 'rejected';
  applied_date?: string;
  match_score?: number;
  cover_letter?: string;
  interview_rounds?: InterviewRound[];
  notes?: string;
  tags: string[];
  next_follow_up?: string;
  follow_up_count: number;
  created_at: string;
  updated_at: string;
}

export interface InterviewRound {
  round_number: number;
  round_type: string;
  scheduled_date?: string;
  completed: boolean;
  notes?: string;
  interviewer?: string;
}

export interface DashboardStats {
  total_applications: number;
  applied: number;
  interviews: number;
  offers: number;
  rejected: number;
  success_rate: number;
  avg_response_time_days?: number;
  active_applications: number;
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail: string }>) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    }
    
    // Handle 500 Server Error
    if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    }
    
    // Handle other errors
    const errorMessage = error.response?.data?.detail || 'An error occurred';
    
    return Promise.reject(new Error(errorMessage));
  }
);

// API methods
export const apiClient = {
  // Auth
  register: (data: { email: string; name: string; password: string }) =>
    api.post('/api/users/register', data),
  
  login: (data: { username: string; password: string }) =>
    api.post('/api/users/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  
  // User
  getMe: () => api.get<User>('/api/users/me'),
  
  updateProfile: (data: Partial<User>) => api.put('/api/users/me', data),
  
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/users/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getUserStats: () => api.get('/api/users/stats'),
  
  // Jobs
  searchJobs: (params: {
    keywords: string;
    location?: string;
    job_type?: string;
    min_salary?: number;
    max_salary?: number;
  }) => api.post('/api/jobs/search', params),
  
  getJobs: (params?: {
    page?: number;
    limit?: number;
    source?: string;
    job_type?: string;
    location?: string;
    company?: string;
  }) => api.get('/api/jobs', { params }),
  
  getJobById: (id: string) => api.get<Job>(`/api/jobs/${id}`),
  
  createManualJob: (data: Partial<Job>) => api.post('/api/jobs/manual', data),
  
  getMatchingJobs: (params?: { min_score?: number; limit?: number }) =>
    api.get('/api/jobs/matches/me', { params }),
  
  // Applications
  createApplication: (data: {
    job_id: string;
    status?: string;
    notes?: string;
    tags?: string[];
  }) => api.post('/api/applications', data),
  
  getApplications: (params?: {
    status_filter?: string;
    page?: number;
    limit?: number;
  }) => api.get<{ applications: Application[]; total: number }>('/api/applications', { params }),
  
  getApplicationById: (id: string) => api.get<Application>(`/api/applications/${id}`),
  
  updateApplication: (id: string, data: Partial<Application>) =>
    api.put(`/api/applications/${id}`, data),
  
  deleteApplication: (id: string) => api.delete(`/api/applications/${id}`),
  
  generateCoverLetter: (id: string) =>
    api.post(`/api/applications/${id}/cover-letter`),
  
  scheduleFollowUp: (id: string, days: number) =>
    api.post(`/api/applications/${id}/follow-up`, { days_from_now: days }),
  
  getApplicationsAnalytics: () => api.get('/api/applications/analytics/overview'),
  
  // Analytics
  getDashboardAnalytics: () => api.get<DashboardStats>('/api/analytics/dashboard'),
  
  getTimeline: (days?: number) => api.get('/api/analytics/timeline', { params: { days } }),
  
  getSkillGap: () => api.get('/api/analytics/skill-gap'),
  
  getCompanyInsights: (companyName: string) =>
    api.get(`/api/analytics/company-insights/${encodeURIComponent(companyName)}`),
  
  getSuccessByCompany: () => api.get('/api/analytics/success-by-company'),
};

export default api;
