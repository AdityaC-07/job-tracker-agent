import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';
import { Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { useSidebar } from '../context/SidebarContext';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  job_type: string;
  description: string;
  salary_min?: number;
  salary_max?: number;
  url: string;
  source: string;
  match_score?: number;
  posted_date?: string;
}

export function JobSearch() {
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('');
  const [minSalary, setMinSalary] = useState('');
  const [maxSalary, setMaxSalary] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'relevance' | 'salary' | 'date'>('relevance');
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [applyingJobId, setApplyingJobId] = useState<string | null>(null);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyNotes, setApplyNotes] = useState('');
  const queryClient = useQueryClient();
  const itemsPerPage = 10;
  const { isCollapsed } = useSidebar();

  const { data: result, isLoading, refetch } = useQuery({
    queryKey: ['jobs', { keywords, location, jobType, minSalary, maxSalary }],
    queryFn: () =>
      apiClient.searchJobs({
        keywords,
        location: location || undefined,
        job_type: jobType || undefined,
        min_salary: minSalary ? parseInt(minSalary) : undefined,
        max_salary: maxSalary ? parseInt(maxSalary) : undefined,
      }),
    enabled: false,
  });

  const jobs = result?.data?.jobs || [];

  const createApplicationMutation = useMutation({
    mutationFn: (data: { job_id: string; status?: string; notes?: string; tags?: string[] }) =>
      apiClient.createApplication(data),
    onSuccess: () => {
      toast.success('Application created!');
      setShowApplyModal(false);
      setApplyNotes('');
      setApplyingJobId(null);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
    onError: (error: any) => {
      console.error('Application creation error:', error);
      toast.error(error.message || 'Failed to create application');
    },
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!keywords.trim()) {
      toast.error('Please enter job keywords');
      return;
    }

    setCurrentPage(1);
    setHasSearched(true);
    await refetch();
  };

  const sortedJobs = useMemo(() => {
    let sorted = [...jobs];
    
    switch (sortBy) {
      case 'salary':
        sorted.sort((a, b) => (b.salary_max || 0) - (a.salary_max || 0));
        break;
      case 'date':
        sorted.sort((a, b) => new Date(b.posted_date || 0).getTime() - new Date(a.posted_date || 0).getTime());
        break;
      case 'relevance':
      default:
        sorted.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
    }
    
    return sorted;
  }, [jobs, sortBy]);

  const paginatedJobs = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return sortedJobs.slice(start, start + itemsPerPage);
  }, [sortedJobs, currentPage]);

  const totalPages = Math.ceil(sortedJobs.length / itemsPerPage);

  const toggleSaveJob = (jobId: string) => {
    const newSaved = new Set(savedJobs);
    if (newSaved.has(jobId)) {
      newSaved.delete(jobId);
      toast.success('Removed from saved');
    } else {
      newSaved.add(jobId);
      toast.success('Saved for later!');
    }
    setSavedJobs(newSaved);
  };

  const handleApplyClick = (jobId: string) => {
    setApplyingJobId(jobId);
    setShowApplyModal(true);
  };

  const handleApplySubmit = async () => {
    if (!applyingJobId) return;
    
    console.log('Submitting application for job:', applyingJobId);
    console.log('Notes:', applyNotes);
    
    createApplicationMutation.mutate({
      job_id: applyingJobId,
      status: 'applied',
      notes: applyNotes || undefined,
    });
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pt-16 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-64'}`}>
      {/* Search Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold mb-6 text-gray-900">Job Search</h1>

          <form onSubmit={handleSearch} className="space-y-4">
            {/* Primary Search Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="md:col-span-2">
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="🔍 Job title, company or key words..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm shadow-sm"
                />
              </div>

              <div>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="📍 Location"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm shadow-sm"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg hover:shadow-xl transition-all text-sm"
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Filters Row */}
            <div className="flex flex-wrap gap-3 items-center">
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="min-w-[180px] w-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white"
              >
                <option value="">All Job Types</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
                <option value="freelance">Freelance</option>
              </select>

              <input
                type="number"
                value={minSalary}
                onChange={(e) => setMinSalary(e.target.value)}
                placeholder="Min $"
                className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
              />

              <input
                type="number"
                value={maxSalary}
                onChange={(e) => setMaxSalary(e.target.value)}
                placeholder="Max $"
                className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
              />

              <button
                type="button"
                onClick={() => {
                  setKeywords('');
                  setLocation('');
                  setJobType('');
                  setMinSalary('');
                  setMaxSalary('');
                  setHasSearched(false);
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium text-sm"
              >
                Clear Filters
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {isLoading && (
          <div className="text-center py-20">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600"></div>
            </div>
            <p className="mt-4 text-gray-600 text-lg">Finding the best jobs for you...</p>
          </div>
        )}

        {hasSearched && !isLoading && jobs.length === 0 && (
          <div className="text-center py-20 bg-white rounded-2xl shadow-sm">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-gray-600 text-xl font-semibold">No jobs found</p>
            <p className="text-gray-500 mt-2">Try adjusting your search criteria</p>
          </div>
        )}

        {jobs.length > 0 && (
          <>
            {/* Results Header */}
            <div className="mb-6 flex justify-between items-center">
              <div>
                <p className="text-gray-900 font-semibold text-lg">
                  <span className="text-indigo-600">{sortedJobs.length}</span> Jobs Found
                </p>
                {sortedJobs.length > itemsPerPage && (
                  <p className="text-sm text-gray-500 mt-1">
                    Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, sortedJobs.length)}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-4">
                <select
                  value={sortBy}
                  onChange={(e) => {
                    setSortBy(e.target.value as any);
                    setCurrentPage(1);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
                >
                  <option value="relevance">⭐ Best Match</option>
                  <option value="salary">💰 Highest Salary</option>
                  <option value="date">📅 Most Recent</option>
                </select>
              </div>
            </div>

            {/* Jobs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
              {paginatedJobs.map((job, index) => (
                <div
                  key={job.id}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-indigo-200 relative group"
                >
                  {/* Top Badge */}
                  {job.match_score && job.match_score > 80 && (
                    <div className="absolute top-3 left-3 z-10">
                      <span className="px-3 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold rounded-full shadow-lg">
                        TOP PICK
                      </span>
                    </div>
                  )}

                  {/* Save Button */}
                  <button
                    onClick={() => toggleSaveJob(job.id)}
                    className={`absolute top-3 right-3 z-10 p-2 rounded-full transition-all ${
                      savedJobs.has(job.id)
                        ? 'bg-red-500 text-white shadow-lg scale-110'
                        : 'bg-white/80 text-gray-400 hover:text-red-500 hover:bg-white shadow-md'
                    }`}
                  >
                    <Heart size={18} fill={savedJobs.has(job._id) ? 'currentColor' : 'none'} />
                  </button>

                  {/* Company Avatar */}
                  <div className="bg-gradient-to-br from-indigo-500 to-purple-600 h-20 flex items-center justify-center">
                    <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center text-2xl font-bold text-indigo-600 shadow-lg">
                      {job.company.charAt(0).toUpperCase()}
                    </div>
                  </div>

                  <div className="p-5">
                    {/* Job Title */}
                    <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-1 group-hover:text-indigo-600 transition-colors">
                      {job.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-3">{job.company}</p>

                    {/* Badges */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium border border-blue-100">
                        📍 {job.location}
                      </span>
                      {job.job_type && (
                        <span className="px-3 py-1 bg-purple-50 text-purple-700 rounded-lg text-xs font-medium border border-purple-100">
                          {job.job_type}
                        </span>
                      )}
                    </div>

                    {/* Match Score */}
                    {job.match_score && (
                      <div className="mb-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-100">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-green-700 font-medium">Match Score</span>
                          <span className="text-lg font-bold text-green-600">{Math.round(job.match_score)}%</span>
                        </div>
                        <div className="mt-2 w-full bg-green-200 rounded-full h-1.5">
                          <div
                            className="bg-green-600 h-1.5 rounded-full transition-all"
                            style={{ width: `${job.match_score}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Salary */}
                    {(job.salary_min || job.salary_max) && (
                      <p className="text-gray-900 font-bold mb-3 flex items-center gap-2">
                        <span className="text-green-600">💰</span>
                        {formatSalary(job.salary_min, job.salary_max)}
                      </p>
                    )}

                    {/* Description */}
                    {job.description && (
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {job.description}
                      </p>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApplyClick(job.id)}
                        disabled={createApplicationMutation.isPending}
                        className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-semibold text-sm shadow-md hover:shadow-lg transition-all"
                      >
                        Apply Now
                      </button>
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2.5 border-2 border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold text-sm transition-all"
                      >
                        View
                      </a>
                    </div>

                    {/* Source Badge */}
                    <div className="mt-3 text-center">
                      <span className="text-xs text-gray-400">via {job.source}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft size={20} />
                </button>
                
                <div className="flex gap-2">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                          currentPage === pageNum
                            ? 'bg-indigo-600 text-white shadow-lg'
                            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight size={20} />
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Apply Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-in">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Apply for this Job</h2>
              <p className="text-sm text-gray-500 mt-1">Tell us why you're interested</p>
            </div>
            <div className="p-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Cover Note (Optional)
              </label>
              <textarea
                value={applyNotes}
                onChange={(e) => setApplyNotes(e.target.value)}
                placeholder="Why are you a great fit for this role?"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                rows={4}
              />
            </div>
            <div className="p-6 bg-gray-50 rounded-b-2xl flex gap-3">
              <button
                onClick={handleApplySubmit}
                disabled={createApplicationMutation.isPending}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 font-semibold shadow-lg"
              >
                {createApplicationMutation.isPending ? 'Applying...' : 'Submit Application'}
              </button>
              <button
                onClick={() => {
                  setShowApplyModal(false);
                  setApplyNotes('');
                  setApplyingJobId(null);
                }}
                className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-100 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatSalary(min?: number, max?: number) {
  if (!min && !max) return 'Not specified';
  if (min && max) return `$${min.toLocaleString('en-US')} - $${max.toLocaleString('en-US')}`;
  if (min) return `$${min.toLocaleString('en-US')}+`;
  return `Up to $${max?.toLocaleString('en-US')}`;
}
