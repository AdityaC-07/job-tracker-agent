import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient, Application, User } from '../services/api';
import { useResumeUpload, useApplications } from '../hooks';
import { Upload, FileText, Sparkles, Briefcase } from 'lucide-react';
import { useSidebar } from '../context/SidebarContext';
import toast from 'react-hot-toast';

export function ResumeManager() {
  const { isCollapsed } = useSidebar();
  const [selectedJobId, setSelectedJobId] = useState('');
  const [suggestions, setSuggestions] = useState<any | null>(null);

  const { data: userResponse, isLoading: userLoading } = useQuery({
    queryKey: ['user'],
    queryFn: () => apiClient.getMe(),
  });

  const user: User | undefined = userResponse?.data;

  const { applications } = useApplications();

  const { uploadResume, isUploading } = useResumeUpload();

  const analyzeMutation = useMutation({
    mutationFn: (jobId: string) => apiClient.getResumeSuggestions(jobId),
    onSuccess: (response) => {
      const nextSuggestions = response.data?.suggestions || null;
      setSuggestions(nextSuggestions);
      if (!nextSuggestions) {
        toast.error('No suggestions returned');
        return;
      }
      toast.success('Resume analysis complete');
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail;
      toast.error(detail || error.message || 'Failed to analyze resume');
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadResume(file);
    }
  };

  const handleAnalyze = () => {
    if (!selectedJobId) {
      toast.error('Select a job to analyze');
      return;
    }
    analyzeMutation.mutate(selectedJobId);
  };

  const skillsCount = user?.skills?.length || 0;
  const experienceYears = user?.experience_years || 0;
  const education = user?.education?.degree || 'Not specified';

  return (
    <div className={`min-h-screen bg-gray-50 pt-16 p-8 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-64'}`}>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Resume Manager</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Upload Resume</h2>
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-indigo-200 rounded-xl p-6 cursor-pointer hover:bg-indigo-50 transition-colors">
                <Upload className="text-indigo-600 mb-2" />
                <span className="text-gray-700">Click to upload or drag and drop</span>
                <span className="text-xs text-gray-500">PDF, DOC, DOCX (max 5MB)</span>
                <input type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
              </label>
              {isUploading && <p className="text-sm text-indigo-600 mt-3">Uploading and parsing...</p>}
            </div>

            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Resume Text</h2>
              {!userLoading && !user?.resume_text && (
                <div className="mb-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
                  No readable text was extracted. Upload a text-based PDF or a DOCX file.
                </div>
              )}
              <textarea
                className="w-full min-h-[220px] border border-gray-200 rounded-lg p-3 text-sm text-gray-700"
                value={user?.resume_text || ''}
                readOnly
                placeholder={userLoading ? 'Loading resume text...' : 'Upload a resume to see parsed text here'}
              />
            </div>

            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="text-indigo-600" />
                <h2 className="text-lg font-semibold">Job-Aligned Suggestions</h2>
              </div>
              <div className="flex flex-col sm:flex-row gap-3 mb-4">
                <select
                  className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(e.target.value)}
                >
                  <option value="">Select an application</option>
                  {applications.map((app) => (
                    <option key={app.id} value={app.id}>
                      {app.job?.title || 'Untitled role'} @ {app.job?.company || 'Company'}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleAnalyze}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700"
                  disabled={analyzeMutation.isPending || !selectedJobId}
                >
                  {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze for Job'}
                </button>
              </div>

              {!suggestions && !analyzeMutation.isPending && (
                <div className="text-sm text-gray-500">
                  Select an application and click Analyze to see job-aligned suggestions.
                </div>
              )}

              {suggestions && (
                <div className="space-y-4">
                  {suggestions.summary && (
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-sm text-indigo-900">
                      {suggestions.summary}
                    </div>
                  )}

                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Missing Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {(suggestions.missing_skills || []).map((skill: string) => (
                        <span key={skill} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-lg">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Keywords to Add</h3>
                    <div className="flex flex-wrap gap-2">
                      {(suggestions.keywords_to_add || []).map((keyword: string) => (
                        <span key={keyword} className="px-2 py-1 bg-amber-50 text-amber-700 text-xs rounded-lg">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">AI Suggestions</h3>
                    <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                      {(suggestions.suggestions || []).map((item: string, idx: number) => (
                        <li key={`${item}-${idx}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Analysis Results</h2>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-indigo-50">
                  <p className="text-xs text-gray-500">Skills Found</p>
                  <p className="text-xl font-bold text-indigo-700">{skillsCount}</p>
                </div>
                <div className="p-3 rounded-lg bg-purple-50">
                  <p className="text-xs text-gray-500">Experience</p>
                  <p className="text-xl font-bold text-purple-700">{experienceYears} years</p>
                </div>
                <div className="p-3 rounded-lg bg-green-50">
                  <p className="text-xs text-gray-500">Education</p>
                  <p className="text-sm font-semibold text-green-700">{education}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="text-indigo-600" />
                <h2 className="text-lg font-semibold">Resume Tips</h2>
              </div>
              <ul className="text-sm text-gray-700 space-y-2">
                <li>Keep it to 1-2 pages and highlight impact.</li>
                <li>Match keywords from the target job description.</li>
                <li>Quantify achievements with metrics.</li>
                <li>Showcase relevant projects and tech stack.</li>
                <li>Use consistent, professional formatting.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
