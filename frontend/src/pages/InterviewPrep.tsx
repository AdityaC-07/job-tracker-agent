import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient, Application } from '../services/api';
import { useApplications } from '../hooks';
import { useSidebar } from '../context/SidebarContext';
import { Sparkles, Zap, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';

export function InterviewPrep() {
  const { isCollapsed } = useSidebar();
  const { applications } = useApplications();

  const [selectedApplicationId, setSelectedApplicationId] = useState('');
  const [prep, setPrep] = useState<any | null>(null);

  const prepMutation = useMutation({
    mutationFn: (applicationId: string) => apiClient.getInterviewPrep(applicationId),
    onSuccess: (response) => {
      setPrep(response.data?.prep || null);
      toast.success('Interview prep ready');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate interview prep');
    },
  });

  const handleGenerate = () => {
    if (!selectedApplicationId) {
      toast.error('Select an application');
      return;
    }
    prepMutation.mutate(selectedApplicationId);
  };

  return (
    <div className={`min-h-screen bg-gray-50 pt-16 p-8 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-64'}`}>
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">Interview Prep</h1>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm"
              value={selectedApplicationId}
              onChange={(e) => setSelectedApplicationId(e.target.value)}
            >
              <option value="">Select an application</option>
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.job?.title || 'Untitled role'} @ {app.job?.company || 'Company'}
                </option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50"
              disabled={prepMutation.isPending}
            >
              {prepMutation.isPending ? 'Generating...' : 'Generate Prep'}
            </button>
          </div>
        </div>

        {prep && (
          <div className="space-y-6">
            {/* Job Info Header */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{prep.role}</h2>
                  <p className="text-gray-600 mt-1">at {prep.company}</p>
                </div>
                <Zap className="text-amber-500" size={32} />
              </div>
            </div>

            {/* Agents Used - Multi-Agent Breakdown */}
            {prep.agents_used && prep.agents_used.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Zap size={20} className="text-blue-600" />
                  AI Agents Working For You
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
                  {prep.agents_used.map((agent: any, idx: number) => (
                    <div key={idx} className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                      <CheckCircle2 size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 break-words">{agent.name}</p>
                        <p className="text-xs text-gray-600 mt-1 capitalize">{agent.status}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Key Requirements */}
            {prep.key_requirements && prep.key_requirements.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-lg font-semibold mb-3">Key Requirements Identified</h3>
                <div className="flex flex-wrap gap-2">
                  {prep.key_requirements.map((req: string, idx: number) => (
                    <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      {req}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Technical Questions */}
            {prep.technical_questions && prep.technical_questions.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold mb-3 text-blue-900">Technical Questions (Role-Specific)</h2>
                <ul className="space-y-2">
                  {prep.technical_questions.map((q: string, idx: number) => (
                    <li key={`tech-${idx}`} className="flex gap-3 text-sm text-gray-700">
                      <span className="text-blue-600 font-semibold flex-shrink-0">T{idx + 1}.</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Behavioral Questions */}
            {prep.behavioral_questions && prep.behavioral_questions.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold mb-3 text-purple-900">Behavioral Questions (Company-Specific)</h2>
                <ul className="space-y-2">
                  {prep.behavioral_questions.map((q: string, idx: number) => (
                    <li key={`behav-${idx}`} className="flex gap-3 text-sm text-gray-700">
                      <span className="text-purple-600 font-semibold flex-shrink-0">B{idx + 1}.</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Tips */}
            {prep.tips && prep.tips.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold mb-3 text-green-900">Interview Tips & Strategies</h2>
                <ul className="space-y-2">
                  {prep.tips.map((tip: string, idx: number) => (
                    <li key={`tip-${idx}`} className="flex gap-3 text-sm text-gray-700">
                      <span className="text-green-600 font-semibold flex-shrink-0">✓</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Preparation Checklist */}
            {prep.preparation_checklist && prep.preparation_checklist.length > 0 && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold mb-3">Preparation Checklist</h2>
                <ul className="space-y-2">
                  {prep.preparation_checklist.map((item: string, idx: number) => (
                    <li key={`checklist-${idx}`} className="flex gap-3 text-sm text-gray-700">
                      <span className="text-amber-600 font-semibold flex-shrink-0">□</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
