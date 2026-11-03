import { useRef } from 'react';
import { AcknowledgementReceiptData } from '../lib/api';
import {
  X,
  Printer,
  ShieldCheck,
  Scale,
  AlertCircle
} from 'lucide-react';

interface Props {
  receipt?: AcknowledgementReceiptData | null;
  data?: AcknowledgementReceiptData | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function AcknowledgementReceiptModal({ receipt, data, isOpen, onClose }: Props) {
  const printRef = useRef<HTMLDivElement>(null);

  const activeReceipt = receipt || data;
  if (!isOpen || !activeReceipt) return null;

  const handlePrint = () => {
    window.print();
  };

  const isNotified = activeReceipt.workflow_type === 'notified_service';

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="bg-white dark:bg-slate-900 rounded-3xl max-w-2xl w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col my-auto max-h-[92vh]">
        
        {/* Modal Header Actions */}
        <div className="bg-slate-900 text-white p-4 px-6 flex items-center justify-between border-b border-slate-800 print:hidden">
          <div className="flex items-center gap-2">
            <ShieldCheck className="text-teal-400" size={20} />
            <span className="font-extrabold text-sm tracking-wide uppercase">
              Official Grievance Acknowledgement Receipt
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm cursor-pointer"
            >
              <Printer size={14} />
              Print / Save PDF
            </button>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition cursor-pointer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Printable Official Receipt Body */}
        <div ref={printRef} className="p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-800 dark:text-slate-200 text-xs">
          
          {/* Government of Andhra Pradesh Official Letterhead */}
          <div className="text-center pb-5 border-b-2 border-slate-200 dark:border-slate-700 space-y-1">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 font-black text-lg mb-1 border border-teal-200 dark:border-teal-800">
              AP
            </div>
            <h2 className="text-base sm:text-lg font-black text-slate-900 dark:text-white tracking-tight uppercase">
              Government of Andhra Pradesh
            </h2>
            <p className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-widest">
              Municipal Administration & Urban Development Department
            </p>
            <p className="text-[10px] text-slate-500">
              Public Grievance Redressal System (PGRS) & Legal Compliance Framework
            </p>
          </div>

          {/* Reference & Date Card */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 dark:bg-slate-800/60 p-4 rounded-2xl border border-slate-200 dark:border-slate-700">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Grievance Reference Number
              </span>
              <span className="text-sm font-black text-teal-700 dark:text-teal-400 tracking-wide font-mono">
                {activeReceipt.grievance_ref_number}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Submission Date & Time
              </span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {new Date(activeReceipt.submission_time).toLocaleString('en-IN', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>

          {/* Statutory Legal Applicability Banner */}
          <div className={`p-4 rounded-2xl border flex items-start gap-3 ${
            isNotified 
              ? 'bg-amber-50/80 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800/60 text-amber-950 dark:text-amber-200' 
              : 'bg-teal-50/80 dark:bg-teal-950/30 border-teal-300 dark:border-teal-800/60 text-teal-950 dark:text-teal-200'
          }`}>
            <Scale className="shrink-0 mt-0.5 text-teal-600 dark:text-teal-400" size={18} />
            <div className="space-y-1">
              <div className="font-black text-xs uppercase tracking-wider">
                {isNotified 
                  ? 'Notified Public Service — Statutory Guarantee Applicable' 
                  : 'Ordinary Civic Grievance — Citizen Charter Applicable'}
              </div>
              <p className="text-[11px] leading-relaxed opacity-90">
                <strong>Governing Framework:</strong> {activeReceipt.legal_source}
                {activeReceipt.go_reference && ` (${activeReceipt.go_reference})`}
              </p>
            </div>
          </div>

          {/* Grievance Details Grid */}
          <div className="space-y-3">
            <h3 className="font-black text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200 dark:border-slate-700 pb-1">
              Grievance Dossier Particulars
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Grievance Subject</span>
                <span className="font-bold text-slate-900 dark:text-white">{activeReceipt.title}</span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Department Wing</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{activeReceipt.department}</span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Current Workflow Status</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 uppercase">
                  {activeReceipt.current_status.replace('_', ' ')}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Citizen Name</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{activeReceipt.citizen_name}</span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Responsible Designated Officer</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">{activeReceipt.designated_officer}</span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase block">Expected Redressal Timeline</span>
                <span className="font-black text-teal-700 dark:text-teal-400">
                  {activeReceipt.expected_resolution_date}
                </span>
                <span className="text-[10px] text-slate-500 block">
                  Calculated based on {activeReceipt.timeline_calculation_method.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>

          {/* Statutory Rights & Appellate Mechanism */}
          <div className="bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-2">
            <h4 className="font-black text-xs uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
              <AlertCircle size={14} className="text-amber-500" />
              Statutory Escalation & Appellate Mechanism
            </h4>
            <p className="text-[11px] leading-relaxed text-slate-600 dark:text-slate-400">
              {isNotified ? (
                <>
                  Under <strong>Section 8 & Section 10 of Act No. 6 of 2018</strong>, if the designated officer fails to provide the service within the stipulated timeline or rejects the application without sufficient reason, you hold the statutory right to file an appeal before the <strong>{activeReceipt.first_appellate_authority}</strong> within <strong>{activeReceipt.appeal_deadline_days} days</strong>.
                  {activeReceipt.compensation_applicable && (
                    <span className="block mt-1 font-bold text-teal-700 dark:text-teal-400">
                      * Section 9 Statutory Compensation applies if disposal is delayed without justifiable cause.
                    </span>
                  )}
                </>
              ) : (
                <>
                  This civic grievance is monitored under the departmental citizen charter. In the event of non-redressal within the prescribed timeline, administrative escalation will automatically dispatch this dossier to the <strong>{activeReceipt.first_appellate_authority}</strong> for inspection.
                </>
              )}
            </p>
          </div>

          {/* Official Verification Seal & QR Verification Note */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[10px]">
            <div>
              <p className="font-bold">Computer Generated Legal Acknowledgment Document</p>
              <p>Authentic Digital Receipt of NEX-CIV Andhra Pradesh</p>
            </div>
            <div className="px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 font-mono text-[10px] text-center">
              CERT-AP-{activeReceipt.grievance_ref_number}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 dark:bg-slate-800/50 p-4 px-6 flex justify-end gap-3 border-t border-slate-200 dark:border-slate-800 print:hidden">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold transition cursor-pointer"
          >
            Close Receipt
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm cursor-pointer"
          >
            <Printer size={14} />
            Print Receipt
          </button>
        </div>
      </div>
    </div>
  );
}
