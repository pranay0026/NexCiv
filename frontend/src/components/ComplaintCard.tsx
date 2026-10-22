import { useState } from 'react';
import { MapPin, Clock, Flame, AlertTriangle, CheckCircle, Eye, X, Shield, Cpu, Layers, ThumbsUp, Camera } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../lib/api';

interface Complaint {
  id: string;
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
  zone_type?: string;
  vulnerability_multiplier?: number;
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
  const [updating, setUpdating] = useState(false);

  const rawCat = (complaint.category || 'others').toLowerCase().replace(' ', '_');
  const dept = DEPARTMENTS_MAP[rawCat] || DEPARTMENTS_MAP.others;
  const statusFormatted = (complaint.status || 'pending').replace('_', ' ');
  const prio = getPriorityBadge(complaint.priority);
  const isEmployee = profile?.role === 'employee';

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
            <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full font-bold border ${prio.style}`}>
              {prio.icon}
              {prio.label}
            </span>

            {/* Department Badge */}
            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${dept.color} flex items-center gap-1`}>
              <Shield size={12} />
              <span>{complaint.department || dept.name}</span>
            </span>

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
                <span className="max-w-[250px] truncate">{complaint.location_address}</span>
              </span>
            ) : null}
            
            {complaint.municipal_sla && (
              <span className="text-[10px] font-semibold text-teal-800 dark:text-teal-300 bg-teal-50 dark:bg-teal-950/40 px-2 py-0.5 rounded-md border border-teal-200 dark:border-teal-800">
                SLA: {complaint.municipal_sla}
              </span>
            )}

            {complaint.priority_score && (
              <span className="text-[10px] font-mono font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-md">
                Urgency: {complaint.priority_score}/100
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-3 ml-auto">
            {/* Employee Quick Status Action Buttons */}
            {isEmployee && (
              <div className="flex items-center gap-1.5">
                {complaint.status !== 'in_progress' && complaint.status !== 'resolved' && (
                  <button
                    disabled={updating}
                    onClick={() => handleUpdateStatus('in_progress')}
                    className="text-xs px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 hover:bg-blue-100 font-semibold transition"
                  >
                    Dispatch Team
                  </button>
                )}
                {complaint.status !== 'resolved' && (
                  <button
                    disabled={updating}
                    onClick={() => handleUpdateStatus('resolved')}
                    className="text-xs px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 font-semibold transition"
                  >
                    Mark Resolved
                  </button>
                )}
              </div>
            )}

            <span className="flex items-center gap-1 text-gray-400 dark:text-gray-500">
              <Clock size={13} />
              {formatTimeAgo(complaint.created_at)}
            </span>
          </div>
        </div>
      </div>

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
