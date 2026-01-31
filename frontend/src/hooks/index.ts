/**
 * Custom React Hooks
 * Reusable hooks for data fetching and state management
 */
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { useState, useEffect, useCallback } from 'react';
import { apiClient, Application, Job, DashboardStats } from '../services/api';
import toast from 'react-hot-toast';

// Auth hooks
export function useAuth() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async (email: string, password: string) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await apiClient.login(formData as any);
      const { access_token, user: userData } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      toast.success('Logged in successfully!');
      return userData;
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await apiClient.register({ name, email, password });
      const { access_token, user: userData } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      toast.success('Registration successful!');
      return userData;
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out successfully');
  };

  return { user, login, register, logout, isAuthenticated: !!user };
}

// Applications hooks
export function useApplications(statusFilter?: string) {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['applications', statusFilter],
    queryFn: async () => {
      const response = await apiClient.getApplications({ status_filter: statusFilter });
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: apiClient.createApplication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Application created!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create application');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Application> }) =>
      apiClient.updateApplication(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Application updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update application');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: apiClient.deleteApplication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Application deleted!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete application');
    },
  });

  return {
    applications: data?.applications || [],
    total: data?.total || 0,
    isLoading,
    error,
    createApplication: createMutation.mutate,
    updateApplication: updateMutation.mutate,
    deleteApplication: deleteMutation.mutate,
  };
}

// Jobs hooks
export function useJobs(filters?: any) {
  return useQuery({
    queryKey: ['jobs', filters],
    queryFn: async () => {
      const response = await apiClient.getJobs(filters);
      return response.data;
    },
  });
}

export function useJobMatches(minScore?: number) {
  return useQuery({
    queryKey: ['job-matches', minScore],
    queryFn: async () => {
      const response = await apiClient.getMatchingJobs({ min_score: minScore });
      return response.data;
    },
  });
}

export function useJobSearch() {
  const [isSearching, setIsSearching] = useState(false);

  const search = async (keywords: string, location?: string) => {
    setIsSearching(true);
    try {
      const response = await apiClient.searchJobs({ keywords, location });
      return response.data;
    } catch (error: any) {
      toast.error(error.message || 'Search failed');
      throw error;
    } finally {
      setIsSearching(false);
    }
  };

  return { search, isSearching };
}

// Analytics hooks
export function useAnalytics() {
  return useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const response = await apiClient.getDashboardAnalytics();
      return response.data;
    },
  });
}

export function useTimeline(days?: number) {
  return useQuery({
    queryKey: ['timeline', days],
    queryFn: async () => {
      const response = await apiClient.getTimeline(days);
      return response.data;
    },
  });
}

export function useSkillGap() {
  return useQuery({
    queryKey: ['skill-gap'],
    queryFn: async () => {
      const response = await apiClient.getSkillGap();
      return response.data;
    },
  });
}

// Debounce hook
export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Resume upload hook
export function useResumeUpload() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: apiClient.uploadResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast.success('Resume uploaded and parsed successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to upload resume');
    },
  });

  return {
    uploadResume: mutation.mutate,
    isUploading: mutation.isPending,
    uploadProgress: mutation.isPending ? 50 : 0,
  };
}

// Cover letter generation hook
export function useCoverLetterGeneration() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: apiClient.generateCoverLetter,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Cover letter generated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate cover letter');
    },
  });

  return {
    generateCoverLetter: mutation.mutate,
    isGenerating: mutation.isPending,
  };
}

export default {
  useAuth,
  useApplications,
  useJobs,
  useJobMatches,
  useJobSearch,
  useAnalytics,
  useTimeline,
  useSkillGap,
  useDebounce,
  useResumeUpload,
  useCoverLetterGeneration,
};
