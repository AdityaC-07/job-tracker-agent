import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, PrivateRoute } from './context/AuthContext';
import { SidebarProvider, useSidebar } from './context/SidebarContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { JobSearch } from './pages/JobSearch';
import { SavedJobs } from './pages/SavedJobs';
import { Dashboard } from './pages/Dashboard';
import { Applications } from './pages/Applications';
import { ResumeManager } from './pages/ResumeManager';
import { InterviewPrep } from './pages/InterviewPrep';
import { Navbar } from './components/Navbar';

// Placeholder component
const Analytics = () => {
  const { isCollapsed } = useSidebar();
  return <div className={`min-h-screen bg-gray-50 pt-16 p-8 transition-all duration-300 ${isCollapsed ? 'pl-20' : 'pl-64'}`}><h1 className="text-3xl font-bold mb-6">Analytics</h1><div className="bg-white p-6 rounded-lg shadow"><p className="text-gray-600">View your application analytics</p></div></div>;
};

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
        <SidebarProvider>
            <BrowserRouter>
              <div className="App">
                <Navbar />
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
                    path="/saved-jobs"
                    element={
                      <PrivateRoute>
                        <SavedJobs />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/applications"
                    element={
                      <PrivateRoute>
                        <Applications />
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
                  <Route
                    path="/resume"
                    element={
                      <PrivateRoute>
                        <ResumeManager />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/interview-prep"
                    element={
                      <PrivateRoute>
                        <InterviewPrep />
                      </PrivateRoute>
                    }
                  />
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
              </div>
              <Toaster position="top-right" />
            </BrowserRouter>
          </SidebarProvider>
        </AuthProvider>
      </QueryClientProvider>
  );
}

export default App;
