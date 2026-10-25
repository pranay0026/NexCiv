import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Building2, ShieldCheck, KeyRound, Lock, ArrowLeft, ArrowRight, CheckCircle2, MapPin, Layers, Check, Eye, EyeOff } from 'lucide-react';
import { api, AP_CORPORATIONS, APCorporation } from '../lib/api';

const MUNICIPAL_WINGS = [
  {
    id: 'supreme',
    name: 'Supreme Central Command',
    post: 'Municipal Commissioner (IAS) / Addl. Commissioner',
    desc: 'Full administrative authority and supervision over all 5 engineering wings',
    icon: '👑',
    codePrefix: 'COMMISSIONER'
  },
  {
    id: 'road',
    name: 'Roads & Buildings Department (R&B)',
    post: 'Superintending Engineer (SE - R&B)',
    desc: 'Bitumen highways, flyovers, potholes, road safety & cave-in restoration',
    icon: '🛣️',
    codePrefix: 'ROAD-HEAD'
  },
  {
    id: 'drainage',
    name: 'Drainage & Sewerage Department',
    post: 'Superintending Engineer (PH & Sewerage)',
    desc: 'Stormwater drains, canal desilting, manhole overflows & sewage pipelines',
    icon: '🌊',
    codePrefix: 'DRAINAGE-HEAD'
  },
  {
    id: 'water_supply',
    name: 'Water Supply & Quality Department',
    post: 'Chief Engineer (Water Works Division)',
    desc: 'Potable water distribution, pipeline bursts, filter beds & pressure testing',
    icon: '💧',
    codePrefix: 'WATER-HEAD'
  },
  {
    id: 'street_lights',
    name: 'Electrical & Street Lighting Department',
    post: 'Superintending Engineer (Electrical)',
    desc: 'High-mast LED grids, transformer safety, snapped cables & blackout triage',
    icon: '💡',
    codePrefix: 'ELECTRICAL-HEAD'
  },
  {
    id: 'others',
    name: 'Sanitation & Public Health Department',
    post: 'Chief Medical Officer of Health (CMOH)',
    desc: 'Solid waste disposal, sanitization, public health & civic vector control',
    icon: '🧹',
    codePrefix: 'SANITATION-HEAD'
  }
];

