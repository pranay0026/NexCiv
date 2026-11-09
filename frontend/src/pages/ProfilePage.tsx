import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  Mail,
  Phone,
  MapPin,
  Building,
  ShieldCheck,
  CheckCircle2,
  Clock,
  FileText,
  Save,
  Navigation,
  ArrowRight,
  LogOut,
  Sparkles,
  Flame,
  Eye,
  Camera,
  Wrench,
  AlertCircle,
  EyeOff,
  Lock,
  KeyRound
} from 'lucide-react';
import { api, ComplaintRecord } from '../lib/api';

export default function ProfilePage() {
  const { profile, updateProfile, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  // Profile Form States (strictly initialize from authenticated profile)
  const [fullName, setFullName] = useState(profile?.name || 'Citizen');
  const [email, setEmail] = useState(profile?.email || '');
  const [phone, setPhone] = useState(profile?.phone || '');
  const [state] = useState(profile?.state || 'Andhra Pradesh');
  const [city, setCity] = useState(profile?.city || profile?.municipalCorporation || 'Andhra Pradesh');
  const [ward, setWard] = useState(profile?.ward || 'Ward not assigned');
  const [address, setAddress] = useState(profile?.address || '');
  const [pincode, setPincode] = useState(profile?.pincode || '');

  // Synchronize state dynamically whenever the auth profile changes
  useEffect(() => {
    if (profile) {
      if (profile.name) setFullName(profile.name);
      if (profile.email) setEmail(profile.email);
      setPhone(profile.phone || '');
      setCity(profile.city || profile.municipalCorporation || 'Andhra Pradesh');
      setWard(profile.ward || 'Ward not assigned');
      setAddress(profile.address || '');
      setPincode(profile.pincode || '');
    }
  }, [profile]);

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [detectingGps, setDetectingGps] = useState(false);

  // Password Update State (Show/hide toggle & change password)
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPass, setShowNewPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);
  const [passwordUpdating, setPasswordUpdating] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');
    if (!newPassword || newPassword.length < 4) {
      setPasswordError('New password must be at least 4 characters long.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New password and confirmation do not match.');
      return;
    }
    setPasswordUpdating(true);
    try {
      const res = await api.changePassword({
        role: 'citizen',
        identifier: email || profile?.email || 'citizen',
        oldPassword: currentPassword,
        newPassword
      });
      setPasswordSuccess(res.message || 'Password updated successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setPasswordSuccess(''), 4000);
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to update password.');
    } finally {
      setPasswordUpdating(false);
    }
  };

  // Tab: Info vs Complaints History
  const [activeTab, setActiveTab] = useState<'info' | 'complaints'>('complaints');

  // Live Complaints State
  const [complaints, setComplaints] = useState<ComplaintRecord[]>([]);
  const [loadingComplaints, setLoadingComplaints] = useState(true);
  const [selectedComplaint, setSelectedComplaint] = useState<ComplaintRecord | null>(null);

  // Fetch live citizen complaints (Strictly scoped to current citizen only)
  const fetchCitizenComplaints = async () => {
    try {
      setLoadingComplaints(true);
      const allComplaints = await api.getComplaints();
      const userEmail = (profile?.email || email || '').trim().toLowerCase();
      const userId = profile?.id;

      let locallyFiled: string[] = [];
      try {
        locallyFiled = JSON.parse(localStorage.getItem('nexciv_my_complaints') || '[]');
      } catch {}

      // A citizen must only ever see complaints they actually filed
      const userComplaints = allComplaints.filter((c) => {
        if (!userEmail && !userId && locallyFiled.length === 0) return false;
        const cEmail = (c.citizen_email || '').trim().toLowerCase();
        const matchesEmail = Boolean(userEmail && cEmail && cEmail === userEmail);
        const matchesUserId = Boolean(userId && c.user_id && c.user_id === userId);
        const shortCode = c.id.length > 8 ? `NXC-${c.id.slice(0, 6).toUpperCase()}` : c.id;
        // Only accept local ID if the complaint email matches or is unassigned
        const matchesLocal = locallyFiled.some(
          (id) => (id === c.id || id === shortCode) && (!cEmail || cEmail === userEmail)
        );
        return matchesEmail || matchesUserId || matchesLocal;
      });

      // Sort so most recent is first. If 0 complaints, show 0 (never leak other citizens' complaints)
      const sorted = [...userComplaints].sort((a, b) => {
        return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
      });

      setComplaints(sorted);
    } catch (err) {
      console.warn('Error fetching citizen complaints:', err);
      setComplaints([]);
    } finally {
      setLoadingComplaints(false);
    }
  };

  useEffect(() => {
    fetchCitizenComplaints();
    window.addEventListener('nexciv_complaints_updated', fetchCitizenComplaints);
    return () => window.removeEventListener('nexciv_complaints_updated', fetchCitizenComplaints);
  }, [profile, email]);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    updateProfile({
      name: fullName,
      phone,
      state,
      city,
      ward,
      address,
      pincode
    });

    setTimeout(() => {
      setSaving(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }, 400);
  };

  const handleGpsDetect = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setDetectingGps(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        try {
          const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18`
          );
          if (resp.ok) {
            const data = await resp.json();
            if (data.display_name) {
              setAddress(data.display_name);
              if (data.address?.postcode) setPincode(data.address.postcode);
              if (data.address?.city || data.address?.state_district) {
                setCity(`${data.address.city || data.address.state_district} (Municipal Corp)`);
              }
            }
          }
        } catch (e) {
          console.warn('Reverse geocode note:', e);
        } finally {
          setDetectingGps(false);
        }
      },
      () => setDetectingGps(false)
    );
  };

  const getInitials = (nameStr: string) => {
    const parts = nameStr.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return nameStr.slice(0, 2).toUpperCase();
  };

  const totalFiled = complaints.length;
  const inProgressCount = complaints.filter(c => c.status === 'in_progress').length;
  const resolvedCount = complaints.filter(c => c.status === 'resolved').length;

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
                CITIZEN GRIEVANCE & RESOLUTION TRACKER
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-xs font-bold text-slate-600">
            <Link to="/" className="hover:text-teal-700 transition">Home</Link>
            <Link to="/#report" className="hover:text-teal-700 transition">Submit Grievance</Link>
            <Link to="/profile" className="text-teal-700 font-black border-b-2 border-teal-600 pb-1">My Complaints</Link>
          </nav>

          <div className="flex items-center gap-3">
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-teal-50 text-teal-800 border border-teal-200">
              <UserIcon size={14} />
              <span className="max-w-[140px] truncate">{fullName}</span>
            </div>

            <button
              onClick={handleSignOut}
              className="text-xs text-slate-400 hover:text-rose-600 p-1.5 font-semibold transition cursor-pointer"
              title="Sign Out"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* 2. MAIN PROFILE CONTAINER */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* HERO CITIZEN CARD */}
        <div className="bg-[#0e2238] text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500 text-white font-black text-2xl flex items-center justify-center shadow-lg shadow-teal-500/20 border-2 border-teal-300/40 shrink-0">
                {getInitials(fullName)}
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-teal-500/20 text-teal-300 border border-teal-400/30">
                    <ShieldCheck size={12} />
                    Verified Citizen &bull; {state}
                  </span>
                  <span className="text-[11px] text-teal-300 font-mono">
                    {profile?.municipalCorporation || 'GVMC'} Municipal Citizen
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  {fullName}
                </h1>

                <div className="flex items-center gap-4 text-xs text-slate-300 flex-wrap pt-0.5">
                  <span className="flex items-center gap-1.5">
                    <Mail size={13} className="text-teal-400" />
                    <span>{email}</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Phone size={13} className="text-teal-400" />
                    <span>{phone}</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <MapPin size={13} className="text-teal-400" />
                    <span>{ward}</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Stat Badges */}
            <div className="grid grid-cols-3 gap-3 shrink-0 bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10 text-center">
              <div>
                <div className="text-2xl font-black text-white">{totalFiled}</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-0.5 font-bold">Filed</div>
              </div>
              <div className="border-x border-white/10 px-3">
                <div className="text-2xl font-black text-amber-400">{inProgressCount}</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-0.5 font-bold">In Progress</div>
              </div>
              <div>
                <div className="text-2xl font-black text-emerald-400">{resolvedCount}</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider mt-0.5 font-bold">Resolved</div>
              </div>
            </div>
          </div>
        </div>

        {/* 3. TABS: MY GRIEVANCES & PROGRESS TRACKER vs CITIZEN INFO */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
          <button
            type="button"
            onClick={() => setActiveTab('complaints')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition cursor-pointer ${
              activeTab === 'complaints'
                ? 'bg-teal-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileText size={15} />
            <span>My Complaints & Live Progress Tracker ({complaints.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('info')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition cursor-pointer ${
              activeTab === 'info'
                ? 'bg-teal-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <UserIcon size={15} />
            <span>Citizen Profile & Jurisdiction Mapping</span>
          </button>
        </div>

        {/* TAB 1: COMPLAINTS & LIVE PROGRESS TRACKER */}
        {activeTab === 'complaints' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-slate-900">
                  Track Your Submitted Civic Grievances
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Every complaint you have submitted is maintained here. Click "Track Live Progress" to see the full timeline, crew assignment, and before/after repair proof.
                </p>
              </div>

              <Link
                to="/#report"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-xs transition"
              >
                <span>+ Submit New Grievance</span>
              </Link>
            </div>

            {loadingComplaints ? (
              <div className="py-12 text-center text-slate-500 flex flex-col items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-teal-600"></div>
                <span className="text-xs">Loading your complaints from municipal database...</span>
              </div>
            ) : complaints.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-3xl border border-slate-200">
                <AlertCircle className="w-12 h-12 text-teal-600 mx-auto mb-2 opacity-70" />
                <h3 className="font-bold text-slate-800 text-sm">No Grievances Submitted Yet</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                  Report potholes, sewage leaks, street light failures, or drainage issues in your ward. NEXCIV AI will automatically inspect and dispatch the repair squad.
                </p>
                <Link
                  to="/#report"
                  className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-600 text-white font-bold text-xs hover:bg-teal-700 transition"
                >
                  Report First Issue Now
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {complaints.map((c) => {
                  const shortId = c.id.length > 8 ? `NXC-${c.id.slice(0, 6).toUpperCase()}` : c.id;
                  const isResolved = c.status === 'resolved';
                  const isInProgress = c.status === 'in_progress';

                  return (
                    <div
                      key={c.id}
                      className="bg-white rounded-2xl p-5 border border-slate-200/90 hover:border-teal-300 hover:shadow-md transition space-y-4"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-mono font-black text-slate-900 bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
                            {shortId}
                          </span>
                          <span className="text-xs font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                            {c.department || c.category}
                          </span>
                          <span className="text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
                            {c.municipal_corporation || 'GVMC'} &bull; {c.ward || 'Ward 12'}
                          </span>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 ${
                              c.priority === 'Critical'
                                ? 'bg-red-50 text-red-700 border-red-200'
                                : c.priority === 'High'
                                ? 'bg-orange-50 text-orange-700 border-orange-200'
                                : 'bg-amber-50 text-amber-700 border-amber-200'
                            }`}
                          >
                            {c.priority === 'Critical' && <Flame size={11} />}
                            {c.priority || 'Medium'} Priority
                          </span>
                        </div>

                        {/* Status Badge */}
                        <span
                          className={`self-start sm:self-auto px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${
                            isResolved
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : isInProgress
                              ? 'bg-blue-50 text-blue-700 border-blue-200'
                              : 'bg-amber-50 text-amber-700 border-amber-200'
                          }`}
                        >
                          <span className={`w-2 h-2 rounded-full ${isResolved ? 'bg-emerald-500' : isInProgress ? 'bg-blue-500 animate-pulse' : 'bg-amber-500'}`} />
                          {isResolved ? 'Resolved & Verified' : isInProgress ? 'Crew In Progress' : 'Awaiting Crew'}
                        </span>
                      </div>

                      {/* Title & Description */}
                      <div>
                        <h3 className="text-sm font-bold text-slate-900">{c.title}</h3>
                        <p className="text-xs text-slate-600 mt-1 line-clamp-2">{c.description}</p>
                      </div>

                      {/* Location & Landmark */}
                      <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
                        {c.location_address && (
                          <span className="flex items-center gap-1">
                            <MapPin size={13} className="text-teal-600" />
                            <span>{c.location_address}</span>
                          </span>
                        )}
                        {c.landmark && (
                          <span className="text-slate-600">
                            <strong>Landmark:</strong> {c.landmark}
                          </span>
                        )}
                        <span className="flex items-center gap-1 text-slate-400">
                          <Clock size={13} />
                          <span>{new Date(c.created_at).toLocaleDateString()}</span>
                        </span>
                      </div>

                      {/* VISUAL 4-STAGE PROGRESS TRACKER */}
                      <div className="pt-2 border-t border-slate-100">
                        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">
                          Live Resolution Milestones
                        </div>
                        <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
                          {/* Step 1 */}
                          <div className="flex flex-col items-center">
                            <div className="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                              ✓
                            </div>
                            <span className="font-bold text-slate-800 mt-1">Grievance Filed</span>
                            <span className="text-[9px] text-slate-400">Registered</span>
                          </div>

                          {/* Step 2 */}
                          <div className="flex flex-col items-center">
                            <div className="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                              ✓
                            </div>
                            <span className="font-bold text-slate-800 mt-1">AI Department Triage</span>
                            <span className="text-[9px] text-slate-400">Routed</span>
                          </div>

                          {/* Step 3 */}
                          <div className="flex flex-col items-center">
                            <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs shadow-xs ${
                              isInProgress || isResolved ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-500'
                            }`}>
                              {isInProgress || isResolved ? '✓' : '3'}
                            </div>
                            <span className={`font-bold mt-1 ${isInProgress || isResolved ? 'text-blue-700' : 'text-slate-500'}`}>
                              Crew Assigned
                            </span>
                            <span className="text-[9px] text-slate-400">
                              {c.assigned_employee_id || 'Queued'}
                            </span>
                          </div>

                          {/* Step 4 */}
                          <div className="flex flex-col items-center">
                            <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs shadow-xs ${
                              isResolved ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'
                            }`}>
                              {isResolved ? '✓' : '4'}
                            </div>
                            <span className={`font-bold mt-1 ${isResolved ? 'text-emerald-700' : 'text-slate-500'}`}>
                              Repair Resolved
                            </span>
                            <span className="text-[9px] text-slate-400">
                              {isResolved ? 'Proof Verified' : 'Pending'}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Track Button & Details Trigger */}
                      <div className="flex items-center justify-between pt-2">
                        <div className="text-xs text-slate-500">
                          SLA Window: <strong className="text-amber-700">{c.municipal_sla || '24 - 48 Hours'}</strong>
                        </div>

                        <div className="flex items-center gap-2">
                          <Link
                            to={`/complaint/${c.id}`}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-slate-700 hover:text-teal-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition"
                          >
                            <FileText size={13} />
                            <span>Detail Page</span>
                          </Link>
                          <button
                            type="button"
                            onClick={() => setSelectedComplaint(c)}
                            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold text-teal-700 hover:text-white bg-teal-50 hover:bg-teal-600 border border-teal-200 transition cursor-pointer"
                          >
                            <Eye size={13} />
                            <span>Track & Proof</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: CITIZEN INFORMATION & WARD MAPPING */}
        {activeTab === 'info' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-xs space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-black text-slate-900">
                    Citizen Information & Civic Jurisdiction
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Your municipal information is used by the NEXCIV AI engine to auto-populate your ward and route complaints to local AP municipal engineers.
                  </p>
                </div>

                {saveSuccess && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold animate-fade-in">
                    <CheckCircle2 size={14} />
                    <span>Saved!</span>
                  </span>
                )}
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">Full Legal Name</label>
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">Email Address</label>
                    <input
                      type="email"
                      disabled
                      value={email}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 text-xs cursor-not-allowed"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">Mobile Number (SMS Updates)</label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">Ward / Division</label>
                    <input
                      type="text"
                      value={ward}
                      onChange={(e) => setWard(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Residential Street Address</label>
                  <input
                    type="text"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <button
                    type="button"
                    onClick={handleGpsDetect}
                    disabled={detectingGps}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-teal-700 hover:text-teal-800 transition cursor-pointer"
                  >
                    <Navigation size={13} className={detectingGps ? 'animate-spin' : ''} />
                    <span>{detectingGps ? 'Detecting current ward...' : 'Detect location via GPS'}</span>
                  </button>

                  <button
                    type="submit"
                    disabled={saving}
                    className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-sm transition cursor-pointer"
                  >
                    <Save size={14} />
                    <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
                  </button>
                </div>
              </form>

              {/* Account Password & Security Card */}
              <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/90 shadow-xs space-y-4 mt-6">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center">
                      <Lock size={16} />
                    </div>
                    <div>
                      <h3 className="text-sm font-black text-slate-900">Account Password & Security</h3>
                      <p className="text-[11px] text-slate-500">Update your citizen login password with end-to-end encryption</p>
                    </div>
                  </div>
                </div>

                {passwordSuccess && (
                  <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold flex items-center gap-2">
                    <CheckCircle2 size={16} className="shrink-0" />
                    <span>{passwordSuccess}</span>
                  </div>
                )}

                {passwordError && (
                  <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
                    <AlertCircle size={16} className="shrink-0" />
                    <span>{passwordError}</span>
                  </div>
                )}

                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">New Password *</label>
                      <div className="relative">
                        <input
                          type={showNewPass ? 'text' : 'password'}
                          required
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Enter new password (min 4 chars)"
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowNewPass(!showNewPass)}
                          className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                          aria-label="Toggle password visibility"
                        >
                          {showNewPass ? <EyeOff size={15} /> : <Eye size={15} />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">Confirm New Password *</label>
                      <div className="relative">
                        <input
                          type={showConfirmPass ? 'text' : 'password'}
                          required
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Re-type new password"
                          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPass(!showConfirmPass)}
                          className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                          aria-label="Toggle password visibility"
                        >
                          {showConfirmPass ? <EyeOff size={15} /> : <Eye size={15} />}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <button
                      type="submit"
                      disabled={passwordUpdating}
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition cursor-pointer"
                    >
                      <KeyRound size={14} />
                      <span>{passwordUpdating ? 'Updating...' : 'Update Password'}</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Right Card: Citizen Trust & SLA Guarantee */}
            <div className="space-y-6">
              <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
                    <Sparkles size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-black text-slate-900">AI Fast-Track Citizen</h3>
                    <p className="text-[11px] text-slate-500">Multimodal verification active</p>
                  </div>
                </div>

                <div className="space-y-2.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Citizen Trust Level:</span>
                    <span className="font-bold text-emerald-600">High (Tier 1)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">AI Priority Boost:</span>
                    <span className="font-bold text-teal-700">1.25x Active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Resolution SLA:</span>
                    <span className="font-bold text-slate-800">4 hrs (Critical)</span>
                  </div>
                </div>
              </div>

              <Link
                to="/#report"
                className="w-full flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-teal-500 to-emerald-600 text-white font-bold text-xs shadow-md shadow-teal-500/20 hover:opacity-95 transition"
              >
                <div className="flex items-center gap-2.5">
                  <Building size={16} />
                  <span>Report a New Civic Issue</span>
                </div>
                <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        )}
      </main>

      {/* 4. MODAL: DETAILED PROGRESS TRACKER & RESOLUTION PROOF */}
      {selectedComplaint && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl border border-slate-200 space-y-5 animate-scale-in">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold bg-teal-100 text-teal-800 px-2 py-0.5 rounded">
                  {selectedComplaint.id.length > 8 ? `NXC-${selectedComplaint.id.slice(0, 6).toUpperCase()}` : selectedComplaint.id}
                </span>
                <h3 className="text-sm font-bold text-slate-900">Live Civic Work Order Tracking</h3>
              </div>
              <button
                onClick={() => setSelectedComplaint(null)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-lg text-lg font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Complaint Header */}
            <div>
              <h2 className="text-base font-black text-slate-900">{selectedComplaint.title}</h2>
              <p className="text-xs text-slate-600 mt-1">{selectedComplaint.description}</p>
              <div className="flex items-center gap-3 text-xs text-slate-500 mt-2 flex-wrap">
                <span><strong>Corporation:</strong> {selectedComplaint.municipal_corporation || 'GVMC'}</span>
                <span><strong>Ward:</strong> {selectedComplaint.ward || 'Ward 12'}</span>
                <span><strong>Landmark:</strong> {selectedComplaint.landmark || selectedComplaint.location_address || 'Main Road'}</span>
              </div>
            </div>

            {/* Before Photo & Resolution Proof Card */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="border border-slate-200 rounded-xl p-3 bg-slate-50 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                  <Camera size={13} className="text-red-600" />
                  <span>Citizen Damage Photo (Before)</span>
                </div>
                {selectedComplaint.image_url || (selectedComplaint.images && selectedComplaint.images.length > 0) ? (
                  <img
                    src={selectedComplaint.image_url || selectedComplaint.images?.[0]}
                    alt="Damage proof"
                    className="w-full h-36 object-cover rounded-lg border border-slate-200"
                  />
                ) : (
                  <div className="w-full h-36 bg-slate-200 rounded-lg flex items-center justify-center text-xs text-slate-500">
                    No photo uploaded
                  </div>
                )}
                {selectedComplaint.defect_type && (
                  <div className="text-[11px] text-slate-600">
                    AI Defect: <strong className="text-teal-700">{selectedComplaint.defect_type.replace(/_/g, ' ')}</strong>
                  </div>
                )}
              </div>

              <div className="border border-slate-200 rounded-xl p-3 bg-emerald-50/50 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800">
                  <Wrench size={13} className="text-emerald-600" />
                  <span>Crew Resolution Proof (After)</span>
                </div>
                {selectedComplaint.resolution_proof_url ? (
                  <img
                    src={selectedComplaint.resolution_proof_url}
                    alt="Resolution proof"
                    className="w-full h-36 object-cover rounded-lg border border-emerald-300"
                  />
                ) : (
                  <div className="w-full h-36 bg-slate-100 rounded-lg flex flex-col items-center justify-center text-xs text-slate-400 p-2 text-center">
                    <Clock size={20} className="mb-1 text-slate-400" />
                    <span>Resolution proof photo will be uploaded by the assigned engineer upon work completion.</span>
                  </div>
                )}
                {selectedComplaint.resolution_notes && (
                  <div className="text-[11px] text-emerald-900 bg-white p-2 rounded border border-emerald-200">
                    <strong>Engineer Completion Log:</strong> {selectedComplaint.resolution_notes}
                  </div>
                )}
                {selectedComplaint.resolution_proof_url && (
                  <div className="text-[10px] bg-emerald-100/70 border border-emerald-300 text-emerald-900 p-2 rounded-lg space-y-1">
                    <div className="font-bold flex items-center justify-between">
                      <span className="flex items-center gap-1">
                        <Sparkles size={11} className="text-emerald-700" />
                        <span>Phase 3 AI Computer Vision Audit</span>
                      </span>
                      <span className="bg-emerald-600 text-white px-2 py-0.5 rounded font-black text-[9px]">
                        Verified
                      </span>
                    </div>
                    <p className="text-[10px] text-emerald-800">
                      Automated visual analysis confirms surface restoration and defect clearance meeting AP municipal standards.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Officer Assignment Info */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-800">
                <span>Assigned Field Officer:</span>
                <span className="text-teal-700 font-mono">{selectedComplaint.assigned_employee_id || 'Queued for Dispatch'}</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Assigned Response Squad:</span>
                <span>{selectedComplaint.assigned_team || 'Municipal Rapid Response Squad'}</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span>Mandated SLA Target:</span>
                <span className="font-semibold text-amber-700">{selectedComplaint.municipal_sla || '24 - 48 Hours'}</span>
              </div>
            </div>

            <div className="flex gap-2">
              <Link
                to={`/complaint/${selectedComplaint.id}`}
                className="flex-1 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs rounded-xl transition text-center flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Eye size={14} />
                <span>Open Dedicated Detail Page</span>
              </Link>
              <button
                onClick={() => setSelectedComplaint(null)}
                className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="bg-[#0e2238] text-white py-6 border-t border-slate-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-400">
          <p>© 2026 NEXCIV — Intelligent Civic Grievance Management System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
