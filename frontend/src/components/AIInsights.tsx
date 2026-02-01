import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { TrendingUp, Sparkles, Target, Lightbulb } from 'lucide-react';

export function AIInsights() {
  const { data, isLoading } = useQuery({
    queryKey: ['ai-insights'],
    queryFn: () => apiClient.getAIInsights(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const insights = data?.data?.insights;

  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-xl p-6 animate-pulse">
        <div className="h-6 bg-white/20 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-white/20 rounded w-2/3 mb-2"></div>
        <div className="h-4 bg-white/20 rounded w-1/2"></div>
      </div>
    );
  }

  if (!insights) return null;

  return (
    <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-xl p-6 text-white">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-white/20 p-3 rounded-xl backdrop-blur-sm">
          <Sparkles className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">AI Insights</h2>
          <p className="text-white/80 text-sm">Powered by IBM watsonx</p>
        </div>
      </div>

      {/* Success Rates */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-5 h-5" />
            <span className="text-sm font-medium">Success Rate</span>
          </div>
          <div className="text-3xl font-bold">{insights.success_rate}%</div>
        </div>
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5" />
            <span className="text-sm font-medium">Interview Rate</span>
          </div>
          <div className="text-3xl font-bold">{insights.interview_rate}%</div>
        </div>
      </div>

      {/* AI Summary */}
      {insights.summary && (
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-4">
          <p className="text-sm leading-relaxed">{insights.summary}</p>
        </div>
      )}

      {/* Recommendations */}
      {insights.recommendations && insights.recommendations.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 font-semibold">
            <Lightbulb className="w-5 h-5" />
            <span>AI Recommendations</span>
          </div>
          <ul className="space-y-2">
            {insights.recommendations.slice(0, 3).map((rec: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <span className="text-yellow-300 font-bold">{i + 1}.</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Skills Needed */}
      {insights.top_skills_needed && insights.top_skills_needed.length > 0 && (
        <div className="mt-4">
          <div className="text-sm font-semibold mb-2">Top Skills in Demand</div>
          <div className="flex flex-wrap gap-2">
            {insights.top_skills_needed.slice(0, 6).map((skill: string, i: number) => (
              <span
                key={i}
                className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-lg text-xs font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AIInsights;
