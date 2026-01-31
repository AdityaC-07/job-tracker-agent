import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, PrivateRoute } from './context/AuthContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { JobSearch } from './pages/JobSearch';

// Placeholder components - will be created
const Dashboard = () => <div className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">Dashboard</h1><div className="grid grid-cols-4 gap-4 mb-8"><div className="bg-white p-6 rounded-lg shadow"><h3 className="text-gray-500 text-sm">Total Applications</h3><p className="text-3xl font-bold">0</p></div><div className="bg-white p-6 rounded-lg shadow"><h3 className="text-gray-500 text-sm">Applied</h3><p className="text-3xl font-bold">0</p></div><div className="bg-white p-6 rounded-lg shadow"><h3 className="text-gray-500 text-sm">Interviews</h3><p className="text-3xl font-bold">0</p></div><div className="bg-white p-6 rounded-lg shadow"><h3 className="text-gray-500 text-sm">Offers</h3><p className="text-3xl font-bold">0</p></div></div></div>;
const ApplicationTracker = () => <div className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">Application Tracker</h1><div className="bg-white p-6 rounded-lg shadow"><p className="text-gray-600">Track your job applications</p></div></div>;
const Analytics = () => <div className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">Analytics</h1><div className="bg-white p-6 rounded-lg shadow"><p className="text-gray-600">View your application analytics</p></div></div>;

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/jobs"
                element={
                  <PrivateRoute>
                    <JobSearch />
                  </PrivateRoute>
                }
              />
              <Route
                path="/applications"
                element={
                  <PrivateRoute>
                    <ApplicationTracker />
                  </PrivateRoute>
                }
              />
              <Route
                path="/analytics"
                element={
                  <PrivateRoute>
                    <Analytics />
                  </PrivateRoute>
                }
              />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
          </div>
          <Toaster position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
