import { ActivityLogRecord, ComplaintRecord } from '../lib/api';
import {
  CheckCircle2,
  Clock,
  RotateCcw,
  UserCheck,
  BrainCircuit,
  Search,
  FileText,
  AlertOctagon,
  Gauge,
  Flame,
  CalendarClock,
  Sparkles
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

  // Dynamic Relative Department Queue Metrics
  const queueRank = complaint.queue_rank || 1;
  const queueTotal = complaint.queue_total || Math.max(1, (logs.length > 2 ? 6 : 4));
  const priorityScore = complaint.priority_score ?? 70.0;
  const priorityTier = complaint.priority || 'Medium';
  const relativePercentile = complaint.relative_percentile ?? Math.round(((queueTotal - queueRank) / Math.max(1, queueTotal - 1)) * 100);
  const isEmergency = complaint.is_emergency_override || priorityTier === 'Critical' || priorityScore >= 85.0;

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

  // Action Timeline Execution Phases
  const timelinePhases = complaint.action_timeline?.phases || [
    {
      phase_id: 'phase_1',
      label: 'Grievance Trigger & Multimodal AI Ingestion',
      timestamp: complaint.created_at,
      status: 'completed',
      priority_snapshot: priorityScore,
      details: `Registered in ${(complaint.department || complaint.category || 'Division').replace(/_/g, ' ')}. Intrinsic severity evaluated.`
    },
    {
      phase_id: 'phase_2',
      label: 'Department Multi-Complaint Queue Placement',
      timestamp: complaint.created_at,
      status: 'completed',
      priority_snapshot: priorityScore,
      details: `Ranked #${queueRank} of ${queueTotal} active ${(complaint.department || complaint.category || 'department').replace(/_/g, ' ')} cases.`
    },
    {
      phase_id: 'phase_3',
      label: 'Cadre Field Inspection & Ground Assessment',
      timestamp: complaint.assigned_employee_id ? complaint.updated_at : complaint.created_at,
      status: (activeIndex >= 4) ? 'completed' : 'in_progress',
      priority_snapshot: priorityScore,
      details: complaint.assigned_employee_id ? `Dispatched to Cadre Officer ${complaint.assigned_employee_id}. Inspection window active.` : 'Scheduled for ground inspection.'
    },
    {
      phase_id: 'phase_4',
      label: 'Remedial Civil / Maintenance Works Window',
      timestamp: complaint.updated_at,
      status: (activeIndex >= 5) ? 'completed' : (activeIndex >= 4 ? 'in_progress' : 'pending'),
      priority_snapshot: priorityScore,
      details: complaint.action_taken || 'Target remediation scheduled in accordance with department priority ranking.'
    },
    {
      phase_id: 'phase_5',
      label: 'Statutory Disposal & Citizen Verification',
      timestamp: complaint.expected_resolution_date || complaint.deadline_formatted || 'Within SLA',
      status: isResolved ? 'completed' : 'pending',
      priority_snapshot: priorityScore,
      details: `Disposal deadline under AP Citizen Charter: ${complaint.expected_resolution_date || complaint.deadline_formatted || 'Within 7 Working Days'}.`
    }
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-black text-sm tracking-tight text-slate-900 dark:text-white uppercase flex items-center gap-1.5">
              <BrainCircuit size={16} className="text-teal-600" />
              <span>Multi-Complaint Dynamic Priority &amp; Action Timeline</span>
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
            {isEmergency && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-600 text-white flex items-center gap-1 animate-pulse">
                <Flame size={10} />
                <span>Emergency Override</span>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time auditable lifecycle progression for Ticket {complaint.grievance_ref_number || complaint.id}
          </p>
        </div>
      </div>

      {/* AI Dynamic Department Prioritization & Queue Position Banner */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950 text-white shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-teal-300">
              <Gauge size={20} />
            </div>
            <div>
              <div className="text-[10px] uppercase font-bold tracking-wider text-teal-300">
                Live Department Queue Placement
              </div>
              <div className="text-sm font-extrabold flex items-center gap-2">
                <span>Rank #{queueRank} of {queueTotal} Active Cases</span>
                <span className="text-xs font-normal text-slate-300">
                  in {(complaint.department || complaint.category || 'Division').replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="px-3 py-1 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 text-center">
              <div className="text-[9px] uppercase font-bold text-slate-300">Dynamic Score</div>
              <div className="text-xs font-black text-amber-300">{priorityScore.toFixed(1)} / 100</div>
            </div>
            <div className="px-3 py-1 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 text-center">
              <div className="text-[9px] uppercase font-bold text-slate-300">Priority Tier</div>
              <div className={`text-xs font-black ${priorityTier === 'Critical' ? 'text-rose-400' : priorityTier === 'High' ? 'text-orange-400' : 'text-teal-300'}`}>
                {priorityTier.toUpperCase()}
              </div>
            </div>
            <div className="px-3 py-1 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 text-center">
              <div className="text-[9px] uppercase font-bold text-slate-300">Relative Urgency</div>
              <div className="text-xs font-black text-emerald-300">{relativePercentile}% Percentile</div>
            </div>
          </div>
        </div>

        {/* Diagnostic Explanation Callout */}
        <div className="text-xs text-slate-300 leading-relaxed bg-black/20 p-2.5 rounded-xl border border-white/5 flex items-start gap-2">
          <Sparkles size={14} className="text-teal-400 shrink-0 mt-0.5" />
          <span>
            {complaint.priority_explanation || (
              `Dynamically ranked #${queueRank} among all active ${complaint.department || complaint.category} grievances. ` +
              `Priority re-evaluates at every lifecycle step incorporating aging SLA depletion, sensitive zones, and citizen demand.`
            )}
          </span>
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

      {/* Detailed Action Timeline Execution Milestones */}
      <div className="bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
        <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
          <CalendarClock size={14} className="text-teal-600" />
          <span>Statutory Action Timeline &amp; Milestone Targets</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {timelinePhases.map((phase: any, pIdx: number) => {
            const isPhaseDone = phase.status === 'completed';
            const isPhaseActive = phase.status === 'in_progress';
            return (
              <div
                key={phase.phase_id || pIdx}
                className={`p-3 rounded-xl border text-xs flex flex-col justify-between ${
                  isPhaseDone
                    ? 'bg-white dark:bg-slate-900 border-teal-200 dark:border-teal-900/50'
                    : isPhaseActive
                    ? 'bg-amber-50/60 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800'
                    : 'bg-white/60 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800 opacity-75'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                    <span className="font-bold uppercase tracking-wider">Milestone {pIdx + 1}</span>
                    <span className={`px-1.5 py-0.2 rounded font-mono text-[9px] ${
                      isPhaseDone ? 'bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300' :
                      isPhaseActive ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                      'bg-slate-100 text-slate-500 dark:bg-slate-800'
                    }`}>
                      {phase.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="font-extrabold text-slate-900 dark:text-white leading-snug">
                    {phase.label}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1 line-clamp-3 leading-relaxed">
                    {phase.details}
                  </div>
                </div>
                <div className="text-[9px] font-mono text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800 mt-2 flex items-center justify-between">
                  <span>Target Slot</span>
                  <strong>{new Date(phase.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}</strong>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Immutable Activity Audit History Feed */}
      <div className="space-y-3 pt-2">
        <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-600 dark:text-slate-400">
          Official Audit History &amp; Action Log (With Step Priority Calculations)
        </h4>

        {loading ? (
          <div className="text-center py-4 text-xs text-slate-400">Loading activity trail...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-4 text-xs text-slate-400">No events logged yet.</div>
        ) : (
          <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
            {logs.map((log: any) => {
              let icon = <Clock size={12} className="text-slate-400" />;
              let dotColor = 'bg-slate-400';

              if (log.action.includes('Registered') || log.action.includes('Submitted')) {
                dotColor = 'bg-blue-500';
                icon = <FileText size={12} className="text-white" />;
              } else if (log.action.includes('AI') || log.action.includes('Classification') || log.action.includes('Priority')) {
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

              const hasPrioMeta = log.metadata?.priority_score !== undefined || log.metadata?.queue_rank !== undefined;

              return (
                <div key={log.id} className="relative group text-xs">
                  <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full ${dotColor} flex items-center justify-center ring-4 ring-white dark:ring-slate-900`}>
                    {icon}
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-800/40 p-3 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-slate-900 dark:text-white">
                          {log.action}
                        </span>
                        {hasPrioMeta && (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300">
                            Queue #{log.metadata.queue_rank || 1} • {log.metadata.priority_score?.toFixed(1) || priorityScore.toFixed(1)} pts
                          </span>
                        )}
                      </div>
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
