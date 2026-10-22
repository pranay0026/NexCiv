import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import DepartmentLoginPage from './pages/DepartmentLoginPage';
import ComplaintDetailPage from './pages/ComplaintDetailPage';
import Dashboard from './pages/Dashboard';
import EmployeeWorkspace from './pages/EmployeeWorkspace';
import ProfilePage from './pages/ProfilePage';
import AnalyticsPortal from './pages/AnalyticsPortal';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, profile, loading } = useAuth();
  
  if (loading) return null;
  
  if (!user && !profile) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function RoleBasedDashboard() {
  const { profile } = useAuth();
  if (profile?.role === 'employee') {
    return <EmployeeWorkspace />;
  }
  return <Dashboard />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      
      {/* Dedicated 2-Step Municipal Corporation & Department Operations Login */}
      <Route path="/department-login" element={<DepartmentLoginPage />} />
      <Route path="/dept-login" element={<DepartmentLoginPage />} />
      <Route path="/admin/login" element={<DepartmentLoginPage />} />

      {/* Dedicated Comprehensive Grievance Detail Page */}
      <Route path="/complaint/:id" element={<ComplaintDetailPage />} />
      <Route path="/complaints/:id" element={<ComplaintDetailPage />} />
      
      {/* Dynamic dashboard routing: Employee gets Staff Workspace, Citizen gets citizen portal */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <RoleBasedDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Dedicated Employee / Staff Workspace matching Canva design */}
      <Route path="/employee" element={<EmployeeWorkspace />} />
      <Route path="/staff" element={<EmployeeWorkspace />} />

      {/* Citizen Profile & Information Gathering Page */}
      <Route path="/profile" element={<ProfilePage />} />

      {/* Dedicated linked Department Head Command Center */}
      <Route path="/department" element={<AnalyticsPortal />} />
      <Route path="/analytics" element={<AnalyticsPortal />} />
      <Route path="/department-portal" element={<AnalyticsPortal />} />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
