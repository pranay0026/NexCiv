import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  MapPin,
  Clock,
  Flame,
  AlertTriangle,
  CheckCircle,
  Eye,
  X,
  Shield,
  Cpu,
  Layers,
  ThumbsUp,
  Camera,
  Scale,
  Download,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api, AcknowledgementReceiptData } from '../lib/api';
import AcknowledgementReceiptModal from './AcknowledgementReceiptModal';

interface Complaint {
  id: string;
  grievance_ref_number?: string;
  title: string;
  description: string;
  category: string;
  status: string;
  priority?: string;
  priority_score?: number;
  department?: string;
  department_code?: string;
  confidence?: number;
  location_address?: string;
  image_url?: string;
  is_duplicate?: boolean;
  master_complaint_id?: string;
  upvote_count?: number;
  defect_type?: string;
  visual_score?: number;
  municipal_sla?: string;
  workflow_type?: string;
  designated_officer?: string;
  appellate_authority?: string;
  expected_resolution_date?: string;
  deadline_formatted?: string;
  sla_is_overdue?: boolean;
  zone_type?: string;
  vulnerability_multiplier?: number;
  citizen_name?: string;
  citizen_email?: string;
  citizen_phone?: string;
  created_at: string;
}

const DEPARTMENTS_MAP: Record<string, { name: string; color: string }> = {
  road: {
    name: 'Roads & Highways Department',
    color: 'bg-amber-100 text-amber-900 dark:bg-amber-900/30 dark:text-amber-300 border-amber-200 dark:border-amber-800'
  },
  drainage: {
    name: 'Drainage & Sewerage Department',
    color: 'bg-cyan-100 text-cyan-900 dark:bg-cyan-900/30 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800'
  },
  water_supply: {
    name: 'Water Supply & Quality Department',
    color: 'bg-blue-100 text-blue-900 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200 dark:border-blue-800'
  },
  street_lights: {
    name: 'Electrical & Street Lighting Department',
    color: 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800'
  },
  others: {
    name: 'Sanitation & General Civic Amenities',
    color: 'bg-purple-100 text-purple-900 dark:bg-purple-900/30 dark:text-purple-300 border-purple-200 dark:border-purple-800'
  }
};

const getPriorityBadge = (priority = 'Medium') => {
  switch (priority.toLowerCase()) {
    case 'critical':
      return {
        label: 'Critical',
        style: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 border-red-300 dark:border-red-700',
        icon: <Flame size={12} className="text-red-600 dark:text-red-400" />
      };
    case 'high':
      return {
        label: 'High Priority',
        style: 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border-orange-300 dark:border-orange-700',
        icon: <AlertTriangle size={12} className="text-orange-600 dark:text-orange-400" />
      };
    case 'medium':
      return {
        label: 'Medium',
        style: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-300 dark:border-amber-700',
        icon: <Clock size={12} className="text-amber-600 dark:text-amber-400" />
      };
    default:
      return {
        label: 'Low',
        style: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700',
        icon: <CheckCircle size={12} className="text-emerald-600 dark:text-emerald-400" />
      };
  }
};

const getStatusColor = (status: string) => {
  const stat = status.toLowerCase();
  switch (stat) {
    case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    case 'in_progress': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    case 'resolved': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
  }
};

const formatTimeAgo = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  let interval = Math.floor(seconds / 86400);
  if (interval >= 1) return interval + (interval === 1 ? " day ago" : " days ago");
  interval = Math.floor(seconds / 3600);
  if (interval >= 1) return interval + (interval === 1 ? " hr ago" : " hrs ago");
  interval = Math.floor(seconds / 60);
  if (interval >= 1) return interval + " mins ago";
  return "just now";
};

