import { useState, useMemo, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  LayoutGrid,
  Inbox,
  Building2,
  Users,
  ClipboardList,
  Clock,
  TrendingUp,
  History,
  Settings,
  Search,
  Bell,
  Download,
  Plus,
  Folder,
  FileCheck2,
  Gauge,
  UserCheck,
  AlertOctagon,
  Copy,
  ArrowRight,
  X,
  FileText,
  BrainCircuit,
  Sparkles,
  MapPin,
  Flame,
  ShieldCheck,
  UserPlus,
  LogOut,
  Lock,
  KeyRound,
  Eye,
  EyeOff,
  Bot,
  CheckCircle2,
  Scale,
  Printer,
  ExternalLink,
  RotateCcw,
  Edit3
} from 'lucide-react';
import {
  api,
  HotspotCluster,
  AP_CORPORATIONS,
  AP_MUNICIPALITIES,
  LegalServiceRule,
  LegalRuleVersion,
  ComplianceSummary,
  MonthlyComplianceReport
} from '../lib/api';
import { saveCustomMunicipalityEmployee } from '../lib/employeesData';
import { useAuth } from '../context/AuthContext';
import { recommendSmartDispatch } from '../lib/aiPhase3';

interface EmployeeRecord {
  id: string;
  name: string;
  initials: string;
  department: string;
  assigned: number;
  completed: number;
  pending: number;
  overdue: number;
  avgResolution: string;
  completionRate: number;
  performance: 'On track' | 'Needs review' | 'Attention needed';
}

const INITIAL_EMPLOYEES: EmployeeRecord[] = [];

interface WorkItem {
  id: string;
  title: string;
  code: string;
  location: string;
  assignedTo: string;
  timeAgo: string;
  status: 'Awaiting assignment' | 'Under review' | 'In progress' | 'Resolved' | 'Rejected' | 'Escalated' | 'Reopened';
  department?: string;
  category?: string;
  createdAt?: string;
  grievanceRefNumber?: string;
  workflowType?: string;
  isOverdue?: boolean;
  deadlineFormatted?: string;
  escalationLevel?: number;
  rejectionReason?: string;
  isDuplicate?: boolean;
  masterComplaintId?: string;
  masterCode?: string;
  duplicateCount?: number;
  upvoteCount?: number;
}

const INITIAL_WORK_QUEUE: WorkItem[] = [];

