import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import toast from 'react-hot-toast';

interface Job {
  _id: string;
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

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!keywords.trim()) {
      toast.error('Please enter job keywords');
      return;
    }

    setHasSearched(true);
    await refetch();
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified';
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `$${min.toLocaleString()}+`;
    return `Up to $${max?.toLocaleString()}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Search Section */}
      <div className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-6">Job Search</h1>

          <form onSubmit={handleSearch} className="space-y-4">
            {/* Keywords and Location */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Keywords *
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., Software Engineer, Data Scientist"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., San Francisco, Remote"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Type
                </label>
                <select
                  value={jobType}
                  onChange={(e) => setJobType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="">All Types</option>
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="temporary">Temporary</option>
                  <option value="freelance">Freelance</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Salary
                </label>
                <input
                  type="number"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value)}
                  placeholder="$50000"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Salary
                </label>
                <input
                  type="number"
                  value={maxSalary}
                  onChange={(e) => setMaxSalary(e.target.value)}
                  placeholder="$150000"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>
            </div>

            {/* Search Button */}
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isLoading ? 'Searching...' : 'Search Jobs'}
              </button>

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
                className="px-6 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 font-medium"
              >
                Clear
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
            <p className="mt-4 text-gray-600">Searching for jobs...</p>
          </div>
        )}

        {hasSearched && !isLoading && jobs.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-600 text-lg">No jobs found matching your criteria</p>
            <p className="text-gray-500 mt-2">Try adjusting your search filters</p>
          </div>
        )}

        {jobs.length > 0 && (
          <>
            <div className="mb-4">
              <p className="text-gray-600">
                Found <span className="font-bold text-indigo-600">{jobs.length}</span> jobs
              </p>
            </div>

            <div className="space-y-4">
              {jobs.map((job) => (
                <div
                  key={job._id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                      <p className="text-gray-600">{job.company}</p>
                    </div>
                    {job.match_score && (
                      <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full">
                        <span className="text-green-700 font-bold">{Math.round(job.match_score)}%</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {job.location}
                    </span>
                    {job.job_type && (
                      <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                        {job.job_type}
                      </span>
                    )}
                    <span className="inline-block px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                      {job.source}
                    </span>
                  </div>

                  {(job.salary_min || job.salary_max) && (
                    <p className="text-gray-700 font-semibold mb-2">
                      {formatSalary(job.salary_min, job.salary_max)}
                    </p>
                  )}

                  {job.description && (
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {job.description}
                    </p>
                  )}

                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                  >
                    View Job →
                  </a>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default JobSearch;
