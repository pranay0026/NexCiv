import { ExternalLink, Scale, FileText, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function RtiVsGrievanceNotice() {
  return (
    <div className="bg-slate-900 text-white rounded-3xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-6">
      
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0">
          <Scale size={24} />
        </div>
        <div>
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-teal-400">
            Legal Transparency Framework
          </span>
          <h3 className="text-base sm:text-lg font-black tracking-tight text-white mt-0.5">
            Understanding Civic Grievances, Public Services & RTI in Andhra Pradesh
          </h3>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
            In accordance with Government of Andhra Pradesh administrative protocols, civic grievances, statutory public services, and Right to Information requests operate under separate legal mandates.
          </p>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Card 1: Ordinary Civic Grievance */}
        <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/60 space-y-2">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle size={18} />
            <h4 className="font-black text-xs uppercase tracking-wider">
              1. Civic Grievance (PGRS)
            </h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Remediation requests for existing public infrastructure (e.g. potholes, sewage overflow, broken street lights, garbage accumulation).
          </p>
          <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-700/40">
            <strong>Governed by:</strong> AP Municipal Citizen Charters & AP PGRS guidelines.
          </div>
        </div>

        {/* Card 2: Public Service Delivery Guarantee */}
        <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/60 space-y-2">
          <div className="flex items-center gap-2 text-teal-400">
            <CheckCircle2 size={18} />
            <h4 className="font-black text-xs uppercase tracking-wider">
              2. Notified Public Service
            </h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Statutory applications for notified services (e.g. tap connection approval, road-cutting permission, trade licenses) with legal timelines.
          </p>
          <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-700/40">
            <strong>Governed by:</strong> AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018).
          </div>
        </div>

        {/* Card 3: Right to Information (RTI) */}
        <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/60 space-y-2">
          <div className="flex items-center gap-2 text-blue-400">
            <FileText size={18} />
            <h4 className="font-black text-xs uppercase tracking-wider">
              3. Right to Information (RTI)
            </h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Legal requests to obtain recorded government records, orders, files, and public documents. <em>An ordinary grievance is NOT an RTI application.</em>
          </p>
          <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-700/40">
            <strong>Governed by:</strong> Right to Information Act, 2005.
          </div>
        </div>
      </div>

      {/* Official Government Links Footer */}
      <div className="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <span className="text-slate-300">
          Need to file an official statutory RTI application under the RTI Act, 2005?
        </span>
        <div className="flex items-center gap-3">
          <a
            href="https://www.rtionline.ap.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold transition shadow-xs"
          >
            AP RTI Online Portal
            <ExternalLink size={13} />
          </a>
          <a
            href="https://meeseva.ap.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-200 font-bold transition"
          >
            MeeSeva AP Services
            <ExternalLink size={13} />
          </a>
        </div>
      </div>
    </div>
  );
}
