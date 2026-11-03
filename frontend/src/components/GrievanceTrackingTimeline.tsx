import { ActivityLogRecord, ComplaintRecord } from '../lib/api';
import {
  CheckCircle2,
  Clock,
  RotateCcw,
  UserCheck,
  BrainCircuit,
  Search,
  FileText,
  AlertOctagon
} from 'lucide-react';

interface Props {
  complaint: ComplaintRecord;
  logs: ActivityLogRecord[];
  loading?: boolean;
}

export default function GrievanceTrackingTimeline({ complaint, logs, loading }: Props) {
  const currentStatus = (complaint.status || 'pending').toLowerCase();
  const isResolved = currentStatus === 'resolved';
  const isRejected = currentStatus === 'rejected';
  const isReopened = (complaint.reopened_count || 0) > 0;
  const isEscalated = (complaint.escalation_level || 1) > 1;

  // Canonical chronological lifecycle stages
  const STAGES = [
    { key: 'submitted', label: 'Submitted', desc: 'Complaint registered by citizen' },
    { key: 'acknowledged', label: 'Acknowledged', desc: 'Official receipt generated & SMS/Email notice sent' },
    { key: 'classified', label: 'AI Classified', desc: 'Multimodal urgency & department routing completed' },
    { key: 'assigned', label: 'Assigned to Officer', desc: complaint.assigned_employee_id ? `Assigned to ${complaint.assigned_employee_id}` : 'Pending cadre dispatch' },
    { key: 'investigating', label: 'Under Investigation', desc: 'Field inspection & evidence collection in progress' },
    { key: 'action_taken', label: 'Action Taken', desc: 'Remediation completed or work order issued' },
    { key: 'resolved', label: isRejected ? 'Rejected with Reasons' : 'Resolved & Closed', desc: isRejected ? 'Disposed with recorded reasons' : 'Verified by department' }
  ];

  // Determine active index
  let activeIndex = 0;
  if (isResolved || isRejected) {
    activeIndex = 6;
  } else if (complaint.action_taken) {
    activeIndex = 5;
  } else if (currentStatus === 'in_progress') {
    activeIndex = 4;
  } else if (complaint.assigned_employee_id) {
    activeIndex = 3;
  } else if (complaint.department) {
    activeIndex = 2;
  } else {
    activeIndex = 1;
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-black text-sm tracking-tight text-slate-900 dark:text-white uppercase">
              Chronological Grievance Tracking Timeline
            </h3>
            {isReopened && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300">
                Reopened Case (x{complaint.reopened_count})
              </span>
            )}
            {isEscalated && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300">
                Escalation Level {complaint.escalation_level}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time auditable lifecycle progression for Ticket {complaint.grievance_ref_number || complaint.id}
          </p>
        </div>
      </div>

      {/* Progress Stepper (Horizontal on desktop, vertical on mobile) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {STAGES.map((stage, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          let badgeColor = 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500';
          let borderStyle = 'border-slate-200 dark:border-slate-800';

          if (isDone) {
            badgeColor = 'bg-teal-600 text-white';
            borderStyle = 'border-teal-500/50 bg-teal-50/40 dark:bg-teal-950/20';
          } else if (isCurrent) {
            if (isRejected) {
              badgeColor = 'bg-rose-600 text-white animate-pulse';
              borderStyle = 'border-rose-400 bg-rose-50/40 dark:bg-rose-950/20';
            } else {
              badgeColor = 'bg-amber-500 text-white animate-pulse';
              borderStyle = 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/20';
            }
          }

          return (
            <div
              key={stage.key}
              className={`p-3 rounded-2xl border ${borderStyle} flex flex-col justify-between transition-all`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-black ${badgeColor}`}>
                  {isDone ? <CheckCircle2 size={14} /> : idx + 1}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  Step {idx + 1}
                </span>
              </div>
              <div>
                <h4 className="text-xs font-black text-slate-900 dark:text-white leading-tight">
                  {stage.label}
                </h4>
                <p className="text-[10px] text-slate-500 mt-1 leading-snug line-clamp-2">
                  {stage.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Immutable Activity Audit History Feed */}
      <div className="space-y-3 pt-2">
        <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-600 dark:text-slate-400">
          Official Audit History & Action Log
        </h4>

        {loading ? (
          <div className="text-center py-4 text-xs text-slate-400">Loading activity trail...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-4 text-xs text-slate-400">No events logged yet.</div>
        ) : (
          <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
            {logs.map((log) => {
              let icon = <Clock size={12} className="text-slate-400" />;
              let dotColor = 'bg-slate-400';

              if (log.action.includes('Registered') || log.action.includes('Submitted')) {
                dotColor = 'bg-blue-500';
                icon = <FileText size={12} className="text-white" />;
              } else if (log.action.includes('AI') || log.action.includes('Classification')) {
                dotColor = 'bg-purple-500';
                icon = <BrainCircuit size={12} className="text-white" />;
              } else if (log.action.includes('Assigned') || log.action.includes('Reassigned')) {
                dotColor = 'bg-amber-500';
                icon = <UserCheck size={12} className="text-white" />;
              } else if (log.action.includes('Investigation') || log.action.includes('Report')) {
                dotColor = 'bg-indigo-500';
                icon = <Search size={12} className="text-white" />;
              } else if (log.action.includes('Reopened')) {
                dotColor = 'bg-rose-500';
                icon = <RotateCcw size={12} className="text-white" />;
              } else if (log.action.includes('Escalation')) {
                dotColor = 'bg-rose-600';
                icon = <AlertOctagon size={12} className="text-white" />;
              } else if (log.action.includes('Resolved')) {
                dotColor = 'bg-teal-500';
                icon = <CheckCircle2 size={12} className="text-white" />;
              }

              return (
                <div key={log.id} className="relative group text-xs">
                  <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full ${dotColor} flex items-center justify-center ring-4 ring-white dark:ring-slate-900`}>
                    {icon}
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-800/40 p-3 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <span className="font-extrabold text-slate-900 dark:text-white">
                        {log.action}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(log.created_at).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-600 dark:text-slate-300">
                      {log.comments || 'Status update logged.'}
                    </div>

                    <div className="flex items-center gap-3 text-[10px] text-slate-400 pt-1">
                      <span><strong>Actor:</strong> {log.actor_name || log.actor_role}</span>
                      {log.previous_status && log.new_status && (
                        <span>
                          <strong>Transition:</strong> {log.previous_status} &rarr; {log.new_status}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
