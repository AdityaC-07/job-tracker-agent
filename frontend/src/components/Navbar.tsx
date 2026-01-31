import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import { LogOut, Menu, X, Heart, Briefcase, BarChart3 } from 'lucide-react';
import { useState } from 'react';

export function Navbar() {
  const { logout, isAuthenticated, user } = useAuthContext();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/dashboard" className="text-2xl font-bold text-indigo-600 flex items-center gap-2">
          🎯 JobFlow
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-6">
          <Link
            to="/dashboard"
            className="text-gray-700 hover:text-indigo-600 font-medium flex items-center gap-1"
          >
            <Briefcase size={20} /> Dashboard
          </Link>
          <Link
            to="/jobs"
            className="text-gray-700 hover:text-indigo-600 font-medium flex items-center gap-1"
          >
            <Briefcase size={20} /> Search Jobs
          </Link>
          <Link
            to="/saved-jobs"
            className="text-gray-700 hover:text-indigo-600 font-medium flex items-center gap-1"
          >
            <Heart size={20} /> Saved Jobs
          </Link>
          <Link
            to="/applications"
            className="text-gray-700 hover:text-indigo-600 font-medium flex items-center gap-1"
          >
            <Briefcase size={20} /> Applications
          </Link>
          <Link
            to="/analytics"
            className="text-gray-700 hover:text-indigo-600 font-medium flex items-center gap-1"
          >
            <BarChart3 size={20} /> Analytics
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

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden border-t border-gray-200 bg-gray-50">
          <div className="px-4 py-4 space-y-2">
            <Link
              to="/dashboard"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg"
              onClick={() => setIsOpen(false)}
            >
              🏠 Dashboard
            </Link>
            <Link
              to="/jobs"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg"
              onClick={() => setIsOpen(false)}
            >
              🔍 Search Jobs
            </Link>
            <Link
              to="/saved-jobs"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg"
              onClick={() => setIsOpen(false)}
            >
              ❤️ Saved Jobs
            </Link>
            <Link
              to="/applications"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg"
              onClick={() => setIsOpen(false)}
            >
              💼 Applications
            </Link>
            <Link
              to="/analytics"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg"
              onClick={() => setIsOpen(false)}
            >
              <BarChart3 size={18} className="inline mr-2" />Analytics
            </Link>
            <button
              onClick={() => {
                handleLogout();
                setIsOpen(false);
              }}
              className="w-full mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium flex items-center justify-center gap-2"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
