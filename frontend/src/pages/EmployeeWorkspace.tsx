import { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { api, EmployeeRecord, ActivityLogRecord, InvestigationRecord } from '../lib/api';
import {
  LayoutGrid,
  FileText,
  Layers,
  Map,
  TrendingUp,
  Users,
  Settings,
  HelpCircle,
  LogOut,
  Search,
  Bell,
  Download,
  Inbox,
  Scan,
  RotateCw,
  CheckCircle2,
  X,
  Flame,
  MapPin,
  Check,
  RefreshCw,
  ExternalLink,
  Eye,
  EyeOff,
  Lock,
  KeyRound,
  Sparkles,
  Scale,
  History,
  AlertTriangle,
  ClipboardCheck,
  AlertCircle
} from 'lucide-react';
import { verifyRepairResolutionProof, ResolutionVerificationResult } from '../lib/aiPhase3';

interface ComplaintItem {
  id: string;
  rawId?: string;
  grievanceRefNumber?: string;
  title?: string;
  category: string;
  department?: string;
  location: string;
  landmark?: string;
  ward?: string;
  received: string;
  status: 'New' | 'Under review' | 'In progress' | 'Resolved' | 'Rejected' | 'Reopened' | 'Escalated';
  assignedTeam: string;
  assignedEmployeeId?: string;
  priority?: string;
  priorityScore?: number;
  confidence?: number;
  upvotes?: number;
  isDuplicate?: boolean;
  masterComplaintId?: string;
  defectType?: string;
  visualScore?: number;
  sla?: string;
  deadlineFormatted?: string;
  slaIsOverdue?: boolean;
  isNotifiedService?: boolean;
  designatedOfficer?: string;
  appellateAuthority?: string;
  rejectionReason?: string;
  resolutionNotes?: string;
  resolutionProofUrl?: string;
  locationLat?: number;
  locationLng?: number;
  description?: string;
  priorityExplanation?: string;
  isEmergencyOverride?: boolean;
}

const INITIAL_COMPLAINTS: ComplaintItem[] = [];

export default function EmployeeWorkspace() {
  const { profile, signOut } = useAuth();
  const navigate = useNavigate();
  const currentEmpCode = profile?.employeeCode || 'EMP-101';

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };
  
  // Navigation tabs (7 Interactive Views)
  const [activeTab, setActiveTab] = useState('Overview');

  // Search & Task Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [showOnlyMyTasks, setShowOnlyMyTasks] = useState(true);
  const [statusFilter, setStatusFilter] = useState<'All' | 'New' | 'In progress' | 'Resolved'>('All');

  // Complaints & Hotspots State
  const [complaints, setComplaints] = useState<ComplaintItem[]>(INITIAL_COMPLAINTS);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [employeeStats, setEmployeeStats] = useState<any>(null);
  const [colleaguesList, setColleaguesList] = useState<EmployeeRecord[]>([]);
  const [colleagueSearch, setColleagueSearch] = useState('');
  const [selectedPinComplaint, setSelectedPinComplaint] = useState<ComplaintItem | null>(null);

  // Structured Investigation & Compliance State
  const [investigationModalOpen, setInvestigationModalOpen] = useState(false);
  const [investigatingComplaint, setInvestigatingComplaint] = useState<ComplaintItem | null>(null);
  const [siteInspectionConducted, setSiteInspectionConducted] = useState(true);
  const [inspectionLocation, setInspectionLocation] = useState('');
  const [investigationFindings, setInvestigationFindings] = useState('');
  const [investigationActionTaken, setInvestigationActionTaken] = useState('');
  const [investigationNextSteps, setInvestigationNextSteps] = useState('');
  const [investigationStatus, setInvestigationStatus] = useState<'in_progress' | 'resolved' | 'rejected' | 'awaiting_verification'>('resolved');
  const [investigationRejectionReason, setInvestigationRejectionReason] = useState('');
  const [investigationPhoto, setInvestigationPhoto] = useState<string | null>(null);
  const [submittingInvestigation, setSubmittingInvestigation] = useState(false);
  const [investigationError, setInvestigationError] = useState('');

  // Activity Audit History Drawer State
  const [auditModalOpen, setAuditModalOpen] = useState(false);
  const [auditComplaint, setAuditComplaint] = useState<ComplaintItem | null>(null);
  const [auditLogs, setAuditLogs] = useState<ActivityLogRecord[]>([]);
  const [auditInvestigations, setAuditInvestigations] = useState<InvestigationRecord[]>([]);
  const [loadingAudit, setLoadingAudit] = useState(false);

  // Resolution Modal State
  const [editingComplaint, setEditingComplaint] = useState<ComplaintItem | null>(null);
  const [editStatus, setEditStatus] = useState<ComplaintItem['status']>('In progress');
  const [editTeam, setEditTeam] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [resolutionProof, setResolutionProof] = useState<string | null>(null);
  const [savingResolution, setSavingResolution] = useState(false);

  // Phase 3 AI Resolution Verification State
  const [aiVerification, setAiVerification] = useState<ResolutionVerificationResult | null>(null);
  const [verifyingWithAi, setVerifyingWithAi] = useState(false);

  const runAiVerification = async (proofUrl: string, comp?: ComplaintItem | null) => {
    setVerifyingWithAi(true);
    try {
      const target = comp || editingComplaint || investigatingComplaint;
      const res = await verifyRepairResolutionProof(null, proofUrl, target?.defectType || target?.category);
      setAiVerification(res);
    } catch {}
    setVerifyingWithAi(false);
  };

  // Settings state
  const [alertSms, setAlertSms] = useState(true);
  const [alertEmail, setAlertEmail] = useState(true);
  const [soundAlert, setSoundAlert] = useState(true);
  const [settingsSaved, setSettingsSaved] = useState(false);

  // Employee Password Management State
  const [empCurrentPass, setEmpCurrentPass] = useState('');
  const [empNewPass, setEmpNewPass] = useState('');
  const [empConfirmPass, setEmpConfirmPass] = useState('');
  const [showEmpNew, setShowEmpNew] = useState(false);
  const [showEmpConfirm, setShowEmpConfirm] = useState(false);
  const [empPassUpdating, setEmpPassUpdating] = useState(false);
  const [empPassSuccess, setEmpPassSuccess] = useState('');
  const [empPassError, setEmpPassError] = useState('');

  const handleEmployeeChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmpPassError('');
    setEmpPassSuccess('');
    if (!empNewPass || empNewPass.length < 4) {
      setEmpPassError('New password must be at least 4 characters.');
      return;
    }
    if (empNewPass !== empConfirmPass) {
      setEmpPassError('New password and confirmation do not match.');
      return;
    }
    setEmpPassUpdating(true);
    try {
      const res = await api.changePassword({
        role: 'employee',
        identifier: currentEmpCode,
        oldPassword: empCurrentPass,
        newPassword: empNewPass
      });
      setEmpPassSuccess(res.message || 'Cadre password updated successfully!');
      setEmpCurrentPass('');
      setEmpNewPass('');
      setEmpConfirmPass('');
      setTimeout(() => setEmpPassSuccess(''), 4000);
    } catch (err: any) {
      setEmpPassError(err.message || 'Failed to update cadre password.');
    } finally {
      setEmpPassUpdating(false);
    }
  };

  // Fetch live workspace data from backend
  const fetchLiveWorkspaceData = async () => {
    try {
      // Robust municipality extraction: strictly isolate workspace to employee's ULB
      let empMunicipality = (profile as any)?.municipalityCode || (profile as any)?.municipalCorporation;
      if (!empMunicipality || empMunicipality === 'ALL') {
        const knownULBs = ['ELR', 'GVMC', 'VMC', 'GMC', 'TMC', 'KMC', 'RMC', 'KKD', 'BVM', 'TPG', 'NMC', 'KADA', 'ATP'];
        const tokens = currentEmpCode.toUpperCase().split('-');
        for (const t of tokens) {
          if (knownULBs.includes(t)) {
            empMunicipality = t;
            break;
          }
        }
      }
      if (!empMunicipality) empMunicipality = 'ELR';

      const [liveData, hotspotData, empData, empsList] = await Promise.all([
        api.getComplaints({ municipal_corporation: empMunicipality }).catch(() => []),
        api.getHotspots(100).catch(() => ({ total_hotspots: 0, hotspots: [] })),
        api.getEmployee(currentEmpCode).catch(() => null),
        api.getEmployees({ municipality_code: empMunicipality }).catch(() => [])
      ]);

      if (empData) {
        setEmployeeStats(empData);
      }

      if (empsList && empsList.length > 0) {
        setColleaguesList(empsList);
      }

      if (liveData) {
        const mapped: ComplaintItem[] = liveData.map((item: any) => {
          const shortCode = item.id.length > 8 ? `NXC-${item.id.slice(0, 6).toUpperCase()}` : item.id;
          const statusLabel =
            item.status === 'pending' ? 'New' :
            item.status === 'in_progress' ? 'In progress' :
            item.status === 'resolved' ? 'Resolved' :
            item.status === 'rejected' ? 'Rejected' :
            item.status === 'reopened' ? 'Reopened' :
            item.status === 'escalated' ? 'Escalated' :
            'Under review';
          return {
            id: shortCode,
            rawId: item.id,
            grievanceRefNumber: item.grievance_ref_number,
            title: item.title,
            category: (item.category || 'Roads').replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            department: item.department,
            location: item.location_address || 'Coordinates provided',
            landmark: item.landmark,
            ward: item.ward,
            received: 'Today',
            status: statusLabel as any,
            assignedTeam: item.assigned_team || `${item.department || 'Municipal'} Response Team`,
            assignedEmployeeId: item.assigned_employee_id,
            priority: item.priority || 'Medium',
            priorityScore: item.priority_score,
            confidence: item.confidence,
            upvotes: item.upvote_count || 1,
            isDuplicate: item.is_duplicate,
            masterComplaintId: item.master_complaint_id,
            defectType: item.defect_type,
            visualScore: item.visual_score,
            sla: item.municipal_sla,
            deadlineFormatted: item.deadline_formatted,
            slaIsOverdue: item.sla_is_overdue,
            isNotifiedService: item.workflow_type === 'notified_service',
            designatedOfficer: item.designated_officer,
            appellateAuthority: item.appellate_authority,
            rejectionReason: item.rejection_reason,
            resolutionNotes: item.resolution_notes,
            resolutionProofUrl: item.resolution_proof_url,
            locationLat: item.location_lat || 16.5062,
            locationLng: item.location_lng || 80.6480,
            description: item.description,
            priorityExplanation: item.priority_explanation || (Array.isArray(item.priority_explanation_points) ? item.priority_explanation_points.join(' | ') : undefined),
            isEmergencyOverride: item.is_emergency_override
          };
        });
        setComplaints(mapped);
        if (!selectedPinComplaint && mapped[0]) {
          setSelectedPinComplaint(mapped[0]);
        }
      }

      if (hotspotData && hotspotData.hotspots) {
        setHotspots(hotspotData.hotspots);
      }
    } catch (err) {
      console.warn('Could not load live backend data in employee workspace:', err);
    }
  };

  // Open Structured Investigation Form
  const handleOpenInvestigationModal = (complaint: ComplaintItem) => {
    setInvestigatingComplaint(complaint);
    setInspectionLocation(complaint.location || '');
    setSiteInspectionConducted(true);
    setInvestigationFindings('');
    setInvestigationActionTaken(complaint.resolutionNotes || '');
    setInvestigationNextSteps('');
    setInvestigationStatus(complaint.status === 'Resolved' ? 'resolved' : 'in_progress');
    setInvestigationRejectionReason(complaint.rejectionReason || '');
    setInvestigationPhoto(complaint.resolutionProofUrl || null);
    setInvestigationError('');
    setAiVerification(null);
    setInvestigationModalOpen(true);
  };

  // Submit Structured Investigation Form
  const handleSubmitInvestigation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!investigatingComplaint) return;
    setInvestigationError('');

    // Validation: Mandatory resolution remarks for resolved status
    if (investigationStatus === 'resolved') {
      if (!investigationActionTaken.trim() || investigationActionTaken.trim().length < 8) {
        setInvestigationError('Statutory Compliance Rule: Action taken and resolution remarks must be provided (minimum 8 characters) before marking as resolved.');
        return;
      }
    }

    // Validation: Mandatory rejection reason for rejected status (Sec 8 of Act 6 of 2018)
    if (investigationStatus === 'rejected') {
      if (!investigationRejectionReason.trim() || investigationRejectionReason.trim().length < 10) {
        setInvestigationError('AP Public Services Act Sec 8: A reasoned order explaining the grounds of rejection must be recorded (minimum 10 characters).');
        return;
      }
    }

    const targetId = investigatingComplaint.rawId || investigatingComplaint.id;
    setSubmittingInvestigation(true);
    try {
      // 1. Record structured investigation record
      await api.recordInvestigation({
        complaint_id: targetId,
        employee_id: currentEmpCode,
        employee_name: profile?.name || 'Assigned Cadre Officer',
        investigation_performed: siteInspectionConducted ? 'yes' : 'no',
        location_inspected: inspectionLocation,
        findings: investigationFindings || 'Site inspected by cadre engineer; observations recorded.',
        action_taken: investigationActionTaken.trim() || 'Site inspection conducted; remedial works in progress.',
        supporting_evidence_urls: investigationPhoto ? [investigationPhoto] : undefined,
        further_action_required: investigationNextSteps || undefined,
        is_resolved: investigationStatus === 'resolved',
        inability_reason: investigationStatus === 'rejected' ? investigationRejectionReason : undefined
      });

      // 2. Update status and remarks
      await api.updateComplaintStatus(
        targetId,
        investigationStatus,
        investigationActionTaken || undefined,
        investigationPhoto || undefined,
        currentEmpCode,
        investigationStatus === 'rejected' ? investigationRejectionReason : undefined
      );

      // 3. Update local state
      setComplaints((prev) =>
        prev.map((c) =>
          c.id === investigatingComplaint.id || c.rawId === investigatingComplaint.rawId
            ? {
                ...c,
                status: (investigationStatus === 'resolved' ? 'Resolved' : investigationStatus === 'rejected' ? 'Rejected' : 'In progress') as any,
                resolutionNotes: investigationActionTaken || c.resolutionNotes,
                resolutionProofUrl: investigationPhoto || c.resolutionProofUrl,
                rejectionReason: investigationRejectionReason || c.rejectionReason
              }
            : c
        )
      );

      setInvestigationModalOpen(false);
      fetchLiveWorkspaceData();
    } catch (err: any) {
      setInvestigationError(err.message || 'Failed to submit investigation record.');
    } finally {
      setSubmittingInvestigation(false);
    }
  };

  // Open Activity & Audit History Modal
  const handleOpenAuditModal = async (complaint: ComplaintItem) => {
    setAuditComplaint(complaint);
    setAuditModalOpen(true);
    setLoadingAudit(true);
    const targetId = complaint.rawId || complaint.id;
    try {
      const [logs, investigations] = await Promise.all([
        api.getActivityLogs(targetId).catch(() => []),
        api.getInvestigations(targetId).catch(() => [])
      ]);
      setAuditLogs(logs);
      setAuditInvestigations(investigations);
    } catch (err) {
      console.warn('Failed to load audit history', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  useEffect(() => {
    fetchLiveWorkspaceData();
    const interval = setInterval(fetchLiveWorkspaceData, 8000);
    return () => clearInterval(interval);
  }, [currentEmpCode]);

  // Complaints assigned strictly to this employee
  const myAssignedComplaints = useMemo(() => {
    return complaints.filter((c) => c.assignedEmployeeId === currentEmpCode);
  }, [complaints, currentEmpCode]);

  // Filtered complaints for the active view
  const filteredComplaints = useMemo(() => {
    let list = showOnlyMyTasks ? myAssignedComplaints : complaints;

    if (statusFilter !== 'All') {
      list = list.filter((c) => c.status === statusFilter);
    }

    if (!searchQuery.trim()) return list;
    const q = searchQuery.toLowerCase();
    return list.filter(
      (c) =>
        c.id.toLowerCase().includes(q) ||
        (c.title && c.title.toLowerCase().includes(q)) ||
        c.category.toLowerCase().includes(q) ||
        c.location.toLowerCase().includes(q) ||
        c.assignedTeam.toLowerCase().includes(q) ||
        c.status.toLowerCase().includes(q)
    );
  }, [complaints, myAssignedComplaints, showOnlyMyTasks, statusFilter, searchQuery]);

  // Department unassigned queue (items awaiting staff pickup)
  const departmentQueue = useMemo(() => {
    return complaints.filter((c) => c.status !== 'Resolved');
  }, [complaints]);

  // Self-assign / Pick up an unassigned complaint
  const handleSelfAssign = async (complaint: ComplaintItem) => {
    if (!complaint.rawId && !complaint.id) return;
    const targetId = complaint.rawId || complaint.id;
    try {
      await api.assignComplaint(targetId, currentEmpCode, profile?.departmentName || 'Field Operations');
      // Update local state immediately
      setComplaints((prev) =>
        prev.map((c) =>
          c.id === complaint.id || c.rawId === complaint.rawId
            ? {
                ...c,
                assignedEmployeeId: currentEmpCode,
                assignedTeam: `${profile?.name || 'Assigned Officer'} (${currentEmpCode})`,
                status: 'In progress'
              }
            : c
        )
      );
      // Refresh stats
      fetchLiveWorkspaceData();
    } catch (err) {
      console.warn('Self-assignment note:', err);
    }
  };

  // Status badge styling
  const getStatusBadge = (status: ComplaintItem['status']) => {
    switch (status) {
      case 'New':
        return 'bg-blue-50 text-blue-700 border border-blue-200';
      case 'Under review':
        return 'bg-amber-50 text-amber-800 border border-amber-200';
      case 'In progress':
        return 'bg-teal-50 text-teal-700 border border-teal-200';
      case 'Resolved':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
      case 'Rejected':
        return 'bg-rose-50 text-rose-700 border border-rose-200';
      case 'Reopened':
        return 'bg-purple-50 text-purple-700 border border-purple-200';
      case 'Escalated':
        return 'bg-red-100 text-red-800 border border-red-300 font-bold';
      default:
        return 'bg-slate-50 text-slate-700 border border-slate-200';
    }
  };

  // Save Resolution & Proof
  const handleSaveEdit = async () => {
    if (!editingComplaint) return;
    const targetStatus = editStatus === 'Resolved' ? 'resolved' : editStatus === 'In progress' ? 'in_progress' : 'pending';

    setSavingResolution(true);
    const targetId = editingComplaint.rawId || editingComplaint.id;
    try {
      await api.updateComplaintStatus(
        targetId,
        targetStatus,
        resolutionNotes || undefined,
        resolutionProof || undefined,
        currentEmpCode
      );
    } catch (err) {
      console.warn('Status update backend note:', err);
    }

    setComplaints((prev) =>
      prev.map((c) =>
        c.id === editingComplaint.id || c.rawId === editingComplaint.rawId
          ? {
              ...c,
              status: editStatus,
              assignedTeam: editTeam || c.assignedTeam,
              resolutionNotes: resolutionNotes || c.resolutionNotes,
              resolutionProofUrl: resolutionProof || c.resolutionProofUrl
            }
          : c
      )
    );

    // Refresh live stats
    fetchLiveWorkspaceData();
    setSavingResolution(false);
    setEditingComplaint(null);
  };

  const handleExportReport = () => {
    const listToExport = showOnlyMyTasks ? myAssignedComplaints : complaints;
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Complaint ID,Title,Category,Location,Status,Priority,Assigned Employee']
        .concat(
          listToExport.map(
            (c) =>
              `"${c.id}","${(c.title || '').replace(/"/g, '""')}","${c.category}","${c.location}","${c.status}","${c.priority || 'Medium'}","${c.assignedEmployeeId || 'Unassigned'}"`
          )
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `NEXCIV_${currentEmpCode}_WorkReport_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Dynamic counts for this logged in employee
  const totalMyTasks = myAssignedComplaints.length;
  const pendingMyTasks = myAssignedComplaints.filter((c) => c.status !== 'Resolved').length;
  const inProgressMyTasks = myAssignedComplaints.filter((c) => c.status === 'In progress').length;
  const resolvedMyTasks = myAssignedComplaints.filter((c) => c.status === 'Resolved').length;
  const resolutionRate = totalMyTasks > 0 ? Math.round((resolvedMyTasks / totalMyTasks) * 100) : 85;

  return (
    <div className="min-h-screen bg-black text-slate-100 flex flex-col font-sans selection:bg-teal-500 selection:text-white">
      {/* 1. TOP NAVBAR */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 text-slate-800 px-6 h-16 flex items-center justify-between shadow-2xs">
        {/* Brand & Workspace title */}
        <div className="flex items-center gap-3">
          <Link to="/" className="text-xl font-black tracking-tight text-slate-900">
            NEXCIV
          </Link>
          <span className="text-slate-300 font-light">|</span>
          <span className="text-xs font-bold tracking-widest text-slate-500 uppercase">
            STAFF WORKSPACE
          </span>
        </div>

        {/* Right tools: Search, Notifications, User Badge */}
        <div className="flex items-center gap-4">
          {/* Search box */}
          <div className="relative hidden md:block">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search assigned cases or ID"
              className="w-64 lg:w-72 pl-9 pr-3.5 py-1.5 text-xs rounded-lg border border-slate-200 bg-white placeholder-slate-400 text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition"
            />
          </div>

          {/* Notification Bell */}
          <button
            type="button"
            className="relative p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
            title="Notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-teal-500 ring-2 ring-white"></span>
          </button>

          {/* User Initials Avatar */}
          <div className="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-800 font-bold text-xs flex items-center justify-center select-none shadow-2xs">
            {profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'EM'}
          </div>

          {/* Employee Role Pill */}
          <span className="text-xs font-bold text-slate-700 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full">
            {currentEmpCode} &middot; Field Cadre
          </span>

          {/* Explicit Sign Out Button */}
          <button
            type="button"
            onClick={handleSignOut}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-600 text-rose-700 hover:text-white border border-rose-200 transition text-xs font-bold shadow-2xs cursor-pointer group"
            title="Log out from employee workspace"
          >
            <LogOut size={13} className="text-rose-600 group-hover:text-white transition" />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* 2. BODY: LEFT SIDEBAR + DARK CANVAS WITH FLOATING WHITE CARDS */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-56 bg-white border-r border-slate-200 text-slate-700 flex flex-col justify-between shrink-0 p-4">
          {/* Main Navigation links */}
          <nav className="space-y-1">
            {[
              { name: 'Overview', icon: LayoutGrid },
              { name: 'Complaints', icon: FileText },
              { name: 'Department Queue', icon: Layers },
              { name: 'Map View', icon: Map },
              { name: 'Reports & Analytics', icon: TrendingUp },
              { name: 'Team Management', icon: Users },
              { name: 'Settings', icon: Settings }
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.name;
              return (
                <button
                  key={item.name}
                  onClick={() => setActiveTab(item.name)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all text-left cursor-pointer ${
                    isActive
                      ? 'bg-teal-50 text-teal-800 shadow-2xs'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon size={16} className={isActive ? 'text-teal-700' : 'text-slate-500'} />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* Bottom Sidebar items */}
          <div className="pt-4 border-t border-slate-100 space-y-1">
            <div className="px-3 py-1 text-[11px] font-bold text-slate-400">AP Municipal Admin</div>
            <button
              onClick={() => alert(`NEXCIV Municipal Staff Support\nCadre ID: ${currentEmpCode}\nSupport Helpline: Ext 402 / helpdesk@nexciv.gov`)}
              className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition text-left cursor-pointer"
            >
              <HelpCircle size={16} className="text-slate-400" />
              <span>Help center</span>
            </button>
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition text-left cursor-pointer"
            >
              <LogOut size={16} className="text-rose-500" />
              <span>Sign out</span>
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 bg-black overflow-y-auto p-6 lg:p-8 space-y-6">
          <div className="max-w-7xl mx-auto space-y-6">
            
            {/* Header row */}
            <div className="space-y-2">
              <div className="text-xs text-slate-400 font-medium">
                Andhra Pradesh Municipal Cadre Portal / {profile?.departmentName || 'Municipal Engineering'} / <span className="text-teal-400 font-bold">{activeTab}</span>
              </div>
              
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight">
                      {profile?.name || employeeStats?.name || 'A. Ramesh Kumar'}
                    </h1>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      {currentEmpCode}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-500/15 text-teal-300 border border-teal-500/30">
                      {profile?.designation || employeeStats?.designation || 'Field Executive Engineer'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Manage your assigned civic work orders, upload completion proof photos, and record field resolutions.
                  </p>
                </div>

                {/* Quick actions */}
                <div className="flex items-center gap-2.5 flex-wrap">
                  <button
                    onClick={handleExportReport}
                    className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-100 text-slate-800 text-xs font-bold border border-slate-200 transition shadow-2xs cursor-pointer"
                  >
                    <Download size={14} />
                    <span>Export report</span>
                  </button>

                  <button
                    onClick={fetchLiveWorkspaceData}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-700 transition cursor-pointer"
                    title="Refresh live data"
                  >
                    <RefreshCw size={13} />
                    <span>Sync</span>
                  </button>
                </div>
              </div>
            </div>

            {/* ============================================================ */}
            {/* VIEW 1: OVERVIEW TAB                                         */}
            {/* ============================================================ */}
            {activeTab === 'Overview' && (
              <div className="space-y-6">
                {/* 4 KEY METRIC CARDS */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Card 1: Assigned Work Orders */}
                  <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs text-slate-800 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-600">Assigned Tasks ({currentEmpCode})</span>
                      <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                        <Inbox size={16} />
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-black text-slate-900 tracking-tight">
                        {employeeStats?.assigned_count ?? totalMyTasks}
                      </div>
                      <div className="text-[11px] text-teal-700 font-bold mt-0.5">Cadre work orders</div>
                    </div>
                  </div>

                  {/* Card 2: Pending Work Orders */}
                  <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs text-slate-800 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-600">Pending Resolution</span>
                      <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                        <Scan size={16} />
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-black text-amber-600 tracking-tight">
                        {employeeStats?.pending_count ?? pendingMyTasks}
                      </div>
                      <div className="text-[11px] text-amber-700 font-bold mt-0.5">Awaiting repair proof</div>
                    </div>
                  </div>

                  {/* Card 3: In progress */}
                  <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs text-slate-800 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-600">In Progress (Field Work)</span>
                      <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                        <RotateCw size={16} />
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-black text-blue-700 tracking-tight">
                        {inProgressMyTasks}
                      </div>
                      <div className="text-[11px] text-blue-600 font-bold mt-0.5">Active field crews</div>
                    </div>
                  </div>

                  {/* Card 4: Resolved with Proof */}
                  <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs text-slate-800 flex flex-col justify-between">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-600">Resolved & Verified</span>
                      <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                        <CheckCircle2 size={16} />
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-black text-emerald-600 tracking-tight">
                        {employeeStats?.completed_count ?? resolvedMyTasks}
                      </div>
                      <div className="text-[11px] text-emerald-700 font-bold mt-0.5">
                        {employeeStats?.completion_rate ? Math.round(employeeStats.completion_rate) : resolutionRate}% Resolution Rate
                      </div>
                    </div>
                  </div>
                </div>

                {/* OVERVIEW WORK ORDER QUEUE TABLE */}
                <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">Assigned Work Queue</h3>
                      <p className="text-xs text-slate-500">Cases specifically assigned to your employee ID for field action.</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setShowOnlyMyTasks(true)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                          showOnlyMyTasks ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900 bg-slate-100'
                        }`}
                      >
                        My Cases ({myAssignedComplaints.length})
                      </button>
                      <button
                        onClick={() => setShowOnlyMyTasks(false)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition cursor-pointer ${
                          !showOnlyMyTasks ? 'bg-teal-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900 bg-slate-100'
                        }`}
                      >
                        All Division ({complaints.length})
                      </button>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                          <th className="pb-3">Reference / ID</th>
                          <th className="pb-3">Category & Scope</th>
                          <th className="pb-3">Priority</th>
                          <th className="pb-3">Location & Landmark</th>
                          <th className="pb-3">Statutory SLA / Due</th>
                          <th className="pb-3">Status</th>
                          <th className="pb-3">Assigned Staff</th>
                          <th className="pb-3 text-right pr-2">Investigation & Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {filteredComplaints.length === 0 ? (
                          <tr>
                            <td colSpan={8} className="py-8 text-center text-slate-400">
                              <p className="font-bold text-slate-700">No work orders currently assigned</p>
                              <p className="text-[11px] text-slate-400 mt-0.5">Switch to "Department Queue" tab to pick up unassigned civic complaints.</p>
                            </td>
                          </tr>
                        ) : (
                          filteredComplaints.slice(0, 6).map((item) => {
                            const refCode = item.grievanceRefNumber || item.id;
                            return (
                              <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                                <td className="py-3.5">
                                  <div className="font-mono font-bold text-slate-900">{refCode}</div>
                                  <div className="text-[10px] text-slate-400">{item.id}</div>
                                </td>
                                <td className="py-3.5">
                                  <div className="font-bold text-slate-800">{item.category}</div>
                                  <div className="flex items-center gap-1 mt-0.5">
                                    {item.isNotifiedService ? (
                                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold flex items-center gap-0.5">
                                        <Scale size={9} />
                                        <span>Act 6/2018</span>
                                      </span>
                                    ) : (
                                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-medium">
                                        Charter
                                      </span>
                                    )}
                                    {item.confidence && (
                                      <span className="text-[9px] text-emerald-600 font-mono">
                                        {Math.round(item.confidence * 100)}%
                                      </span>
                                    )}
                                  </div>
                                </td>
                                <td className="py-3.5">
                                  <span
                                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                                      item.priority?.toLowerCase() === 'critical'
                                        ? 'bg-red-100 text-red-800 border border-red-200'
                                        : item.priority?.toLowerCase() === 'high'
                                        ? 'bg-orange-100 text-orange-800 border border-orange-200'
                                        : 'bg-amber-100 text-amber-800 border border-amber-200'
                                    }`}
                                  >
                                    {item.priority?.toLowerCase() === 'critical' && <Flame size={10} />}
                                    {item.priority || 'Medium'} {item.priorityScore ? `(${Math.round(item.priorityScore)})` : ''}
                                  </span>
                                </td>
                                <td className="py-3.5 text-slate-600 max-w-[180px] truncate">
                                  <div>{item.location}</div>
                                  {item.landmark && <div className="text-[10px] text-slate-400 truncate">{item.landmark}</div>}
                                </td>
                                <td className="py-3.5">
                                  <div className="text-slate-700 font-medium text-[11px]">{item.deadlineFormatted || item.sla || 'Within 7 AP Days'}</div>
                                  {item.slaIsOverdue ? (
                                    <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-red-600 animate-pulse">
                                      <AlertTriangle size={10} /> Overdue
                                    </span>
                                  ) : (
                                    <span className="text-[10px] text-emerald-600">On Track</span>
                                  )}
                                </td>
                                <td className="py-3.5">
                                  <span className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold ${getStatusBadge(item.status)}`}>
                                    {item.status}
                                  </span>
                                </td>
                                <td className="py-3.5 text-slate-700 font-medium">
                                  {item.assignedEmployeeId === currentEmpCode ? (
                                    <span className="text-teal-700 font-bold">You ({currentEmpCode})</span>
                                  ) : (
                                    item.assignedEmployeeId || 'Unassigned'
                                  )}
                                </td>
                                <td className="py-3.5 text-right pr-2">
                                  <div className="flex items-center justify-end gap-1.5 flex-wrap">
                                    <button
                                      onClick={() => handleOpenInvestigationModal(item)}
                                      className="inline-flex items-center gap-1 px-2.5 py-1 bg-teal-50 hover:bg-teal-600 text-teal-700 hover:text-white rounded-lg font-bold text-xs transition border border-teal-200 cursor-pointer"
                                      title="Record Structured Investigation / Disposal"
                                    >
                                      <ClipboardCheck size={12} />
                                      <span>Investigate</span>
                                    </button>

                                    <button
                                      onClick={() => handleOpenAuditModal(item)}
                                      className="inline-flex items-center p-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-xs transition"
                                      title="View Activity & Investigation Logs"
                                    >
                                      <History size={13} />
                                    </button>

                                    <Link
                                      to={`/complaint/${item.rawId || item.id}`}
                                      className="inline-flex items-center p-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs transition"
                                      title="Open Full Case Dossier"
                                    >
                                      <ExternalLink size={13} />
                                    </Link>
                                  </div>
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* REGIONAL HOTSPOTS WORK ORDERS SECTION */}
                {hotspots.length > 0 && (
                  <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center">
                          <Layers size={16} />
                        </div>
                        <div>
                          <h3 className="text-sm font-bold text-slate-900">Incident Hotspots & Consolidated Work Orders</h3>
                          <p className="text-[11px] text-slate-500">
                            Phase 2 AI merges duplicate nearby reports into single dispatch work orders.
                          </p>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-200">
                        {hotspots.length} Active Hotspots
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 pt-1">
                      {hotspots.map((h: any) => (
                        <div key={h.cluster_id} className="p-4 rounded-xl border border-teal-100 bg-teal-50/40 flex flex-col justify-between">
                          <div>
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-teal-900 tracking-tight">{h.cluster_id}</span>
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-200 text-teal-900">
                                {h.complaint_count || h.count || 3} Reports Merged
                              </span>
                            </div>
                            <p className="text-xs font-bold text-slate-900 mt-2 line-clamp-1">{h.primary_title || h.department}</p>
                            <p className="text-[11px] text-slate-600 mt-0.5 line-clamp-1">{h.address_sample || h.location || 'Local corridor'}</p>
                          </div>
                          <div className="mt-3 pt-2.5 border-t border-teal-200/60 flex items-center justify-between text-[11px] text-slate-600 font-mono">
                            <span>({(h.centroid_lat || h.latitude || 16.5).toFixed(3)}, {(h.centroid_lng || h.longitude || 80.6).toFixed(3)})</span>
                            <span className="text-teal-800 font-bold">Priority Unit</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 2: COMPLAINTS TAB (Dedicated Field Work Orders)         */}
            {/* ============================================================ */}
            {activeTab === 'Complaints' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-black text-slate-900">Field Work Orders Management</h2>
                    <p className="text-xs text-slate-500">
                      Direct queue assigned to <span className="font-bold text-teal-700">{currentEmpCode}</span>. Update status and attach resolution proof photos.
                    </p>
                  </div>

                  {/* Filter Pills */}
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {(['All', 'In progress', 'New', 'Resolved'] as const).map((st) => (
                      <button
                        key={st}
                        onClick={() => setStatusFilter(st)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                          statusFilter === st
                            ? 'bg-teal-600 text-white shadow-xs'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Complaint Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  {filteredComplaints.length === 0 ? (
                    <div className="col-span-2 py-12 text-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl">
                      <Inbox size={32} className="mx-auto text-slate-300 mb-2" />
                      <p className="font-bold text-slate-700">No work orders match this filter</p>
                      <p className="text-xs text-slate-400 mt-1">Try clearing your search query or selecting a different status filter.</p>
                    </div>
                  ) : (
                    filteredComplaints.map((item) => {
                      const refCode = item.grievanceRefNumber || item.id;
                      return (
                        <div
                          key={item.id}
                          className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-teal-300 hover:shadow-md transition-all flex flex-col justify-between space-y-3"
                        >
                          <div className="space-y-2">
                            <div className="flex items-center justify-between gap-2 flex-wrap">
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="font-mono font-black text-xs text-slate-900 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-2xs">
                                  {refCode}
                                </span>
                                {item.isNotifiedService ? (
                                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold flex items-center gap-1">
                                    <Scale size={10} />
                                    <span>Act 6/2018 Notified</span>
                                  </span>
                                ) : (
                                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                                    Citizen Charter
                                  </span>
                                )}
                              </div>
                              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${getStatusBadge(item.status)}`}>
                                {item.status}
                              </span>
                            </div>

                            <h4 className="text-sm font-bold text-slate-900 line-clamp-2">
                              {item.title || `${item.category} Incident at ${item.location}`}
                            </h4>

                            {item.description && (
                              <p className="text-xs text-slate-600 line-clamp-2 bg-white/70 p-2 rounded-lg border border-slate-100">
                                {item.description}
                              </p>
                            )}

                            <div className="space-y-1 text-xs text-slate-600">
                              <div className="flex items-center gap-1.5">
                                <MapPin size={13} className="text-teal-600 shrink-0" />
                                <span className="truncate">{item.location}</span>
                              </div>
                              {item.landmark && (
                                <div className="text-[11px] text-slate-500 pl-5">
                                  Landmark: <strong>{item.landmark}</strong> {item.ward ? `(Ward ${item.ward})` : ''}
                                </div>
                              )}
                              <div className="flex items-center justify-between text-[11px] pt-1">
                                <span className="text-slate-500 font-medium">
                                  Due: <strong>{item.deadlineFormatted || item.sla || 'Within 7 AP Working Days'}</strong>
                                </span>
                                {item.slaIsOverdue ? (
                                  <span className="font-bold text-red-600 flex items-center gap-1 animate-pulse">
                                    <AlertTriangle size={11} />
                                    <span>Overdue Default</span>
                                  </span>
                                ) : (
                                  <span className="text-emerald-700 font-semibold">Statutory Target Active</span>
                                )}
                              </div>
                            </div>

                            {item.resolutionProofUrl && (
                              <div className="mt-2 pt-2 border-t border-slate-200">
                                <span className="text-[10px] font-bold text-emerald-700 uppercase block mb-1">Attached Completion Proof</span>
                                <img
                                  src={item.resolutionProofUrl}
                                  alt="Resolution evidence"
                                  className="w-24 h-24 object-cover rounded-xl border border-emerald-300 shadow-2xs"
                                />
                              </div>
                            )}

                            {item.resolutionNotes && (
                              <p className="text-xs text-slate-600 bg-white p-2.5 rounded-xl border border-slate-200 italic">
                                "{item.resolutionNotes}"
                              </p>
                            )}

                            {item.rejectionReason && (
                              <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
                                <span className="font-bold block text-[10px] uppercase">Statutory Rejection Grounds:</span>
                                <span>{item.rejectionReason}</span>
                              </div>
                            )}

                            {/* AI Priority Explainability Panel */}
                            {item.priorityExplanation && (
                              <div className="mt-2.5 p-2.5 rounded-xl bg-indigo-50/70 border border-indigo-200/80 text-xs text-slate-800">
                                <div className="flex items-center gap-1.5 font-bold text-[11px] text-indigo-900 mb-1">
                                  <Sparkles size={13} className="text-indigo-600 shrink-0" />
                                  <span>Why was this complaint assigned {item.priority || 'High'} Priority?</span>
                                </div>
                                <p className="text-[11px] text-slate-700 leading-relaxed font-sans">
                                  {item.priorityExplanation}
                                </p>
                              </div>
                            )}
                          </div>

                          {/* Card Footer Actions */}
                          <div className="pt-3 border-t border-slate-200 flex items-center justify-between gap-2 flex-wrap">
                            <div className="text-[11px] font-bold text-slate-500 flex items-center gap-2 flex-wrap">
                              <span>Priority: <span className="text-rose-600">{item.priority || 'Medium'}</span> {item.priorityScore ? `(${Math.round(item.priorityScore)}/100)` : ''}</span>
                              {item.masterComplaintId && (
                                <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold bg-indigo-50 border border-indigo-200 text-indigo-700 px-2 py-0.5 rounded-md">
                                  <span>Incident: {item.masterComplaintId}</span>
                                  {item.isDuplicate && (
                                    <span className="bg-amber-100 text-amber-800 text-[9px] px-1 rounded font-sans">Duplicate Linked</span>
                                  )}
                                </span>
                              )}
                            </div>

                            <div className="flex items-center gap-1.5 ml-auto">
                              <button
                                onClick={() => handleOpenAuditModal(item)}
                                className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold text-xs transition flex items-center gap-1"
                                title="Audit Trail"
                              >
                                <History size={12} />
                                <span>Audit</span>
                              </button>

                              <Link
                                to={`/complaint/${item.rawId || item.id}`}
                                className="p-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-xl text-xs transition"
                                title="Open Full Dossier"
                              >
                                <ExternalLink size={13} />
                              </Link>

                              <button
                                onClick={() => handleOpenInvestigationModal(item)}
                                className="inline-flex items-center gap-1 px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer"
                              >
                                <ClipboardCheck size={13} />
                                <span>Investigate</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 3: DEPARTMENT QUEUE TAB (Open items to pick up)          */}
            {/* ============================================================ */}
            {activeTab === 'Department Queue' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-black text-slate-900">Municipal Department Intake Queue</h2>
                    <p className="text-xs text-slate-500">
                      Broad department cases awaiting field dispatch. You can self-assign any open task to your work queue.
                    </p>
                  </div>
                  <span className="text-xs font-bold text-teal-800 bg-teal-50 px-3 py-1.5 rounded-xl border border-teal-200">
                    {departmentQueue.length} Active Intake Cases
                  </span>
                </div>

                <div className="overflow-x-auto pt-2">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                        <th className="pb-3">Case ID</th>
                        <th className="pb-3">Title & Category</th>
                        <th className="pb-3">Location & Landmark</th>
                        <th className="pb-3">Priority Score</th>
                        <th className="pb-3">Current Assignment</th>
                        <th className="pb-3 text-right pr-2">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {departmentQueue.map((item) => {
                        const isAssignedToMe = item.assignedEmployeeId === currentEmpCode;
                        return (
                          <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                            <td className="py-3.5 font-bold text-slate-900 font-mono">{item.id}</td>
                            <td className="py-3.5">
                              <div className="font-bold text-slate-900 line-clamp-1">{item.title}</div>
                              <div className="text-[11px] text-teal-700 font-semibold">{item.category}</div>
                            </td>
                            <td className="py-3.5 text-slate-600 max-w-[220px] truncate">
                              {item.location} {item.landmark ? `(${item.landmark})` : ''}
                            </td>
                            <td className="py-3.5">
                              <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                                {item.priority || 'Medium'} {item.priorityScore ? `(${Math.round(item.priorityScore)})` : ''}
                              </span>
                            </td>
                            <td className="py-3.5 font-medium">
                              {isAssignedToMe ? (
                                <span className="text-emerald-700 font-bold">Assigned to You</span>
                              ) : item.assignedEmployeeId ? (
                                <span className="text-slate-600">{item.assignedEmployeeId}</span>
                              ) : (
                                <span className="text-amber-600 font-bold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                                  Unassigned
                                </span>
                              )}
                            </td>
                            <td className="py-3.5 text-right pr-2">
                              {isAssignedToMe ? (
                                <span className="text-xs font-bold text-emerald-600 inline-flex items-center gap-1">
                                  <Check size={14} /> In your queue
                                </span>
                              ) : (
                                <button
                                  type="button"
                                  onClick={() => handleSelfAssign(item)}
                                  className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer"
                                >
                                  Pick Up Task
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 4: MAP VIEW TAB (Geospatial Cadre Grid)                  */}
            {/* ============================================================ */}
            {activeTab === 'Map View' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-black text-slate-900">Geospatial GIS Cadre Map</h2>
                    <p className="text-xs text-slate-500">
                      Geographic distribution of municipal complaints and cluster hotspots across Andhra Pradesh.
                    </p>
                  </div>
                  <div className="text-xs font-bold text-slate-600 flex items-center gap-3">
                    <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" /> Critical</span>
                    <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> High/Medium</span>
                    <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Resolved</span>
                  </div>
                </div>

                {/* Google Maps GIS Cadre Grid with Real Coordinates & Turn-by-Turn Navigation */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                  <div className="lg:col-span-2 relative rounded-2xl overflow-hidden border border-slate-200 shadow-sm h-[440px] flex flex-col bg-slate-100">
                    {/* Header overlay with Google Maps status */}
                    <div className="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between text-xs font-bold shrink-0">
                      <div className="flex items-center gap-2">
                        <MapPin size={15} className="text-teal-400" />
                        <span>Google Maps AP Municipal Radar &bull; {selectedPinComplaint ? selectedPinComplaint.id : 'AP Cadre Grid'}</span>
                      </div>
                      <a
                        href={`https://www.google.com/maps/dir/?api=1&destination=${selectedPinComplaint?.locationLat || 16.5062},${selectedPinComplaint?.locationLng || 80.6480}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-600 hover:bg-teal-500 text-white rounded-lg text-[11px] font-bold transition shadow-xs"
                      >
                        <ExternalLink size={12} />
                        <span>Turn-by-Turn Navigation ↗</span>
                      </a>
                    </div>

                    {/* Live Google Maps Iframe Embed */}
                    <iframe
                      title="Google Maps AP Location"
                      src={`https://maps.google.com/maps?q=${selectedPinComplaint?.locationLat || 16.5062},${selectedPinComplaint?.locationLng || 80.6480}&hl=en&z=15&output=embed`}
                      className="w-full flex-1 border-0"
                      loading="lazy"
                    />

                    {/* Complaint Quick Pins Pill Bar */}
                    {complaints.length > 0 && (
                      <div className="bg-white/95 backdrop-blur-xs p-2.5 border-t border-slate-200 flex items-center gap-2 overflow-x-auto shrink-0">
                        <span className="text-[11px] font-bold text-slate-500 uppercase shrink-0">Incidents:</span>
                        {complaints.map((item) => (
                          <button
                            key={item.id}
                            type="button"
                            onClick={() => setSelectedPinComplaint(item)}
                            className={`px-2.5 py-1 rounded-lg text-xs font-bold shrink-0 transition flex items-center gap-1.5 cursor-pointer ${
                              selectedPinComplaint?.id === item.id
                                ? 'bg-[#0e2238] text-white shadow-xs ring-1 ring-teal-400'
                                : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                            }`}
                          >
                            <span className={`w-2 h-2 rounded-full ${
                              item.priority?.toLowerCase() === 'critical' ? 'bg-rose-500' : item.status === 'Resolved' ? 'bg-emerald-500' : 'bg-amber-500'
                            }`} />
                            <span>{item.id}</span>
                            <span className="text-[10px] opacity-75 truncate max-w-[120px]">{item.title?.slice(0, 18)}...</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Selected Pin Details Card */}
                  <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col justify-between space-y-3">
                    {selectedPinComplaint ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                            {selectedPinComplaint.id}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getStatusBadge(selectedPinComplaint.status)}`}>
                            {selectedPinComplaint.status}
                          </span>
                        </div>

                        <div>
                          <h4 className="text-sm font-black text-slate-900">{selectedPinComplaint.title}</h4>
                          <p className="text-xs text-slate-500 mt-1">{selectedPinComplaint.category}</p>
                        </div>

                        <div className="text-xs text-slate-700 space-y-1.5 bg-white p-3 rounded-xl border border-slate-200">
                          <div><strong>Location:</strong> {selectedPinComplaint.location}</div>
                          {selectedPinComplaint.landmark && <div><strong>Landmark:</strong> {selectedPinComplaint.landmark}</div>}
                          {selectedPinComplaint.ward && <div><strong>Ward:</strong> {selectedPinComplaint.ward}</div>}
                          <div><strong>GPS Coordinates:</strong> {selectedPinComplaint.locationLat || 16.5062}° N, {selectedPinComplaint.locationLng || 80.6480}° E</div>
                          <div><strong>Priority Score:</strong> {Math.round(selectedPinComplaint.priorityScore || 75)}/100</div>
                          <div><strong>Assigned To:</strong> {selectedPinComplaint.assignedEmployeeId || 'Unassigned'}</div>
                        </div>

                        <div className="space-y-2">
                          <a
                            href={`https://www.google.com/maps/dir/?api=1&destination=${selectedPinComplaint.locationLat || 16.5062},${selectedPinComplaint.locationLng || 80.6480}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center gap-1.5"
                          >
                            <ExternalLink size={14} />
                            <span>Navigate via Google Maps ↗</span>
                          </a>

                          <button
                            type="button"
                            onClick={() => {
                              setEditingComplaint(selectedPinComplaint);
                              setEditStatus(selectedPinComplaint.status === 'Resolved' ? 'Resolved' : 'In progress');
                              setEditTeam(selectedPinComplaint.assignedTeam);
                            }}
                            className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs rounded-xl shadow-xs transition cursor-pointer"
                          >
                            Take Action on this Incident
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="my-auto text-center py-8 text-slate-400">
                        <MapPin size={28} className="mx-auto text-slate-300 mb-2" />
                        <p className="text-xs font-bold text-slate-700">Click any incident pin above</p>
                        <p className="text-[11px] text-slate-400 mt-1">To view live Google Maps GPS coordinates, category, and citizen report details.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 5: REPORTS & ANALYTICS TAB                              */}
            {/* ============================================================ */}
            {activeTab === 'Reports & Analytics' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-6">
                <div>
                  <h2 className="text-lg font-black text-slate-900">Cadre Performance Dossier & Analytics</h2>
                  <p className="text-xs text-slate-500">
                    Official resolution performance audit for officer <span className="font-bold text-teal-700">{currentEmpCode}</span> under AP Municipal Administration guidelines.
                  </p>
                </div>

                {/* Scorecards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-4 rounded-xl bg-teal-50 border border-teal-100">
                    <span className="text-xs font-bold text-teal-700 uppercase">SLA Compliance</span>
                    <div className="text-2xl font-black text-teal-900 mt-1">94.2%</div>
                    <span className="text-[10px] text-teal-600 font-semibold">Exceeds state target</span>
                  </div>

                  <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
                    <span className="text-xs font-bold text-blue-700 uppercase">Avg. Turnaround</span>
                    <div className="text-2xl font-black text-blue-900 mt-1">
                      {employeeStats?.avg_resolution_days ? `${employeeStats.avg_resolution_days} Days` : '1.8 Days'}
                    </div>
                    <span className="text-[10px] text-blue-600 font-semibold">Standard SLA 48h</span>
                  </div>

                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
                    <span className="text-xs font-bold text-emerald-700 uppercase">Completed Work</span>
                    <div className="text-2xl font-black text-emerald-900 mt-1">
                      {employeeStats?.completed_count ?? resolvedMyTasks}
                    </div>
                    <span className="text-[10px] text-emerald-600 font-semibold">Verified with proof</span>
                  </div>

                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                    <span className="text-xs font-bold text-amber-700 uppercase">Citizen Rating</span>
                    <div className="text-2xl font-black text-amber-900 mt-1">
                      {employeeStats?.rating ? `${employeeStats.rating} / 5.0` : '4.8 / 5.0'}
                    </div>
                    <span className="text-[10px] text-amber-600 font-semibold">Cadre Tier 1</span>
                  </div>
                </div>

                {/* Download Dossier */}
                <div className="p-5 rounded-2xl border border-slate-200 bg-slate-50 flex items-center justify-between gap-4">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Official Cadre Evaluation Summary</h4>
                    <p className="text-xs text-slate-500 mt-0.5">Download official CSV performance log signed with AP Municipal Administration timestamp.</p>
                  </div>
                  <button
                    onClick={handleExportReport}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer shrink-0"
                  >
                    <Download size={14} />
                    <span>Download Dossier</span>
                  </button>
                </div>
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 6: TEAM MANAGEMENT TAB                                  */}
            {/* ============================================================ */}
            {activeTab === 'Team Management' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-black text-slate-900">Municipal Cadre Division Team</h2>
                    <p className="text-xs text-slate-500">
                      Officers and engineers deployed across the municipal engineering wings in your corporation.
                    </p>
                  </div>

                  <div className="relative">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={colleagueSearch}
                      onChange={(e) => setColleagueSearch(e.target.value)}
                      placeholder="Search colleague or designation"
                      className="pl-9 pr-3.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 text-slate-800 font-medium focus:outline-none focus:border-teal-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
                  {colleaguesList
                    .filter((c) =>
                      !colleagueSearch.trim() ||
                      c.name.toLowerCase().includes(colleagueSearch.toLowerCase()) ||
                      c.designation?.toLowerCase().includes(colleagueSearch.toLowerCase()) ||
                      c.department?.toLowerCase().includes(colleagueSearch.toLowerCase())
                    )
                    .map((colleague) => (
                      <div
                        key={colleague.id}
                        className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:shadow-xs transition space-y-3"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 font-black text-sm flex items-center justify-center shrink-0">
                            {colleague.initials || colleague.name.slice(0, 2).toUpperCase()}
                          </div>
                          <div className="min-w-0">
                            <h4 className="text-xs font-bold text-slate-900 truncate">{colleague.name}</h4>
                            <p className="text-[11px] text-teal-700 font-semibold truncate">{colleague.designation || 'Municipal Engineer'}</p>
                            <span className="font-mono text-[10px] text-slate-400 font-bold">{colleague.id}</span>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-center text-[10px] bg-white p-2 rounded-xl border border-slate-100">
                          <div>
                            <span className="text-slate-400 block font-semibold">Assigned</span>
                            <span className="font-black text-slate-800">{colleague.assigned_count ?? 24}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-semibold">Done</span>
                            <span className="font-black text-emerald-600">{colleague.completed_count ?? 20}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-semibold">Pending</span>
                            <span className="font-black text-amber-600">{colleague.pending_count ?? 4}</span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-[11px] pt-1">
                          <span className="text-slate-500">{colleague.department}</span>
                          <span className="text-emerald-700 font-bold flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Active Cadre
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* ============================================================ */}
            {/* VIEW 7: SETTINGS TAB                                         */}
            {/* ============================================================ */}
            {activeTab === 'Settings' && (
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs text-slate-800 space-y-6 max-w-3xl">
                <div>
                  <h2 className="text-lg font-black text-slate-900">Cadre Officer Profile & Alert Preferences</h2>
                  <p className="text-xs text-slate-500">
                    Configuration settings for employee <span className="font-bold text-teal-700">{currentEmpCode}</span>.
                  </p>
                </div>

                {/* Profile Details */}
                <div className="space-y-4 pt-1">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">Officer Name</label>
                      <input
                        type="text"
                        disabled
                        value={profile?.name || employeeStats?.name || 'A. Ramesh Kumar'}
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-semibold"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">Employee Code</label>
                      <input
                        type="text"
                        disabled
                        value={currentEmpCode}
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 font-mono font-bold text-teal-700"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">Cadre Designation</label>
                      <input
                        type="text"
                        disabled
                        value={profile?.designation || employeeStats?.designation || 'Field Executive Engineer'}
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-semibold"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">Municipal Department Wing</label>
                      <input
                        type="text"
                        disabled
                        value={profile?.departmentName || 'Roads & Buildings'}
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-semibold"
                      />
                    </div>
                  </div>

                  {/* Notification Alert Toggles */}
                  <div className="pt-4 border-t border-slate-200 space-y-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">Dispatch Notification Alerts</h4>
                    
                    <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer">
                      <div>
                        <div className="text-xs font-bold text-slate-900">SMS Critical Dispatch Alerts</div>
                        <div className="text-[11px] text-slate-500">Immediate SMS when a priority 95+ critical case is assigned</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={alertSms}
                        onChange={(e) => setAlertSms(e.target.checked)}
                        className="w-4 h-4 accent-teal-600 rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer">
                      <div>
                        <div className="text-xs font-bold text-slate-900">Daily Workload Digest Email</div>
                        <div className="text-[11px] text-slate-500">Daily 8:00 AM summary of pending cases and SLA deadlines</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={alertEmail}
                        onChange={(e) => setAlertEmail(e.target.checked)}
                        className="w-4 h-4 accent-teal-600 rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer">
                      <div>
                        <div className="text-xs font-bold text-slate-900">Emergency Dispatch Audio Tone</div>
                        <div className="text-[11px] text-slate-500">Chime alert when new emergency case drops into department intake</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={soundAlert}
                        onChange={(e) => setSoundAlert(e.target.checked)}
                        className="w-4 h-4 accent-teal-600 rounded"
                      />
                    </label>
                  </div>

                  {settingsSaved && (
                    <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-2">
                      <CheckCircle2 size={16} />
                      <span>Officer preferences saved successfully!</span>
                    </div>
                  )}

                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={() => {
                        setSettingsSaved(true);
                        setTimeout(() => setSettingsSaved(false), 3000);
                      }}
                      className="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer"
                    >
                      Save Preferences
                    </button>
                  </div>

                  {/* Cadre Security & Password Management */}
                  <div className="pt-6 border-t border-slate-200 space-y-4">
                    <div className="flex items-center gap-2">
                      <Lock size={16} className="text-teal-700" />
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                        Cadre Security & Password Management
                      </h4>
                    </div>

                    {empPassSuccess && (
                      <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-2">
                        <CheckCircle2 size={16} />
                        <span>{empPassSuccess}</span>
                      </div>
                    )}

                    {empPassError && (
                      <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold">
                        {empPassError}
                      </div>
                    )}

                    <form onSubmit={handleEmployeeChangePassword} className="space-y-3">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-bold text-slate-700 mb-1">New Password *</label>
                          <div className="relative">
                            <input
                              type={showEmpNew ? 'text' : 'password'}
                              required
                              value={empNewPass}
                              onChange={(e) => setEmpNewPass(e.target.value)}
                              placeholder="Minimum 4 characters"
                              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-xs font-medium focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-9"
                            />
                            <button
                              type="button"
                              onClick={() => setShowEmpNew(!showEmpNew)}
                              className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 cursor-pointer"
                            >
                              {showEmpNew ? <EyeOff size={14} /> : <Eye size={14} />}
                            </button>
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-slate-700 mb-1">Confirm New Password *</label>
                          <div className="relative">
                            <input
                              type={showEmpConfirm ? 'text' : 'password'}
                              required
                              value={empConfirmPass}
                              onChange={(e) => setEmpConfirmPass(e.target.value)}
                              placeholder="Re-enter new password"
                              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-xs font-medium focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-9"
                            />
                            <button
                              type="button"
                              onClick={() => setShowEmpConfirm(!showEmpConfirm)}
                              className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 cursor-pointer"
                            >
                              {showEmpConfirm ? <EyeOff size={14} /> : <Eye size={14} />}
                            </button>
                          </div>
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={empPassUpdating}
                        className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer flex items-center gap-1.5"
                      >
                        <KeyRound size={13} />
                        <span>{empPassUpdating ? 'Updating...' : 'Update Cadre Password'}</span>
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            )}

            {/* BOTTOM FOOTER */}
            <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
              <div>NEXCIV Staff Workspace &middot; Municipal Cadre Admin</div>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => alert(`NEXCIV Help Desk: helpdesk@nexciv.gov\nCadre ID: ${currentEmpCode}`)}
                  className="hover:text-slate-200 transition cursor-pointer"
                >
                  Help
                </button>
                <button
                  onClick={() => alert('NEXCIV Municipal Data Security & Privacy Policy')}
                  className="hover:text-slate-200 transition cursor-pointer"
                >
                  Privacy
                </button>
              </div>
            </div>

          </div>
        </main>
      </div>

      {/* WORK RESOLUTION & PROOF SUBMISSION MODAL */}
      {editingComplaint && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white text-slate-800 rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-black text-slate-900">
                  Update Work Order Resolution
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Case <span className="font-mono font-bold text-teal-700">{editingComplaint.id}</span> &bull; {editingComplaint.category} &bull; {editingComplaint.location}
                </p>
              </div>
              <button
                onClick={() => setEditingComplaint(null)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3.5 pt-1">
              {/* Google Maps Incident Location Embed */}
              <div className="rounded-xl overflow-hidden border border-slate-200 shadow-2xs">
                <iframe
                  title="Incident Google Maps Location"
                  src={`https://maps.google.com/maps?q=${editingComplaint.locationLat || 16.5062},${editingComplaint.locationLng || 80.6480}&hl=en&z=15&output=embed`}
                  className="w-full h-32 border-0"
                  loading="lazy"
                />
                <div className="bg-slate-50 px-3 py-1.5 flex items-center justify-between text-[11px] text-slate-600 font-medium border-t border-slate-200">
                  <span className="truncate max-w-[260px]">{editingComplaint.location}</span>
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${editingComplaint.locationLat || 16.5062},${editingComplaint.locationLng || 80.6480}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-teal-700 font-bold hover:underline flex items-center gap-1 shrink-0"
                  >
                    <span>Google Maps ↗</span>
                    <ExternalLink size={11} />
                  </a>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Work Order Status</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value as ComplaintItem['status'])}
                  className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none font-bold"
                >
                  <option value="In progress">In progress (Crew deployed on site)</option>
                  <option value="Resolved">Resolved (Work completed & proof attached)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Upload Resolution Proof Photo (Evidence of Completed Work)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onloadend = () => {
                        const resultStr = reader.result as string;
                        setResolutionProof(resultStr);
                        runAiVerification(resultStr);
                      };
                      reader.readAsDataURL(file);
                    }
                  }}
                  className="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
                />
                {resolutionProof && (
                  <div className="mt-2.5 space-y-2">
                    <div className="relative inline-block">
                      <img src={resolutionProof} alt="Repair proof" className="w-28 h-28 object-cover rounded-xl border-2 border-emerald-400 shadow-sm" />
                      <button
                        type="button"
                        onClick={() => {
                          setResolutionProof(null);
                          setAiVerification(null);
                        }}
                        className="absolute -top-1.5 -right-1.5 bg-red-600 text-white rounded-full p-1 shadow cursor-pointer"
                      >
                        <X size={11} />
                      </button>
                    </div>

                    {verifyingWithAi && (
                      <div className="text-xs text-teal-700 font-bold flex items-center gap-2">
                        <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-teal-600 border-t-transparent" />
                        <span>Running Phase 3 Computer Vision Resolution Audit...</span>
                      </div>
                    )}

                    {aiVerification && (
                      <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs space-y-1.5 animate-fade-in">
                        <div className="flex items-center justify-between text-emerald-900 font-bold">
                          <span className="flex items-center gap-1.5">
                            <Sparkles size={14} className="text-emerald-600" />
                            <span>Phase 3 AI Resolution Audit</span>
                          </span>
                          <span className="bg-emerald-200/70 text-emerald-900 px-2 py-0.5 rounded text-[10px] font-black">
                            {aiVerification.qualityGrade} &bull; {aiVerification.confidenceScore}%
                          </span>
                        </div>
                        <p className="text-[11px] text-emerald-800">{aiVerification.auditSummary}</p>
                        <div className="flex items-center gap-3 text-[10px] text-emerald-700 font-semibold pt-0.5">
                          <span>Texture Smoothness: {aiVerification.textureSmoothnessScore}%</span>
                          <span>Defect Edge Reduction: {aiVerification.edgeReductionPercent}%</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Engineer Completion Remarks & Details
                </label>
                <textarea
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="e.g. Filled crater with bituminous asphalt; surface leveled and rolled. Reopened street for normal traffic."
                  className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none font-medium resize-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setEditingComplaint(null)}
                className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={savingResolution}
                onClick={handleSaveEdit}
                className="px-5 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition shadow-sm flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <CheckCircle2 size={14} />
                <span>{savingResolution ? 'Saving...' : 'Submit Proof & Update Work Order'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 5.2 STRUCTURED INVESTIGATION & COMPLIANCE MODAL               */}
      {/* ============================================================ */}
      {investigationModalOpen && investigatingComplaint && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white text-slate-800 rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 my-8 space-y-4 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-slate-100 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-teal-50 text-teal-700">
                    <ClipboardCheck size={18} />
                  </span>
                  <h3 className="text-base font-black text-slate-900">
                    Field Investigation & Statutory Disposal
                  </h3>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Ref: <span className="font-mono font-bold text-teal-800">{investigatingComplaint.grievanceRefNumber || investigatingComplaint.id}</span> &bull; {investigatingComplaint.category}
                </p>
              </div>
              <button
                onClick={() => setInvestigationModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {/* Legal Framework Notice Banner */}
            <div className={`p-3 rounded-2xl text-xs flex items-start gap-2.5 ${
              investigatingComplaint.isNotifiedService
                ? 'bg-indigo-50 border border-indigo-200 text-indigo-900'
                : 'bg-slate-100 border border-slate-200 text-slate-700'
            }`}>
              <Scale size={16} className={investigatingComplaint.isNotifiedService ? 'text-indigo-600 mt-0.5' : 'text-slate-500 mt-0.5'} />
              <div>
                <span className="font-bold block">
                  {investigatingComplaint.isNotifiedService
                    ? 'AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018) Statutory Case'
                    : 'Municipal Citizen Charter & PGRS Grievance Handling Guidelines'}
                </span>
                <span className="text-[11px] leading-relaxed">
                  {investigatingComplaint.isNotifiedService
                    ? 'Disposal and reasoned orders are subject to statutory Section 8 compliance. Rejections require mandatory written reasons.'
                    : 'Grievance resolution will be verified by the supervising division officer and citizen feedback.'}
                </span>
              </div>
            </div>

            {investigationError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold flex items-center gap-2">
                <AlertCircle size={15} />
                <span>{investigationError}</span>
              </div>
            )}

            <form onSubmit={handleSubmitInvestigation} className="space-y-4">
              {/* Site Inspection Check */}
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                <label className="text-xs font-bold text-slate-800 flex items-center justify-between">
                  <span>Site Inspection Conducted?</span>
                  <input
                    type="checkbox"
                    checked={siteInspectionConducted}
                    onChange={(e) => setSiteInspectionConducted(e.target.checked)}
                    className="w-4 h-4 rounded text-teal-600 focus:ring-teal-500"
                  />
                </label>
                {siteInspectionConducted && (
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                      Inspection Location / Landmarks Inspected
                    </label>
                    <input
                      type="text"
                      value={inspectionLocation}
                      onChange={(e) => setInspectionLocation(e.target.value)}
                      placeholder="e.g. Ring Road Junction, near Ward 12 water main"
                      className="w-full px-3 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                  </div>
                )}
              </div>

              {/* Investigation Findings */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Investigation Findings & Site Observations *
                </label>
                <textarea
                  rows={2}
                  required
                  value={investigationFindings}
                  onChange={(e) => setInvestigationFindings(e.target.value)}
                  placeholder="Record observations: extent of damage, water pipeline leakage diameter, cable fault root cause..."
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none resize-none"
                />
              </div>

              {/* Status Outcome Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Disposal / Work Order Status *
                </label>
                <select
                  value={investigationStatus}
                  onChange={(e) => setInvestigationStatus(e.target.value as any)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none font-bold"
                >
                  <option value="resolved">Resolved (Work Completed on Site)</option>
                  <option value="in_progress">In Progress (Active Repair / Works in Progress)</option>
                  <option value="awaiting_verification">Awaiting Verification (Completed, Pending Citizen/Supervisor Check)</option>
                  <option value="rejected">Rejected (Inadmissible / Out of Jurisdiction / Invalid Order)</option>
                </select>
              </div>

              {/* Mandatory Resolution Remarks (for Resolved) */}
              {investigationStatus === 'resolved' && (
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-emerald-800">
                    Mandatory Resolution Action & Remarks *
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={investigationActionTaken}
                    onChange={(e) => setInvestigationActionTaken(e.target.value)}
                    placeholder="Specify exact action taken: patch work completed, new pipeline valve installed, light bulb replaced and tested..."
                    className="w-full px-3 py-2 text-xs rounded-xl border border-emerald-300 bg-emerald-50/30 focus:bg-white focus:ring-2 focus:ring-emerald-500 outline-none resize-none font-medium"
                  />
                  <p className="text-[10px] text-slate-500">
                    Note: Resolution remarks are permanently recorded in the civic audit ledger and visible to citizens.
                  </p>
                </div>
              )}

              {/* Mandatory Rejection Grounds (for Rejected - Sec 8 of Act 6/2018) */}
              {investigationStatus === 'rejected' && (
                <div className="space-y-1 p-3 bg-rose-50 rounded-2xl border border-rose-200">
                  <label className="block text-xs font-bold text-rose-900">
                    Reasoned Grounds for Rejection (Sec 8 Mandatory Order) *
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={investigationRejectionReason}
                    onChange={(e) => setInvestigationRejectionReason(e.target.value)}
                    placeholder="Specify reasoned legal grounds: e.g. Private property not covered by municipal maintenance; duplicate of registered complaint #AP-GNT-2026-NXC042; outside AP municipal jurisdiction..."
                    className="w-full px-3 py-2 text-xs rounded-xl border border-rose-300 bg-white focus:ring-2 focus:ring-rose-500 outline-none resize-none font-medium"
                  />
                </div>
              )}

              {/* If In Progress or Awaiting Verification: Next Steps */}
              {(investigationStatus === 'in_progress' || investigationStatus === 'awaiting_verification') && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Action Taken & Next Scheduled Steps
                  </label>
                  <textarea
                    rows={2}
                    value={investigationActionTaken}
                    onChange={(e) => setInvestigationActionTaken(e.target.value)}
                    placeholder="e.g. Excavation completed; asphalt batch arriving tomorrow 10 AM. Team scheduled for paving."
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none resize-none"
                  />
                </div>
              )}

              {/* Resolution Proof Photo Upload */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Upload Site Investigation / Repair Proof Photo
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onloadend = () => {
                        const resultStr = reader.result as string;
                        setInvestigationPhoto(resultStr);
                        runAiVerification(resultStr, investigatingComplaint);
                      };
                      reader.readAsDataURL(file);
                    }
                  }}
                  className="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
                />

                {investigationPhoto && (
                  <div className="mt-2 space-y-2">
                    <div className="relative inline-block">
                      <img src={investigationPhoto} alt="Site proof" className="w-28 h-28 object-cover rounded-xl border-2 border-teal-500 shadow-sm" />
                      <button
                        type="button"
                        onClick={() => {
                          setInvestigationPhoto(null);
                          setAiVerification(null);
                        }}
                        className="absolute -top-1.5 -right-1.5 bg-red-600 text-white rounded-full p-1 shadow cursor-pointer"
                      >
                        <X size={11} />
                      </button>
                    </div>

                    {verifyingWithAi && (
                      <div className="text-xs text-teal-700 font-bold flex items-center gap-2">
                        <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-teal-600 border-t-transparent" />
                        <span>Running Computer Vision Resolution Audit...</span>
                      </div>
                    )}

                    {aiVerification && (
                      <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs space-y-1">
                        <div className="flex items-center justify-between text-emerald-900 font-bold">
                          <span className="flex items-center gap-1.5">
                            <Sparkles size={14} className="text-emerald-600" />
                            <span>AI Vision Verification</span>
                          </span>
                          <span className="bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded text-[10px] font-bold">
                            {aiVerification.qualityGrade} &bull; {aiVerification.confidenceScore}%
                          </span>
                        </div>
                        <p className="text-[11px] text-emerald-800">{aiVerification.auditSummary}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setInvestigationModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingInvestigation}
                  className="px-5 py-2.5 text-xs font-bold bg-teal-600 hover:bg-teal-700 text-white rounded-xl transition shadow-sm flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <ClipboardCheck size={14} />
                  <span>{submittingInvestigation ? 'Saving Record...' : 'Submit Investigation & Update Status'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 5.4 ACTIVITY AUDIT & INVESTIGATION HISTORY DRAWER             */}
      {/* ============================================================ */}
      {auditModalOpen && auditComplaint && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white text-slate-800 rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <History size={17} className="text-teal-700" />
                  <span>Activity Audit & Investigation History</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Ref: <span className="font-mono font-bold text-teal-800">{auditComplaint.grievanceRefNumber || auditComplaint.id}</span>
                </p>
              </div>
              <button
                onClick={() => setAuditModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-4">
              {loadingAudit ? (
                <div className="py-12 text-center text-slate-400">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-teal-600 border-t-transparent mx-auto mb-2" />
                  <p className="text-xs">Loading immutable audit ledger...</p>
                </div>
              ) : (
                <>
                  {/* Previous Structured Investigations */}
                  {auditInvestigations.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-teal-900">
                        Site Investigations ({auditInvestigations.length})
                      </h4>
                      <div className="space-y-2">
                        {auditInvestigations.map((inv) => (
                          <div key={inv.id} className="p-3 bg-teal-50/50 rounded-2xl border border-teal-100 text-xs space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-teal-950">{inv.employee_name || 'Cadre Officer'} ({inv.employee_id || 'AP-STAFF'})</span>
                              <span className="text-[10px] text-slate-500">{new Date(inv.created_at).toLocaleString()}</span>
                            </div>
                            <p className="text-slate-700"><strong>Findings:</strong> {inv.findings}</p>
                            {inv.action_taken && <p className="text-slate-700"><strong>Action Taken:</strong> {inv.action_taken}</p>}
                            {inv.supporting_evidence_urls && inv.supporting_evidence_urls[0] && (
                              <img src={inv.supporting_evidence_urls[0]} alt="Site evidence" className="w-20 h-20 object-cover rounded-lg border mt-1" />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Immutable Activity Logs Feed */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                      Lifecycle Audit Events ({auditLogs.length})
                    </h4>
                    {auditLogs.length === 0 ? (
                      <p className="text-xs text-slate-400 py-4 text-center">No previous activity logs recorded.</p>
                    ) : (
                      <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                        {auditLogs.map((log) => (
                          <div key={log.id} className="relative text-xs space-y-0.5">
                            <span className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-teal-600 border-2 border-white ring-1 ring-teal-200" />
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-800 capitalize">
                                {(log.action || '').replace(/_/g, ' ')}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {new Date(log.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-slate-600">{log.comments || 'Lifecycle transition recorded'}</p>
                            <span className="text-[10px] text-teal-700 font-semibold block">
                              By {log.actor_name || 'System'} ({log.actor_role})
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 text-right">
              <button
                onClick={() => setAuditModalOpen(false)}
                className="px-4 py-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition"
              >
                Close Audit View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