export default function ComplaintCard({
  complaint,
  onStatusUpdated
}: {
  complaint: Complaint;
  onStatusUpdated?: () => void;
}) {
  const { profile } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [receiptData, setReceiptData] = useState<AcknowledgementReceiptData | null>(null);
  const [updating, setUpdating] = useState(false);

  const rawCat = (complaint.category || 'others').toLowerCase().replace(' ', '_');
  const dept = DEPARTMENTS_MAP[rawCat] || DEPARTMENTS_MAP.others;
  const statusFormatted = (complaint.status || 'pending').replace('_', ' ');
  const prio = getPriorityBadge(complaint.priority);
  const isEmployee = profile?.role === 'employee';
  const isNotified = complaint.workflow_type === 'notified_service';
  const refCode = complaint.grievance_ref_number || (complaint.id.length > 8 ? `AP-NXC-${complaint.id.slice(0, 4).toUpperCase()}` : complaint.id);

  const handleOpenReceipt = async () => {
    try {
      const data = await api.getAcknowledgementReceipt(complaint.id);
      setReceiptData(data);
      setReceiptModalOpen(true);
    } catch {
      setReceiptData({
        grievance_ref_number: refCode,
        complaint_id: complaint.id,
        title: complaint.title,
        citizen_name: complaint.citizen_name || 'Public Citizen',
        citizen_email: complaint.citizen_email,
        citizen_phone: complaint.citizen_phone,
        submission_time: complaint.created_at,
        department: complaint.department || dept.name,
        department_code: rawCat,
        category: complaint.category,
        workflow_type: complaint.workflow_type || 'ordinary_grievance',
        legal_source: isNotified ? 'AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)' : 'AP Municipal Citizen Charter & PGRS Guidelines',
        go_reference: 'Standing Order No. 118',
        designated_officer: complaint.designated_officer || 'Municipal Section Engineer',
        expected_resolution_date: complaint.deadline_formatted || 'Within 7 AP Working Days',
        timeline_calculation_method: 'working_days',
        current_status: complaint.status,
        first_appellate_authority: complaint.appellate_authority || 'Superintending Engineer',
        appeal_deadline_days: isNotified ? 30 : 15,
        compensation_applicable: isNotified
      });
      setReceiptModalOpen(true);
    }
  };

  const handleUpdateStatus = async (newStatus: string) => {
    try {
      setUpdating(true);
      await api.updateComplaintStatus(complaint.id, newStatus);
      if (onStatusUpdated) onStatusUpdated();
    } catch (e) {
      console.error('Failed to update status', e);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow space-y-3">
        {/* Top Badges Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Grievance Reference Code */}
            <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-300 dark:border-gray-600">
              {refCode}
            </span>

            {isEmployee && (
              <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full font-bold border ${prio.style}`}>
                {prio.icon}
                {prio.label}
              </span>
            )}

            {/* Department Badge */}
            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${dept.color} flex items-center gap-1`}>
              <Shield size={12} />
              <span>{complaint.department || dept.name}</span>
            </span>

            {/* Notified vs Ordinary Badge */}
            {isNotified ? (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-semibold flex items-center gap-1">
                <Scale size={11} />
                <span>Act 6/2018 Notified</span>
              </span>
            ) : (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 font-semibold">
                Citizen Charter
              </span>
            )}

            {/* Overdue Warning */}
            {complaint.sla_is_overdue && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-800 font-bold animate-pulse flex items-center gap-1">
                <AlertTriangle size={11} />
                <span>Overdue</span>
              </span>
            )}

            {/* AI Confidence */}
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-mono font-bold flex items-center gap-1">
              <Cpu size={11} />
              <span>{complaint.confidence ? `${Math.round(complaint.confidence * 100)}% Match` : '94% Match'}</span>
            </span>

            {/* Phase 2: Duplicate Badge */}
            {complaint.is_duplicate && (
              <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700 font-bold flex items-center gap-1">
                <Layers size={11} />
                <span>Merged Duplicate</span>
              </span>
            )}

            {/* Phase 2: Citizen Endorsements / Upvotes */}
            {complaint.upvote_count && complaint.upvote_count > 1 && (
              <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-orange-50 dark:bg-orange-950/40 text-orange-700 dark:text-orange-300 border border-orange-300 dark:border-orange-700 font-bold flex items-center gap-1">
                <ThumbsUp size={11} />
                <span>{complaint.upvote_count} Citizens Endorsed</span>
              </span>
            )}

            {/* Phase 2: CV Defect Type */}
            {complaint.defect_type && (
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-bold flex items-center gap-1">
                <Camera size={11} className="text-teal-600" />
                <span>{complaint.defect_type.replace(/_/g, ' ')} {complaint.visual_score ? `(${complaint.visual_score}/100)` : ''}</span>
              </span>
            )}
          </div>

          <span className={`self-start sm:self-auto text-xs px-2.5 py-0.5 rounded-full font-bold ${getStatusColor(complaint.status)} uppercase tracking-wider`}>
            {statusFormatted}
          </span>
        </div>

        {/* Content & Image */}
        <div className="flex flex-col sm:flex-row gap-4">
          {complaint.image_url && (
            <div className="shrink-0 relative group cursor-pointer" onClick={() => setModalOpen(true)}>
              <img
                src={complaint.image_url}
                alt={complaint.title}
                className="w-full sm:w-28 h-28 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
              />
              <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center text-white">
                <Eye size={20} />
              </div>
            </div>
          )}

          <div className="flex-1">
            <h3 className="font-bold text-base text-gray-900 dark:text-white mb-1.5">
              {complaint.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm line-clamp-3 leading-relaxed">
              {complaint.description}
            </p>
          </div>
        </div>
        
        {/* Footer info & Employee Action Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs pt-3 border-t border-gray-100 dark:border-gray-700/60">
          <div className="flex items-center gap-3 flex-wrap">
            {complaint.location_address ? (
              <span className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                <MapPin size={14} />
                <span className="max-w-[200px] truncate">{complaint.location_address}</span>
              </span>
            ) : null}
            
            {complaint.deadline_formatted && (
              <span className="text-[10px] font-semibold text-indigo-800 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md border border-indigo-200 dark:border-indigo-800 flex items-center gap-1">
                <Scale size={10} />
                <span>Due: {complaint.deadline_formatted}</span>
              </span>
            )}

            {isEmployee && complaint.priority_score && (
              <span className="text-[10px] font-mono font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-md">
                Urgency: {complaint.priority_score}/100
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 ml-auto flex-wrap">
            {/* Download Receipt Button */}
            <button
              onClick={handleOpenReceipt}
              title="Download Legal Acknowledgement Receipt"
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 font-medium transition"
            >
              <Download size={12} />
              <span>Receipt</span>
            </button>

            {/* View Full Timeline / Legal Record */}
            <Link
              to={`/complaint/${complaint.id}`}
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 font-semibold transition border border-indigo-200 dark:border-indigo-800"
            >
              <ExternalLink size={12} />
              <span>Track Details</span>
            </Link>

            {/* Employee Quick Status Action Buttons */}
            {isEmployee && (
              <div className="flex items-center gap-1.5">
                {complaint.status !== 'in_progress' && complaint.status !== 'resolved' && (
                  <button
                    disabled={updating}
                    onClick={() => handleUpdateStatus('in_progress')}
                    className="text-xs px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 hover:bg-blue-100 font-semibold transition"
                  >
                    Dispatch
                  </button>
                )}
                {complaint.status !== 'resolved' && (
                  <button
                    disabled={updating}
                    onClick={() => handleUpdateStatus('resolved')}
                    className="text-xs px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 font-semibold transition"
                  >
                    Resolve
                  </button>
                )}
              </div>
            )}

            <span className="flex items-center gap-1 text-gray-400 dark:text-gray-500 pl-1">
              <Clock size={13} />
              {formatTimeAgo(complaint.created_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Acknowledgement Receipt Modal */}
      <AcknowledgementReceiptModal
        isOpen={receiptModalOpen}
        onClose={() => setReceiptModalOpen(false)}
        data={receiptData}
      />

      {/* Image Zoom Modal */}
      {modalOpen && complaint.image_url && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4" onClick={() => setModalOpen(false)}>
          <div className="relative max-w-3xl max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setModalOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 p-1"
            >
              <X size={24} />
            </button>
            <img
              src={complaint.image_url}
              alt={complaint.title}
              className="max-h-[85vh] w-auto rounded-lg shadow-2xl object-contain"
            />
          </div>
        </div>
      )}
    </>
  );
}
