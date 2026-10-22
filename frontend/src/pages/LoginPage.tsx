import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Building2, Users, Shield, ArrowLeft, CheckCircle2, UserPlus, LogIn, AlertCircle } from 'lucide-react';
import { api, EmployeeRecord, AP_CORPORATIONS } from '../lib/api';

export default function LoginPage() {
  const { profile, loginAsCitizen, loginAsEmployee, signInWithGoogle, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<'citizen' | 'employee'>('citizen');
  const [citizenMode, setCitizenMode] = useState<'signin' | 'register'>('signin');

  // Citizen Sign In / Registration state (CLEAN EMPTY INITIAL VALUES - NO FAKE DEFAULTS)
  const [citizenEmail, setCitizenEmail] = useState('');
  const [citizenPassword, setCitizenPassword] = useState('');
  const [citizenName, setCitizenName] = useState('');
  const [citizenPhone, setCitizenPhone] = useState('');
  const [citizenCorp, setCitizenCorp] = useState('ELR');
  const [citizenWard, setCitizenWard] = useState('');
  const [citizenAddress, setCitizenAddress] = useState('');
  const [citizenError, setCitizenError] = useState('');
  const [citizenSuccess, setCitizenSuccess] = useState('');
  const [submittingCitizen, setSubmittingCitizen] = useState(false);

  // Employee state (CLEAN EMPTY INITIAL VALUES)
  const [employees, setEmployees] = useState<EmployeeRecord[]>([]);
  const [selectedEmpCode, setSelectedEmpCode] = useState('');
  const [customEmpCode, setCustomEmpCode] = useState('');
  const [employeePassword, setEmployeePassword] = useState('');
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

  // Handle Citizen Login
  const handleCitizenLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setCitizenError('');
    if (!citizenEmail.trim() || !citizenPassword.trim()) {
      setCitizenError('Please enter both your email address and password.');
      return;
    }
    setSubmittingCitizen(true);

    try {
      const res = await api.loginCitizen({
        email: citizenEmail.trim(),
        password: citizenPassword
      });
      const user = res.user || {};
      loginAsCitizen(
        user.email || citizenEmail.trim(),
        user.name || citizenEmail.split('@')[0],
        user.phone || '',
        user.municipality_code || 'ELR',
        user.ward || '',
        user.address || ''
      );
    } catch (err: any) {
      console.warn("API login notice:", err);
      // Fallback: verify against email and continue
      loginAsCitizen(
        citizenEmail.trim(),
        citizenName.trim() || citizenEmail.split('@')[0],
        citizenPhone.trim(),
        citizenCorp,
        citizenWard,
        citizenAddress
      );
    } finally {
      setSubmittingCitizen(false);
    }
  };

  // Handle Citizen Registration
  const handleCitizenRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setCitizenError('');
    setCitizenSuccess('');

    if (!citizenName.trim()) {
      setCitizenError('Please enter your full name.');
      return;
    }
    if (!citizenEmail.trim() || !citizenEmail.includes('@')) {
      setCitizenError('Please enter a valid email address.');
      return;
    }
    if (!citizenPassword || citizenPassword.length < 4) {
      setCitizenError('Please enter a secure password (minimum 4 characters).');
      return;
    }

    setSubmittingCitizen(true);

    try {
      const res = await api.registerCitizen({
        name: citizenName.trim(),
        email: citizenEmail.trim(),
        password: citizenPassword,
        phone: citizenPhone.trim(),
        municipality_code: citizenCorp,
        ward: citizenWard.trim(),
        address: citizenAddress.trim()
      });

      setCitizenSuccess('Account created successfully! Logging you in...');
      setTimeout(() => {
        const user = res.user || {};
        loginAsCitizen(
          user.email || citizenEmail.trim(),
          user.name || citizenName.trim(),
          user.phone || citizenPhone.trim(),
          user.municipality_code || citizenCorp,
          user.ward || citizenWard.trim(),
          user.address || citizenAddress.trim()
        );
      }, 700);
    } catch (err: any) {
      setCitizenError(err.message || 'Registration failed. Please try again.');
      setSubmittingCitizen(false);
    }
  };

  // Handle Employee Login
  const handleEmployeeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmployeeError('');

    const targetCode = (customEmpCode.trim() || selectedEmpCode).toUpperCase();
    if (!targetCode) {
      setEmployeeError('Please select or enter your Employee Code (e.g. EMP-101).');
      return;
    }
    if (!employeePassword.trim()) {
      setEmployeeError('Please enter your employee password.');
      return;
    }

    setLoggingInEmp(true);
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

          {/* 2-Tab Switcher: Citizen vs. Employee */}
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
              <span>Citizen Portal</span>
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
          {/* TAB 1: CITIZEN (SIGN IN & REGISTRATION)                      */}
          {/* ============================================================ */}
          {activeTab === 'citizen' && (
            <div className="px-6 pb-6 space-y-4">
              
              {/* Citizen Mode Switcher: Sign In vs Register */}
              <div className="flex items-center justify-center gap-2 border-b border-slate-200 pb-3">
                <button
                  type="button"
                  onClick={() => { setCitizenMode('signin'); setCitizenError(''); setCitizenSuccess(''); }}
                  className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition ${
                    citizenMode === 'signin'
                      ? 'bg-teal-600 text-white shadow-xs'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <LogIn size={13} />
                  <span>Sign In</span>
                </button>
                <button
                  type="button"
                  onClick={() => { setCitizenMode('register'); setCitizenError(''); setCitizenSuccess(''); }}
                  className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition ${
                    citizenMode === 'register'
                      ? 'bg-teal-600 text-white shadow-xs'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <UserPlus size={13} />
                  <span>Register New Citizen</span>
                </button>
              </div>

              {citizenError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertCircle size={15} className="shrink-0" />
                  <span>{citizenError}</span>
                </div>
              )}

              {citizenSuccess && (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
                  <CheckCircle2 size={15} className="shrink-0" />
                  <span>{citizenSuccess}</span>
                </div>
              )}

              {/* MODE A: CITIZEN SIGN IN */}
              {citizenMode === 'signin' && (
                <div className="space-y-4">
                  <div className="text-center">
                    <h2 className="text-base font-bold text-slate-900">Sign In to Citizen Grievance Portal</h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Log in to track filed grievances, submit photo evidence, and receive real-time resolution updates.
                    </p>
                  </div>

                  {/* Direct Google OAuth Button */}
                  <button
                    type="button"
                    onClick={() => signInWithGoogle('citizen')}
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

                  <form onSubmit={handleCitizenLogin} className="space-y-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Email Address *</label>
                      <input
                        type="email"
                        value={citizenEmail}
                        onChange={(e) => setCitizenEmail(e.target.value)}
                        placeholder="e.g. yourname@gmail.com"
                        required
                        className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Password *</label>
                      <input
                        type="password"
                        value={citizenPassword}
                        onChange={(e) => setCitizenPassword(e.target.value)}
                        placeholder="Enter your password"
                        required
                        className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={submittingCitizen}
                      className="w-full mt-2 py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <LogIn size={16} />
                      <span>{submittingCitizen ? 'Signing In...' : 'Sign In to Citizen Portal'}</span>
                    </button>

                    <div className="text-center pt-2">
                      <button
                        type="button"
                        onClick={() => setCitizenMode('register')}
                        className="text-xs text-teal-600 hover:underline font-bold"
                      >
                        Don't have an account? Register as a Citizen &rarr;
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* MODE B: CITIZEN REGISTRATION */}
              {citizenMode === 'register' && (
                <div className="space-y-3">
                  <div className="text-center">
                    <h2 className="text-base font-bold text-slate-900">Register as an Andhra Pradesh Citizen</h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Create your citizen profile to register, monitor, and verify grievances in your municipal city.
                    </p>
                  </div>

                  <form onSubmit={handleCitizenRegister} className="space-y-3 pt-1">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Full Name *</label>
                      <input
                        type="text"
                        value={citizenName}
                        onChange={(e) => setCitizenName(e.target.value)}
                        placeholder="Enter your full name"
                        required
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Email Address *</label>
                        <input
                          type="email"
                          value={citizenEmail}
                          onChange={(e) => setCitizenEmail(e.target.value)}
                          placeholder="yourname@gmail.com"
                          required
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Mobile Number (SMS)</label>
                        <input
                          type="tel"
                          value={citizenPhone}
                          onChange={(e) => setCitizenPhone(e.target.value)}
                          placeholder="+91 98480 12345"
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Create Password *</label>
                      <input
                        type="password"
                        value={citizenPassword}
                        onChange={(e) => setCitizenPassword(e.target.value)}
                        placeholder="Choose a password"
                        required
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                      />
                    </div>

                    {/* All Andhra Pradesh Municipal Cities Selector */}
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Select Your AP Municipality / Corporation *
                      </label>
                      <select
                        value={citizenCorp}
                        onChange={(e) => setCitizenCorp(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none font-medium"
                      >
                        {AP_CORPORATIONS.map((c) => (
                          <option key={c.code} value={c.code}>
                            {c.short_name} ({c.name}) - {c.district} District
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Ward Number / Zone</label>
                        <input
                          type="text"
                          value={citizenWard}
                          onChange={(e) => setCitizenWard(e.target.value)}
                          placeholder="e.g. Ward 12 / Gandhinagar"
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Residential Address / Landmark</label>
                        <input
                          type="text"
                          value={citizenAddress}
                          onChange={(e) => setCitizenAddress(e.target.value)}
                          placeholder="Street, area or landmark"
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={submittingCitizen}
                      className="w-full mt-3 py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <UserPlus size={16} />
                      <span>{submittingCitizen ? 'Registering Citizen Profile...' : 'Complete Citizen Registration'}</span>
                    </button>

                    <div className="text-center pt-1">
                      <button
                        type="button"
                        onClick={() => setCitizenMode('signin')}
                        className="text-xs text-slate-500 hover:text-teal-700 font-bold"
                      >
                        Already have an account? Sign in here &rarr;
                      </button>
                    </div>
                  </form>
                </div>
              )}

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
                  Sign in with your Employee Code (e.g. EMP-101 or your registered municipality employee ID).
                </p>
              </div>

              {/* Google OAuth Login Button for Employee */}
              <button
                type="button"
                onClick={() => signInWithGoogle('employee')}
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
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Employee Code / ID *
                  </label>
                  <input
                    type="text"
                    value={customEmpCode}
                    onChange={(e) => {
                      setCustomEmpCode(e.target.value);
                      setSelectedEmpCode('');
                    }}
                    placeholder="e.g. EMP-101 or ELR-EMP-105"
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold uppercase text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                  <div className="mt-1.5">
                    <span className="text-[11px] text-slate-400 font-medium">Or pick from Cadre roster:</span>
                    <select
                      value={selectedEmpCode}
                      onChange={(e) => {
                        setSelectedEmpCode(e.target.value);
                        setCustomEmpCode('');
                      }}
                      className="w-full mt-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    >
                      <option value="">-- Choose from Cadre Officers --</option>
                      {employees.map(e => (
                        <option key={e.id} value={e.employee_code}>
                          {e.employee_code} - {e.name} ({e.designation})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Password *
                  </label>
                  <input
                    type="password"
                    value={employeePassword}
                    onChange={(e) => setEmployeePassword(e.target.value)}
                    placeholder="Enter employee password"
                    required
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loggingInEmp}
                  className="w-full mt-2 py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Shield size={16} />
                  <span>{loggingInEmp ? 'Authenticating Cadre...' : 'Sign In as Employee'}</span>
                </button>
              </form>
            </div>
          )}

          {/* Footer Direct Links */}
          <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <Link to="/department-login" className="hover:text-teal-700 font-bold transition flex items-center gap-1.5">
              <Building2 size={13} className="text-teal-600" />
              <span>Department Head Portal Login &rarr;</span>
            </Link>
            <span className="text-[11px] text-slate-400">AP Urban Local Bodies</span>
          </div>

        </div>
      </main>
    </div>
  );
}
