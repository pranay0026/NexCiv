import React, { useState } from 'react';
import { api } from '../lib/api';
import {
  X,
  Star,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Upload,
  Loader2,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';

interface Props {
  complaintId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  citizenName?: string;
}

export default function CitizenFeedbackModal({
  complaintId,
  isOpen,
  onClose,
  onSuccess,
  citizenName
}: Props) {
  const [activeMode, setActiveMode] = useState<'feedback' | 'reopen'>('feedback');
  
  // Feedback state
  const [rating, setRating] = useState(5);
  const [isResolvedConfirmed, setIsResolvedConfirmed] = useState(true);
  const [comments, setComments] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  // Reopen state
  const [reopenReason, setReopenReason] = useState('');
  const [reopenEvidence, setReopenEvidence] = useState<string | null>(null);
  const [submittingReopen, setSubmittingReopen] = useState(false);
  const [reopenError, setReopenError] = useState('');

  if (!isOpen) return null;

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingFeedback(true);
    try {
      await api.submitFeedback({
        complaint_id: complaintId,
        citizen_name: citizenName || 'Public Citizen',
        rating,
        is_resolved_confirmed: isResolvedConfirmed,
        comments
      });
      setFeedbackSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      console.warn('Feedback submit error:', err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleReopenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setReopenError('');
    if (!reopenReason.trim()) {
      setReopenError('Please provide an explanation for reopening this grievance.');
      return;
    }
    setSubmittingReopen(true);
    try {
      await api.reopenComplaint(
        complaintId,
        reopenReason,
        reopenEvidence || undefined,
        citizenName
      );
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setReopenError(err.message || 'Failed to submit reopening request');
    } finally {
      setSubmittingReopen(false);
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setReopenEvidence(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col">
        
        {/* Header Tabs */}
        <div className="p-4 px-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveMode('feedback')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeMode === 'feedback'
                  ? 'bg-teal-600 text-white shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Rate Resolution
            </button>
            <button
              onClick={() => setActiveMode('reopen')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5 ${
                activeMode === 'reopen'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <RotateCcw size={13} />
              Request Reopen
            </button>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Feedback Mode */}
        {activeMode === 'feedback' ? (
          <form onSubmit={handleFeedbackSubmit} className="p-6 space-y-5 text-xs text-slate-800 dark:text-slate-200">
            <div>
              <h3 className="text-sm font-black text-slate-900 dark:text-white">
                How satisfied are you with the redressal?
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Your feedback directly impacts municipal engineer performance evaluations.
              </p>
            </div>

            {/* Star Rating */}
            <div className="flex items-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 text-amber-400 hover:scale-110 transition cursor-pointer"
                >
                  <Star
                    size={28}
                    fill={star <= rating ? 'currentColor' : 'none'}
                    className={star <= rating ? 'text-amber-400' : 'text-slate-300 dark:text-slate-700'}
                  />
                </button>
              ))}
              <span className="ml-2 font-black text-slate-700 dark:text-slate-300">
                {rating === 5 ? 'Excellent' : rating === 4 ? 'Good' : rating === 3 ? 'Average' : rating === 2 ? 'Poor' : 'Unsatisfactory'}
              </span>
            </div>

            {/* Resolved Confirmation */}
            <div className="space-y-1.5">
              <label className="font-bold block">Was your issue actually resolved on the ground?</label>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setIsResolvedConfirmed(true)}
                  className={`flex-1 p-2.5 rounded-xl border flex items-center justify-center gap-2 font-bold transition cursor-pointer ${
                    isResolvedConfirmed
                      ? 'bg-teal-50 dark:bg-teal-950/40 border-teal-500 text-teal-700 dark:text-teal-300'
                      : 'border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  <ThumbsUp size={14} />
                  Yes, fully resolved
                </button>
                <button
                  type="button"
                  onClick={() => setIsResolvedConfirmed(false)}
                  className={`flex-1 p-2.5 rounded-xl border flex items-center justify-center gap-2 font-bold transition cursor-pointer ${
                    !isResolvedConfirmed
                      ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-500 text-rose-700 dark:text-rose-300'
                      : 'border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  <ThumbsDown size={14} />
                  No, still unresolved
                </button>
              </div>
            </div>

            {/* Comments */}
            <div className="space-y-1">
              <label className="font-bold block">Feedback Comments (Optional)</label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Share your experience regarding the quality and speed of field work..."
                rows={3}
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-teal-500"
              />
            </div>

            {feedbackSuccess && (
              <div className="p-3 bg-teal-50 dark:bg-teal-950/40 border border-teal-300 dark:border-teal-800 rounded-xl text-teal-800 dark:text-teal-300 flex items-center gap-2 font-bold">
                <CheckCircle2 size={16} />
                Thank you! Your feedback has been recorded in the permanent audit trail.
              </div>
            )}

            <button
              type="submit"
              disabled={submittingFeedback}
              className="w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
            >
              {submittingFeedback ? <Loader2 size={16} className="animate-spin" /> : 'Submit Feedback'}
            </button>
          </form>
        ) : (
          /* Reopen Mode */
          <form onSubmit={handleReopenSubmit} className="p-6 space-y-4 text-xs text-slate-800 dark:text-slate-200">
            <div>
              <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-1.5 text-rose-600">
                <RotateCcw size={16} />
                Request Grievance Reopening
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                If the ground repair was incomplete or defective, you may request reopening. This records an auditable event for supervisory review.
              </p>
            </div>

            {reopenError && (
              <div className="p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 rounded-xl text-rose-800 dark:text-rose-300 flex items-center gap-2">
                <AlertTriangle size={16} />
                {reopenError}
              </div>
            )}

            <div className="space-y-1">
              <label className="font-bold block">
                Detailed Reason for Reopening <span className="text-rose-500">*</span>
              </label>
              <textarea
                value={reopenReason}
                onChange={(e) => setReopenReason(e.target.value)}
                placeholder="Explain why the issue is not resolved (e.g. trench not filled properly, water still leaking)..."
                rows={3}
                required
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-rose-500"
              />
            </div>

            {/* Photo Evidence */}
            <div className="space-y-1">
              <label className="font-bold block">Supporting Photo Evidence (Optional)</label>
              {reopenEvidence ? (
                <div className="relative w-32 h-24 rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700">
                  <img src={reopenEvidence} alt="Evidence" className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => setReopenEvidence(null)}
                    className="absolute top-1 right-1 p-1 bg-black/60 text-white rounded-full hover:bg-black/80"
                  >
                    <X size={12} />
                  </button>
                </div>
              ) : (
                <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-rose-400 p-4 rounded-xl flex flex-col items-center justify-center text-slate-500 hover:text-rose-600 transition cursor-pointer">
                  <Upload size={20} className="mb-1" />
                  <span className="font-bold text-[11px]">Upload fresh site photograph</span>
                  <input type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                </label>
              )}
            </div>

            <div className="bg-amber-50 dark:bg-amber-950/30 p-3 rounded-xl border border-amber-200 dark:border-amber-800 text-[11px] text-amber-800 dark:text-amber-300">
              * Note: Reopening is an administrative review mechanism. For statutory notified services, you may also file a formal appeal under Section 10 of Act 6 of 2018.
            </div>

            <button
              type="submit"
              disabled={submittingReopen}
              className="w-full py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
            >
              {submittingReopen ? <Loader2 size={16} className="animate-spin" /> : 'Confirm Reopening Request'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
