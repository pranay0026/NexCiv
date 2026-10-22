import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api, ComplaintRecord } from '../lib/api';
import {
  ArrowLeft,
  Copy,
  Check,
  Clock,
  MapPin,
  Camera,
  BrainCircuit,
  Building2,
  ThumbsUp,
  Printer,
  ShieldCheck,
  AlertTriangle,
  Loader2
} from 'lucide-react';

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<ComplaintRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [upvoted, setUpvoted] = useState(false);
  const [upvotesCount, setUpvotesCount] = useState<number>(1);
  const [upvoting, setUpvoting] = useState(false);

  useEffect(() => {
    if (!id) {
      setError('Invalid Complaint ID');
      setLoading(false);
      return;
    }

    setLoading(true);
    api.getComplaint(id)
      .then((data) => {
        if (data) {
          setComplaint(data);
          setUpvotesCount(data.upvote_count || 1);
        } else {
          setError(`Complaint ${id} could not be located in the municipal records.`);
        }
      })
      .catch((err) => {
        console.warn('Complaint fetch error:', err);
        setError(err.message || `Complaint ${id} not found.`);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleCopyId = () => {
    if (!complaint) return;
    const code = complaint.id.length > 8 ? `NXC-${complaint.id.slice(0, 6).toUpperCase()}` : complaint.id;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleUpvote = async () => {
    if (!complaint || upvoted || upvoting) return;
    setUpvoting(true);
    try {
      const res = await api.upvoteComplaint(complaint.id);
      if (res && res.upvote_count !== undefined) {
        setUpvotesCount(res.upvote_count);
      } else {
        setUpvotesCount((prev) => prev + 1);
      }
      setUpvoted(true);
    } catch (err) {
      console.warn('Upvote error:', err);
      setUpvotesCount((prev) => prev + 1);
      setUpvoted(true);
    } finally {
      setUpvoting(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-4">
        <Loader2 size={36} className="text-teal-600 animate-spin mb-3" />
        <h2 className="text-base font-bold text-slate-800">Fetching Municipal Grievance Dossier...</h2>
        <p className="text-xs text-slate-500 mt-1">Connecting to Andhra Pradesh Cadre Central Database</p>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4 border border-rose-200">
          <AlertTriangle size={32} />
        </div>
        <h2 className="text-xl font-black text-slate-900">Grievance Ticket Not Found</h2>
        <p className="text-xs text-slate-600 mt-2 max-w-md">
          {error || `We could not retrieve complaint "${id}". It may still be syncing to the database.`}
        </p>
        <div className="flex gap-3 mt-6">
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
          >
            &larr; Go Back
          </button>
          <Link
            to="/"
            className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
          >
            Public Home Portal
          </Link>
        </div>
      </div>
    );
  }

  const shortCode = complaint.id.length > 8 ? `NXC-${complaint.id.slice(0, 6).toUpperCase()}` : complaint.id;
  const isResolved = (complaint.status as string)?.toLowerCase() === 'resolved';
  const isInProgress = (complaint.status as string)?.toLowerCase() === 'in_progress';
  const isAssigned = !!complaint.assigned_employee_id || !!complaint.assigned_team || isInProgress || isResolved;

  const priorityScore = complaint.priority_score ?? (complaint.priority?.toLowerCase() === 'critical' ? 95 : complaint.priority?.toLowerCase() === 'high' ? 75 : 50);

  // Photos list
  const photos: string[] = complaint.images && complaint.images.length > 0
    ? complaint.images
    : complaint.image_url
    ? [complaint.image_url]
    : complaint.image_data
    ? [complaint.image_data]
    : [];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col font-sans selection:bg-teal-500 selection:text-white print:bg-white print:p-0">
      
      {/* 1. TOP NAVBAR */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-2xs print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition cursor-pointer"
              title="Go back"
            >
              <ArrowLeft size={16} />
            </button>
            <div className="flex flex-col">
              <span className="text-xs font-extrabold text-slate-900 leading-tight">
                Public Grievance Dossier
              </span>
              <span className="text-[10px] text-teal-600 font-bold uppercase tracking-wider">
                {complaint.municipal_corporation || 'GVMC'} Municipal Corporation
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border border-slate-200 transition cursor-pointer"
              title="Print official receipt"
            >
              <Printer size={13} />
              <span className="hidden sm:inline">Print Receipt</span>
            </button>
            <Link
              to="/profile"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-2xs"
            >
              <span>My Grievances</span>
            </Link>
          </div>
        </div>
      </header>

      {/* 2. MAIN DOSSIER CONTAINER */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* TICKET HEADER CARD */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Grievance Tracking Ticket
                </span>
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold uppercase tracking-wider flex items-center gap-1.5 ${
                  isResolved
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : isInProgress
                    ? 'bg-blue-100 text-blue-800 border border-blue-300'
                    : 'bg-amber-100 text-amber-800 border border-amber-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${isResolved ? 'bg-emerald-500' : isInProgress ? 'bg-blue-500 animate-pulse' : 'bg-amber-500'}`} />
                  {isResolved ? 'Resolved & Verified' : isInProgress ? 'Field Crew Deployed' : 'Registered & Queued'}
                </span>
              </div>

              <div className="flex items-center gap-3 mt-1.5">
                <h1 className="text-2xl sm:text-3xl font-mono font-black text-slate-900 tracking-tight">
                  {shortCode}
                </h1>
                <button
                  onClick={handleCopyId}
                  className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition cursor-pointer"
                  title="Copy Tracking ID"
                >
                  {copied ? <Check size={15} className="text-emerald-600" /> : <Copy size={15} />}
                </button>
                {copied && <span className="text-[11px] text-emerald-600 font-bold">Copied!</span>}
              </div>

              <p className="text-sm font-semibold text-slate-700 mt-2 max-w-2xl leading-relaxed">
                {complaint.title}
              </p>
            </div>

            {/* Endorse / Upvote Action */}
            <div className="shrink-0 flex sm:flex-col items-center sm:items-end justify-between gap-2 bg-slate-50 p-3 sm:p-4 rounded-2xl border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Citizen Endorsements
              </span>
              <button
                type="button"
                onClick={handleUpvote}
                disabled={upvoted || upvoting}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer ${
                  upvoted
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white hover:bg-teal-50 text-slate-800 hover:text-teal-700 border border-slate-200'
                }`}
              >
                <ThumbsUp size={14} className={upvoted ? 'text-white' : 'text-teal-600'} />
                <span>{upvoted ? 'Endorsed' : 'Upvote Issue'}</span>
                <span className="px-1.5 py-0.5 rounded bg-black/10 font-mono font-black text-[11px]">
                  {upvotesCount}
                </span>
              </button>
            </div>
          </div>

          {/* 4 KEY METRIC TILES */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-6 text-xs">
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">AI Priority Score</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className={`text-xl font-black ${
                  priorityScore >= 75 ? 'text-rose-600' : priorityScore >= 50 ? 'text-amber-600' : 'text-teal-600'
                }`}>
                  {Math.round(priorityScore)}/100
                </span>
                <span className="text-[10px] font-bold text-slate-500">({complaint.priority || 'Medium'})</span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Department Wing</span>
              <div className="text-sm font-bold text-slate-900 mt-1 truncate">
                {complaint.department || 'Roads & Buildings'}
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Resolution SLA</span>
              <div className="text-sm font-bold text-rose-700 mt-1 truncate">
                {complaint.municipal_sla || '24 - 48 Hours'}
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Municipality &amp; Ward</span>
              <div className="text-sm font-bold text-teal-800 mt-1 truncate">
                {complaint.municipal_corporation || 'GVMC'} {complaint.ward ? `&bull; Ward ${complaint.ward}` : ''}
              </div>
            </div>
          </div>
        </div>

        {/* 4-STAGE LIVE RESOLUTION PIPELINE */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Clock size={18} className="text-teal-600" />
              <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider">
                Live Resolution Milestones
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-medium">Stage Tracker</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-2">
            {/* Stage 1 */}
            <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 flex flex-col justify-between">
              <div>
                <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-black text-xs shadow-xs mb-2">
                  ✓
                </div>
                <div className="font-bold text-slate-900 text-xs">1. Grievance Filed</div>
                <p className="text-[11px] text-slate-500 mt-0.5">Citizen logged issue with geotagged evidence</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-800 mt-3 font-semibold">
                {new Date(complaint.created_at).toLocaleDateString()}
              </span>
            </div>

            {/* Stage 2 */}
            <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 flex flex-col justify-between">
              <div>
                <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-black text-xs shadow-xs mb-2">
                  ✓
                </div>
                <div className="font-bold text-slate-900 text-xs">2. AI Triaged &amp; Scored</div>
                <p className="text-[11px] text-slate-500 mt-0.5">Automated NLP &amp; CV priority ({Math.round(priorityScore)}/100)</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-800 mt-3 font-semibold">
                {complaint.municipal_sla || 'Automated SLA'}
              </span>
            </div>

            {/* Stage 3 */}
            <div className={`p-4 rounded-2xl border flex flex-col justify-between ${
              isAssigned ? 'bg-blue-50/60 border-blue-200' : 'bg-slate-50 border-slate-200'
            }`}>
              <div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-xs shadow-xs mb-2 ${
                  isAssigned ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'
                }`}>
                  {isAssigned ? '✓' : '3'}
                </div>
                <div className={`font-bold text-xs ${isAssigned ? 'text-slate-900' : 'text-slate-500'}`}>
                  3. Crew Dispatched
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  {complaint.assigned_employee_id ? `Assigned to ${complaint.assigned_employee_id}` : complaint.assigned_team || 'Awaiting field assignment'}
                </p>
              </div>
              <span className={`text-[10px] font-mono mt-3 font-semibold ${isAssigned ? 'text-blue-800' : 'text-slate-400'}`}>
                {isAssigned ? 'Active Field Work' : 'Queued'}
              </span>
            </div>

            {/* Stage 4 */}
            <div className={`p-4 rounded-2xl border flex flex-col justify-between ${
              isResolved ? 'bg-emerald-50/60 border-emerald-200' : 'bg-slate-50 border-slate-200'
            }`}>
              <div>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-xs shadow-xs mb-2 ${
                  isResolved ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-400'
                }`}>
                  {isResolved ? '✓' : '4'}
                </div>
                <div className={`font-bold text-xs ${isResolved ? 'text-slate-900' : 'text-slate-500'}`}>
                  4. Proof Verified
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  {isResolved ? 'Field repair completed and verified' : 'Pending resolution proof'}
                </p>
              </div>
              <span className={`text-[10px] font-mono mt-3 font-semibold ${isResolved ? 'text-emerald-800' : 'text-slate-400'}`}>
                {isResolved ? 'Certified Complete' : 'In Progress'}
              </span>
            </div>
          </div>
        </div>

        {/* ISSUE DETAILS & LOCATION */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Detailed Description */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-3">
            <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
              <BrainCircuit size={16} className="text-teal-600" />
              <span>Grievance Description &amp; Details</span>
            </h3>
            <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-100 whitespace-pre-wrap">
              {complaint.description}
            </p>

            <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 pt-2">
              <div>
                <span className="text-slate-400 block text-[10px] font-bold">CITIZEN NAME</span>
                <strong>{complaint.citizen_name || 'Anonymous Citizen'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] font-bold">CONTACT PHONE</span>
                <strong>{complaint.citizen_phone || '+91 ••••• •••••'}</strong>
              </div>
            </div>
          </div>

          {/* Location & GPS */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-3">
            <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
              <MapPin size={16} className="text-teal-600" />
              <span>Location &amp; Geocoding</span>
            </h3>

            <div className="space-y-2 bg-slate-50 p-4 rounded-2xl border border-slate-100 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] font-bold">STREET ADDRESS</span>
                <strong className="text-slate-900">{complaint.location_address || 'Address provided on filing'}</strong>
              </div>
              {complaint.landmark && (
                <div>
                  <span className="text-slate-400 block text-[10px] font-bold">SPECIFIC LANDMARK</span>
                  <strong className="text-teal-700">{complaint.landmark}</strong>
                </div>
              )}
              {complaint.location_lat && complaint.location_lng && (
                <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                  <span className="text-slate-500 font-mono">
                    GPS: {complaint.location_lat.toFixed(4)}, {complaint.location_lng.toFixed(4)}
                  </span>
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${complaint.location_lat},${complaint.location_lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-teal-600 hover:text-teal-700 font-bold underline"
                  >
                    View on Map &rarr;
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* PHOTO EVIDENCE GALLERY */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Camera size={18} className="text-teal-600" />
              <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider">
                Photo Evidence ({photos.length} Photos)
              </h3>
            </div>
            {complaint.defect_type && (
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-teal-50 text-teal-800 border border-teal-200">
                CV Tag: {complaint.defect_type.replace('_', ' ')}
              </span>
            )}
          </div>

          {photos.length === 0 ? (
            <div className="p-8 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
              <Camera size={28} className="mx-auto text-slate-300 mb-2" />
              <p className="text-xs font-semibold">No direct photo evidence uploaded</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {photos.map((img, idx) => (
                <div key={idx} className="rounded-2xl overflow-hidden border border-slate-200 shadow-2xs group relative">
                  <img
                    src={img}
                    alt={`Evidence ${idx + 1}`}
                    className="w-full h-48 object-cover group-hover:scale-105 transition duration-300"
                  />
                  <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-black/60 text-white text-[10px] font-bold">
                    Citizen Photo #{idx + 1}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* OFFICIAL RESOLUTION DOSSIER (IF RESOLVED OR IN PROGRESS) */}
        {(isResolved || complaint.resolution_notes || complaint.resolution_proof_url) && (
          <div className="bg-gradient-to-r from-emerald-50/50 to-teal-50/50 rounded-3xl p-6 sm:p-8 border border-emerald-200 shadow-xs space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-emerald-200">
              <ShieldCheck size={20} className="text-emerald-600" />
              <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider">
                Field Engineer Resolution Dossier
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <div className="space-y-3">
                <div className="text-xs text-slate-600">
                  <span className="font-bold text-slate-800 block text-xs">Official Completion Remarks:</span>
                  <p className="mt-1 bg-white p-3.5 rounded-xl border border-emerald-200 text-slate-700 italic">
                    "{complaint.resolution_notes || 'Field repair successfully carried out and verified under municipal cadre standards.'}"
                  </p>
                </div>

                <div className="text-xs text-slate-600">
                  <span className="font-bold text-slate-800">Resolved By Staff:</span>{' '}
                  <span className="text-teal-800 font-bold">{complaint.assigned_employee_id || 'AP Field Engineer'}</span>
                </div>
              </div>

              {complaint.resolution_proof_url && (
                <div>
                  <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block mb-1">
                    Verified Resolution Proof Photo
                  </span>
                  <div className="rounded-2xl overflow-hidden border-2 border-emerald-400 shadow-md">
                    <img
                      src={complaint.resolution_proof_url}
                      alt="Work completed proof"
                      className="w-full h-48 object-cover"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* OFFICIAL AP GOVERNMENT SEAL FOOTER */}
        <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-center text-xs text-slate-500 space-y-1">
          <div className="flex items-center justify-center gap-1.5 font-bold text-slate-700">
            <Building2 size={14} className="text-teal-600" />
            <span>Government of Andhra Pradesh &bull; Municipal Administration &amp; Urban Development</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Ticket ID: <span className="font-mono font-bold text-slate-600">{shortCode}</span> &bull; Recorded in Central Citizen Grievance Registry
          </p>
        </div>

      </main>
    </div>
  );
}
