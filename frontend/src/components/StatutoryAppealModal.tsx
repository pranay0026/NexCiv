import { useState } from 'react';
import { ComplaintRecord, api } from '../lib/api';
import {
  X,
  Scale,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  ShieldCheck
} from 'lucide-react';

interface Props {
  complaint: ComplaintRecord;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function StatutoryAppealModal({
  complaint,
  isOpen,
  onClose,
  onSuccess
}: Props) {
  const isNotified = complaint.workflow_type === 'notified_service';
  const firstAppellate = complaint.appellate_authority || 'Superintending Engineer / District Collector';

  const [appealLevel, setAppealLevel] = useState<number>(1);
  const [appellantName, setAppellantName] = useState(complaint.citizen_name || '');
  const [appellantEmail, setAppellantEmail] = useState(complaint.citizen_email || '');
  const [appealGround, setAppealGround] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!appealGround.trim()) {
      setError('Please provide specific legal/factual grounds for your appeal.');
      return;
    }
    setSubmitting(true);
    try {
      if (isNotified) {
        await api.fileAppeal({
          complaint_id: complaint.id,
          appeal_level: appealLevel,
          appellant_name: appellantName,
          appellant_email: appellantEmail,
          appeal_ground: appealGround
        });
      } else {
        await api.escalateComplaint(
          complaint.id,
          2,
          appealGround,
          firstAppellate
        );
      }
      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to submit appeal');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col my-auto max-h-[90vh]">
        
        {/* Header */}
        <div className="p-4 px-6 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Scale className="text-teal-400" size={18} />
            <h3 className="font-extrabold text-sm uppercase tracking-wide">
              {isNotified ? 'Statutory Service Guarantee Appeal' : 'Departmental Grievance Escalation'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs text-slate-800 dark:text-slate-200 overflow-y-auto">
          
          {/* Statutory Context Banner */}
          <div className={`p-4 rounded-2xl border ${
            isNotified
              ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200'
              : 'bg-teal-50 dark:bg-teal-950/30 border-teal-300 dark:border-teal-800 text-teal-900 dark:text-teal-200'
          }`}>
            <div className="font-black text-xs uppercase mb-1 flex items-center gap-1.5">
              <ShieldCheck size={14} />
              {isNotified
                ? 'Section 10, AP Public Services Delivery Guarantee Act, 2017'
                : 'Departmental Grievance Escalation Protocol'}
            </div>
            <p className="text-[11px] leading-relaxed opacity-90">
              {isNotified ? (
                <>
                  This complaint pertains to a <strong>Notified Public Service</strong>. Under Section 10 of Act No. 6 of 2018, you may file this appeal before the <strong>{firstAppellate}</strong> within 30 days of the disposal date or expiry of the prescribed deadline.
                </>
              ) : (
                <>
                  This issue is an <strong>Ordinary Civic Grievance</strong> governed by departmental citizen charters. Non-redressal will be escalated directly to the <strong>{firstAppellate}</strong> for administrative review.
                </>
              )}
            </p>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 rounded-xl text-rose-800 dark:text-rose-300 flex items-center gap-2">
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 bg-teal-50 dark:bg-teal-950/40 border border-teal-300 dark:border-teal-800 rounded-xl text-teal-800 dark:text-teal-300 flex items-center gap-2 font-bold">
              <CheckCircle2 size={16} />
              Appeal successfully recorded in the central compliance docket.
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="font-bold block mb-1">Appellant Name</label>
              <input
                type="text"
                value={appellantName}
                onChange={(e) => setAppellantName(e.target.value)}
                required
                className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
              />
            </div>
            <div>
              <label className="font-bold block mb-1">Appellant Contact Email</label>
              <input
                type="email"
                value={appellantEmail}
                onChange={(e) => setAppellantEmail(e.target.value)}
                required
                className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
              />
            </div>
          </div>

          {isNotified && (
            <div>
              <label className="font-bold block mb-1">Appellate Tier</label>
              <select
                value={appealLevel}
                onChange={(e) => setAppealLevel(Number(e.target.value))}
                className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
              >
                <option value={1}>Tier 1: First Appellate Authority ({firstAppellate})</option>
                <option value={2}>Tier 2: Second Appellate Authority (District Collector / State Commission)</option>
              </select>
            </div>
          )}

          <div>
            <label className="font-bold block mb-1">
              Grounds of Appeal / Non-Compliance Particulars <span className="text-rose-500">*</span>
            </label>
            <textarea
              value={appealGround}
              onChange={(e) => setAppealGround(e.target.value)}
              placeholder="State the facts: failure to deliver within prescribed timeline, unjustified rejection, or substandard execution..."
              rows={4}
              required
              className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-teal-500"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
          >
            {submitting ? <Loader2 size={16} className="animate-spin" /> : 'Submit Formal Appeal / Escalation'}
          </button>
        </form>
      </div>
    </div>
  );
}
