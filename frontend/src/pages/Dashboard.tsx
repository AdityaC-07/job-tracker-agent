import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { useSidebar } from '../context/SidebarContext';
import { TrendingUp, Briefcase, Calendar, CheckCircle, XCircle } from 'lucide-react';
import { AIInsights } from '../components/AIInsights';

export function Dashboard() {
  const { isCollapsed } = useSidebar();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => apiClient.getDashboardStats(),
  });

  const dashboardStats = stats?.data || {
    total_applications: 0,
    applied: 0,
    interviews: 0,
    offers: 0,
    rejected: 0,
    success_rate: 0,
    avg_response_time_days: 0,
    active_applications: 0,
  };

  const statCards = [
    {
      title: 'Total Applications',
      value: dashboardStats.total_applications,
      icon: Briefcase,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      title: 'Active',
      value: dashboardStats.active_applications,
      icon: TrendingUp,
      color: 'bg-green-500',
      change: '+8%',
    },
    {
      title: 'Interviews',
      value: dashboardStats.interviews,
      icon: Calendar,
      color: 'bg-purple-500',
      change: '+23%',
    },
    {
      title: 'Offers',
      value: dashboardStats.offers,
      icon: CheckCircle,
      color: 'bg-emerald-500',
      change: '+15%',
    },
  ];

  return (
    <div
      className={`min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 pt-16 transition-all duration-300 ${
        isCollapsed ? 'pl-20' : 'pl-64'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Track your job search progress</p>
        </div>

          {/* AI Insights */}
          <div className="lg:col-span-2">
            <AIInsights />
          </div>

        {/* Stats Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
                <div className="h-12 bg-gray-200 rounded mb-4"></div>
                <div className="h-8 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {statCards.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all p-6 border border-gray-100"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`${stat.color} p-3 rounded-xl`}>
                      <Icon className="text-white" size={24} />
                    </div>
                    <span className="text-sm text-green-600 font-semibold">{stat.change}</span>
                  </div>
                  <h3 className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</h3>
                  <p className="text-sm text-gray-600">{stat.title}</p>
                </div>
              );
            })}
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Success Rate */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Success Rate</h3>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all"
                    style={{ width: `${dashboardStats.success_rate}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-2xl font-bold text-gray-900">
                {dashboardStats.success_rate}%
              </span>
            </div>
          </div>

          {/* Response Time */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Avg Response Time</h3>
            <div className="flex items-center gap-3">
              <Calendar className="text-indigo-600" size={32} />
              <div>
                <p className="text-3xl font-bold text-gray-900">
                  {dashboardStats.avg_response_time_days || 0}
                </p>
                <p className="text-sm text-gray-600">days</p>
              </div>
            </div>
          </div>
        </div>

        {/* Status Breakdown */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Application Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-xl border border-blue-100">
              <p className="text-2xl font-bold text-blue-600">{dashboardStats.applied}</p>
              <p className="text-sm text-gray-600">Applied</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-xl border border-purple-100">
              <p className="text-2xl font-bold text-purple-600">{dashboardStats.interviews}</p>
              <p className="text-sm text-gray-600">Interviews</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-xl border border-green-100">
              <p className="text-2xl font-bold text-green-600">{dashboardStats.offers}</p>
              <p className="text-sm text-gray-600">Offers</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-xl border border-red-100">
              <p className="text-2xl font-bold text-red-600">{dashboardStats.rejected}</p>
              <p className="text-sm text-gray-600">Rejected</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-xl border border-gray-200">
              <p className="text-2xl font-bold text-gray-600">
                {dashboardStats.total_applications - dashboardStats.rejected}
              </p>
              <p className="text-sm text-gray-600">In Progress</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
