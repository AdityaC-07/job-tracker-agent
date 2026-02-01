import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, Application } from '../services/api';
import { useSidebar } from '../context/SidebarContext';
import toast from 'react-hot-toast';
import { Briefcase, MapPin, Building, Calendar, Trash2, ExternalLink, Sparkles, FileText, Mail, Target, PenTool } from 'lucide-react';
import { AIFeatureModal } from '../components/AIFeatureModal';

export function Applications() {
  const { isCollapsed } = useSidebar();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [modalState, setModalState] = useState<{
    isOpen: boolean;
    title: string;
    content: string | React.ReactNode;
    isLoading: boolean;
  }>({
    isOpen: false,
    title: '',
    content: '',
    isLoading: false,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['applications', statusFilter],
    queryFn: () =>
      apiClient.getApplications({
        status_filter: statusFilter || undefined,
        page: 1,
        limit: 100,
      }),
  });

  const applications = data?.data?.applications || [];

  const deleteApplicationMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteApplication(id),
    onSuccess: () => {
      toast.success('Application deleted');
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
    onError: () => {
      toast.error('Failed to delete application');
    },
  });

  const generateCoverLetterMutation = useMutation({
    mutationFn: (id: string) => apiClient.generateCoverLetter(id),
    onSuccess: (response) => {
      const content = response.data?.cover_letter || 'Cover letter generated successfully';
      setModalState({
        isOpen: true,
        title: '📄 AI-Generated Cover Letter',
        content: content,
        isLoading: false,
      });
    },
    onError: () => {
      toast.error('Failed to generate cover letter');
      setModalState(prev => ({ ...prev, isLoading: false }));
    },
  });

  const interviewPrepMutation = useMutation({
    mutationFn: (id: string) => apiClient.getInterviewPrep(id),
    onSuccess: (response) => {
      const prep = response.data?.prep;
      const content = (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">📝 Common Interview Questions</h3>
            <ul className="space-y-2">
              {prep?.common_questions?.map((q: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-blue-600 font-bold">{i + 1}.</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">💡 Interview Tips</h3>
            <ul className="space-y-2">
              {prep?.tips?.map((tip: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-green-600">✓</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">✅ Preparation Checklist</h3>
            <ul className="space-y-2">
              {prep?.preparation_checklist?.map((item: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-purple-600">□</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      );
      setModalState({
        isOpen: true,
        title: '🎯 Interview Preparation Guide',
        content: content,
        isLoading: false,
      });
    },
    onError: () => {
      toast.error('Failed to generate interview prep');
      setModalState(prev => ({ ...prev, isLoading: false }));
    },
  });

  const jobAnalysisMutation = useMutation({
    mutationFn: (id: string) => apiClient.analyzeJob(id),
    onSuccess: (response) => {
      const analysis = response.data?.analysis;
      const content = (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">📊 Match Score</h3>
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-lg text-center">
              <div className="text-4xl font-bold">{analysis?.match_percentage || 0}%</div>
              <div className="text-sm opacity-90">Skills Match</div>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">✅ Matching Skills</h3>
            <div className="flex flex-wrap gap-2">
              {analysis?.matching_skills?.map((skill: string, i: number) => (
                <span key={i} className="px-3 py-1 bg-green-100 text-green-800 rounded-lg text-sm font-medium">
                  {skill}
                </span>
              ))}
            </div>
          </div>
          {analysis?.missing_skills?.length > 0 && (
            <div>
              <h3 className="text-lg font-bold mb-3 text-gray-900">📚 Skills to Learn</h3>
              <div className="flex flex-wrap gap-2">
                {analysis?.missing_skills?.map((skill: string, i: number) => (
                  <span key={i} className="px-3 py-1 bg-orange-100 text-orange-800 rounded-lg text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {analysis?.analysis && (
            <div>
              <h3 className="text-lg font-bold mb-3 text-gray-900">🤖 AI Analysis</h3>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{analysis.analysis}</p>
            </div>
          )}
        </div>
      );
      setModalState({
        isOpen: true,
        title: '🎯 Job Requirements Analysis',
        content: content,
        isLoading: false,
      });
    },
    onError: () => {
      toast.error('Failed to analyze job');
      setModalState(prev => ({ ...prev, isLoading: false }));
    },
  });

  const optimizeResumeMutation = useMutation({
    mutationFn: (id: string) => apiClient.optimizeResume(id),
    onSuccess: (response) => {
      const data = response.data?.suggestions;
      const content = (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-3 text-gray-900">✨ Optimization Suggestions</h3>
            <ul className="space-y-2">
              {data?.suggestions?.map((item: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-blue-600 font-bold">{i + 1}.</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
          {data?.keywords_to_add?.length > 0 && (
            <div>
              <h3 className="text-lg font-bold mb-3 text-gray-900">🔑 Keywords to Add</h3>
              <div className="flex flex-wrap gap-2">
                {data.keywords_to_add.map((skill: string, i: number) => (
                  <span key={i} className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-lg text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      );
      setModalState({
        isOpen: true,
        title: '🧩 Resume Optimizer',
        content: content,
        isLoading: false,
      });
    },
    onError: () => {
      toast.error('Failed to optimize resume');
      setModalState(prev => ({ ...prev, isLoading: false }));
    },
  });

  const emailTemplateMutation = useMutation({
    mutationFn: ({ type, id }: { type: 'follow_up' | 'thank_you' | 'negotiation'; id: string }) =>
      apiClient.generateEmailTemplate(type, id),
    onSuccess: (response) => {
      const email = response.data?.email || 'Email generated successfully';
      setModalState({
        isOpen: true,
        title: '✉️ Email Template',
        content: email,
        isLoading: false,
      });
    },
    onError: () => {
      toast.error('Failed to generate email');
      setModalState(prev => ({ ...prev, isLoading: false }));
    },
  });

  const handleAIAction = (
    action: 'cover_letter' | 'interview_prep' | 'job_analysis' | 'email' | 'resume_optimize',
    applicationId: string,
    emailType?: 'follow_up' | 'thank_you' | 'negotiation'
  ) => {
    setModalState({
      isOpen: true,
      title: 'Generating...',
      content: '',
      isLoading: true,
    });

    switch (action) {
      case 'cover_letter':
        generateCoverLetterMutation.mutate(applicationId);
        break;
      case 'interview_prep':
        interviewPrepMutation.mutate(applicationId);
        break;
      case 'job_analysis':
        jobAnalysisMutation.mutate(applicationId);
        break;
      case 'resume_optimize':
        optimizeResumeMutation.mutate(applicationId);
        break;
      case 'email':
        if (emailType) {
          emailTemplateMutation.mutate({ type: emailType, id: applicationId });
        }
        break;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      saved: 'bg-gray-100 text-gray-700 border-gray-300',
      applied: 'bg-blue-100 text-blue-700 border-blue-300',
      interview_scheduled: 'bg-purple-100 text-purple-700 border-purple-300',
      offer_received: 'bg-green-100 text-green-700 border-green-300',
      rejected: 'bg-red-100 text-red-700 border-red-300',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div
      className={`min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pt-16 transition-all duration-300 ${
        isCollapsed ? 'pl-20' : 'pl-64'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Track Applications</h1>
          <p className="text-gray-600">Manage and track all your job applications</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-gray-100">
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setStatusFilter('')}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                statusFilter === ''
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All ({applications.length})
            </button>
            <button
              onClick={() => setStatusFilter('applied')}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                statusFilter === 'applied'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Applied
            </button>
            <button
              onClick={() => setStatusFilter('interview_scheduled')}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                statusFilter === 'interview_scheduled'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Interviews
            </button>
            <button
              onClick={() => setStatusFilter('offer_received')}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                statusFilter === 'offer_received'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Offers
            </button>
            <button
              onClick={() => setStatusFilter('rejected')}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                statusFilter === 'rejected'
                  ? 'bg-red-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Rejected
            </button>
          </div>
        </div>

        {/* Applications List */}
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : applications.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <Briefcase className="mx-auto mb-4 text-gray-400" size={64} />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Applications Yet</h3>
            <p className="text-gray-600 mb-6">
              Start applying to jobs from the Job Search page
            </p>
            <a
              href="/jobs"
              className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-semibold shadow-lg"
            >
              Search Jobs
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map((app: Application) => (
              <div
                key={app.id}
                className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all p-6 border border-gray-100"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Job Title & Company */}
                    <div className="flex items-start gap-4 mb-4">
                      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg">
                        {app.job?.company?.charAt(0).toUpperCase() || 'J'}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-1">
                          {app.job?.title || 'Job Title'}
                        </h3>
                        <div className="flex flex-wrap gap-3 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Building size={16} />
                            {app.job?.company || 'Company'}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin size={16} />
                            {app.job?.location || 'Location'}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar size={16} />
                            Applied {formatDate(app.applied_date)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Status & Match Score */}
                    <div className="flex flex-wrap gap-3 mb-4">
                      <span
                        className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getStatusColor(
                          app.status
                        )}`}
                      >
                        {app.status.replace('_', ' ').toUpperCase()}
                      </span>
                      {app.match_score && (
                        <span className="px-3 py-1 bg-green-50 text-green-700 rounded-lg text-sm font-semibold border border-green-200">
                          {Math.round(app.match_score)}% Match
                        </span>
                      )}
                    </div>

                    {/* Notes */}
                    {app.notes && (
                      <p className="text-sm text-gray-600 mb-4 bg-gray-50 p-3 rounded-lg border border-gray-200">
                        📝 {app.notes}
                      </p>
                    )}

                    {/* AI Action Buttons */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <button
                        onClick={() => handleAIAction('cover_letter', app.id)}
                        className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all"
                      >
                        <FileText size={14} />
                        Cover Letter
                      </button>
                      <button
                        onClick={() => handleAIAction('job_analysis', app.id)}
                        className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-green-500 to-teal-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all"
                      >
                        <Target size={14} />
                        Job Analysis
                      </button>
                      <button
                        onClick={() => handleAIAction('resume_optimize', app.id)}
                        className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all"
                      >
                        <PenTool size={14} />
                        Resume Optimizer
                      </button>
                      {(app.status === 'interview_scheduled' || app.status === 'applied') && (
                        <button
                          onClick={() => handleAIAction('interview_prep', app.id)}
                          className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all"
                        >
                          <Sparkles size={14} />
                          Interview Prep
                        </button>
                      )}
                      <div className="relative group">
                        <button
                          className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all"
                        >
                          <Mail size={14} />
                          Email Templates
                        </button>
                        <div className="absolute left-0 top-full mt-1 bg-white shadow-xl rounded-lg border border-gray-200 overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                          <button
                            onClick={() => handleAIAction('email', app.id, 'follow_up')}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          >
                            Follow Up
                          </button>
                          <button
                            onClick={() => handleAIAction('email', app.id, 'thank_you')}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          >
                            Thank You
                          </button>
                          <button
                            onClick={() => handleAIAction('email', app.id, 'negotiation')}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          >
                            Negotiation
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    {app.job?.url && (
                      <a
                        href={app.job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                        title="View Job"
                      >
                        <ExternalLink size={20} />
                      </a>
                    )}
                    <button
                      onClick={() => deleteApplicationMutation.mutate(app.id)}
                      disabled={deleteApplicationMutation.isPending}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all disabled:opacity-50"
                      title="Delete"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Feature Modal */}
      <AIFeatureModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState(prev => ({ ...prev, isOpen: false }))}
        title={modalState.title}
        content={modalState.content}
        isLoading={modalState.isLoading}
      />
    </div>
  );
}