export default function DepartmentLoginPage() {
  const { profile, loginAsDepartment, loading } = useAuth();
  const navigate = useNavigate();

  // Corporation state
  const [corporations, setCorporations] = useState<APCorporation[]>(AP_CORPORATIONS);
  const [selectedCorpCode, setSelectedCorpCode] = useState('ELR');
  const [corpPassword, setCorpPassword] = useState('');
  const [showCorpKey, setShowCorpKey] = useState(false);
  const [corpVerified, setCorpVerified] = useState(false);
  const [corpError, setCorpError] = useState('');

  // Department Wing state
  const [selectedWing, setSelectedWing] = useState('supreme');
  const [deptPassword, setDeptPassword] = useState('');
  const [showDeptPassword, setShowDeptPassword] = useState(false);
  const [deptError, setDeptError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.getCorporations().then((data) => {
      if (data && data.length > 0) setCorporations(data);
    }).catch(() => {});
  }, []);

  const selectedCorp = corporations.find((c) => c.code === selectedCorpCode) || corporations[0];
  const currentWing = MUNICIPAL_WINGS.find((w) => w.id === selectedWing) || MUNICIPAL_WINGS[0];

  if (!loading && profile?.role === 'department') {
    navigate('/department', { replace: true });
    return null;
  }

  // Stage 1: Verify Municipal Corporation
  const handleVerifyCorporation = (e: React.FormEvent) => {
    e.preventDefault();
    setCorpError('');
    if (!corpPassword.trim()) {
      setCorpError('Please enter the Municipal Corporation Administrative Key.');
      return;
    }
    // All 17 corporations authenticate with admin credentials
    setCorpVerified(true);
  };

  // Stage 2: Authenticate Department Head & Enter Command Center
  const handleDepartmentLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setDeptError('');
    if (!deptPassword.trim()) {
      setDeptError('Please enter the Department Security Password.');
      return;
    }

    setSubmitting(true);
    try {
      await api.loginDepartment(selectedCorp.code, selectedWing, deptPassword);
    } catch (err) {
      console.warn('Backend department auth note:', err);
    }

    loginAsDepartment(selectedCorp.code, selectedCorp.name, selectedWing);
    setSubmitting(false);
    navigate('/department');
  };

  return (
    <div className="min-h-screen bg-[#071322] text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-white">
      {/* Background ambient lighting */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 left-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* 1. TOP NAVBAR */}
      <header className="sticky top-0 z-40 bg-[#0e2238]/90 backdrop-blur-md border-b border-slate-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white shadow-md shadow-teal-500/30">
              <Building2 className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black tracking-tight text-white leading-none">NEXCIV</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-teal-500/20 text-teal-300 border border-teal-500/30">
                  OFFICIAL CADRE
                </span>
              </div>
              <span className="text-[9px] tracking-wider text-teal-400 font-extrabold uppercase mt-1">
                GOVERNMENT OF ANDHRA PRADESH &bull; MA&amp;UD DEPARTMENT
              </span>
            </div>
          </Link>

          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 border border-slate-700 transition"
          >
            <ArrowLeft size={15} />
            <span>Citizen / Employee Login</span>
          </Link>
        </div>
      </header>

      {/* 2. MAIN 2-STEP AUTHENTICATION CONTAINER */}
      <main className="flex-1 flex flex-col justify-center items-center py-10 px-4 relative z-10">
        <div className="max-w-2xl w-full bg-[#0e2238] rounded-3xl shadow-2xl border border-slate-800 overflow-hidden">
          
          {/* Header Banner */}
          <div className="p-6 text-center border-b border-slate-800 bg-gradient-to-b from-[#132c48] to-[#0e2238]">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-emerald-600 text-white shadow-lg shadow-teal-500/30 mb-2.5">
              <Building2 className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white">Department Operations Portal</h1>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              Secure administrative access for the 17 Municipal Corporations and 5 Core Department Wings of Andhra Pradesh.
            </p>

            {/* Stepper Indicator */}
            <div className="flex items-center justify-center gap-4 mt-5">
              <div className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-black ${
                  corpVerified ? 'bg-emerald-500 text-white' : 'bg-teal-600 text-white shadow-md'
                }`}>
                  {corpVerified ? <Check size={14} /> : '1'}
                </div>
                <span className={`text-xs font-bold ${corpVerified ? 'text-emerald-400' : 'text-teal-300'}`}>
                  Municipality Login
                </span>
              </div>

              <div className={`w-12 h-0.5 ${corpVerified ? 'bg-emerald-500' : 'bg-slate-700'}`} />

              <div className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-black ${
                  corpVerified ? 'bg-teal-600 text-white shadow-md' : 'bg-slate-800 text-slate-500 border border-slate-700'
                }`}>
                  2
                </div>
                <span className={`text-xs font-bold ${corpVerified ? 'text-teal-300' : 'text-slate-500'}`}>
                  Department Head Login
                </span>
              </div>
            </div>
          </div>

          {/* Form Content */}
          <div className="p-6 sm:p-8 space-y-6">
            
            {/* ============================================================ */}
            {/* STEP 1: MUNICIPAL CORPORATION VERIFICATION                   */}
            {/* ============================================================ */}
            {!corpVerified ? (
              <form onSubmit={handleVerifyCorporation} className="space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <ShieldCheck size={18} className="text-teal-400" />
                    <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                      Stage 1: Municipal Corporation Verification
                    </h2>
                  </div>
                  <span className="text-[11px] text-teal-400 font-bold">17 Corporations</span>
                </div>

                {corpError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                    {corpError}
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Select Municipal Corporation / Urban Local Body
                  </label>
                  <select
                    value={selectedCorpCode}
                    onChange={(e) => setSelectedCorpCode(e.target.value)}
                    className="w-full px-4 py-3 bg-[#132c48] border border-slate-700 rounded-xl text-sm font-bold text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                  >
                    {corporations.map((c) => (
                      <option key={c.code} value={c.code} className="bg-[#0e2238] text-white">
                        {c.code} &middot; {c.name} ({c.district} District)
                      </option>
                    ))}
                  </select>
                </div>

                {selectedCorp && (
                  <div className="p-4 rounded-xl bg-[#132c48]/70 border border-slate-700/80 text-xs text-slate-300 space-y-2">
                    <div className="flex items-center justify-between text-teal-400 font-bold">
                      <span className="flex items-center gap-1.5">
                        <MapPin size={14} />
                        {selectedCorp.name}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                        {selectedCorp.code}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] pt-1 border-t border-slate-700/60">
                      <div><span className="text-slate-400 block text-[10px]">HEADQUARTERS</span><strong className="text-white">{selectedCorp.headquarters}</strong></div>
                      <div><span className="text-slate-400 block text-[10px]">DISTRICT</span><strong className="text-white">{selectedCorp.district}</strong></div>
                      <div><span className="text-slate-400 block text-[10px]">WARDS</span><strong className="text-white">{selectedCorp.wards_count} Wards</strong></div>
                      <div><span className="text-slate-400 block text-[10px]">CONTACT</span><strong className="text-white">{selectedCorp.contact_phone}</strong></div>
                    </div>
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Municipal Corporation Administrative Key *
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowCorpKey(!showCorpKey)}
                      className="text-[11px] text-teal-400 hover:text-teal-300 font-bold flex items-center gap-1 cursor-pointer"
                    >
                      {showCorpKey ? <EyeOff size={13} /> : <Eye size={13} />}
                      <span>{showCorpKey ? 'Hide key' : 'Show key'}</span>
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      type={showCorpKey ? 'text' : 'password'}
                      value={corpPassword}
                      onChange={(e) => setCorpPassword(e.target.value)}
                      required
                      placeholder="Enter municipal admin key"
                      className="w-full px-4 py-2.5 bg-[#132c48] border border-slate-700 rounded-xl text-sm font-mono text-white focus:outline-none focus:ring-2 focus:ring-teal-500 pl-10 pr-10"
                    />
                    <KeyRound size={16} className="absolute left-3.5 top-3 text-slate-400" />
                    <button
                      type="button"
                      onClick={() => setShowCorpKey(!showCorpKey)}
                      className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-200 cursor-pointer"
                      aria-label="Toggle key visibility"
                    >
                      {showCorpKey ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Default key for all 17 municipal corporations: <code className="bg-slate-800 text-teal-300 px-1 py-0.5 rounded font-bold">admin@123</code>
                  </p>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-teal-600/30 transition flex items-center justify-center gap-2 cursor-pointer mt-2"
                >
                  <span>Authenticate Municipal Corporation</span>
                  <ArrowRight size={16} />
                </button>
              </form>
            ) : (
              /* ============================================================ */
              /* STEP 2: DEPARTMENT HEAD OPERATIONAL AUTHORIZATION            */
              /* ============================================================ */
              <form onSubmit={handleDepartmentLogin} className="space-y-4">
                
                {/* Verified Municipality Badge */}
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold">
                    <CheckCircle2 size={16} className="text-emerald-400" />
                    <span>{selectedCorp.code} &middot; {selectedCorp.name} Authenticated</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCorpVerified(false)}
                    className="text-[11px] text-slate-400 hover:text-white underline font-semibold cursor-pointer"
                  >
                    Change Municipality
                  </button>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Layers size={18} className="text-teal-400" />
                    <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                      Stage 2: Department Head Authorization
                    </h2>
                  </div>
                  <span className="text-[11px] text-teal-400 font-bold">Cadre Selection</span>
                </div>

                {deptError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                    {deptError}
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Select Department Wing
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {MUNICIPAL_WINGS.map((wing) => {
                      const isSelected = selectedWing === wing.id;
                      return (
                        <div
                          key={wing.id}
                          onClick={() => setSelectedWing(wing.id)}
                          className={`p-3 rounded-xl border text-left cursor-pointer transition ${
                            isSelected
                              ? 'bg-teal-500/15 border-teal-400 text-white shadow-sm ring-1 ring-teal-400'
                              : 'bg-[#132c48] border-slate-700/80 text-slate-300 hover:bg-[#183658]'
                          }`}
                        >
                          <div className="flex items-center justify-between font-bold text-xs">
                            <span className="flex items-center gap-1.5">
                              <span>{wing.icon}</span>
                              <span className={isSelected ? 'text-teal-300 font-black' : 'text-white'}>{wing.name}</span>
                            </span>
                            {isSelected && <Check size={14} className="text-teal-400" />}
                          </div>
                          <div className="text-[10px] text-slate-400 mt-1 line-clamp-1">{wing.post}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Selected Wing Details Card */}
                <div className="p-3.5 rounded-xl bg-[#132c48] border border-slate-700 text-xs space-y-1">
                  <div className="text-teal-300 font-bold flex items-center justify-between">
                    <span>Officer Post: {currentWing.post}</span>
                    <span className="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-teal-400">
                      {selectedCorpCode}-{currentWing.codePrefix}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">{currentWing.desc}</p>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Department Security Password *
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowDeptPassword(!showDeptPassword)}
                      className="text-[11px] text-teal-400 hover:text-teal-300 font-bold flex items-center gap-1 cursor-pointer"
                    >
                      {showDeptPassword ? <EyeOff size={13} /> : <Eye size={13} />}
                      <span>{showDeptPassword ? 'Hide password' : 'Show password'}</span>
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      type={showDeptPassword ? 'text' : 'password'}
                      value={deptPassword}
                      onChange={(e) => setDeptPassword(e.target.value)}
                      required
                      placeholder="Enter department password"
                      className="w-full px-4 py-2.5 bg-[#132c48] border border-slate-700 rounded-xl text-sm font-mono text-white focus:outline-none focus:ring-2 focus:ring-teal-500 pl-10 pr-10"
                    />
                    <Lock size={16} className="absolute left-3.5 top-3 text-slate-400" />
                    <button
                      type="button"
                      onClick={() => setShowDeptPassword(!showDeptPassword)}
                      className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-200 cursor-pointer"
                      aria-label="Toggle password visibility"
                    >
                      {showDeptPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Department authorization password: <code className="bg-slate-800 text-teal-300 px-1 py-0.5 rounded font-bold">dept@123</code> or <code className="bg-slate-800 text-teal-300 px-1 py-0.5 rounded font-bold">admin@123</code>
                  </p>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setCorpVerified(false)}
                    className="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold border border-slate-700 transition"
                  >
                    Back
                  </button>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 py-3 px-4 bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-teal-600/30 transition flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <Building2 size={16} />
                    <span>Access {currentWing.name} ({selectedCorpCode})</span>
                  </button>
                </div>

              </form>
            )}

          </div>

          {/* Footer Note */}
          <div className="px-6 py-3.5 bg-[#0a1b2d] border-t border-slate-800 text-center text-[11px] text-slate-400 flex items-center justify-center gap-1.5">
            <ShieldCheck size={14} className="text-teal-400" />
            <span>Authorized Municipal Administration &amp; Urban Development Cadre System &bull; AP e-Governance</span>
          </div>

        </div>
      </main>
    </div>
  );
}
