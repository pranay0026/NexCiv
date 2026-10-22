import { useAuth } from '../context/AuthContext';
import ThemeToggle from './ThemeToggle';
import { LogOut, Shield, User as UserIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  const { user, profile, signOut } = useAuth();

  const displayName = profile?.name || user?.email?.split('@')[0] || 'User';
  const isEmployee = profile?.role === 'employee';

  return (
    <nav className="sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-slate-200/80 dark:border-gray-800 px-4 sm:px-6 py-3 flex items-center justify-between shadow-xs">
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white shadow-sm shadow-teal-500/20">
            <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-black text-slate-900 dark:text-white tracking-tight leading-none">NEXCIV</span>
            <span className="text-[8px] tracking-wider text-teal-600 dark:text-teal-400 font-extrabold uppercase mt-0.5">
              CLEANER CITIES. STRONGER COMMUNITIES.
            </span>
          </div>
        </Link>

        {/* Home Link */}
        <Link
          to="/"
          className="hidden sm:inline-flex text-xs font-bold text-slate-600 dark:text-gray-300 hover:text-teal-600 dark:hover:text-teal-400 transition ml-2"
        >
          Portal Home
        </Link>

        {/* Current Active Persona Badge */}
        {profile && (
          <div className={`hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${
            isEmployee
              ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800'
              : 'bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border-teal-200 dark:border-teal-800'
          }`}>
            {isEmployee ? <Shield size={13} /> : <UserIcon size={13} />}
            <span>{isEmployee ? `Officer: ${profile.departmentName}` : 'Citizen Portal'}</span>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        
        {(user || profile) && (
          <div className="flex items-center gap-3 border-l border-gray-200 dark:border-gray-700 pl-3">
            <Link
              to="/profile"
              className="hidden lg:flex flex-col text-right hover:opacity-85 transition"
              title="View & Edit Profile"
            >
              <span className="text-xs font-bold text-gray-800 dark:text-gray-200 leading-tight">
                {displayName}
              </span>
              <span className="text-[10px] text-teal-600 dark:text-teal-400 font-semibold">
                {profile?.role === 'employee' ? 'Municipal Staff' : 'Resident Profile →'}
              </span>
            </Link>
            
            <button
              onClick={signOut}
              className="text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 transition-colors flex items-center gap-1 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              title="Sign out"
            >
              <LogOut size={18} />
              <span className="sr-only">Sign out</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
