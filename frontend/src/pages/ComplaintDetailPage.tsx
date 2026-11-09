import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  api,
  ComplaintRecord,
  ActivityLogRecord,
  AcknowledgementReceiptData
} from '../lib/api';
import {
  ArrowLeft,
  Copy,
  Check,
  MapPin,
  Camera,
  BrainCircuit,
  Building2,
  ThumbsUp,
  AlertTriangle,
  Loader2,
  Scale,
  RotateCcw,
  Star,
  FileCheck2,
  Download
} from 'lucide-react';
import AcknowledgementReceiptModal from '../components/AcknowledgementReceiptModal';
import GrievanceTrackingTimeline from '../components/GrievanceTrackingTimeline';
import CitizenFeedbackModal from '../components/CitizenFeedbackModal';
import StatutoryAppealModal from '../components/StatutoryAppealModal';
import RtiVsGrievanceNotice from '../components/RtiVsGrievanceNotice';

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<ComplaintRecord | null>(null);
  const [timelineLogs, setTimelineLogs] = useState<ActivityLogRecord[]>([]);
  const [receiptData, setReceiptData] = useState<AcknowledgementReceiptData | null>(null);

  const [loading, setLoading] = useState(true);
  const [logsLoading, setLogsLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [upvoted, setUpvoted] = useState(false);
  const [upvotesCount, setUpvotesCount] = useState<number>(1);
  const [upvoting, setUpvoting] = useState(false);

  // Modals
  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [appealModalOpen, setAppealModalOpen] = useState(false);

  const fetchComplaintData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.getComplaint(id);
      if (data) {
        setComplaint(data);
        setUpvotesCount(data.upvote_count || 1);
      } else {
        setError(`Complaint ${id} could not be located in the municipal records.`);
      }
    } catch (err: any) {
      console.warn('Complaint fetch error:', err);
      setError(err.message || `Complaint ${id} not found.`);
    } finally {
      setLoading(false);
    }
  };

  const fetchTimelineData = async () => {
    if (!id) return;
    try {
      setLogsLoading(true);
      const logs = await api.getActivityLogs(id);
      setTimelineLogs(logs);
    } catch (err) {
      console.warn('Timeline fetch error:', err);
    } finally {
      setLogsLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaintData();
    fetchTimelineData();
  }, [id]);

  const handleOpenReceipt = async () => {
    if (!complaint) return;
    try {
      const receipt = await api.getAcknowledgementReceipt(complaint.id);
      setReceiptData(receipt);
      setReceiptModalOpen(true);
    } catch {
      // Fallback using current complaint record
      const ref = complaint.grievance_ref_number || `AP-${complaint.municipal_corporation || 'GVMC'}-2026-NXC${complaint.id.slice(0, 4).toUpperCase()}`;
      setReceiptData({
        grievance_ref_number: ref,
        complaint_id: complaint.id,
        title: complaint.title,
        citizen_name: complaint.citizen_name || 'Public Citizen',
        citizen_email: complaint.citizen_email,
        citizen_phone: complaint.citizen_phone,
        submission_time: complaint.created_at,
        department: complaint.department || 'Municipal Services',
        department_code: complaint.department_code || 'others',
        category: complaint.category,
        workflow_type: complaint.workflow_type || 'ordinary_grievance',
        legal_source: complaint.legal_source || 'AP Municipal Citizen Charter & PGRS Guidelines',
        go_reference: 'Standing Order No. 118',
        designated_officer: complaint.designated_officer || 'Municipal Field Engineer',
        expected_resolution_date: complaint.expected_resolution_date || complaint.deadline_formatted || 'Within 7 Working Days',
        timeline_calculation_method: 'working_days',
        current_status: complaint.status,
        first_appellate_authority: complaint.appellate_authority || 'Superintending Engineer / Commissioner',
        appeal_deadline_days: complaint.workflow_type === 'notified_service' ? 30 : 15,
        compensation_applicable: complaint.workflow_type === 'notified_service'
      });
      setReceiptModalOpen(true);
    }
  };

  const handleCopyId = () => {
    if (!complaint) return;
    const code = complaint.grievance_ref_number || (complaint.id.length > 8 ? `NXC-${complaint.id.slice(0, 6).toUpperCase()}` : complaint.id);
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
    } catch {
      setUpvotesCount((prev) => prev + 1);
      setUpvoted(true);
    } finally {
      setUpvoting(false);
    }
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
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition cursor-pointer"
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

  const refNumber = complaint.grievance_ref_number || (complaint.id.length > 8 ? `NXC-${complaint.id.slice(0, 6).toUpperCase()}` : complaint.id);
  const isResolved = (complaint.status as string)?.toLowerCase() === 'resolved';
  const isRejected = (complaint.status as string)?.toLowerCase() === 'rejected';
  const isInProgress = (complaint.status as string)?.toLowerCase() === 'in_progress';
  const isNotified = complaint.workflow_type === 'notified_service';
  const isOverdue = complaint.sla_is_overdue;

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
                Public Grievance Dossier &amp; Legal Compliance
              </span>
              <span className="text-[10px] text-teal-600 font-bold uppercase tracking-wider">
                {complaint.municipal_corporation || 'GVMC'} Municipal Corporation &bull; Andhra Pradesh
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleOpenReceipt}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 text-xs font-bold border border-teal-200 transition cursor-pointer"
              title="Official Acknowledgement Receipt"
            >
              <Download size={13} />
              <span className="hidden sm:inline">Acknowledgement Receipt</span>
            </button>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-2xs"
            >
              <span>Citizen Dashboard</span>
            </Link>
          </div>
        </div>
      </header>

      {/* 2. MAIN DOSSIER CONTAINER */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* TICKET HEADER CARD */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs relative overflow-hidden space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Unique Reference Code
                </span>
                
                {/* Workflow Classification Badge */}
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider flex items-center gap-1 ${
                  isNotified
                    ? 'bg-amber-100 text-amber-900 border border-amber-300'
                    : 'bg-teal-100 text-teal-900 border border-teal-300'
                }`}>
                  <Scale size={11} />
                  {isNotified ? 'Notified Public Service (Act 6 of 2018)' : 'Ordinary Civic Grievance (Citizen Charter)'}
                </span>

                {/* Status Badge */}
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider flex items-center gap-1.5 ${
                  isResolved
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : isRejected
                    ? 'bg-rose-100 text-rose-800 border border-rose-300'
                    : isInProgress
                    ? 'bg-blue-100 text-blue-800 border border-blue-300'
                    : 'bg-amber-100 text-amber-800 border border-amber-300'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${isResolved ? 'bg-emerald-500' : isRejected ? 'bg-rose-500' : isInProgress ? 'bg-blue-500 animate-pulse' : 'bg-amber-500'}`} />
                  {isResolved ? 'Resolved & Verified' : isRejected ? 'Rejected with Reasons' : isInProgress ? 'Field Crew Deployed' : 'Awaiting Assignment'}
                </span>
              </div>

              <div className="flex items-center gap-3 mt-2">
                <h1 className="text-2xl sm:text-3xl font-mono font-black text-slate-900 tracking-tight">
                  {refNumber}
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

            {/* Endorse & Quick Receipt */}
            <div className="shrink-0 flex sm:flex-col items-center sm:items-end justify-between gap-2.5 bg-slate-50 p-4 rounded-2xl border border-slate-100">
              <button
                type="button"
                onClick={handleOpenReceipt}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-xs cursor-pointer"
              >
                <Download size={13} />
                Download Receipt
              </button>
              
              <button
                type="button"
                onClick={handleUpvote}
                disabled={upvoted || upvoting}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold transition border cursor-pointer ${
                  upvoted
                    ? 'bg-emerald-600 text-white border-emerald-600'
                    : 'bg-white hover:bg-teal-50 text-slate-800 border-slate-200'
                }`}
              >
                <ThumbsUp size={13} className={upvoted ? 'text-white' : 'text-teal-600'} />
                <span>{upvoted ? 'Endorsed' : 'Upvote'}</span>
                <span className="font-mono font-black text-[11px]">{upvotesCount}</span>
              </button>
            </div>
          </div>

          {/* 4 STATUTORY & SLA METRIC TILES */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">AI Classification</span>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="text-xl font-black text-teal-600">
                  {complaint.confidence ? `${Math.round(complaint.confidence * 100)}% Match` : 'AI Routed'}
                </span>
                <span className="text-[10px] font-bold text-slate-500 uppercase">
                  ({complaint.category ? complaint.category.replace('_', ' ') : 'Civic Service'})
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Department Wing</span>
              <div className="text-sm font-bold text-slate-900 mt-1 truncate">
                {complaint.department || 'Roads & Buildings'}
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">Designated Officer</span>
              <div className="text-sm font-bold text-teal-800 mt-1 truncate">
                {complaint.designated_officer || 'Municipal Engineer'}
              </div>
            </div>

            <div className={`p-3.5 rounded-2xl border ${
              isOverdue && !isResolved
                ? 'bg-rose-50 border-rose-200 text-rose-900'
                : 'bg-slate-50 border-slate-100 text-slate-900'
            }`}>
              <span className="text-slate-400 block text-[10px] font-bold uppercase tracking-wider">
                {isOverdue && !isResolved ? 'Statutory SLA Overdue' : 'Statutory Redressal SLA'}
              </span>
              <div className="text-sm font-bold mt-1 truncate">
                {complaint.deadline_formatted || complaint.municipal_sla || 'Under Review'}
              </div>
            </div>
          </div>
        </div>

        {/* REASONED RESOLUTION OR REJECTION DOSSIER (Rule 4.4) */}
        {(isResolved || isRejected || complaint.action_taken || complaint.resolution_summary || complaint.rejection_reason) && (
          <div className={`rounded-3xl p-6 sm:p-8 border shadow-xs space-y-4 ${
            isRejected
              ? 'bg-rose-50/60 border-rose-200'
              : 'bg-gradient-to-r from-emerald-50/60 to-teal-50/60 border-emerald-200'
          }`}>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200/60">
              <div className="flex items-center gap-2">
                <FileCheck2 size={20} className={isRejected ? 'text-rose-600' : 'text-teal-600'} />
                <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider">
                  {isRejected ? 'Statutory Rejection Dossier (Section 8 Reasons)' : 'Official Reasoned Resolution Dossier'}
                </h3>
              </div>
              <span className="text-xs text-slate-500 font-bold">
                {complaint.resolved_at ? new Date(complaint.resolved_at).toLocaleDateString() : 'Disposed Record'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
              <div className="space-y-3">
                {isRejected ? (
                  <div>
                    <span className="font-bold text-rose-900 block mb-1 uppercase tracking-wider text-[10px]">
                      Recorded Reasons for Rejection / Inability:
                    </span>
                    <p className="bg-white p-3.5 rounded-xl border border-rose-200 text-slate-800 leading-relaxed font-semibold">
                      "{complaint.rejection_reason || complaint.resolution_notes || 'Grievance does not fall within municipal jurisdiction or requires private owner NOC.'}"
                    </p>
                  </div>
                ) : (
                  <>
                    <div>
                      <span className="font-bold text-slate-700 block mb-1 uppercase tracking-wider text-[10px]">
                        Department Action Taken:
                      </span>
                      <p className="bg-white p-3.5 rounded-xl border border-emerald-200 text-slate-800 leading-relaxed font-medium">
                        {complaint.action_taken || complaint.resolution_notes || 'Remediation completed according to departmental standards.'}
                      </p>
                    </div>

                    {complaint.resolution_summary && (
                      <div>
                        <span className="font-bold text-slate-700 block mb-1 uppercase tracking-wider text-[10px]">
                          Public Investigation Summary:
                        </span>
                        <p className="bg-white/80 p-3 rounded-xl border border-emerald-100 text-slate-700">
                          {complaint.resolution_summary}
                        </p>
                      </div>
                    )}
                  </>
                )}

                <div className="text-slate-500 text-[11px] pt-1">
                  <strong>Investigating Officer:</strong> {complaint.assigned_employee_id || 'Designated Municipal Engineer'} &bull; {complaint.department}
                </div>
              </div>

              {/* Resolution Proof Photo */}
              {complaint.resolution_proof_url && (
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                    Certified Resolution Proof Photo
                  </span>
                  <div className="rounded-2xl overflow-hidden border-2 border-emerald-300 shadow-md">
                    <img
                      src={complaint.resolution_proof_url}
                      alt="Work completed proof"
                      className="w-full h-44 object-cover"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Action Bar for Feedback, Reopening & Appeal */}
            <div className="pt-3 border-t border-slate-200/60 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => setFeedbackModalOpen(true)}
                className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer flex items-center gap-1.5"
              >
                <Star size={14} />
                Submit Citizen Feedback
              </button>
              
              <button
                type="button"
                onClick={() => setFeedbackModalOpen(true)}
                className="px-4 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5"
              >
                <RotateCcw size={14} className="text-rose-600" />
                Request Reopening
              </button>

              <button
                type="button"
                onClick={() => setAppealModalOpen(true)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5 ml-auto"
              >
                <Scale size={14} className="text-teal-400" />
                {isNotified ? 'File Statutory Appeal (Act 6 of 2018)' : 'Departmental Escalation'}
              </button>
            </div>
          </div>
        )}

        {/* CHRONOLOGICAL GRIEVANCE TRACKING TIMELINE (Rule 4.2) */}
        <GrievanceTrackingTimeline
          complaint={complaint}
          logs={timelineLogs}
          loading={logsLoading}
        />

        {/* ISSUE DETAILS & LOCATION */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Detailed Description */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-3 text-xs">
            <h3 className="font-extrabold text-slate-900 text-sm uppercase tracking-wider flex items-center gap-2">
              <BrainCircuit size={16} className="text-teal-600" />
              <span>Grievance Description &amp; Particulars</span>
            </h3>
            <p className="text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-100 whitespace-pre-wrap">
              {complaint.description}
            </p>

            <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 pt-2 border-t border-slate-100">
              <div>
                <span className="text-slate-400 block text-[10px] font-bold">CITIZEN NAME</span>
                <strong>{complaint.citizen_name || 'Public Citizen'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] font-bold">CONTACT PHONE</span>
                <strong>{complaint.citizen_phone || '+91 ••••• •••••'}</strong>
              </div>
            </div>
          </div>

          {/* Location & GPS */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-3 text-xs">
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

        {/* RTI VS GRIEVANCE SEPARATION SECTION (Rule 10) */}
        <RtiVsGrievanceNotice />

        {/* OFFICIAL AP GOVERNMENT SEAL FOOTER */}
        <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-center text-xs text-slate-500 space-y-1">
          <div className="flex items-center justify-center gap-1.5 font-bold text-slate-700">
            <Building2 size={14} className="text-teal-600" />
            <span>Government of Andhra Pradesh &bull; Municipal Administration &amp; Urban Development</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Reference: <span className="font-mono font-bold text-slate-600">{refNumber}</span> &bull; Recorded in Central Citizen Grievance Registry
          </p>
        </div>

      </main>

      {/* MODALS */}
      {receiptData && (
        <AcknowledgementReceiptModal
          receipt={receiptData}
          isOpen={receiptModalOpen}
          onClose={() => setReceiptModalOpen(false)}
        />
      )}

      <CitizenFeedbackModal
        complaintId={complaint.id}
        citizenName={complaint.citizen_name}
        isOpen={feedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
        onSuccess={() => {
          fetchComplaintData();
          fetchTimelineData();
        }}
      />

      <StatutoryAppealModal
        complaint={complaint}
        isOpen={appealModalOpen}
        onClose={() => setAppealModalOpen(false)}
        onSuccess={() => {
          fetchComplaintData();
          fetchTimelineData();
        }}
      />
    </div>
  );
}
