import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import { useSidebar } from '../context/SidebarContext';
import { LogOut, Menu, X, Heart, Briefcase, BarChart3, LayoutDashboard, Search, ChevronLeft, ChevronRight } from 'lucide-react';

export function Navbar() {
  const { logout, isAuthenticated, user } = useAuthContext();
  const navigate = useNavigate();
  const { isCollapsed, toggleSidebar } = useSidebar();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Top Bar */}
      <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-30">
        <div className="px-6 py-4 flex justify-between items-center">
          <Link to="/dashboard" className="text-2xl font-bold text-indigo-600 flex items-center gap-2">
            JobFlow
          </Link>

          <div className="flex items-center gap-4">
            <span className="text-gray-600 text-sm">{user?.name}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium flex items-center gap-2"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Sidebar */}
      <aside
        className={`fixed top-16 left-0 bottom-0 bg-white border-r border-gray-200 transition-all duration-300 z-20 ${
          isCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Toggle Button */}
        <button
          onClick={toggleSidebar}
          className="absolute -right-3 top-6 bg-indigo-600 text-white rounded-full p-1 shadow-lg hover:bg-indigo-700"
        >
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>

        {/* Navigation Links */}
        <nav className="px-4 py-6 space-y-2">
          <Link
            to="/dashboard"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors font-medium"
          >
            <LayoutDashboard size={22} />
            {!isCollapsed && <span>Dashboard</span>}
          </Link>

          <Link
            to="/jobs"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors font-medium"
          >
            <Search size={22} />
            {!isCollapsed && <span>Search Jobs</span>}
          </Link>

          <Link
            to="/saved-jobs"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors font-medium"
          >
            <Heart size={22} />
            {!isCollapsed && <span>Saved Jobs</span>}
          </Link>

          <Link
            to="/applications"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors font-medium"
          >
            <Briefcase size={22} />
            {!isCollapsed && <span>Applications</span>}
          </Link>

          <Link
            to="/analytics"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors font-medium"
          >
            <BarChart3 size={22} />
            {!isCollapsed && <span>Analytics</span>}
          </Link>
        </nav>
      </aside>
    </>
  );
}

export default Navbar;
