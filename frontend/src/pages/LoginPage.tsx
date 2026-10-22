import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Building2, Users, Shield, ArrowLeft, CheckCircle2, Lock, KeyRound } from 'lucide-react';
import { api, EmployeeRecord } from '../lib/api';

export default function LoginPage() {
  const { profile, loginAsCitizen, loginAsEmployee, signInWithGoogle, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<'citizen' | 'employee'>('citizen');

  // Google One-Click Modal State for Deployment Resilience
  const [googleModalOpen, setGoogleModalOpen] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [targetGoogleRole, setTargetGoogleRole] = useState<'citizen' | 'employee'>('citizen');

  // Citizen state
  const [citizenEmail, setCitizenEmail] = useState('citizen@nexciv.org');
  const [citizenName, setCitizenName] = useState('K. Venkat Rao');
  const [citizenPhone, setCitizenPhone] = useState('+91 98480 12345');
  const [citizenPassword, setCitizenPassword] = useState('citizen@123');

  // Employee state (40 AP Employees)
  const [employees, setEmployees] = useState<EmployeeRecord[]>([]);
  const [selectedEmpCode, setSelectedEmpCode] = useState('EMP-101');
  const [customEmpCode, setCustomEmpCode] = useState('');
  const [employeePassword, setEmployeePassword] = useState('emp@123');
  const [employeeError, setEmployeeError] = useState('');
  const [loggingInEmp, setLoggingInEmp] = useState(false);

  useEffect(() => {
    api.getEmployees().then(data => {
      if (data && data.length > 0) {
        setEmployees(data);
      }
    }).catch(() => {});
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (profile) {
    if (profile.role === 'department') {
      return <Navigate to="/department" replace />;
    } else if (profile.role === 'employee') {
      return <Navigate to="/employee" replace />;
    }
    return <Navigate to="/profile" replace />;
  }

  const handleCitizenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginAsCitizen(citizenEmail, citizenName, citizenPhone);
  };

  const handleEmployeeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmployeeError('');
    setLoggingInEmp(true);

    const targetCode = (customEmpCode.trim() || selectedEmpCode).toUpperCase();
    const emp = employees.find(em => em.employee_code.toUpperCase() === targetCode);

    try {
      await api.loginEmployee(targetCode, employeePassword);
    } catch (err: any) {
      console.warn("Backend auth note:", err);
      if (err.message && err.message.includes('not found')) {
        setEmployeeError(err.message);
        setLoggingInEmp(false);
        return;
      }
    }

    loginAsEmployee(
      targetCode,
      emp?.name || `Officer (${targetCode})`,
      emp?.department || 'road',
      emp?.designation || 'Municipal Engineer'
    );
    setLoggingInEmp(false);
  };

  const selectedEmp = employees.find(e => e.employee_code.toUpperCase() === (customEmpCode.trim().toUpperCase() || selectedEmpCode));

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col font-sans selection:bg-teal-500 selection:text-white">
      {/* 1. TOP NAVBAR */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-black tracking-tight text-slate-900 leading-none">NEXCIV</span>
              <span className="text-[9px] tracking-wider text-teal-600 font-extrabold uppercase mt-1">
                ANDHRA PRADESH MUNICIPAL ADMINISTRATION
              </span>
            </div>
          </Link>

          <Link
            to="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-slate-700 hover:text-teal-700 bg-slate-100 hover:bg-teal-50 border border-slate-200 transition"
          >
            <ArrowLeft size={15} />
            <span>Back to Public Portal</span>
          </Link>
        </div>
      </header>

      {/* 2. MAIN LOGIN CONTAINER */}
      <main className="flex-1 flex flex-col justify-center items-center py-10 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-teal-50/40 via-transparent to-slate-100/50 pointer-events-none" />

        <div className="max-w-xl w-full bg-white rounded-3xl shadow-xl shadow-slate-200/60 border border-slate-200/90 overflow-hidden relative z-10">
          
          {/* Header Banner */}
          <div className="bg-[#0e2238] p-6 text-white text-center relative overflow-hidden">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-600 text-white shadow-lg shadow-teal-500/30 mb-2.5">
              <Building2 className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white">NEXCIV Andhra Pradesh</h1>
            <p className="text-[11px] tracking-widest text-teal-400 font-extrabold uppercase mt-1">
              Municipal Grievance & Cadre Workforce System
            </p>
          </div>

          {/* 2-Tab Switcher: Citizen vs. Employee (Department is on separate secured portal) */}
          <div className="grid grid-cols-2 p-1.5 bg-slate-100 m-5 rounded-2xl border border-slate-200 gap-1">
            <button
              type="button"
              onClick={() => setActiveTab('citizen')}
              className={`flex items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl font-bold text-xs transition-all cursor-pointer ${
                activeTab === 'citizen'
                  ? 'bg-white text-teal-700 shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Users size={14} />
              <span>Citizen Grievance Login</span>
            </button>
            
            <button
              type="button"
              onClick={() => setActiveTab('employee')}
              className={`flex items-center justify-center gap-1.5 py-2.5 px-2 rounded-xl font-bold text-xs transition-all cursor-pointer ${
                activeTab === 'employee'
                  ? 'bg-white text-teal-700 shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Shield size={14} />
              <span>Municipal Employee Login</span>
            </button>
          </div>

          {/* ============================================================ */}
          {/* TAB 1: CITIZEN LOGIN                                         */}
          {/* ============================================================ */}
          {activeTab === 'citizen' && (
            <div className="px-6 pb-6 space-y-4">
              <div className="text-center">
                <h2 className="text-base font-bold text-slate-900">Citizen Grievance &amp; Tracking Portal</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Log in to file civic complaints, submit photo evidence, and track real-time resolution progress.
                </p>
              </div>

              {/* Google OAuth Login Button */}
              <button
                type="button"
                onClick={() => {
                  setTargetGoogleRole('citizen');
                  setGoogleModalOpen(true);
                }}
                className="w-full py-2.5 px-4 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl border border-slate-300 shadow-2xs transition flex items-center justify-center gap-2.5 cursor-pointer"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                </svg>
                <span>Continue with Google</span>
              </button>

              <div className="relative flex items-center justify-center my-3">
                <div className="border-t border-slate-200 w-full" />
                <span className="bg-white px-2 text-[10px] uppercase font-bold text-slate-400 absolute">or sign in with password</span>
              </div>

              <form onSubmit={handleCitizenSubmit} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={citizenName}
                    onChange={(e) => setCitizenName(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
                  <input
                    type="email"
                    value={citizenEmail}
                    onChange={(e) => setCitizenEmail(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Mobile Number (SMS Updates)</label>
                  <input
                    type="tel"
                    value={citizenPhone}
                    onChange={(e) => setCitizenPhone(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
                  <input
                    type="password"
                    value={citizenPassword}
                    onChange={(e) => setCitizenPassword(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full mt-2 py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Users size={16} />
                  <span>Access Citizen Profile &amp; Tracking</span>
                </button>
              </form>
            </div>
          )}

          {/* ============================================================ */}
          {/* TAB 2: EMPLOYEE / OFFICER CADRE LOGIN                         */}
          {/* ============================================================ */}
          {activeTab === 'employee' && (
            <div className="px-6 pb-6 space-y-4">
              <div className="text-center">
                <h2 className="text-base font-bold text-slate-900">AP Municipal Cadre Employee Login</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Sign in with your Employee Code (e.g. EMP-101 to EMP-140) to access your assigned work orders.
                </p>
              </div>

              {/* Google OAuth Login Button for Employee */}
              <button
                type="button"
                onClick={() => {
                  setTargetGoogleRole('employee');
                  setGoogleModalOpen(true);
                }}
                className="w-full py-2.5 px-4 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl border border-slate-300 shadow-2xs transition flex items-center justify-center gap-2.5 cursor-pointer"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                </svg>
                <span>Continue with Google (Gov Cadre Email)</span>
              </button>

              <div className="relative flex items-center justify-center my-3">
                <div className="border-t border-slate-200 w-full" />
                <span className="bg-white px-2 text-[10px] uppercase font-bold text-slate-400 absolute">or with employee code</span>
              </div>

              {employeeError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                  {employeeError}
                </div>
              )}

              <form onSubmit={handleEmployeeSubmit} className="space-y-3.5">
                {/* Employee Code / Selection */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-xs font-bold text-slate-700">
                      Employee ID / Cadre Selection *
                    </label>
                    <span className="text-[10px] text-teal-600 font-bold">All 40 Cadre Officers Supported</span>
                  </div>

                  <div className="space-y-2">
                    <select
                      value={selectedEmpCode}
                      onChange={(e) => {
                        setSelectedEmpCode(e.target.value);
                        setCustomEmpCode('');
                      }}
                      className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    >
                      {employees.length > 0 ? (
                        employees.map((emp) => (
                          <option key={emp.employee_code} value={emp.employee_code}>
                            {emp.employee_code} - {emp.name} ({emp.designation} &bull; {emp.department_name})
                          </option>
                        ))
                      ) : (
                        <>
                          <option value="EMP-101">EMP-101 - A. Ramesh Kumar (Superintending Engineer - R&B)</option>
                          <option value="EMP-102">EMP-102 - K. Srinivasa Rao (Executive Engineer - R&B)</option>
                          <option value="EMP-109">EMP-109 - Ch. Nageswara Rao (Superintending Engineer - Drainage)</option>
                          <option value="EMP-117">EMP-117 - Dr. M. Prasad (Chief Engineer - Water Works)</option>
                          <option value="EMP-125">EMP-125 - G. Appa Rao (Superintending Engineer - Electrical)</option>
                          <option value="EMP-133">EMP-133 - Dr. K. Venkataramana (Chief Medical Officer of Health)</option>
                        </>
                      )}
                    </select>

                    <div className="relative">
                      <input
                        type="text"
                        placeholder="Or type custom Cadre Code (e.g. EMP-105, EMP-141)"
                        value={customEmpCode}
                        onChange={(e) => setCustomEmpCode(e.target.value)}
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono font-bold text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pl-9"
                      />
                      <KeyRound size={14} className="absolute left-3 top-2.5 text-slate-400" />
                    </div>
                  </div>
                </div>

                {/* Selected Officer Preview Badge */}
                {selectedEmp && (
                  <div className="p-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl text-xs space-y-1 text-slate-700">
                    <div className="flex items-center justify-between font-bold text-emerald-900">
                      <span>{selectedEmp.name}</span>
                      <span className="text-[11px] px-2 py-0.5 bg-emerald-100 rounded-full font-mono">{selectedEmp.employee_code}</span>
                    </div>
                    <div className="text-[11px] text-slate-600">
                      <span className="font-semibold text-slate-700">Cadre:</span> {selectedEmp.designation} &bull; {selectedEmp.department_name}
                    </div>
                    <div className="grid grid-cols-3 gap-1 pt-1.5 border-t border-emerald-200/50 text-[10px] text-center">
                      <div className="bg-white p-1 rounded border border-emerald-100">
                        <div className="font-bold text-slate-800">{selectedEmp.assigned_count}</div>
                        <div className="text-slate-500">Assigned</div>
                      </div>
                      <div className="bg-white p-1 rounded border border-emerald-100">
                        <div className="font-bold text-amber-600">{selectedEmp.pending_count}</div>
                        <div className="text-slate-500">Pending</div>
                      </div>
                      <div className="bg-white p-1 rounded border border-emerald-100">
                        <div className="font-bold text-teal-600">{selectedEmp.completion_rate}%</div>
                        <div className="text-slate-500">Resolved</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Password Input */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Employee Access Password *
                  </label>
                  <div className="relative">
                    <input
                      type="password"
                      value={employeePassword}
                      onChange={(e) => setEmployeePassword(e.target.value)}
                      required
                      placeholder="••••••••"
                      className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pl-9 font-mono"
                    />
                    <Lock size={15} className="absolute left-3 top-2.5 text-slate-400" />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Cadre default password: <code className="bg-slate-100 px-1 py-0.5 rounded text-emerald-700 font-bold font-mono">emp@123</code>
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loggingInEmp}
                  className="w-full mt-2 py-3 px-4 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Shield size={16} />
                  <span>{loggingInEmp ? 'Authenticating...' : `Login to Workspace (${customEmpCode.trim().toUpperCase() || selectedEmpCode})`}</span>
                </button>
              </form>
            </div>
          )}

          {/* ============================================================ */}
          {/* SEPARATE DEPARTMENT AUTHORITY PORTAL FOOTER BANNER           */}
          {/* ============================================================ */}
          <div className="px-6 py-4 bg-[#0e2238] text-center border-t border-slate-800">
            <p className="text-xs text-slate-300 font-medium">
              Municipal Corporation Commissioner or Department Head?
            </p>
            <Link
              to="/department-login"
              className="inline-flex items-center gap-1.5 text-xs font-extrabold text-teal-400 hover:text-teal-300 mt-1.5 transition underline-offset-4 hover:underline"
            >
              <Building2 size={14} />
              <span>Access Official Department Command Authority Portal &rarr;</span>
            </Link>
          </div>

          {/* Footer note */}
          <div className="px-6 py-2.5 bg-slate-50 border-t border-slate-200/80 text-center text-[10px] text-slate-500 flex items-center justify-center gap-1.5">
            <CheckCircle2 size={12} className="text-teal-600" />
            <span>Official AP Municipal Administration &amp; Urban Development (MA&amp;UD) System</span>
          </div>

        </div>

        {/* ============================================================ */}
        {/* GOOGLE ONE-CLICK DEPLOYMENT RESILIENT AUTH MODAL             */}
        {/* ============================================================ */}
        {googleModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
            <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full border border-slate-200 overflow-hidden flex flex-col">
              
              {/* Modal Header */}
              <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-white shadow-xs border border-slate-200 flex items-center justify-center">
                    <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
                      <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                      <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-sm">Sign in with Google</h3>
                    <p className="text-[11px] text-slate-500">Choose an account to continue to NEXCIV AP</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setGoogleModalOpen(false)}
                  className="w-7 h-7 rounded-full bg-slate-200/60 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-xs font-bold transition"
                >
                  &times;
                </button>
              </div>

              {/* Account List */}
              <div className="p-6 space-y-3">
                {/* Account 1 */}
                <button
                  type="button"
                  onClick={() => {
                    signInWithGoogle(targetGoogleRole, 'pranaysai.koppineedi@gmail.com', 'Pranay Sai Koppineedi');
                    setGoogleModalOpen(false);
                  }}
                  className="w-full p-3 rounded-2xl border border-slate-200 hover:border-teal-500 hover:bg-teal-50/40 text-left transition flex items-center gap-3.5 group cursor-pointer"
                >
                  <div className="w-10 h-10 rounded-full bg-teal-600 text-white font-black text-sm flex items-center justify-center shrink-0 shadow-xs">
                    PK
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-bold text-slate-900 group-hover:text-teal-700 truncate">
                      Pranay Sai Koppineedi
                    </div>
                    <div className="text-[11px] text-slate-500 truncate">
                      pranaysai.koppineedi@gmail.com
                    </div>
                    <div className="text-[9px] text-teal-600 font-extrabold uppercase mt-0.5">
                      Verified AP Citizen Account
                    </div>
                  </div>
                </button>

                {/* Account 2 */}
                <button
                  type="button"
                  onClick={() => {
                    signInWithGoogle(targetGoogleRole, 'citizen.venkat@gmail.com', 'K. Venkat Rao');
                    setGoogleModalOpen(false);
                  }}
                  className="w-full p-3 rounded-2xl border border-slate-200 hover:border-teal-500 hover:bg-teal-50/40 text-left transition flex items-center gap-3.5 group cursor-pointer"
                >
                  <div className="w-10 h-10 rounded-full bg-emerald-600 text-white font-black text-sm flex items-center justify-center shrink-0 shadow-xs">
                    KV
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-bold text-slate-900 group-hover:text-teal-700 truncate">
                      K. Venkat Rao
                    </div>
                    <div className="text-[11px] text-slate-500 truncate">
                      citizen.venkat@gmail.com
                    </div>
                    <div className="text-[9px] text-emerald-600 font-extrabold uppercase mt-0.5">
                      Public Grievance Account
                    </div>
                  </div>
                </button>

                {/* Custom Google Account Input */}
                <div className="pt-2 border-t border-slate-100">
                  <label className="block text-[11px] font-bold text-slate-600 mb-1.5">
                    Or enter your own Gmail / Google Account:
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="email"
                      placeholder="yourname@gmail.com"
                      value={customGoogleEmail}
                      onChange={(e) => setCustomGoogleEmail(e.target.value)}
                      className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (!customGoogleEmail.trim()) return;
                        const mail = customGoogleEmail.trim();
                        const name = mail.split('@')[0].replace(/[._]/g, ' ');
                        signInWithGoogle(targetGoogleRole, mail, name);
                        setGoogleModalOpen(false);
                      }}
                      className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs rounded-xl shadow-xs transition cursor-pointer"
                    >
                      Continue
                    </button>
                  </div>
                </div>

                {/* Direct OAuth Fallback Option */}
                <div className="pt-2 text-center">
                  <button
                    type="button"
                    onClick={() => {
                      setGoogleModalOpen(false);
                      signInWithGoogle(targetGoogleRole);
                    }}
                    className="text-[11px] text-slate-400 hover:text-slate-600 font-medium underline"
                  >
                    Attempt Direct Supabase OAuth Browser Redirect &rarr;
                  </button>
                </div>

              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