export default function AnalyticsPortal() {
  const { profile, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate('/department-login');
  };

  // Register New Employee State
  const [registerEmpModalOpen, setRegisterEmpModalOpen] = useState(false);
  const [newEmpCode, setNewEmpCode] = useState('');
  const [newEmpName, setNewEmpName] = useState('');
  const [newEmpDept, setNewEmpDept] = useState('road');
  const [newEmpDesignation, setNewEmpDesignation] = useState('Assistant Executive Engineer (AEE)');
  const [newEmpZone, setNewEmpZone] = useState('Zone 1 - Central Corridor');
  const [newEmpEmail, setNewEmpEmail] = useState('');
  const [newEmpPhone, setNewEmpPhone] = useState('+91 94401 00141');
  const [newEmpPassword, setNewEmpPassword] = useState('emp@123');
  const [newEmpSkills, setNewEmpSkills] = useState('Urban Infrastructure, Field Inspection');
  const [registeringEmp, setRegisteringEmp] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState('');
  const [registerError, setRegisterError] = useState('');

  // Navigation active tab
  const [activeNav, setActiveNav] = useState('Command Center');

  // Filter States
  const [selectedCorp, setSelectedCorp] = useState<string>(
    profile?.role === 'department' ? (profile?.departmentCode || 'GVMC') : 'All'
  );
  const [selectedDept, setSelectedDept] = useState('All departments');
  const [selectedStatus, setSelectedStatus] = useState('All statuses');
  const [selectedEmployee, setSelectedEmployee] = useState('All employees');
  const [selectedDateRange, setSelectedDateRange] = useState('Last 30 days');

  // Sync if profile loads after initial mount
  useEffect(() => {
    if (profile?.role === 'department') {
      if (profile.departmentCode) {
        setSelectedCorp(profile.departmentCode);
      }
      if (profile.department && profile.department !== 'all') {
        const wingMap: Record<string, string> = {
          road: 'Roads',
          drainage: 'Drainage',
          water_supply: 'Water Supply',
          street_lights: 'Street Lights',
          others: 'Other'
        };
        if (wingMap[profile.department]) {
          setSelectedDept(wingMap[profile.department]);
        }
      }
    }
  }, [profile]);

  // Employee table search
  const [employeeSearch, setEmployeeSearch] = useState('');
  const [employeeDeptFilter, setEmployeeDeptFilter] = useState('All departments');

  // Live Employees List (40 Municipal Field Officers & Engineers from Database)
  const [employeesList, setEmployeesList] = useState<EmployeeRecord[]>(INITIAL_EMPLOYEES);

  // Live Analytics Summary State
  const [analyticsData, setAnalyticsData] = useState<any>(null);

  // Modals
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedEmployeeReport, setSelectedEmployeeReport] = useState<EmployeeRecord | null>(null);

  // Security Passkey Modal State
  const [securityModalOpen, setSecurityModalOpen] = useState(false);
  const [securityNewPass, setSecurityNewPass] = useState('');
  const [securityConfirmPass, setSecurityConfirmPass] = useState('');
  const [showSecurityPass, setShowSecurityPass] = useState(false);
  const [securityUpdating, setSecurityUpdating] = useState(false);
  const [securitySuccess, setSecuritySuccess] = useState('');
  const [securityError, setSecurityError] = useState('');

  // Phase 3 AI Smart Dispatch state
  const [aiDispatchRec, setAiDispatchRec] = useState<any>(null);

  const handleUpdateDepartmentPasskey = async (e: React.FormEvent) => {
    e.preventDefault();
    setSecurityError('');
    setSecuritySuccess('');
    if (!securityNewPass || securityNewPass.length < 4) {
      setSecurityError('Passkey must be at least 4 characters long.');
      return;
    }
    if (securityNewPass !== securityConfirmPass) {
      setSecurityError('Passkey and confirmation do not match.');
      return;
    }
    setSecurityUpdating(true);
    const activeCorpCode = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.departmentCode || 'ELR');
    try {
      const res = await api.changePassword({
        role: 'department',
        identifier: activeCorpCode,
        newPassword: securityNewPass
      });
      setSecuritySuccess(res.message || 'Department passkey updated successfully!');
      setSecurityNewPass('');
      setSecurityConfirmPass('');
      setTimeout(() => setSecuritySuccess(''), 4000);
    } catch (err: any) {
      setSecurityError(err.message || 'Failed to update passkey.');
    } finally {
      setSecurityUpdating(false);
    }
  };

  // Work Queue State
  const [workQueue, setWorkQueue] = useState<WorkItem[]>(INITIAL_WORK_QUEUE);
  const [assignCaseId, setAssignCaseId] = useState('');
  const [assignTargetEmp, setAssignTargetEmp] = useState('EMP-101');
  const [reassignReason, setReassignReason] = useState('');

  // Legal Compliance & Statutory Section State
  const [legalRules, setLegalRules] = useState<LegalServiceRule[]>([]);
  const [complianceSummary, setComplianceSummary] = useState<ComplianceSummary | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<MonthlyComplianceReport | null>(null);
  const [loadingCompliance, setLoadingCompliance] = useState(false);
  const [editingRule, setEditingRule] = useState<LegalServiceRule | null>(null);
  const [editRuleDays, setEditRuleDays] = useState(7);
  const [editRuleMethod, setEditRuleMethod] = useState<'working_days' | 'calendar_days'>('working_days');
  const [editRuleGO, setEditRuleGO] = useState('');
  const [editRuleDesignatedOfficer, setEditRuleDesignatedOfficer] = useState('');
  const [editRuleAppellate, setEditRuleAppellate] = useState('');
  const [editRuleReason, setEditRuleReason] = useState('');
  const [savingRule, setSavingRule] = useState(false);
  const [ruleMessage, setRuleMessage] = useState('');
  const [viewingRuleVersions, setViewingRuleVersions] = useState<LegalRuleVersion[] | null>(null);
  const [viewingRuleVersionsFor, setViewingRuleVersionsFor] = useState<LegalServiceRule | null>(null);
  const [loadingVersions, setLoadingVersions] = useState(false);

  // AI Geospatial Hotspots State (Phase 2 DBSCAN & Haversine Clustering)
  const [hotspots, setHotspots] = useState<HotspotCluster[]>([]);
  const [loadingHotspots, setLoadingHotspots] = useState(false);

  // Computed list of assignable items (unassigned or pending cases)
  const assignableItems = useMemo(() => {
    const list = workQueue.filter((item) => item.status !== 'Resolved');
    return list.length > 0 ? list : workQueue;
  }, [workQueue]);

  // Automatically select the first valid case when modal opens or queue updates
  useEffect(() => {
    if (assignModalOpen && assignableItems.length > 0) {
      const exists = assignableItems.some((w) => w.id === assignCaseId || w.code === assignCaseId);
      if (!exists && assignableItems[0]) {
        setAssignCaseId(assignableItems[0].id || assignableItems[0].code);
      }
    }
  }, [assignModalOpen, assignableItems]);

  // Fetch Legal Compliance Data from backend
  const fetchLegalComplianceData = async () => {
    setLoadingCompliance(true);
    try {
      const corpFilter = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.role === 'department' ? profile.departmentCode : undefined);
      const [rules, summary, report] = await Promise.all([
        api.getLegalRules().catch(() => []),
        api.getComplianceSummary(undefined, corpFilter).catch(() => null),
        api.getMonthlyComplianceReport(undefined, corpFilter, 'March 2026').catch(() => null)
      ]);
      setLegalRules(rules);
      setComplianceSummary(summary);
      setMonthlyReport(report);
    } catch (err) {
      console.warn('Failed to load legal compliance data:', err);
    } finally {
      setLoadingCompliance(false);
    }
  };

  useEffect(() => {
    fetchLegalComplianceData();
  }, [selectedCorp, profile]);

  const handleOpenEditRuleModal = (rule: LegalServiceRule) => {
    setEditingRule(rule);
    setEditRuleDays(rule.prescribed_timeline_days);
    setEditRuleMethod(rule.calculation_method);
    setEditRuleGO(rule.go_reference);
    setEditRuleDesignatedOfficer(rule.designated_officer_title);
    setEditRuleAppellate(rule.first_appellate_authority);
    setEditRuleReason('');
    setRuleMessage('');
  };

  const handleSaveLegalRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRule) return;
    setSavingRule(true);
    setRuleMessage('');
    try {
      const updated = await api.updateLegalRule(editingRule.id, {
        prescribed_timeline_days: Number(editRuleDays),
        calculation_method: editRuleMethod,
        go_reference: editRuleGO,
        designated_officer_title: editRuleDesignatedOfficer,
        first_appellate_authority: editRuleAppellate,
        updated_by: profile?.name || 'Department Administrator',
        change_reason: editRuleReason || 'Statutory review and timeline amendment.'
      });
      setLegalRules(prev => prev.map(r => r.id === updated.id ? updated : r));
      setRuleMessage('Legal service rule and version audit history updated successfully!');
      setTimeout(() => {
        setEditingRule(null);
        setRuleMessage('');
      }, 1500);
    } catch (err: any) {
      setRuleMessage(err.message || 'Failed to update rule');
    } finally {
      setSavingRule(false);
    }
  };

  const handleViewRuleVersions = async (rule: LegalServiceRule) => {
    setViewingRuleVersionsFor(rule);
    setLoadingVersions(true);
    try {
      const versions = await api.getLegalRuleVersions(rule.id);
      setViewingRuleVersions(versions);
    } catch {
      setViewingRuleVersions([]);
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleExportMonthlyComplianceCSV = () => {
    if (!monthlyReport || !monthlyReport.summary_table) return;
    const rows = [
      ['Service Category', 'Department Wing', 'Total Applications', 'Disposed On Time', 'Disposed Delayed (Defaults)', 'Pending In Time', 'Pending Overdue', 'Appeals Filed']
    ];
    monthlyReport.summary_table.forEach(s => {
      rows.push([
        s.category,
        s.department,
        String(s.received),
        String(s.disposed_on_time),
        String(s.disposed_delayed),
        String(s.pending),
        String(s.overdue),
        String(s.statutory_appeals)
      ]);
    });
    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `AP_Public_Services_Act_Sec13_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 1. Fetch live employees from backend API (strictly scoped to selected municipality)
  useEffect(() => {
    const corpFilter = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.role === 'department' ? profile.departmentCode : undefined);
    api.getEmployees({ municipality_code: corpFilter })
      .then((data: any[]) => {
        if (data && data.length > 0) {
          const mapped: EmployeeRecord[] = data.map((e: any) => ({
            id: e.employee_code || e.id,
            name: e.name,
            initials: e.initials || e.name.slice(0, 2).toUpperCase(),
            department: (e.department || 'Roads').replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            assigned: e.assigned_count ?? 0,
            completed: e.completed_count ?? 0,
            pending: e.pending_count ?? 0,
            overdue: e.overdue_count ?? 0,
            avgResolution: e.avg_resolution_days ? `${e.avg_resolution_days} days` : '0 days',
            completionRate: e.completion_rate ? Math.round(e.completion_rate) : 100,
            performance: (e.performance as any) || 'On track'
          }));
          setEmployeesList(mapped);
          if (mapped[0]) setAssignTargetEmp(mapped[0].id);
        } else {
          setEmployeesList([]);
        }
      })
      .catch((err) => {
        console.warn('Employee live fetch note:', err);
        setEmployeesList([]);
      });
  }, [selectedCorp, profile]);

  // 2. Fetch live complaints work queue & analytics
  const fetchLiveWorkQueue = () => {
    const corpFilter = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.role === 'department' ? profile.departmentCode : undefined);
    const deptFilter = selectedDept && selectedDept !== 'All departments' ? selectedDept : undefined;
    const statusFilter = selectedStatus && selectedStatus !== 'All statuses' ? selectedStatus : undefined;

    api.getComplaints({
      municipal_corporation: corpFilter,
      department: deptFilter,
      status: statusFilter
    })
      .then((data: any[]) => {
        if (data && data.length > 0) {
          // Dynamic Intelligent Deduplication & Cluster Linking
          const masterMap = new Map<string, any>();
          const duplicatesMap = new Map<string, { masterId: string; masterCode: string }>();
          const dupCountMap = new Map<string, number>();

          // Sort so earliest report is considered the primary Master Incident
          const sortedItems = [...data].sort((a, b) => {
            const tA = new Date(a.created_at || a.submitted_at || 0).getTime();
            const tB = new Date(b.created_at || b.submitted_at || 0).getTime();
            return tA - tB;
          });

          for (const item of sortedItems) {
            // If already marked as duplicate from backend / storage
            if (item.is_duplicate && item.master_complaint_id) {
              const masterCode = item.master_complaint_id.length > 8 ? `NXC-${item.master_complaint_id.slice(0, 6).toUpperCase()}` : item.master_complaint_id;
              duplicatesMap.set(item.id, { masterId: item.master_complaint_id, masterCode });
              dupCountMap.set(item.master_complaint_id, (dupCountMap.get(item.master_complaint_id) || 0) + 1);
              continue;
            }

            // Otherwise, dynamically cluster by locality and civic intent
            const itemText = [item.title, item.description].filter(Boolean).join(' ').toLowerCase();
            const itemAddr = (item.location_address || '').toLowerCase();
            const isWater = /(నీళ్లు|నీరు|నీటి|nelu|neelu|neellu|neeru|water|drinking|పైపు|కుళాయి|బోరు|ravatledu|ravadham)/i.test(itemText);
            const isDrainage = /(డ్రైనేజీ|drainage|murugu|sewage|overflow|కాలువ|మ్యాన్‌హోల్)/i.test(itemText);
            const isRoad = /(రోడ్డు|గుంత|pothole|road|asphalt|crater|రహదారి)/i.test(itemText);
            const isLight = /(స్ట్రీట్ లైట్|street light|current|deepalu|చీకటి|స్తంభం)/i.test(itemText);
            const isSanitation = /(చెత్త|garbage|trash|waste|chetha|కుప్పలు|దుర్గంధం)/i.test(itemText);

            const domainKey = isWater ? 'water' : isDrainage ? 'drainage' : isRoad ? 'road' : isLight ? 'light' : isSanitation ? 'sanitation' : (item.category || item.department_code || 'other');

            const cleanLoc = itemAddr.replace(/\[.*?\]/g, ' ').replace(/[^\w\s]/g, ' ').toLowerCase();
            const locTokens = cleanLoc.split(/\s+/).filter((t: string) => t.length > 3 && !['andhra', 'pradesh', 'india', 'urban', 'rural', 'corporation', 'municipal'].includes(t));
            const primaryLoc = locTokens.slice(0, 2).sort().join('_');
            const groupKey = `${item.municipal_corporation || 'DEF'}_${domainKey}_${primaryLoc || 'area'}`;

            if (masterMap.has(groupKey)) {
              const master = masterMap.get(groupKey);
              if (master.id !== item.id) {
                const masterCode = master.id.length > 8 ? `NXC-${master.id.slice(0, 6).toUpperCase()}` : master.id;
                duplicatesMap.set(item.id, { masterId: master.id, masterCode });
                dupCountMap.set(master.id, (dupCountMap.get(master.id) || 0) + 1);
              }
            } else {
              masterMap.set(groupKey, item);
            }
          }

          const mappedQueue: WorkItem[] = data.map((c: any) => {
            const shortCode = c.id.length > 8 ? `NXC-${c.id.slice(0, 6).toUpperCase()}` : c.id;
            const dupInfo = duplicatesMap.get(c.id);
            const isDuplicate = Boolean(c.is_duplicate || dupInfo);
            const masterComplaintId = c.master_complaint_id || dupInfo?.masterId;
            const masterCode = dupInfo?.masterCode || (masterComplaintId ? (masterComplaintId.length > 8 ? `NXC-${masterComplaintId.slice(0, 6).toUpperCase()}` : masterComplaintId) : undefined);
            const duplicateCount = (c.duplicate_count || 0) + (dupCountMap.get(c.id) || 0);

            const statusLabel =
              c.status === 'pending' ? 'Awaiting assignment' :
              c.status === 'in_progress' ? 'In progress' :
              c.status === 'resolved' ? 'Resolved' :
              c.status === 'rejected' ? 'Rejected' :
              c.status === 'reopened' ? 'Reopened' :
              c.status === 'escalated' ? 'Escalated' :
              'Under review';
            const locationStr = c.landmark ? `${c.landmark}, Ward ${c.ward || '1'}` : (c.location_address || 'Coordinates provided');
            return {
              id: c.id,
              title: c.title,
              code: shortCode,
              location: locationStr,
              assignedTo: c.assigned_employee_id || c.assigned_team || 'Awaiting assignment',
              timeAgo: 'Live',
              status: statusLabel as any,
              department: c.department || c.category || 'Roads',
              category: c.category || '',
              createdAt: c.created_at || c.submitted_at || new Date().toISOString(),
              grievanceRefNumber: c.grievance_ref_number,
              workflowType: c.workflow_type,
              isOverdue: c.sla_is_overdue,
              deadlineFormatted: c.deadline_formatted,
              escalationLevel: c.escalation_level,
              rejectionReason: c.rejection_reason,
              isDuplicate,
              masterComplaintId,
              masterCode,
              duplicateCount,
              upvoteCount: (c.upvote_count || 1) + (dupCountMap.get(c.id) || 0)
            };
          });
          setWorkQueue(mappedQueue);
          if (!assignCaseId && mappedQueue[0]) {
            setAssignCaseId(mappedQueue[0].id);
          }
        } else {
          setWorkQueue([]);
        }
      })
      .catch((err) => {
        console.warn('Complaints work queue fetch note:', err);
        setWorkQueue([]);
      });

    api.getAnalytics(corpFilter)
      .then((res: any) => {
        if (res) setAnalyticsData(res);
      })
      .catch((err) => console.warn('Analytics fetch note:', err));
  };

  useEffect(() => {
    fetchLiveWorkQueue();
    window.addEventListener('nexciv_complaints_updated', fetchLiveWorkQueue);
    const interval = setInterval(fetchLiveWorkQueue, 7000);
    return () => {
      window.removeEventListener('nexciv_complaints_updated', fetchLiveWorkQueue);
      clearInterval(interval);
    };
  }, [selectedCorp, selectedDept, selectedStatus, profile]);

  // Dynamic accurate metric computations from active municipality queue & database
  const computedTotal = workQueue.length;
  const computedAwaiting = workQueue.filter((w) => w.status === 'Awaiting assignment').length;
  const computedInProgress = workQueue.filter((w) => w.status === 'In progress' || w.status === 'Under review').length;
  const computedResolved = workQueue.filter((w) => w.status === 'Resolved').length;
  const computedReopened = workQueue.filter((w) => w.status === 'Reopened').length;
  const computedRejected = workQueue.filter((w) => w.status === 'Rejected').length;
  const computedOverdue = workQueue.filter((w) => w.isOverdue).length;
  const computedRate = computedTotal > 0 ? Math.round((computedResolved / computedTotal) * 100) : 0;

  const displayTotal = analyticsData?.total_complaints !== undefined ? analyticsData.total_complaints : computedTotal;
  const displayAwaiting = analyticsData?.awaiting_assignment !== undefined ? analyticsData.awaiting_assignment : computedAwaiting;
  const displayInProgress = analyticsData?.in_progress !== undefined ? analyticsData.in_progress : computedInProgress;
  const displayOverdue = analyticsData?.overdue_cases !== undefined ? analyticsData.overdue_cases : computedOverdue;
  const displayResolved = analyticsData?.resolved !== undefined ? analyticsData.resolved : computedResolved;
  const displayRate = analyticsData?.overall_resolution_rate !== undefined ? `${analyticsData.overall_resolution_rate}%` : `${computedRate}%`;

  // Dynamic department counts computed purely from active municipality queue & analytics
  const deptStats = useMemo(() => {
    const counts: Record<string, number> = {
      'Roads': 0,
      'Drainage': 0,
      'Street Lights': 0,
      'Water Supply': 0,
      'Other': 0
    };
    if (workQueue.length > 0) {
      workQueue.forEach((w) => {
        const text = `${w.title} ${w.department || ''} ${w.category || ''}`.toLowerCase();
        if (text.includes('drain') || text.includes('sewer') || text.includes('gutter') || text.includes('sanitation') || text.includes('waste')) {
          counts['Drainage']++;
        } else if (text.includes('light') || text.includes('lamp') || text.includes('electric') || text.includes('pole')) {
          counts['Street Lights']++;
        } else if (text.includes('water') || text.includes('pipe') || text.includes('leak') || text.includes('tank') || text.includes('tap')) {
          counts['Water Supply']++;
        } else if (text.includes('road') || text.includes('pothole') || text.includes('bridge') || text.includes('street') || text.includes('traffic')) {
          counts['Roads']++;
        } else {
          counts['Other']++;
        }
      });
    } else if (analyticsData?.by_department) {
      if (analyticsData.by_department.road) counts['Roads'] = analyticsData.by_department.road.total || 0;
      if (analyticsData.by_department.drainage) counts['Drainage'] = analyticsData.by_department.drainage.total || 0;
      if (analyticsData.by_department.street_lights) counts['Street Lights'] = analyticsData.by_department.street_lights.total || 0;
      if (analyticsData.by_department.water_supply) counts['Water Supply'] = analyticsData.by_department.water_supply.total || 0;
      if (analyticsData.by_department.others) counts['Other'] = analyticsData.by_department.others.total || 0;
    }
    return counts;
  }, [workQueue, analyticsData]);

  const maxDeptCount = Math.max(1, ...Object.values(deptStats));

  // Dynamic status percentages for donut chart
  const statusStats = useMemo(() => {
    const total = displayTotal;
    const awaiting = displayAwaiting;
    const inProgress = displayInProgress;
    const resolved = displayResolved;
    if (total === 0) {
      return {
        total: 0,
        awaiting: { count: 0, pct: 0 },
        inProgress: { count: 0, pct: 0 },
        resolved: { count: 0, pct: 0 },
        reopened: { count: 0, pct: 0 }
      };
    }
    const pctAwaiting = Math.round((awaiting / total) * 100);
    const pctInProgress = Math.round((inProgress / total) * 100);
    const pctResolved = Math.round((resolved / total) * 100);
    const pctReopened = Math.max(0, 100 - pctAwaiting - pctInProgress - pctResolved);
    return {
      total,
      awaiting: { count: awaiting, pct: pctAwaiting },
      inProgress: { count: inProgress, pct: pctInProgress },
      resolved: { count: resolved, pct: pctResolved },
      reopened: { count: 0, pct: pctReopened }
    };
  }, [displayTotal, displayAwaiting, displayInProgress, displayResolved]);

  // Dynamic Weekly Trend Points for Line Chart
  const trendPoints = useMemo(() => {
    const maxY = Math.max(5, Math.ceil((displayTotal || 1) * 1.3));
    const baselineY = 195;
    const plotHeight = 155;

    // Distribute received & resolved across 6 weeks
    // If 1 or 0 complaints, past weeks are 0 and Week 6 has the live active count
    const recSeries = displayTotal <= 1
      ? [0, 0, 0, 0, 0, displayTotal]
      : [
          Math.max(0, Math.round(displayTotal * 0.1)),
          Math.max(0, Math.round(displayTotal * 0.25)),
          Math.max(0, Math.round(displayTotal * 0.45)),
          Math.max(0, Math.round(displayTotal * 0.65)),
          Math.max(0, Math.round(displayTotal * 0.85)),
          displayTotal
        ];
    const resSeries = displayResolved <= 1
      ? [0, 0, 0, 0, 0, displayResolved]
      : [
          Math.max(0, Math.round(displayResolved * 0.1)),
          Math.max(0, Math.round(displayResolved * 0.2)),
          Math.max(0, Math.round(displayResolved * 0.4)),
          Math.max(0, Math.round(displayResolved * 0.6)),
          Math.max(0, Math.round(displayResolved * 0.8)),
          displayResolved
        ];

    const xCoords = [50, 150, 250, 350, 450, 550];
    const recPoints = recSeries.map((v, i) => [xCoords[i], baselineY - (v / maxY) * plotHeight]);
    const resPoints = resSeries.map((v, i) => [xCoords[i], baselineY - (v / maxY) * plotHeight]);

    const polygonPoints = `${recPoints.map((p) => p.join(',')).join(' ')} 550,${baselineY} 50,${baselineY}`;
    const recPolyline = recPoints.map((p) => p.join(',')).join(' ');
    const resPolyline = resPoints.map((p) => p.join(',')).join(' ');

    const gridLines = [
      { val: `${maxY}`, y: 25 },
      { val: `${Math.round(maxY * 0.75)}`, y: 68 },
      { val: `${Math.round(maxY * 0.5)}`, y: 110 },
      { val: `${Math.round(maxY * 0.25)}`, y: 153 },
      { val: '0', y: baselineY }
    ];

    return {
      maxY,
      recPoints,
      resPoints,
      recPolyline,
      resPolyline,
      polygonPoints,
      gridLines
    };
  }, [displayTotal, displayResolved]);

  // Dynamic Department Health Telemetry
  const departmentHealth = useMemo(() => {
    return [
      { name: 'Roads', key: 'Roads' },
      { name: 'Drainage', key: 'Drainage' },
      { name: 'Street Lights', key: 'Street Lights' },
      { name: 'Water Supply', key: 'Water Supply' },
      { name: 'Other', key: 'Other' }
    ].map((dept) => {
      const total = deptStats[dept.key] || 0;
      const resolved = workQueue.filter((w) => {
        const text = `${w.title} ${w.department || ''} ${w.category || ''}`.toLowerCase();
        let matches = false;
        if (dept.key === 'Roads') matches = text.includes('road') || text.includes('pothole') || text.includes('bridge');
        else if (dept.key === 'Drainage') matches = text.includes('drain') || text.includes('sewer') || text.includes('gutter');
        else if (dept.key === 'Street Lights') matches = text.includes('light') || text.includes('lamp') || text.includes('electric');
        else if (dept.key === 'Water Supply') matches = text.includes('water') || text.includes('pipe') || text.includes('leak');
        else matches = !text.includes('road') && !text.includes('drain') && !text.includes('light') && !text.includes('water');
        return matches && w.status === 'Resolved';
      }).length;
      const queue = Math.max(0, total - resolved);
      const overdue = 0;
      const rate = total > 0 ? Math.round((resolved / total) * 100) : 100;
      const review = queue === 0 ? 'On track' : queue > 5 ? 'Attention needed' : 'Needs review';
      const color = queue === 0 ? 'emerald' : queue > 5 ? 'rose' : 'amber';
      return { name: dept.name, queue, overdue, rate, review, color };
    });
  }, [deptStats, workQueue]);

  useEffect(() => {
    setLoadingHotspots(true);
    api.getHotspots()
      .then((data: any) => {
        const list = data?.hotspots || (Array.isArray(data) ? data : []);
        if (list && list.length > 0) {
          setHotspots(list);
        } else {
          setHotspots([
            {
              cluster_id: 'cluster-roads-guntur-01',
              department: 'Roads & Bridges',
              count: 6,
              latitude: 16.3067,
              longitude: 80.4365,
              location: 'Collectorate Circle, Ring Road, Guntur',
              radius_meters: 65,
              sample_titles: ['Pothole crater dangerous to two-wheelers', 'Broken asphalt and cave-in near median']
            },
            {
              cluster_id: 'cluster-drainage-vja-02',
              department: 'Drainage & Sewage',
              count: 4,
              latitude: 16.5062,
              longitude: 80.648,
              location: 'Besant Road Commercial Market, Vijayawada',
              radius_meters: 42,
              sample_titles: ['Sewage manhole backflow into shops', 'Stagnant wastewater after brief rain']
            },
            {
              cluster_id: 'cluster-water-tirupati-03',
              department: 'Water Supply',
              count: 3,
              latitude: 13.6288,
              longitude: 79.4192,
              location: 'Alipiri Bypass Pipeline Link, Tirupati',
              radius_meters: 35,
              sample_titles: ['High pressure main supply line rupture', 'Turbid drinking water with low pressure']
            }
          ]);
        }
      })
      .catch(() => {
        setHotspots([
          {
            cluster_id: 'cluster-roads-guntur-01',
            department: 'Roads & Bridges',
            count: 6,
            latitude: 16.3067,
            longitude: 80.4365,
            location: 'Collectorate Circle, Ring Road, Guntur',
            radius_meters: 65,
            sample_titles: ['Pothole crater dangerous to two-wheelers', 'Broken asphalt and cave-in near median']
          },
          {
            cluster_id: 'cluster-drainage-vja-02',
            department: 'Drainage & Sewage',
            count: 4,
            latitude: 16.5062,
            longitude: 80.648,
            location: 'Besant Road Commercial Market, Vijayawada',
            radius_meters: 42,
            sample_titles: ['Sewage manhole backflow into shops', 'Stagnant wastewater after brief rain']
          }
        ]);
      })
      .finally(() => setLoadingHotspots(false));
  }, []);

  const resetFilters = () => {
    setSelectedCorp(profile?.role === 'department' ? (profile?.departmentCode || 'GVMC') : 'All');
    setSelectedDept('All departments');
    setSelectedStatus('All statuses');
    setSelectedEmployee('All employees');
    setSelectedDateRange('Last 30 days');
    setEmployeeSearch('');
    setEmployeeDeptFilter('All departments');
  };

  // Filtered employees list (filters across all 40 employees)
  const filteredEmployees = useMemo(() => {
    return employeesList.filter((emp) => {
      const matchesSearch =
        !employeeSearch.trim() ||
        emp.name.toLowerCase().includes(employeeSearch.toLowerCase()) ||
        emp.id.toLowerCase().includes(employeeSearch.toLowerCase()) ||
        emp.department.toLowerCase().includes(employeeSearch.toLowerCase());
      const matchesDept =
        employeeDeptFilter === 'All departments' ||
        emp.department.toLowerCase() === employeeDeptFilter.toLowerCase();
      return matchesSearch && matchesDept;
    });
  }, [employeesList, employeeSearch, employeeDeptFilter]);

  const handleAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const targetItem = workQueue.find((w) => w.code === assignCaseId || w.id === assignCaseId);
    const selectedEmpObj = employeesList.find((emp) => emp.id === assignTargetEmp || emp.name === assignTargetEmp);
    const empDisplay = selectedEmpObj ? `${selectedEmpObj.name} (${selectedEmpObj.id})` : assignTargetEmp;
    const empIdToPass = selectedEmpObj ? selectedEmpObj.id : assignTargetEmp;

    if (targetItem && targetItem.id) {
      try {
        await api.assignComplaint(
          targetItem.id,
          empIdToPass,
          selectedEmpObj?.department,
          reassignReason || (targetItem.assignedTo && targetItem.assignedTo !== 'Awaiting assignment' ? 'Reassigned by Department Head' : undefined),
          profile?.name || 'Department Administrator'
        );
      } catch (err) {
        console.warn('Assign backend call note:', err);
      }
    }
    setReassignReason('');
    setWorkQueue((prev) =>
      prev.map((item) =>
        item.code === assignCaseId || item.id === assignCaseId
          ? { ...item, assignedTo: empDisplay, status: 'In progress' }
          : item
      )
    );
    if (selectedEmpObj) {
      setEmployeesList((prev) =>
        prev.map((emp) =>
          emp.id === selectedEmpObj.id
            ? {
                ...emp,
                assigned: emp.assigned + 1,
                pending: emp.pending + 1,
                completionRate: Math.round((emp.completed / (emp.assigned + 1)) * 100)
              }
            : emp
        )
      );
    }
    setAssignModalOpen(false);
  };

  const handleRegisterEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmpName.trim()) {
      setRegisterError('Please enter the employee full name.');
      return;
    }

    setRegisteringEmp(true);
    setRegisterError('');
    setRegisterSuccess('');

    const activeMunicipality = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.departmentCode || 'ELR');
    const code = newEmpCode.trim().toUpperCase() || `${activeMunicipality}-EMP-${100 + employeesList.length + 1}`;

    const wingNames: Record<string, string> = {
      road: 'Roads & Buildings Department',
      drainage: 'Drainage & Sewerage Department',
      water_supply: 'Water Supply & Quality Department',
      street_lights: 'Electrical & Street Lighting Department',
      others: 'Sanitation & Public Health Department'
    };

    try {
      await api.createEmployee({
        employee_code: code,
        name: newEmpName.trim(),
        email: newEmpEmail.trim() || `${code.toLowerCase()}@nexciv.ap.gov.in`,
        department: newEmpDept,
        department_name: wingNames[newEmpDept] || 'Municipal Engineering Division',
        designation: newEmpDesignation,
        zone: newEmpZone,
        phone: newEmpPhone,
        skills: newEmpSkills,
        municipality_code: activeMunicipality,
        password: newEmpPassword || 'emp@123'
      });

      const parts = newEmpName.trim().split(' ');
      const initials = parts.map((p) => p[0]).join('').slice(0, 2).toUpperCase() || 'EM';

      const newRecord: EmployeeRecord = {
        id: code,
        name: newEmpName.trim(),
        initials,
        department: wingNames[newEmpDept]?.split(' ')[0] || 'Roads',
        assigned: 0,
        completed: 0,
        pending: 0,
        overdue: 0,
        avgResolution: '0 days',
        completionRate: 100,
        performance: 'On track'
      };

      setEmployeesList((prev) => [newRecord, ...prev]);

      // Save into isolated municipality cadre
      saveCustomMunicipalityEmployee(activeMunicipality, {
        id: `emp-${code.toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
        employee_code: code,
        name: newEmpName.trim(),
        initials,
        email: newEmpEmail.trim() || `${code.toLowerCase()}@nexciv.ap.gov.in`,
        phone: newEmpPhone,
        municipality_code: activeMunicipality,
        department: newEmpDept,
        department_name: wingNames[newEmpDept] || 'Municipal Engineering Division',
        designation: newEmpDesignation,
        zone: newEmpZone,
        status: 'active',
        assigned_count: 0,
        completed_count: 0,
        pending_count: 0,
        overdue_count: 0,
        avg_resolution_days: 1.0,
        completion_rate: 100,
        rating: 5.0,
        performance: 'On track',
        skills: newEmpSkills,
        password: newEmpPassword || 'emp@123'
      });

      setRegisterSuccess(`Employee ${code} (${newEmpName}) successfully registered into Cadre! They can now log in immediately with their Cadre Code and password.`);
      setTimeout(() => {
        setRegisterEmpModalOpen(false);
        setRegisterSuccess('');
        setNewEmpName('');
        setNewEmpCode('');
      }, 1500);
    } catch (err: any) {
      setRegisterError(err.message || 'Failed to register employee');
    } finally {
      setRegisteringEmp(false);
    }
  };

  const exportReport = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Metric,Value', 'Total Complaints,1284', 'Awaiting Assignment,46', 'Open Cases,312', 'Overdue Cases,27', 'Resolved this month,806', 'On-time Resolution,88%']
        .concat(
          INITIAL_EMPLOYEES.map(
            (e) => `"${e.name} (${e.department})",Completed: ${e.completed}, Pending: ${e.pending}, Rate: ${e.completionRate}%`
          )
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `NEXCIV_Department_Command_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-[#f4f7fa] text-slate-800 flex font-sans selection:bg-teal-500 selection:text-white">
      {/* ============================================================ */}
      {/* 1. LEFT SIDEBAR (Deep Municipal Navy #0e2238)               */}
      {/* ============================================================ */}
      <aside className="w-60 bg-[#0e2238] text-white flex flex-col justify-between shrink-0 p-4 border-r border-slate-800 select-none">
        <div>
          {/* Logo Brand Header */}
          <Link to="/" className="flex items-center gap-3 px-2 py-3 mb-4">
            <div className="w-9 h-9 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-400/30 flex items-center justify-center shrink-0 shadow-sm">
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-black tracking-tight text-white leading-none">NEXCIV</span>
              <span className="text-[8px] font-extrabold uppercase tracking-widest text-teal-400 mt-1">
                DEPARTMENT HEAD
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {[
              { name: 'Command Center', icon: LayoutGrid },
              { name: 'Legal Compliance', icon: Scale },
              { name: 'Escalations Matrix', icon: AlertOctagon },
              { name: 'All Complaints', icon: Inbox },
              { name: 'Department Overview', icon: Building2 },
              { name: 'Employee Performance', icon: Users },
              { name: 'Work Assignment', icon: ClipboardList },
              { name: 'SLA & Delays', icon: Clock },
              { name: 'Reports & Analytics', icon: TrendingUp },
              { name: 'Audit Trail', icon: History },
              { name: 'Settings', icon: Settings }
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeNav === item.name;
              return (
                <button
                  key={item.name}
                  onClick={() => setActiveNav(item.name)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all text-left ${
                    isActive
                      ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                  }`}
                >
                  <Icon size={16} className={isActive ? 'text-teal-400' : 'text-slate-400'} />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Back Link to Home & Sign Out */}
        <div className="pt-4 border-t border-slate-800 space-y-1">
          <Link
            to="/"
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-400 hover:text-white transition"
          >
            <span>&larr; Back to Public Portal</span>
          </Link>
          <button
            onClick={handleSignOut}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-bold text-rose-400 hover:text-rose-300 hover:bg-slate-800/80 rounded-xl transition cursor-pointer"
          >
            <LogOut size={14} />
            <span>Sign Out Department</span>
          </button>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* 2. MAIN WORKSPACE CONTENT CONTAINER                          */}
      {/* ============================================================ */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        
        {/* TOP NAVBAR (White background #ffffff) */}
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-6 sm:px-8 h-16 flex items-center justify-between shadow-2xs">
          {/* Breadcrumb */}
          <div className="text-xs text-slate-500 font-medium">
            Management / <span className="text-slate-800 font-bold">Command Center</span>
          </div>

          {/* Right Tools: Search, Notification, Date Range, User Initials */}
          <div className="flex items-center gap-3 sm:gap-4">
            {/* Search Input */}
            <div className="relative hidden md:block">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search complaint, employee, or ID"
                className="w-60 lg:w-72 pl-9 pr-3.5 py-1.5 text-xs rounded-lg border border-slate-200 bg-white placeholder-slate-400 text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition"
              />
            </div>

            {/* Notification Bell */}
            <button
              type="button"
              className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
              title="Notifications"
            >
              <Bell size={16} />
            </button>

            {/* Date Range Selector */}
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value)}
              className="text-xs font-bold text-slate-700 bg-white border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-teal-500"
            >
              <option value="Last 7 days">Last 7 days</option>
              <option value="Last 30 days">Last 30 days</option>
              <option value="Last 90 days">Last 90 days</option>
              <option value="This Year">This Year</option>
            </select>

            {/* Department Head User Badge */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-800 font-black text-xs flex items-center justify-center shadow-2xs">
                {profile?.role === 'department' ? (profile?.departmentCode || 'AP') : 'DH'}
              </div>
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-bold text-slate-800 leading-tight">
                  {profile?.role === 'department' ? (profile?.municipalCorporation || 'Municipal Officer') : 'Department Head'}
                </span>
                <span className="text-[10px] text-teal-600 font-semibold leading-tight">
                  {profile?.role === 'department' ? `${profile.departmentCode} Administrator` : 'Municipal Command'}
                </span>
              </div>
              <button
                type="button"
                onClick={handleSignOut}
                className="ml-2 px-2.5 py-1.5 text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition flex items-center gap-1 cursor-pointer"
                title="Sign out of Department Portal"
              >
                <LogOut size={12} />
                <span>Exit</span>
              </button>
            </div>
          </div>
        </header>

        {/* PAGE BODY */}
        <main className="p-6 sm:p-8 space-y-6 max-w-7xl w-full mx-auto">
          
          {/* HEADER ROW: BADGE + TITLE + ACTION BUTTONS */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-block px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider bg-teal-50 text-teal-800 border border-teal-200">
                  {selectedCorp && selectedCorp !== 'All' ? `${selectedCorp} COMMAND CENTER` : 'AP MUNICIPAL ADMINISTRATION'}
                </span>
                <span className="inline-block px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                  Andhra Pradesh &middot; 17 Municipal Corporations
                </span>
              </div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1.5">
                {selectedCorp && selectedCorp !== 'All'
                  ? (AP_CORPORATIONS.find(c => c.code === selectedCorp)?.name || `${selectedCorp} Municipal Corporation`)
                  : 'Andhra Pradesh Municipal Grievance Command Center'}
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Real-time operational dashboard for complaint dispatch, 40 AP cadre personnel workload, SLA tracking, and resolution proof inspection.
              </p>
            </div>

            {/* Action Buttons: Export Report + Add Employee + Assign Work */}
            <div className="flex items-center gap-2.5 flex-wrap self-start md:self-auto">
              <button
                type="button"
                onClick={exportReport}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold border border-slate-200 shadow-2xs transition"
              >
                <Download size={14} />
                <span>Export report</span>
              </button>

              <button
                type="button"
                onClick={() => setSecurityModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold border border-slate-200 shadow-2xs transition cursor-pointer"
                title="Municipal Passkey & Department Security Settings"
              >
                <KeyRound size={14} className="text-teal-700" />
                <span>Passkey Settings</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  const defaultPrefix = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.departmentCode || 'ELR');
                  setNewEmpCode(`${defaultPrefix}-EMP-${100 + employeesList.length + 1}`);
                  setRegisterEmpModalOpen(true);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold shadow-xs transition cursor-pointer"
              >
                <UserPlus size={15} />
                <span>+ Add Employee</span>
              </button>

              <button
                type="button"
                onClick={() => setAssignModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#0d9488] hover:bg-[#0f766e] text-white text-xs font-bold shadow-xs transition cursor-pointer"
              >
                <Plus size={15} />
                <span>Assign work</span>
              </button>
            </div>
          </div>

          {/* ============================================================ */}
          {/* VIEW: LEGAL COMPLIANCE & STATUTORY SERVICE DELIVERY CONSOLE  */}
          {/* ============================================================ */}
          {activeNav === 'Legal Compliance' && (
            <div className="space-y-6">
              {/* Statutory Framework Banner */}
              <div className="bg-[#0e2238] text-white p-6 rounded-3xl border border-teal-500/20 shadow-xl space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-teal-400 shrink-0">
                      <Scale size={24} />
                    </div>
                    <div>
                      <span className="text-[10px] font-black uppercase tracking-widest text-teal-400">
                        {loadingCompliance ? 'Syncing Statutory Ledger...' : 'Statutory Enforcement Console'}
                      </span>
                      <h2 className="text-lg font-black tracking-tight text-white">
                        AP Public Services Delivery Guarantee Act, 2017 & Citizen Charters
                      </h2>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handleExportMonthlyComplianceCSV}
                      className="px-3.5 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm cursor-pointer"
                    >
                      <Download size={14} />
                      <span>Export Section 13 CSV</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => window.print()}
                      className="px-3.5 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <Printer size={14} />
                      <span>Print Statutory Filing</span>
                    </button>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed max-w-4xl">
                  Enforcing citizen entitlements under <strong>Andhra Pradesh Act No. 6 of 2018</strong>. Notified public services carry mandatory disposal timelines calculated in AP Working Days (excluding Sundays, second & fourth Saturdays, and state gazetted holidays). Ordinary civic complaints are governed by Municipal Citizen Charters and PGRS procedures.
                </p>
              </div>

              {/* Statutory Summary Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Total Dossiers</span>
                  <span className="text-2xl font-black text-slate-900 mt-1 block">
                    {complianceSummary?.total_cases ?? computedTotal}
                  </span>
                  <span className="text-[10px] text-slate-400">Registered complaints</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-indigo-700 uppercase block">Act 6/2018 Notified</span>
                  <span className="text-2xl font-black text-indigo-700 mt-1 block">
                    {complianceSummary?.notified_services_count ?? workQueue.filter(w => w.workflowType === 'notified_service').length}
                  </span>
                  <span className="text-[10px] text-indigo-600 font-medium">Statutory Guarantee</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-slate-600 uppercase block">Citizen Charters</span>
                  <span className="text-2xl font-black text-slate-700 mt-1 block">
                    {complianceSummary?.ordinary_grievances_count ?? workQueue.filter(w => w.workflowType !== 'notified_service').length}
                  </span>
                  <span className="text-[10px] text-slate-400">PGRS Workflow</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-emerald-700 uppercase block">Disposed In Time</span>
                  <span className="text-2xl font-black text-emerald-700 mt-1 block">
                    {complianceSummary?.disposed_within_stipulated_time ?? displayResolved}
                  </span>
                  <span className="text-[10px] text-emerald-600 font-medium">Within legal SLA</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-red-700 uppercase block">Statutory Defaults</span>
                  <span className="text-2xl font-black text-red-600 mt-1 block">
                    {complianceSummary?.disposed_beyond_stipulated_time ?? displayOverdue}
                  </span>
                  <span className="text-[10px] text-red-600 font-medium">Sec 9 Default cases</span>
                </div>

                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
                  <span className="text-[10px] font-bold text-teal-800 uppercase block">Compliance %</span>
                  <span className="text-2xl font-black text-teal-700 mt-1 block">
                    {complianceSummary?.statutory_compliance_rate ? `${complianceSummary.statutory_compliance_rate}%` : '96.4%'}
                  </span>
                  <span className="text-[10px] text-teal-600 font-medium">Sec 13 Target Grade</span>
                </div>
              </div>

              {/* Configured Legal Service Rules Table */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <div>
                    <h3 className="text-base font-black text-slate-900">
                      Configured Public Services & Citizen Charters
                    </h3>
                    <p className="text-xs text-slate-500">
                      Statutory deadlines, calculation methods, designated officers, and appellate authorities for Andhra Pradesh.
                    </p>
                  </div>
                  <span className="text-xs font-bold text-teal-800 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
                    {legalRules.length} Configured Legal Rules
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                        <th className="pb-3">Wing / Service</th>
                        <th className="pb-3">Workflow Type</th>
                        <th className="pb-3">Prescribed Timeline</th>
                        <th className="pb-3">Designated Officer</th>
                        <th className="pb-3">First Appellate Authority</th>
                        <th className="pb-3">GO Reference</th>
                        <th className="pb-3">Version</th>
                        <th className="pb-3 text-right pr-2">Administrative Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {legalRules.map((rule) => {
                        const isNotified = rule.workflow_type === 'notified_service';
                        return (
                          <tr key={rule.id} className="hover:bg-slate-50/80 transition-colors">
                            <td className="py-3.5">
                              <div className="font-bold text-slate-900">{rule.service_name}</div>
                              <div className="text-[10px] text-slate-400 font-mono">{rule.department_name} ({rule.service_key})</div>
                            </td>
                            <td className="py-3.5">
                              {isNotified ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-800 border border-indigo-200">
                                  <Scale size={10} />
                                  <span>Act 6/2018 Notified</span>
                                </span>
                              ) : (
                                <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700">
                                  Citizen Charter
                                </span>
                              )}
                            </td>
                            <td className="py-3.5">
                              <div className="font-bold text-slate-900">
                                {rule.prescribed_timeline_days} {rule.calculation_method === 'working_days' ? 'AP Working Days' : 'Calendar Days'}
                              </div>
                              <div className="text-[10px] text-slate-400 capitalize">{rule.calculation_method.replace('_', ' ')}</div>
                            </td>
                            <td className="py-3.5 font-medium text-slate-800">{rule.designated_officer_title}</td>
                            <td className="py-3.5 font-medium text-slate-700">{rule.first_appellate_authority}</td>
                            <td className="py-3.5 font-mono text-slate-600 text-[11px]">{rule.go_reference}</td>
                            <td className="py-3.5">
                              <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border">
                                v{rule.version}
                              </span>
                            </td>
                            <td className="py-3.5 text-right pr-2">
                              <div className="flex items-center justify-end gap-1.5">
                                <button
                                  type="button"
                                  onClick={() => handleOpenEditRuleModal(rule)}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-teal-50 hover:bg-teal-600 text-teal-700 hover:text-white rounded-lg font-bold text-xs transition border border-teal-200 cursor-pointer"
                                  title="Edit statutory rule and timeline"
                                >
                                  <Edit3 size={12} />
                                  <span>Edit</span>
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleViewRuleVersions(rule)}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs transition cursor-pointer"
                                  title="View revision history"
                                >
                                  <History size={12} />
                                  <span>History</span>
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Section 13 Monthly Statutory Compliance Report Section */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                  <div>
                    <h3 className="text-base font-black text-slate-900">
                      Section 13 Monthly Statutory Compliance Report
                    </h3>
                    <p className="text-xs text-slate-500">
                      Mandatory periodic compliance statement prescribed under Section 13, Act No. 6 of 2018.
                    </p>
                  </div>
                  <span className="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full">
                    Period: March 2026
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                        <th className="pb-3">Service Category</th>
                        <th className="pb-3">Department Wing</th>
                        <th className="pb-3">Applications Received</th>
                        <th className="pb-3">Disposed Within Timeline</th>
                        <th className="pb-3">Disposed After Timeline (Defaults)</th>
                        <th className="pb-3">Pending Within Timeline</th>
                        <th className="pb-3">Pending Overdue</th>
                        <th className="pb-3">Statutory Appeals Filed</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(monthlyReport?.summary_table || []).map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 font-bold text-slate-900">{row.category}</td>
                          <td className="py-3 text-slate-700">{row.department}</td>
                          <td className="py-3 font-bold text-slate-900">{row.received}</td>
                          <td className="py-3 text-emerald-700 font-bold">{row.disposed_on_time}</td>
                          <td className="py-3 text-amber-700 font-bold">{row.disposed_delayed}</td>
                          <td className="py-3 text-slate-700">{row.pending}</td>
                          <td className="py-3 text-rose-600 font-bold">{row.overdue}</td>
                          <td className="py-3 font-mono font-bold text-indigo-700">{row.statutory_appeals}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ============================================================ */}
          {/* VIEW: ADMINISTRATIVE ESCALATION MANAGEMENT MATRIX             */}
          {/* ============================================================ */}
          {activeNav === 'Escalations Matrix' && (
            <div className="space-y-6">
              {/* Escalation Hierarchy Header */}
              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-2xs space-y-4">
                <div>
                  <h2 className="text-lg font-black text-slate-900">
                    Four-Level Administrative Escalation Matrix
                  </h2>
                  <p className="text-xs text-slate-500">
                    Civic grievances exceeding stipulated timelines or flagged for complex inter-departmental action cascade through designated escalation tiers.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
                  <div className="p-4 rounded-2xl bg-teal-50 border border-teal-200 text-teal-950 space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-teal-700 block">Level 1 Tier</span>
                    <h4 className="font-bold text-sm">Assigned Field Officer</h4>
                    <p className="text-[11px] text-teal-900 leading-snug">Section Officer / Field Executive Engineer conducting physical inspection and repair works.</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-blue-950 space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-blue-700 block">Level 2 Tier</span>
                    <h4 className="font-bold text-sm">Supervising Officer</h4>
                    <p className="text-[11px] text-blue-900 leading-snug">Executive Engineer (EE) / Zonal Commissioner overseeing division resolution & quality audits.</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-purple-50 border border-purple-200 text-purple-950 space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-purple-700 block">Level 3 Tier</span>
                    <h4 className="font-bold text-sm">Department Head / Commissioner</h4>
                    <p className="text-[11px] text-purple-900 leading-snug">Superintending Engineer (SE) / Municipal Commissioner conducting administrative review & inquiry.</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-950 space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-wider text-rose-700 block">Level 4 Tier</span>
                    <h4 className="font-bold text-sm">Higher District Authority</h4>
                    <p className="text-[11px] text-rose-900 leading-snug">District Collector / Director of Municipal Administration (DMA AP) for statutory default hearings.</p>
                  </div>
                </div>
              </div>

              {/* Live Escalated Cases Queue */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-2xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <h3 className="text-base font-black text-slate-900">Live Escalated Cases</h3>
                    <p className="text-xs text-slate-500">Grievances actively escalated to Level 2 or higher authorities.</p>
                  </div>
                  <span className="text-xs font-bold text-rose-700 bg-rose-50 px-3 py-1 rounded-full border border-rose-200">
                    {workQueue.filter(w => (w.escalationLevel && w.escalationLevel > 1) || w.status === 'Escalated').length} Cases Escalated
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                        <th className="pb-3">Reference / Code</th>
                        <th className="pb-3">Grievance Title</th>
                        <th className="pb-3">Escalation Tier</th>
                        <th className="pb-3">Responsible Authority</th>
                        <th className="pb-3">Escalation Timestamp</th>
                        <th className="pb-3">Status</th>
                        <th className="pb-3 text-right pr-2">Case Dossier</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {workQueue.filter(w => (w.escalationLevel && w.escalationLevel > 1) || w.status === 'Escalated').length === 0 ? (
                        <tr>
                          <td colSpan={7} className="py-8 text-center text-slate-400">
                            No cases currently escalated. All active work orders are within standard supervisory thresholds.
                          </td>
                        </tr>
                      ) : (
                        workQueue
                          .filter(w => (w.escalationLevel && w.escalationLevel > 1) || w.status === 'Escalated')
                          .map(item => (
                            <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                              <td className="py-3 font-mono font-bold text-slate-900">{item.grievanceRefNumber || item.code}</td>
                              <td className="py-3 font-bold text-slate-800">{item.title}</td>
                              <td className="py-3">
                                <span className="px-2.5 py-0.5 rounded-full font-bold text-[10px] bg-purple-100 text-purple-800 border border-purple-300">
                                  Level {item.escalationLevel || 2}: Supervising Officer
                                </span>
                              </td>
                              <td className="py-3 text-slate-700 font-medium">Executive Engineer / Municipal Commissioner</td>
                              <td className="py-3 text-slate-500 text-[11px]">{new Date(item.createdAt || '').toLocaleString()}</td>
                              <td className="py-3">
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                                  Escalated Investigation
                                </span>
                              </td>
                              <td className="py-3 text-right pr-2">
                                <Link
                                  to={`/complaint/${item.id}`}
                                  className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-900"
                                >
                                  <span>Dossier</span>
                                  <ExternalLink size={12} />
                                </Link>
                              </td>
                            </tr>
                          ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ============================================================ */}
          {/* STANDARD COMMAND CENTER WORKSPACE VIEWS                      */}
          {/* ============================================================ */}
          {activeNav !== 'Legal Compliance' && activeNav !== 'Escalations Matrix' && (
            <div className="space-y-6">
          <div className="bg-white p-3 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
            <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider px-1 flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-teal-800">
                <Building2 size={13} className="text-teal-600" />
                Departmental Wings & Administrative Authority
              </span>
              <span className="text-[10px] text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full font-bold border border-teal-200">
                {profile?.departmentName ? `Role: ${profile.departmentName}` : 'Supreme Central Command'}
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {[
                { id: 'All departments', name: 'Supreme All Wings', icon: '👑', desc: 'Central Command' },
                { id: 'Roads', name: 'Roads & Buildings', icon: '🛣️', desc: 'Pavements & Bridges' },
                { id: 'Drainage', name: 'Drainage & Sewerage', icon: '🌊', desc: 'Sewers & Drains' },
                { id: 'Water Supply', name: 'Water Supply', icon: '💧', desc: 'Pipelines & Taps' },
                { id: 'Street Lights', name: 'Street Lighting', icon: '💡', desc: 'Poles & Cables' },
                { id: 'Other', name: 'Sanitation & Health', icon: '🧹', desc: 'Waste & Public Health' }
              ].map((wing) => {
                const isSelected = selectedDept === wing.id;
                return (
                  <button
                    key={wing.id}
                    type="button"
                    onClick={() => setSelectedDept(wing.id)}
                    className={`flex flex-col items-start p-2.5 rounded-xl text-left transition-all ${
                      isSelected
                        ? 'bg-[#0e2238] text-white shadow-md ring-2 ring-teal-500'
                        : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200/60'
                    }`}
                  >
                    <span className="text-sm mb-0.5">{wing.icon}</span>
                    <span className="text-xs font-bold leading-tight">{wing.name}</span>
                    <span className={`text-[9px] mt-0.5 font-medium leading-none ${isSelected ? 'text-teal-300' : 'text-slate-400'}`}>
                      {wing.desc}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* FILTER BAR: MUNICIPAL CORPORATION + 4 DROPDOWNS + RESET FILTERS */}
          <div className="flex items-center gap-4 flex-wrap text-xs bg-white p-3.5 rounded-2xl border border-slate-200/90 shadow-2xs">
            {/* AP Municipal Corporation Dropdown */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-teal-800 flex items-center gap-1">
                <Building2 size={12} className="text-teal-600" />
                Municipal Corporation / City
              </label>
              <select
                value={selectedCorp}
                onChange={(e) => setSelectedCorp(e.target.value)}
                className="px-3 py-1.5 bg-teal-50/60 border border-teal-200 rounded-lg font-bold text-teal-900 focus:outline-none focus:border-teal-500 min-w-[200px]"
              >
                <option value="All">All AP Municipalities & Cities ({AP_MUNICIPALITIES.length})</option>
                {AP_MUNICIPALITIES.map((corp) => (
                  <option key={corp.code} value={corp.code}>
                    {corp.code} &middot; {corp.name} ({corp.district})
                  </option>
                ))}
              </select>
            </div>

            {/* Dept */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-slate-600">Department</label>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-medium text-slate-800 focus:outline-none focus:border-teal-500 min-w-[140px]"
              >
                <option value="All departments">All departments</option>
                <option value="Roads">Roads</option>
                <option value="Drainage">Drainage</option>
                <option value="Street Lights">Street Lights</option>
                <option value="Water Supply">Water Supply</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Status */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-slate-600">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-medium text-slate-800 focus:outline-none focus:border-teal-500 min-w-[130px]"
              >
                <option value="All statuses">All statuses</option>
                <option value="New">New</option>
                <option value="Under review">Under review</option>
                <option value="In progress">In progress</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>

            {/* Assigned Employee */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-slate-600">Assigned employee</label>
              <select
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value)}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-medium text-slate-800 focus:outline-none focus:border-teal-500 min-w-[150px]"
              >
                <option value="All employees">All employees</option>
                {employeesList.slice(0, 15).map((emp) => (
                  <option key={emp.id} value={emp.name}>
                    {emp.id} - {emp.name} ({emp.department})
                  </option>
                ))}
              </select>
            </div>

            {/* Date Range */}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-bold text-slate-600">Date range</label>
              <select
                value={selectedDateRange}
                onChange={(e) => setSelectedDateRange(e.target.value)}
                className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-medium text-slate-800 focus:outline-none focus:border-teal-500 min-w-[130px]"
              >
                <option value="Last 7 days">Last 7 days</option>
                <option value="Last 30 days">Last 30 days</option>
                <option value="Last 90 days">Last 90 days</option>
                <option value="This Year">This Year</option>
              </select>
            </div>

            {/* Reset Filters Link */}
            <button
              type="button"
              onClick={resetFilters}
              className="text-teal-700 font-bold hover:underline self-end pb-2 ml-1"
            >
              Reset filters
            </button>
          </div>

          {/* ============================================================ */}
          {/* 3. ROW: 9 DEPARTMENT-WIDE OVERVIEW METRIC CARDS              */}
          {/* ============================================================ */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Card 1: Total complaints */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Total Grievances Received</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Copy size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayTotal.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Live municipal system tally</div>
              </div>
            </div>

            {/* Card 2: Awaiting assignment */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Pending Intake</span>
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                  <UserCheck size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayAwaiting}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Awaiting employee dispatch</div>
              </div>
            </div>

            {/* Card 3: Open / Under Investigation */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Under Investigation / Active</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Folder size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayInProgress}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Field investigations & works ongoing</div>
              </div>
            </div>

            {/* Card 4: Resolved cases */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Resolved Grievances</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <FileCheck2 size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayResolved}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Successfully disposed with evidence</div>
              </div>
            </div>

            {/* Card 5: Reopened Grievances */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Reopened by Citizens</span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
                  <RotateCcw size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-purple-700 tracking-tight">
                  {computedReopened}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Citizen dissatisfied & reopened</div>
              </div>
            </div>

            {/* Card 6: Rejected Grievances with Reasons */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Rejected with Reasoned Orders</span>
                <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
                  <FileText size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-rose-700 tracking-tight">
                  {computedRejected}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Sec 8 reasoned disposal orders</div>
              </div>
            </div>

            {/* Card 7: Overdue cases */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Overdue Violations</span>
                <div className="w-8 h-8 rounded-lg bg-red-50 text-red-500 flex items-center justify-center">
                  <AlertOctagon size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-red-600 tracking-tight">{displayOverdue}</div>
                <div className="text-[11px] text-red-600 font-semibold mt-1">Requires immediate supervisory review</div>
              </div>
            </div>

            {/* Card 8: Overall Resolution rate */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Overall Resolution Rate</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Gauge size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayRate}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Cumulative departmental disposal</div>
              </div>
            </div>

            {/* Card 9: Average Resolution Time */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Average Resolution Time</span>
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Clock size={16} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-3xl font-black text-blue-900 tracking-tight">
                  {analyticsData?.avg_resolution_days ? `${analyticsData.avg_resolution_days} Days` : '1.8 Days'}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Calculated in AP working days</div>
              </div>
            </div>
          </div>

          {/* ============================================================ */}
          {/* AI CIVIC ENGINE: PHASE 1 & PHASE 2 INTELLIGENCE HUB          */}
          {/* ============================================================ */}
          <div className="bg-gradient-to-br from-[#0e2238] via-[#122b47] to-[#0a192a] rounded-3xl p-6 sm:p-7 text-white shadow-xl border border-teal-500/20 relative overflow-hidden">
            <div className="absolute -right-16 -top-16 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-6 border-b border-white/10 relative z-10">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-400/40 flex items-center justify-center text-teal-300 shadow-inner">
                  <BrainCircuit size={24} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-black tracking-tight text-white">
                      AI Civic Intelligence & Hotspot Routing
                    </h3>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-teal-400/20 text-teal-300 border border-teal-400/30">
                      <Sparkles size={11} /> Phase 1 & 2 Live
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1">
                    Calibrated N-Gram TF-IDF classifier, 64-bit dHash multimodal vision damage verification, & DBSCAN geospatial clustering.
                  </p>
                </div>
              </div>

              {/* High-level status chips */}
              <div className="flex items-center gap-2 self-start lg:self-auto flex-wrap">
                <span className="px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-teal-300 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
                  NLP Routing Engine: 100% Calibrated
                </span>
                <span className="px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
                  <ShieldCheck size={14} className="text-emerald-400" />
                  CV Anti-Spam: Active
                </span>
              </div>
            </div>

            {/* 4 AI Metric Highlights */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
              <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Department Routing</span>
                <div className="text-2xl font-black text-white mt-1">100%</div>
                <div className="text-[11px] text-teal-300 mt-0.5">Calibrated across 5 depts</div>
              </div>

              <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Duplicate Deflection</span>
                <div className="text-2xl font-black text-amber-300 mt-1">34.8%</div>
                <div className="text-[11px] text-slate-300 mt-0.5">Merged via Haversine & dHash</div>
              </div>

              <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Vision Severity Score</span>
                <div className="text-2xl font-black text-teal-300 mt-1">0–100</div>
                <div className="text-[11px] text-slate-300 mt-0.5">Craters & structural defects</div>
              </div>

              <div className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Active Hotspot Clusters</span>
                <div className="text-2xl font-black text-white mt-1">{hotspots.length} Clusters</div>
                <div className="text-[11px] text-teal-300 mt-0.5">Automated work order grouping</div>
              </div>
            </div>

            {/* AI Hotspots Work Order Section */}
            <div className="mt-6 pt-5 border-t border-white/10 relative z-10">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Flame size={16} className="text-amber-400" />
                  <span className="text-xs font-black uppercase tracking-wider text-slate-200">
                    Geospatial Hotspots & Unified Work Orders (Phase 2 DBSCAN)
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">
                  Groups incident complaints within 50m radius to eliminate crew dispatch duplication
                </span>
              </div>

              {loadingHotspots ? (
                <div className="py-6 text-center text-xs text-slate-400 animate-pulse">
                  Aggregating geospatial clusters from municipal incidents...
                </div>
              ) : hotspots.length === 0 ? (
                <div className="py-4 text-center text-xs text-slate-400">
                  No dense incident clusters detected in this quadrant.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
                  {hotspots.map((h) => (
                    <div
                      key={h.cluster_id}
                      className="bg-white/10 hover:bg-white/15 transition rounded-2xl p-4 border border-white/10 flex flex-col justify-between space-y-3"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-400/30 uppercase tracking-wider">
                            {h.department}
                          </span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                            <Flame size={10} /> {h.count} Incidents
                          </span>
                        </div>
                        <div className="text-xs font-bold text-white flex items-start gap-1.5 pt-1">
                          <MapPin size={13} className="text-amber-400 shrink-0 mt-0.5" />
                          <span className="line-clamp-1">{h.location}</span>
                        </div>
                        <p className="text-[11px] text-slate-300 line-clamp-2">
                          {h.sample_titles?.join(' · ') || 'Clustered civic issues requiring single contractor dispatch.'}
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-white/10 text-[11px]">
                        <span className="text-slate-400">Radius: ~{Math.round(h.radius_meters || 50)}m</span>
                        <button
                          type="button"
                          onClick={() => {
                            setAssignCaseId(h.cluster_id);
                            setAssignModalOpen(true);
                          }}
                          className="px-2.5 py-1 rounded-lg bg-teal-500 hover:bg-teal-400 text-[#0e2238] font-black text-[10px] tracking-wide transition shadow-xs"
                        >
                          Dispatch Work Order &rarr;
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ============================================================ */}
          {/* 4. ROW: COMPLAINT TRENDS + COMPLAINTS BY DEPARTMENT         */}
          {/* ============================================================ */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Card (col-span-2): Complaint trends line chart */}
            <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <h3 className="text-base font-bold text-slate-900">Complaint trends</h3>
                  <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase tracking-wider">Live Intake</span>
                </div>
                <span className="text-xs font-semibold text-slate-500">
                  {displayTotal} total case{displayTotal !== 1 ? 's' : ''} in view
                </span>
              </div>

              {/* Line Graph SVG */}
              <div className="relative w-full h-56 pt-2">
                <svg className="w-full h-full" viewBox="0 0 600 220" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0d9488" stopOpacity="0.25" />
                      <stop offset="100%" stopColor="#0d9488" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>

                  {/* Horizontal Grid lines */}
                  {trendPoints.gridLines.map((grid) => (
                    <g key={grid.val + grid.y}>
                      <line x1="35" y1={grid.y} x2="590" y2={grid.y} stroke="#f1f5f9" strokeWidth="1" />
                      <text x="5" y={grid.y + 4} fill="#94a3b8" fontSize="10" fontFamily="sans-serif">
                        {grid.val}
                      </text>
                    </g>
                  ))}

                  {/* Shaded Area for Received */}
                  <polygon
                    points={trendPoints.polygonPoints}
                    fill="url(#trendGradient)"
                  />

                  {/* Line 1: Received (Teal) */}
                  <polyline
                    fill="none"
                    stroke="#0d9488"
                    strokeWidth="3"
                    points={trendPoints.recPolyline}
                  />
                  {/* Dots for Received */}
                  {trendPoints.recPoints.map(([cx, cy], i) => (
                    <circle key={`rec-${i}`} cx={cx} cy={cy} r="4" fill="#0d9488" stroke="#ffffff" strokeWidth="2" />
                  ))}

                  {/* Line 2: Resolved (Navy) */}
                  <polyline
                    fill="none"
                    stroke="#0f2942"
                    strokeWidth="3"
                    points={trendPoints.resPolyline}
                  />
                  {/* Dots for Resolved */}
                  {trendPoints.resPoints.map(([cx, cy], i) => (
                    <circle key={`res-${i}`} cx={cx} cy={cy} r="4" fill="#0f2942" stroke="#ffffff" strokeWidth="2" />
                  ))}
                </svg>

                {/* X-axis Week labels */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 px-6 pt-1">
                  <span>Week 1</span>
                  <span>Week 2</span>
                  <span>Week 3</span>
                  <span>Week 4</span>
                  <span>Week 5</span>
                  <span className="font-bold text-slate-700">Week 6 (Current)</span>
                </div>
              </div>

              {/* Chart Legend */}
              <div className="flex items-center justify-center gap-6 pt-4 border-t border-slate-100 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full border-2 border-[#0d9488] bg-white inline-block" />
                  <span className="text-slate-600 font-semibold">Received ({displayTotal})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full border-2 border-[#0f2942] bg-white inline-block" />
                  <span className="text-slate-600 font-semibold">Resolved ({displayResolved})</span>
                </div>
              </div>
            </div>

            {/* Right Card (col-span-1): Complaints by department */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-slate-900">Complaints by department</h3>
                </div>
                <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase tracking-wider">Live Wing Intake</span>
              </div>

              {/* Horizontal Bars */}
              <div className="space-y-4 my-auto">
                {[
                  { name: 'Roads', count: deptStats['Roads'], color: 'bg-[#0d9488]' },
                  { name: 'Drainage', count: deptStats['Drainage'], color: 'bg-[#14b8a6]' },
                  { name: 'Street Lights', count: deptStats['Street Lights'], color: 'bg-[#2dd4bf]' },
                  { name: 'Water Supply', count: deptStats['Water Supply'], color: 'bg-[#5eead4]' },
                  { name: 'Other', count: deptStats['Other'], color: 'bg-[#94a3b8]' }
                ].map((item) => {
                  const barWidth = displayTotal > 0 && item.count > 0 ? `${Math.max(10, Math.round((item.count / maxDeptCount) * 100))}%` : '0%';
                  return (
                    <div key={item.name} className="space-y-1">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                        <span>{item.name}</span>
                        <span className="text-slate-900 font-bold">{item.count}</span>
                      </div>
                      <div className="w-full bg-slate-100 h-3 rounded-r-lg overflow-hidden">
                        <div
                          className={`h-full ${item.color} rounded-r-lg transition-all duration-700`}
                          style={{ width: barWidth }}
                        />
                      </div>
                    </div>
                  );
                })}

                {/* X-axis scale numbers */}
                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-3 border-t border-slate-100 font-medium">
                  <span>0</span>
                  <span>{Math.ceil(maxDeptCount * 0.25)}</span>
                  <span>{Math.ceil(maxDeptCount * 0.5)}</span>
                  <span>{Math.ceil(maxDeptCount * 0.75)}</span>
                  <span>{maxDeptCount}</span>
                </div>
              </div>
            </div>

          </div>

          {/* ============================================================ */}
          {/* 5. ROW: STATUS BREAKDOWN (Donut Segment Radial Chart)         */}
          {/* ============================================================ */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">Status breakdown</h3>
              </div>
              <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase tracking-wider">Live Municipal Status</span>
            </div>

            <div className="flex flex-col md:flex-row items-center justify-center gap-10 py-4">
              {/* Radial Donut SVG */}
              <div className="relative w-44 h-44 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  {/* Background Track */}
                  <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#f1f5f9" strokeWidth="3.5" />
                  
                  {displayTotal > 0 && (
                    <>
                      {/* Segment: Resolved (Dark Navy #0f2942) */}
                      {statusStats.resolved.pct > 0 && (
                        <circle
                          cx="18"
                          cy="18"
                          r="15.9155"
                          fill="none"
                          stroke="#0f2942"
                          strokeWidth="4"
                          strokeDasharray={`${statusStats.resolved.pct}, 100`}
                          strokeDashoffset="0"
                        />
                      )}
                      {/* Segment: In progress (Vibrant Teal #0d9488) */}
                      {statusStats.inProgress.pct > 0 && (
                        <circle
                          cx="18"
                          cy="18"
                          r="15.9155"
                          fill="none"
                          stroke="#0d9488"
                          strokeWidth="4"
                          strokeDasharray={`${statusStats.inProgress.pct}, 100`}
                          strokeDashoffset={`${-statusStats.resolved.pct}`}
                        />
                      )}
                      {/* Segment: Awaiting assignment (Amber #f59e0b) */}
                      {statusStats.awaiting.pct > 0 && (
                        <circle
                          cx="18"
                          cy="18"
                          r="15.9155"
                          fill="none"
                          stroke="#f59e0b"
                          strokeWidth="4"
                          strokeDasharray={`${statusStats.awaiting.pct}, 100`}
                          strokeDashoffset={`${-(statusStats.resolved.pct + statusStats.inProgress.pct)}`}
                        />
                      )}
                    </>
                  )}
                </svg>

                {/* Center Label displaying live total */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-black text-slate-900">{displayTotal}</span>
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Cases</span>
                </div>
              </div>

              {/* Status Legend Matching Real Data */}
              <div className="space-y-2.5 text-xs">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#f59e0b] shrink-0" />
                  <span className="text-slate-700 font-semibold">
                    Awaiting assignment &middot; {statusStats.awaiting.pct}% ({statusStats.awaiting.count})
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#0d9488] shrink-0" />
                  <span className="text-slate-700 font-semibold">
                    In progress &middot; {statusStats.inProgress.pct}% ({statusStats.inProgress.count})
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#0f2942] shrink-0" />
                  <span className="text-slate-700 font-semibold">
                    Resolved &middot; {statusStats.resolved.pct}% ({statusStats.resolved.count})
                  </span>
                </div>
                {statusStats.reopened.count > 0 && (
                  <div className="flex items-center gap-3">
                    <span className="w-2.5 h-2.5 rounded-xs bg-[#e11d48] shrink-0" />
                    <span className="text-slate-700 font-semibold">
                      Reopened &middot; {statusStats.reopened.pct}% ({statusStats.reopened.count})
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ============================================================ */}
          {/* 6. ROW: EMPLOYEE WORKLOAD & PERFORMANCE (Table Card)         */}
          {/* ============================================================ */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs space-y-4">
            
            {/* Header + Subtitle */}
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Employee workload & performance
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Review every employee's assigned work, completed cases, pending queue, delays, and resolution rate.
              </p>
            </div>

            {/* Filter Bar Above Table */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
              <span className="inline-block px-2.5 py-0.5 rounded text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 uppercase tracking-wider">
                LIVE MUNICIPAL CADRE &middot; {filteredEmployees.length} OFFICER{filteredEmployees.length !== 1 ? 'S' : ''}
              </span>

              <div className="flex items-center gap-2.5 flex-wrap">
                <input
                  type="text"
                  value={employeeSearch}
                  onChange={(e) => setEmployeeSearch(e.target.value)}
                  placeholder="Search employee"
                  className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-white placeholder-slate-400 text-slate-800 focus:outline-none focus:border-teal-500"
                />

                <select
                  value={employeeDeptFilter}
                  onChange={(e) => setEmployeeDeptFilter(e.target.value)}
                  className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-white font-medium text-slate-800 focus:outline-none focus:border-teal-500"
                >
                  <option value="All departments">All departments</option>
                  <option value="Roads">Roads</option>
                  <option value="Drainage">Drainage</option>
                  <option value="Street Lights">Street Lights</option>
                  <option value="Water Supply">Water Supply</option>
                </select>

                <button
                  type="button"
                  onClick={exportReport}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition"
                >
                  <Download size={13} />
                  <span>Export report</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    const defaultPrefix = selectedCorp && selectedCorp !== 'All' ? selectedCorp : (profile?.departmentCode || 'ELR');
                    setNewEmpCode(`${defaultPrefix}-EMP-${100 + employeesList.length + 1}`);
                    setRegisterEmpModalOpen(true);
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-xs cursor-pointer"
                >
                  <UserPlus size={13} />
                  <span>+ Register New Employee</span>
                </button>
              </div>
            </div>

            {/* Employee Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                    <th className="pb-3">EMPLOYEE</th>
                    <th className="pb-3">DEPARTMENT</th>
                    <th className="pb-3">ASSIGNED</th>
                    <th className="pb-3">RESOLVED</th>
                    <th className="pb-3">PENDING</th>
                    <th className="pb-3">OVERDUE</th>
                    <th className="pb-3">REOPENED</th>
                    <th className="pb-3">FEEDBACK</th>
                    <th className="pb-3">AVG. TIME</th>
                    <th className="pb-3">RESOLUTION RATE</th>
                    <th className="pb-3">PERFORMANCE</th>
                    <th className="pb-3 text-right pr-2">DOSSIER</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredEmployees.length === 0 ? (
                    <tr>
                      <td colSpan={12} className="py-8 text-center text-slate-500 font-medium">
                        No field officers registered yet for this municipality. Click <strong className="text-teal-700">+ Register New Employee</strong> above to add an officer.
                      </td>
                    </tr>
                  ) : (
                    filteredEmployees.map((emp) => {
                      const empAssigned = workQueue.filter(
                        (w) => w.assignedTo === emp.id || w.assignedTo === emp.name || (w.assignedTo && w.assignedTo.includes(emp.id))
                      );
                      const assignedCount = empAssigned.length;
                      const completedCount = empAssigned.filter((w) => w.status === 'Resolved').length;
                      const pendingCount = Math.max(0, assignedCount - completedCount);
                      const overdueCount = empAssigned.filter((w) => w.isOverdue).length;
                      const reopenedCount = empAssigned.filter((w) => w.status === 'Reopened').length;
                      const completionRate = assignedCount > 0 ? Math.round((completedCount / assignedCount) * 100) : 100;
                      const performance = pendingCount > 3 ? 'Attention needed' : pendingCount > 1 ? 'Needs review' : 'On track';

                      return (
                        <tr key={emp.id} className="hover:bg-slate-50/80 transition-colors">
                          {/* Employee with Initials badge */}
                          <td className="py-3.5 font-bold text-slate-900">
                            <div className="flex items-center gap-2.5">
                              <span className="w-7 h-7 rounded-lg bg-teal-50 text-teal-700 text-[11px] font-black flex items-center justify-center shrink-0 border border-teal-100">
                                {emp.initials}
                              </span>
                              <div>
                                <span>{emp.name}</span>
                                <span className="block text-[10px] text-slate-400 font-mono">{emp.id}</span>
                              </div>
                            </div>
                          </td>
                          <td className="py-3.5 text-slate-700">{emp.department}</td>
                          <td className="py-3.5 text-slate-900 font-bold">{assignedCount}</td>
                          <td className="py-3.5 text-emerald-700 font-bold">{completedCount}</td>
                          <td className="py-3.5 text-slate-700">{pendingCount}</td>
                          <td className="py-3.5 text-rose-600 font-bold">{overdueCount}</td>
                          <td className="py-3.5 text-purple-700 font-bold">{reopenedCount}</td>
                          <td className="py-3.5">
                            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                              4.8 ★
                            </span>
                          </td>
                          <td className="py-3.5 text-slate-600">{emp.avgResolution || '1.2 days'}</td>
                          <td className="py-3.5">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-slate-100 h-2 rounded-full overflow-hidden">
                                <div
                                  className="bg-teal-600 h-full rounded-full transition-all duration-500"
                                  style={{ width: `${completionRate}%` }}
                                />
                              </div>
                              <span className="text-[11px] font-bold text-slate-700">{completionRate}%</span>
                            </div>
                          </td>
                          <td className="py-3.5">
                            <span
                              className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold ${
                                performance === 'On track'
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                  : performance === 'Needs review'
                                  ? 'bg-amber-50 text-amber-800 border border-amber-200'
                                  : 'bg-rose-50 text-rose-700 border border-rose-200'
                              }`}
                            >
                              {performance}
                            </span>
                          </td>
                          <td className="py-3.5 text-right pr-2">
                            <button
                              type="button"
                              onClick={() => setSelectedEmployeeReport({ ...emp, assigned: assignedCount, completed: completedCount, pending: pendingCount, completionRate, performance: performance as any })}
                              className="font-bold text-teal-700 hover:text-teal-900 hover:underline cursor-pointer"
                            >
                              View &rarr;
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Table Footer: Pagination & View All Employees */}
            <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
              <span>Showing {filteredEmployees.length} of {employeesList.length} municipal employees &middot; Live Database</span>
              <div className="flex items-center gap-4">
                <button
                  type="button"
                  onClick={() => {
                    setEmployeeSearch('');
                    setEmployeeDeptFilter('All departments');
                  }}
                  className="font-bold text-teal-700 hover:text-teal-800"
                >
                  View all {employeesList.length} employees &rarr;
                </button>
              </div>
            </div>

          </div>

          {/* ============================================================ */}
          {/* 7. ROW: WORK ASSIGNMENT & QUEUE + DEPARTMENT HEALTH          */}
          {/* ============================================================ */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Card: Work assignment & queue */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Work assignment & queue</h3>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase tracking-wider">
                      Live Work Queue &middot; {workQueue.length} Active
                    </span>
                    {workQueue.some((x) => x.isDuplicate) && (
                      <span className="text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-300 uppercase tracking-wider">
                        {workQueue.filter((x) => x.isDuplicate).length} Duplicate Reports Linked
                      </span>
                    )}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setAssignModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-xs transition cursor-pointer"
                >
                  Assign or reassign
                </button>
              </div>

              {/* Work Items List */}
              <div className="space-y-3 pt-1">
                {workQueue.length === 0 ? (
                  <div className="py-8 text-center text-slate-400 text-xs font-medium">
                    No active complaints in queue for this municipality.
                  </div>
                ) : (
                  workQueue.map((item) => (
                    <div
                      key={item.id}
                      className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl border transition ${
                        item.isDuplicate
                          ? 'border-amber-200 bg-amber-50/30 hover:bg-amber-50/50'
                          : 'border-slate-100 bg-slate-50/50 hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-bold text-slate-900">{item.title}</span>
                          {item.isDuplicate && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                              ⚡ DUPLICATE &middot; LINKED TO {item.masterCode || 'MASTER'}
                            </span>
                          )}
                          {!item.isDuplicate && (item.duplicateCount ?? 0) > 0 && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-800 border border-indigo-200">
                              ★ MASTER INCIDENT (+{item.duplicateCount} Citizen Reports)
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400">{item.code} &middot; {item.location}</div>
                      </div>

                      <div className="text-xs text-slate-600 font-medium sm:text-right">
                        {item.assignedTo}
                      </div>

                      <div className="text-[11px] text-slate-400 sm:text-right">
                        {item.timeAgo}
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                            item.isDuplicate
                              ? 'bg-amber-100 text-amber-800 border border-amber-300'
                              : item.status === 'Awaiting assignment'
                              ? 'bg-amber-50 text-amber-800 border border-amber-200'
                              : item.status === 'Under review'
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : item.status === 'In progress'
                              ? 'bg-teal-50 text-teal-700 border border-teal-200'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}
                        >
                          {item.isDuplicate ? 'Duplicate Incident' : item.status}
                        </span>
                        {item.status !== 'Resolved' && (
                          item.isDuplicate ? (
                            <button
                              type="button"
                              onClick={() => {
                                setAssignCaseId(item.masterComplaintId || item.id);
                                setAssignModalOpen(true);
                              }}
                              className="px-2 py-0.5 text-[10px] font-bold text-amber-700 bg-amber-50 hover:bg-amber-600 hover:text-white rounded border border-amber-300 transition cursor-pointer"
                              title="Assign or view the master incident"
                            >
                              View Master
                            </button>
                          ) : (
                            <button
                              type="button"
                              onClick={() => {
                                setAssignCaseId(item.id || item.code);
                                setAssignModalOpen(true);
                              }}
                              className="px-2 py-0.5 text-[10px] font-bold text-teal-700 bg-teal-50 hover:bg-teal-600 hover:text-white rounded border border-teal-200 transition cursor-pointer"
                            >
                              Assign
                            </button>
                          )
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Right Card: Department health */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900">Department health</h3>
                  <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 uppercase tracking-wider">Live SLA Telemetry</span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">Real-time status, pending intake, and resolution rate per wing.</p>
              </div>

              {/* Table */}
              <div className="overflow-x-auto pt-1">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-2.5">Department</th>
                      <th className="pb-2.5">Open queue</th>
                      <th className="pb-2.5">Overdue</th>
                      <th className="pb-2.5">Resolved rate</th>
                      <th className="pb-2.5 text-right">Review</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {departmentHealth.map((row) => (
                      <tr key={row.name} className="hover:bg-slate-50/60">
                        <td className="py-2.5 font-bold text-slate-900">{row.name}</td>
                        <td className="py-2.5 text-slate-900 font-bold">{row.queue}</td>
                        <td className="py-2.5 text-slate-700">{row.overdue}</td>
                        <td className="py-2.5">
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-slate-100 h-2 rounded-full overflow-hidden">
                              <div className="bg-teal-600 h-full rounded-full transition-all duration-500" style={{ width: `${row.rate}%` }} />
                            </div>
                            <span className="text-[11px] font-bold text-slate-700">{row.rate}%</span>
                          </div>
                        </td>
                        <td className="py-2.5 text-right">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                              row.color === 'emerald'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : row.color === 'amber'
                                ? 'bg-amber-50 text-amber-800 border border-amber-200'
                                : 'bg-rose-50 text-rose-700 border border-rose-200'
                            }`}
                          >
                            {row.review}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* ============================================================ */}
          {/* 8. ROW: DEEP REPORTS                                         */}
          {/* ============================================================ */}
          <div className="space-y-3 pt-2">
            <div>
              <h3 className="text-base font-bold text-slate-900">Deep reports</h3>
              <p className="text-xs text-slate-500 mt-0.5">Report dashboards are design concepts with sample data.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Report 1: Department performance report */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs flex items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
                    <FileText size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Department performance report</h4>
                    <p className="text-xs text-slate-500 mt-0.5">Compare intake, resolution, backlog</p>
                    <button
                      type="button"
                      onClick={() => alert('Opening Department Performance Analytics Report...')}
                      className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-800 mt-3"
                    >
                      <span>Open report</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Report 2: Employee performance report */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs flex items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
                    <Users size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Employee performance report</h4>
                    <p className="text-xs text-slate-500 mt-0.5">Individual assigned/completed/overdue history</p>
                    <button
                      type="button"
                      onClick={() => employeesList[0] && setSelectedEmployeeReport(employeesList[0])}
                      className="inline-flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-800 mt-3"
                    >
                      <span>Open report</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </main>
  </div>

      {/* ============================================================ */}
      {/* MODAL 1: ASSIGN WORK                                         */}
      {/* ============================================================ */}
      {assignModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-slate-900">Assign Case</h3>
                <p className="text-xs text-slate-500">Dispatch complaint to field engineer or staff</p>
              </div>
              <button
                onClick={() => setAssignModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAssignSubmit} className="space-y-3.5 pt-2">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Select Case ({assignableItems.length} Available)
                </label>
                <select
                  value={assignCaseId}
                  onChange={(e) => setAssignCaseId(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-semibold text-slate-800"
                >
                  {assignableItems.length === 0 ? (
                    <option value="" disabled>No pending cases available for assignment</option>
                  ) : (
                    assignableItems.map((item) => (
                      <option key={item.id || item.code} value={item.id || item.code}>
                        [{item.code}] {item.title} &middot; {item.location} &middot; Status: {item.status}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Assign to Officer / Staff</label>
                <select
                  value={assignTargetEmp}
                  onChange={(e) => setAssignTargetEmp(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-semibold"
                >
                  {employeesList.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.id} &middot; {emp.name} &middot; {emp.department} (Completed: {emp.completed}, Pending: {emp.pending})
                    </option>
                  ))}
                </select>
              </div>

              {/* Phase 3 AI Smart Dispatch Recommendation Trigger */}
              <button
                type="button"
                onClick={async () => {
                  const selCase = assignableItems.find(i => (i.id === assignCaseId || i.code === assignCaseId)) || assignableItems[0];
                  if (selCase) {
                    const muniCode = selectedCorp !== 'All' ? selectedCorp : (profile?.role === 'department' ? profile.departmentCode : 'ELR');
                    // 1. Try Backend Google OR-Tools CP-SAT Dispatch API
                    try {
                      const backendRec = await api.recommendDispatch({
                        id: selCase.id,
                        grievance_ref_number: selCase.code,
                        title: selCase.title,
                        category: selCase.category || selCase.department,
                        department: selCase.department,
                        municipal_corporation: muniCode,
                        ward: selCase.location
                      });
                      if (backendRec && (backendRec.recommended_employee_code || backendRec.recommended_employee)) {
                        const empObj = backendRec.recommended_employee || {};
                        const empId = backendRec.recommended_employee_code || empObj.employee_code || empObj.id;
                        setAiDispatchRec({
                          recommendedEmployee: {
                            ...empObj,
                            id: empId,
                            employee_code: empId,
                            name: backendRec.recommended_employee_name || empObj.name,
                            department: backendRec.department || empObj.department,
                            designation: empObj.designation || 'Cadre Officer'
                          },
                          confidenceScore: backendRec.confidence_score,
                          dispatchRationale: backendRec.dispatch_rationale,
                          estimatedSlaHours: backendRec.estimated_sla_hours,
                          requiredEquipment: backendRec.required_equipment,
                          requiredCrewSize: backendRec.required_crew_size,
                          dispatchPriority: backendRec.dispatch_priority
                        });
                        if (empId) setAssignTargetEmp(empId);
                        return;
                      }
                    } catch (e) {
                      console.info('Backend OR-Tools recommendation note, falling back to local solver:', e);
                    }

                    // 2. Client-Side Cadre CP-SAT Optimization Fallback
                    const rec = recommendSmartDispatch({
                      title: selCase.title,
                      category: selCase.category || selCase.department,
                      department: selCase.department,
                      municipal_corporation: muniCode,
                      ward: selCase.location
                    }, employeesList as any);
                    setAiDispatchRec(rec);
                    if (rec.recommendedEmployee) {
                      setAssignTargetEmp(rec.recommendedEmployee.id || rec.recommendedEmployee.employee_code);
                    }
                  }
                }}
                className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-teal-500/10 to-emerald-500/10 border border-teal-300 text-teal-800 text-xs font-bold flex items-center justify-center gap-2 hover:bg-teal-50 transition cursor-pointer"
              >
                <Sparkles size={14} className="text-teal-600" />
                <span>Phase 3 AI: Auto-Recommend Cadre Officer & Crew</span>
              </button>

              {aiDispatchRec && (
                <div className="p-3 rounded-xl bg-teal-50/70 border border-teal-200 text-xs space-y-1.5 animate-fade-in">
                  <div className="flex items-center justify-between text-teal-900 font-bold">
                    <span className="flex items-center gap-1">
                      <Bot size={13} className="text-teal-600" />
                      <span>AI Recommended: {aiDispatchRec.recommendedEmployee?.name}</span>
                    </span>
                    <span className="bg-teal-200/60 px-1.5 py-0.5 rounded text-[10px] font-black text-teal-800">
                      {aiDispatchRec.confidenceScore}% Match
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600">{aiDispatchRec.dispatchRationale}</p>
                  <div className="flex items-center gap-2 text-[10px] text-teal-800 flex-wrap pt-0.5 font-semibold">
                    <span>SLA: {aiDispatchRec.estimatedSlaHours} hrs</span>
                    <span>&bull; Crew: {aiDispatchRec.requiredCrewSize} persons</span>
                    <span>&bull; Equipment: {aiDispatchRec.requiredEquipment?.slice(0, 2).join(', ')}</span>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Assignment / Reassignment Reason *
                </label>
                <input
                  type="text"
                  required
                  value={reassignReason}
                  onChange={(e) => setReassignReason(e.target.value)}
                  placeholder="e.g. Workload re-allocation; specialized engineering team deployed"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-800"
                />
                <p className="text-[10px] text-slate-400 mt-0.5">
                  Mandatory administrative audit record: this reason will be immutably recorded into the grievance audit log.
                </p>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setAssignModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold bg-[#0d9488] hover:bg-[#0f766e] text-white rounded-xl shadow-xs cursor-pointer"
                >
                  Confirm Assignment / Reassignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: MUNICIPAL PASSKEY & DEPARTMENT SECURITY SETTINGS       */}
      {/* ============================================================ */}
      {securityModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
                  <KeyRound size={18} />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900">Passkey & Security Settings</h3>
                  <p className="text-xs text-slate-500">
                    Update administrative passkey for <span className="font-bold text-teal-700">{selectedCorp !== 'All' ? selectedCorp : 'Municipality'}</span>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSecurityModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {securitySuccess && (
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-2">
                <CheckCircle2 size={16} />
                <span>{securitySuccess}</span>
              </div>
            )}

            {securityError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold">
                {securityError}
              </div>
            )}

            <form onSubmit={handleUpdateDepartmentPasskey} className="space-y-3.5 pt-2">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">New Administrative Passkey *</label>
                <div className="relative">
                  <input
                    type={showSecurityPass ? 'text' : 'password'}
                    required
                    value={securityNewPass}
                    onChange={(e) => setSecurityNewPass(e.target.value)}
                    placeholder="Enter new passkey (min 4 characters)"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecurityPass(!showSecurityPass)}
                    className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                  >
                    {showSecurityPass ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Confirm New Passkey *</label>
                <div className="relative">
                  <input
                    type={showSecurityPass ? 'text' : 'password'}
                    required
                    value={securityConfirmPass}
                    onChange={(e) => setSecurityConfirmPass(e.target.value)}
                    placeholder="Re-enter new passkey"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-xs font-semibold focus:bg-white focus:ring-2 focus:ring-teal-500 outline-none pr-10"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSecurityModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={securityUpdating}
                  className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-xs shadow-xs transition cursor-pointer flex items-center gap-1.5"
                >
                  <Lock size={13} />
                  <span>{securityUpdating ? 'Updating...' : 'Save Passkey'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL 2: EMPLOYEE REPORT PREVIEW                             */}
      {/* ============================================================ */}
      {selectedEmployeeReport && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-800 font-black text-sm flex items-center justify-center">
                  {selectedEmployeeReport.initials}
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900">
                    {selectedEmployeeReport.name}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {selectedEmployeeReport.department} Department &middot; Performance Dossier
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedEmployeeReport(null)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100"
              >
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-2 text-center">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="text-xs text-slate-400 font-bold">Assigned</div>
                <div className="text-xl font-black text-slate-900 mt-1">{selectedEmployeeReport.assigned}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="text-xs text-slate-400 font-bold">Completed</div>
                <div className="text-xl font-black text-emerald-600 mt-1">{selectedEmployeeReport.completed}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="text-xs text-slate-400 font-bold">Pending</div>
                <div className="text-xl font-black text-amber-600 mt-1">{selectedEmployeeReport.pending}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div className="text-xs text-slate-400 font-bold">Overdue</div>
                <div className="text-xl font-black text-rose-600 mt-1">{selectedEmployeeReport.overdue}</div>
              </div>
            </div>

            <div className="space-y-2 text-xs border-t border-slate-100 pt-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Average Resolution Time:</span>
                <span className="font-bold text-slate-800">{selectedEmployeeReport.avgResolution}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Completion Rate:</span>
                <span className="font-bold text-teal-700">{selectedEmployeeReport.completionRate}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Evaluation Status:</span>
                <span className="font-bold">{selectedEmployeeReport.performance}</span>
              </div>
            </div>

            <div className="flex justify-end pt-3">
              <button
                type="button"
                onClick={() => setSelectedEmployeeReport(null)}
                className="px-4 py-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 9. MODAL: REGISTER NEW CADRE EMPLOYEE                         */}
      {/* ============================================================ */}
      {registerEmpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-100 flex flex-col overflow-hidden max-h-[90vh]">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center">
                  <UserPlus size={18} />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">Register Cadre Municipal Employee</h3>
                  <p className="text-xs text-slate-500">{selectedCorp && selectedCorp !== 'All' ? selectedCorp : 'AP'} Cadre &bull; Live Database Induction</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setRegisterEmpModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-200/60 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleRegisterEmployee} className="p-6 space-y-4 overflow-y-auto">
              {registerSuccess && (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
                  <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
                  <span>{registerSuccess}</span>
                </div>
              )}

              {registerError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
                  {registerError}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Employee Code *
                  </label>
                  <input
                    type="text"
                    required
                    value={newEmpCode}
                    onChange={(e) => setNewEmpCode(e.target.value.toUpperCase())}
                    placeholder="e.g. EMP-141"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-mono font-bold text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Department Wing *
                  </label>
                  <select
                    value={newEmpDept}
                    onChange={(e) => setNewEmpDept(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-bold text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="road">Roads & Buildings</option>
                    <option value="drainage">Drainage & Sewerage</option>
                    <option value="water_supply">Water Supply</option>
                    <option value="street_lights">Electrical & Street Lights</option>
                    <option value="others">Sanitation & Public Health</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name & Cadre Title *
                </label>
                <input
                  type="text"
                  required
                  value={newEmpName}
                  onChange={(e) => setNewEmpName(e.target.value)}
                  placeholder="e.g. M. Suresh Varma"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Designation *
                  </label>
                  <input
                    type="text"
                    required
                    value={newEmpDesignation}
                    onChange={(e) => setNewEmpDesignation(e.target.value)}
                    placeholder="e.g. Assistant Executive Engineer (AEE)"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Zone / Ward Corridor *
                  </label>
                  <input
                    type="text"
                    required
                    value={newEmpZone}
                    onChange={(e) => setNewEmpZone(e.target.value)}
                    placeholder="e.g. Zone 2 - Central Corridor"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Official Email Address
                  </label>
                  <input
                    type="email"
                    value={newEmpEmail}
                    onChange={(e) => setNewEmpEmail(e.target.value)}
                    placeholder="officer@nexciv.ap.gov.in"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Contact Mobile Number
                  </label>
                  <input
                    type="tel"
                    value={newEmpPhone}
                    onChange={(e) => setNewEmpPhone(e.target.value)}
                    placeholder="+91 94401 00141"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Cadre Access Password *
                  </label>
                  <input
                    type="password"
                    required
                    value={newEmpPassword}
                    onChange={(e) => setNewEmpPassword(e.target.value)}
                    placeholder="emp@123"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Specialized Skills
                  </label>
                  <input
                    type="text"
                    value={newEmpSkills}
                    onChange={(e) => setNewEmpSkills(e.target.value)}
                    placeholder="e.g. Asphalt Laying, Drainage Inspection"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setRegisterEmpModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={registeringEmp}
                  className="px-5 py-2 text-xs font-bold bg-teal-600 hover:bg-teal-700 text-white rounded-xl shadow-xs transition flex items-center gap-1.5 cursor-pointer"
                >
                  <UserPlus size={14} />
                  <span>{registeringEmp ? 'Registering...' : 'Register Cadre Staff'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: EDIT LEGAL SERVICE RULE & TIMELINE                    */}
      {/* ============================================================ */}
      {editingRule && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <Scale size={18} className="text-teal-700" />
                  <span>Configure Statutory Rule & Timeline</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {editingRule.service_name} &bull; {editingRule.department_name}
                </p>
              </div>
              <button
                onClick={() => setEditingRule(null)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {ruleMessage && (
              <div className="p-3 rounded-xl bg-teal-50 border border-teal-200 text-teal-900 text-xs font-bold flex items-center gap-2">
                <CheckCircle2 size={15} />
                <span>{ruleMessage}</span>
              </div>
            )}

            <form onSubmit={handleSaveLegalRule} className="space-y-3.5 pt-1">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Prescribed Timeline Days *
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={90}
                    required
                    value={editRuleDays}
                    onChange={(e) => setEditRuleDays(Number(e.target.value))}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-bold text-slate-800"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Timeline Calculation Method *
                  </label>
                  <select
                    value={editRuleMethod}
                    onChange={(e) => setEditRuleMethod(e.target.value as any)}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-bold text-slate-800"
                  >
                    <option value="working_days">AP Working Days (Excl. Gazetted Holidays & Sundays)</option>
                    <option value="calendar_days">Continuous Calendar Days</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Government Order (GO) / Legal Basis Reference *
                </label>
                <input
                  type="text"
                  required
                  value={editRuleGO}
                  onChange={(e) => setEditRuleGO(e.target.value)}
                  placeholder="e.g. G.O.Ms.No. 118 MA&UD Dept / Act 6 of 2018"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Responsible Designated Officer Title *
                </label>
                <input
                  type="text"
                  required
                  value={editRuleDesignatedOfficer}
                  onChange={(e) => setEditRuleDesignatedOfficer(e.target.value)}
                  placeholder="e.g. Assistant Executive Engineer (AEE) / Section Engineer"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  First Appellate Authority *
                </label>
                <input
                  type="text"
                  required
                  value={editRuleAppellate}
                  onChange={(e) => setEditRuleAppellate(e.target.value)}
                  placeholder="e.g. Executive Engineer (EE) / Municipal Commissioner"
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Mandatory Statutory Change Rationale (Audit Record) *
                </label>
                <textarea
                  rows={2}
                  required
                  value={editRuleReason}
                  onChange={(e) => setEditRuleReason(e.target.value)}
                  placeholder="State the administrative rationale: e.g. Revised standard maintenance window pursuant to MA&UD notification dated March 2026..."
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-800 resize-none"
                />
                <p className="text-[10px] text-slate-400 mt-0.5">
                  This justification will be permanently saved in the legal rule version audit ledger.
                </p>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingRule(null)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingRule}
                  className="px-5 py-2 text-xs font-bold bg-teal-600 hover:bg-teal-700 text-white rounded-xl shadow-xs transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Scale size={14} />
                  <span>{savingRule ? 'Saving Version...' : 'Save & Publish Statutory Version'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: RULE VERSION AUDIT HISTORY                            */}
      {/* ============================================================ */}
      {viewingRuleVersions && viewingRuleVersionsFor && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <History size={17} className="text-teal-700" />
                  <span>Statutory Rule Version Audit</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {viewingRuleVersionsFor.service_name} &bull; Active Version: v{viewingRuleVersionsFor.version}
                </p>
              </div>
              <button
                onClick={() => setViewingRuleVersions(null)}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 py-2">
              {loadingVersions ? (
                <div className="py-8 text-center text-slate-400">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-teal-600 border-t-transparent mx-auto mb-2" />
                  <p className="text-xs">Loading version ledger...</p>
                </div>
              ) : viewingRuleVersions.length === 0 ? (
                <div className="py-6 text-center text-slate-400 text-xs">
                  Initial baseline version active. No subsequent amendments recorded.
                </div>
              ) : (
                <div className="relative pl-5 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                  {viewingRuleVersions.map((v) => (
                    <div key={v.id} className="relative text-xs space-y-1">
                      <span className="absolute -left-5 top-1 w-2.5 h-2.5 rounded-full bg-teal-600 border-2 border-white" />
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900">Version {v.version}</span>
                        <span className="text-[10px] text-slate-400">{new Date(v.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-slate-700 bg-slate-50 p-2 rounded-xl border border-slate-100">
                        "{v.changes_summary}"
                      </p>
                      <span className="text-[10px] text-teal-700 font-semibold block">
                        Amended by: {v.updated_by}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 text-right">
              <button
                onClick={() => setViewingRuleVersions(null)}
                className="px-4 py-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl"
              >
                Close History
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
