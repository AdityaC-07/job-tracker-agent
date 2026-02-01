import { useState } from 'react';
import { useApplications } from '../hooks';
import { Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useSidebar } from '../context/SidebarContext';

export function SavedJobs() {
  const { applications, isLoading, deleteApplication } = useApplications('saved');
  const [sortBy, setSortBy] = useState<'date' | 'salary'>('date');
  const { isCollapsed } = useSidebar();

  const sortedApplications = [...applications].sort((a, b) => {
    if (sortBy === 'salary') {
      return (b.job?.salary_max || 0) - (a.job?.salary_max || 0);
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Not specified';
    if (min && max) return `$${min.toLocaleString('en-US')} - $${max.toLocaleString('en-US')}`;
    if (min) return `$${min.toLocaleString('en-US')}+`;
    return `Up to $${max?.toLocaleString('en-US')}`;
  };

  return (
    <div className={`min-h-screen bg-gray-50 pt-16 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-64'}`}>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Saved Jobs</h1>

        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-gray-600">Loading saved jobs...</p>
          </div>
        )}

        {!isLoading && applications.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-600 text-lg">No saved jobs yet</p>
            <p className="text-gray-500 mt-2">
              Search for jobs and click the heart icon to save them for later
            </p>
          </div>
        )}

        {!isLoading && applications.length > 0 && (
          <>
            <div className="mb-6 flex justify-between items-center">
              <p className="text-gray-600">
                <span className="font-bold text-primary-600">{sortedApplications.length}</span> saved jobs
              </p>
              <div>
                <label className="text-sm font-medium text-gray-700 mr-2">Sort by:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="date">Most Recent</option>
                  <option value="salary">Highest Salary</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              {sortedApplications.map((app) => (
                <div
                  key={app.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{app.job?.title}</h3>
                      <p className="text-gray-600">{app.job?.company}</p>
                    </div>
                    {app.match_score && (
                      <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full">
                        <span className="text-primary-700 font-bold">{Math.round(app.match_score)}%</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                      {app.job?.location}
                    </span>
                    {app.job?.job_type && (
                      <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                        {app.job?.job_type}
                      </span>
                    )}
                    <span className="inline-block px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                      {app.job?.source}
                    </span>
                  </div>

                  {(app.job?.salary_min || app.job?.salary_max) && (
                    <p className="text-gray-700 font-semibold mb-2 text-lg">
                      💰 {formatSalary(app.job?.salary_min, app.job?.salary_max)}
                    </p>
                  )}

                  {app.job?.description && (
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {app.job?.description}
                    </p>
                  )}

                  {app.notes && (
                    <p className="text-gray-700 text-sm mb-3 p-3 bg-gray-50 rounded italic">
                      {app.notes}
                    </p>
                  )}

                  <div className="flex gap-2">
                    <a
                      href={app.job?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium text-center"
                    >
                      View Job →
                    </a>
                    <button
                      onClick={() => {
                        deleteApplication(app.id);
                        toast.success('Removed from saved');
                      }}
                      className="px-4 py-2 border border-primary-300 text-primary-600 rounded-lg hover:bg-primary-50 font-medium flex items-center gap-2"
                    >
                      <Trash2 size={18} />
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default SavedJobs;
