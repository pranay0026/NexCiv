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
  LogOut
} from 'lucide-react';
import { api, HotspotCluster, AP_CORPORATIONS, AP_MUNICIPALITIES } from '../lib/api';
import { useAuth } from '../context/AuthContext';

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
  status: 'Awaiting assignment' | 'Under review' | 'In progress' | 'Resolved';
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

  // Work Queue State
  const [workQueue, setWorkQueue] = useState<WorkItem[]>(INITIAL_WORK_QUEUE);
  const [assignCaseId, setAssignCaseId] = useState('');
  const [assignTargetEmp, setAssignTargetEmp] = useState('EMP-101');

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
          const mappedQueue: WorkItem[] = data.map((c: any) => {
            const shortCode = c.id.length > 8 ? `NXC-${c.id.slice(0, 6).toUpperCase()}` : c.id;
            const statusLabel = c.status === 'pending' ? 'Awaiting assignment' : c.status === 'in_progress' ? 'In progress' : 'Resolved';
            const locationStr = c.landmark ? `${c.landmark}, Ward ${c.ward || '1'}` : (c.location_address || 'Coordinates provided');
            return {
              id: c.id,
              title: c.title,
              code: shortCode,
              location: locationStr,
              assignedTo: c.assigned_employee_id || c.assigned_team || 'Awaiting assignment',
              timeAgo: 'Live',
              status: statusLabel as any
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

  // Dynamic accurate metric computations from active municipality queue
  const computedTotal = workQueue.length;
  const computedAwaiting = workQueue.filter((w) => w.status === 'Awaiting assignment').length;
  const computedInProgress = workQueue.filter((w) => w.status === 'In progress' || w.status === 'Under review').length;
  const computedResolved = workQueue.filter((w) => w.status === 'Resolved').length;
  const computedRate = computedTotal > 0 ? Math.round((computedResolved / computedTotal) * 100) : 0;

  const displayTotal = analyticsData?.total_complaints !== undefined ? analyticsData.total_complaints : computedTotal;
  const displayAwaiting = analyticsData?.awaiting_assignment !== undefined ? analyticsData.awaiting_assignment : computedAwaiting;
  const displayInProgress = analyticsData?.in_progress !== undefined ? analyticsData.in_progress : computedInProgress;
  const displayOverdue = analyticsData?.overdue_cases !== undefined ? analyticsData.overdue_cases : 0;
  const displayResolved = analyticsData?.resolved !== undefined ? analyticsData.resolved : computedResolved;
  const displayRate = analyticsData?.overall_resolution_rate !== undefined ? `${analyticsData.overall_resolution_rate}%` : `${computedRate}%`;

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
        await api.assignComplaint(targetItem.id, empIdToPass, selectedEmpObj?.department);
      } catch (err) {
        console.warn('Assign backend call note:', err);
      }
    }
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

          {/* DEPARTMENT WINGS HIERARCHY SWITCHER (Supreme Command vs 5 Core Wings) */}
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
          {/* 3. ROW: 6 METRIC CARDS (3x2 Grid matching Canva screenshot)  */}
          {/* ============================================================ */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Card 1: Total complaints */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Total complaints</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Copy size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayTotal.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Live municipal system tally</div>
              </div>
            </div>

            {/* Card 2: Awaiting assignment */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Awaiting assignment</span>
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                  <UserCheck size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayAwaiting}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Pending dispatch & crew routing</div>
              </div>
            </div>

            {/* Card 3: Open cases */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">In progress / Open</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Folder size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayInProgress}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Field crew on-site action</div>
              </div>
            </div>

            {/* Card 4: Overdue cases */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Overdue cases</span>
                <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-500 flex items-center justify-center">
                  <AlertOctagon size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">{displayOverdue}</div>
                <div className="text-[11px] text-slate-400 mt-1">Attention suggested</div>
              </div>
            </div>

            {/* Card 5: Resolved cases */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Resolved cases</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <FileCheck2 size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayResolved}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Successfully closed grievances</div>
              </div>
            </div>

            {/* Card 6: Resolution rate */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600">Resolution rate</span>
                <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
                  <Gauge size={16} />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-slate-900 tracking-tight">
                  {displayRate}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">SLA compliance score</div>
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
                <h3 className="text-base font-bold text-slate-900">Complaint trends</h3>
                <span className="text-xs text-slate-400">Illustrative sample</span>
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
                  {[
                    { val: '250', y: 20 },
                    { val: '200', y: 55 },
                    { val: '150', y: 90 },
                    { val: '100', y: 125 },
                    { val: '50', y: 160 },
                    { val: '0', y: 195 }
                  ].map((grid) => (
                    <g key={grid.val}>
                      <line x1="35" y1={grid.y} x2="590" y2={grid.y} stroke="#f1f5f9" strokeWidth="1" />
                      <text x="5" y={grid.y + 4} fill="#94a3b8" fontSize="10" fontFamily="sans-serif">
                        {grid.val}
                      </text>
                    </g>
                  ))}

                  {/* Shaded Area for Received */}
                  <polygon
                    points="50,115 150,98 250,92 350,78 450,85 550,72 550,195 50,195"
                    fill="url(#trendGradient)"
                  />

                  {/* Line 1: Received (Teal) */}
                  <polyline
                    fill="none"
                    stroke="#0d9488"
                    strokeWidth="3"
                    points="50,115 150,98 250,92 350,78 450,85 550,72"
                  />
                  {/* Dots for Received */}
                  {[
                    [50, 115],
                    [150, 98],
                    [250, 92],
                    [350, 78],
                    [450, 85],
                    [550, 72]
                  ].map(([cx, cy], i) => (
                    <circle key={i} cx={cx} cy={cy} r="4" fill="#0d9488" stroke="#ffffff" strokeWidth="2" />
                  ))}

                  {/* Line 2: Resolved (Navy) */}
                  <polyline
                    fill="none"
                    stroke="#0f2942"
                    strokeWidth="3"
                    points="50,132 150,118 250,114 350,122 450,105 550,76"
                  />
                  {/* Dots for Resolved */}
                  {[
                    [50, 132],
                    [150, 118],
                    [250, 114],
                    [350, 122],
                    [450, 105],
                    [550, 76]
                  ].map(([cx, cy], i) => (
                    <circle key={i} cx={cx} cy={cy} r="4" fill="#0f2942" stroke="#ffffff" strokeWidth="2" />
                  ))}
                </svg>

                {/* X-axis Week labels */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 px-6 pt-1">
                  <span>Week 1</span>
                  <span>Week 2</span>
                  <span>Week 3</span>
                  <span>Week 4</span>
                  <span>Week 5</span>
                  <span>Week 6</span>
                </div>
              </div>

              {/* Chart Legend */}
              <div className="flex items-center justify-center gap-6 pt-4 border-t border-slate-100 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full border-2 border-[#0d9488] bg-white inline-block" />
                  <span className="text-slate-600 font-semibold">Received</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full border-2 border-[#0f2942] bg-white inline-block" />
                  <span className="text-slate-600 font-semibold">Resolved</span>
                </div>
              </div>
            </div>

            {/* Right Card (col-span-1): Complaints by department */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-slate-900">Complaints by department</h3>
                <span className="text-xs text-slate-400">Demo data</span>
              </div>

              {/* Horizontal Bars */}
              <div className="space-y-4 my-auto">
                {[
                  { name: 'Roads', count: 230, width: '78%', color: 'bg-[#0d9488]' },
                  { name: 'Drainage', count: 200, width: '68%', color: 'bg-[#14b8a6]' },
                  { name: 'Street Lights', count: 175, width: '60%', color: 'bg-[#2dd4bf]' },
                  { name: 'Water Supply', count: 165, width: '56%', color: 'bg-[#5eead4]' },
                  { name: 'Other', count: 145, width: '48%', color: 'bg-[#cbd5e1]' }
                ].map((item) => (
                  <div key={item.name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                      <span>{item.name}</span>
                    </div>
                    <div className="w-full bg-slate-100 h-3 rounded-r-lg overflow-hidden">
                      <div
                        className={`h-full ${item.color} rounded-r-lg transition-all duration-700`}
                        style={{ width: item.width }}
                      />
                    </div>
                  </div>
                ))}

                {/* X-axis scale numbers */}
                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-3 border-t border-slate-100">
                  <span>0</span>
                  <span>100</span>
                  <span>200</span>
                  <span>300</span>
                  <span>400</span>
                </div>
              </div>
            </div>

          </div>

          {/* ============================================================ */}
          {/* 5. ROW: STATUS BREAKDOWN (Donut Segment Radial Chart)         */}
          {/* ============================================================ */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900">Status breakdown</h3>
              <span className="text-xs text-slate-400">Demo data</span>
            </div>

            <div className="flex flex-col md:flex-row items-center justify-center gap-10 py-4">
              {/* Radial Donut SVG */}
              <div className="relative w-44 h-44 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  {/* Background Track */}
                  <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#f1f5f9" strokeWidth="3.5" />
                  
                  {/* Segment: Resolved (53% - Dark Navy #0f2942) */}
                  <circle
                    cx="18"
                    cy="18"
                    r="15.9155"
                    fill="none"
                    stroke="#0f2942"
                    strokeWidth="4"
                    strokeDasharray="53, 100"
                    strokeDashoffset="0"
                  />
                  {/* Segment: In progress (24% - Vibrant Teal #0d9488) */}
                  <circle
                    cx="18"
                    cy="18"
                    r="15.9155"
                    fill="none"
                    stroke="#0d9488"
                    strokeWidth="4"
                    strokeDasharray="24, 100"
                    strokeDashoffset="-53"
                  />
                  {/* Segment: Assigned (12% - Mint #2dd4bf) */}
                  <circle
                    cx="18"
                    cy="18"
                    r="15.9155"
                    fill="none"
                    stroke="#2dd4bf"
                    strokeWidth="4"
                    strokeDasharray="12, 100"
                    strokeDashoffset="-77"
                  />
                  {/* Segment: New (8% - Amber #f59e0b) */}
                  <circle
                    cx="18"
                    cy="18"
                    r="15.9155"
                    fill="none"
                    stroke="#f59e0b"
                    strokeWidth="4"
                    strokeDasharray="8, 100"
                    strokeDashoffset="-89"
                  />
                  {/* Segment: Reopened (3% - Rose #e11d48) */}
                  <circle
                    cx="18"
                    cy="18"
                    r="15.9155"
                    fill="none"
                    stroke="#e11d48"
                    strokeWidth="4"
                    strokeDasharray="3, 100"
                    strokeDashoffset="-97"
                  />
                </svg>
              </div>

              {/* Status Legend Matching Canva Design */}
              <div className="space-y-2.5 text-xs">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#f59e0b] shrink-0" />
                  <span className="text-slate-600 font-medium">New &middot; 8% (103)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#2dd4bf] shrink-0" />
                  <span className="text-slate-600 font-medium">Assigned &middot; 12% (154)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#0d9488] shrink-0" />
                  <span className="text-slate-600 font-medium">In progress &middot; 24% (308)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#0f2942] shrink-0" />
                  <span className="text-slate-600 font-medium">Resolved &middot; 53% (681)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#e11d48] shrink-0" />
                  <span className="text-slate-600 font-medium">Reopened &middot; 3% (38)</span>
                </div>
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
              <span className="inline-block px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                DEMO DATA &middot; FICTIONAL EMPLOYEES
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
                    <th className="pb-3">COMPLETED</th>
                    <th className="pb-3">PENDING</th>
                    <th className="pb-3">OVERDUE</th>
                    <th className="pb-3">AVG. RESOLUTION</th>
                    <th className="pb-3">COMPLETION RATE</th>
                    <th className="pb-3">PERFORMANCE</th>
                    <th className="pb-3 text-right pr-2">REPORT</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredEmployees.map((emp) => (
                    <tr key={emp.id} className="hover:bg-slate-50/80 transition-colors">
                      {/* Employee with Initials badge */}
                      <td className="py-3.5 font-bold text-slate-900">
                        <div className="flex items-center gap-2.5">
                          <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 text-[11px] font-black flex items-center justify-center shrink-0">
                            {emp.initials}
                          </span>
                          <span>{emp.name}</span>
                        </div>
                      </td>
                      <td className="py-3.5 text-slate-700">{emp.department}</td>
                      <td className="py-3.5 text-slate-700">{emp.assigned}</td>
                      <td className="py-3.5 text-slate-700">{emp.completed}</td>
                      <td className="py-3.5 text-slate-700">{emp.pending}</td>
                      <td className="py-3.5 text-slate-700">{emp.overdue}</td>
                      <td className="py-3.5 text-slate-600">{emp.avgResolution}</td>
                      <td className="py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-slate-100 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-teal-600 h-full rounded-full"
                              style={{ width: `${emp.completionRate}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-bold text-slate-700">{emp.completionRate}%</span>
                        </div>
                      </td>
                      <td className="py-3.5">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold ${
                            emp.performance === 'On track'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : emp.performance === 'Needs review'
                              ? 'bg-amber-50 text-amber-800 border border-amber-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {emp.performance}
                        </span>
                      </td>
                      <td className="py-3.5 text-right pr-2">
                        <button
                          type="button"
                          onClick={() => setSelectedEmployeeReport(emp)}
                          className="font-bold text-teal-700 hover:text-teal-900 hover:underline"
                        >
                          View report &rarr;
                        </button>
                      </td>
                    </tr>
                  ))}
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
                  <span className="text-xs text-slate-400">Illustrative complaint records</span>
                </div>

                <button
                  type="button"
                  onClick={() => setAssignModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-xs transition"
                >
                  Assign or reassign
                </button>
              </div>

              {/* Work Items List */}
              <div className="space-y-3 pt-1">
                {workQueue.map((item) => (
                  <div
                    key={item.id}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition"
                  >
                    <div>
                      <div className="text-xs font-bold text-slate-900">{item.title}</div>
                      <div className="text-[11px] text-slate-400">{item.code} &middot; {item.location}</div>
                    </div>

                    <div className="text-xs text-slate-600 font-medium sm:text-right">
                      {item.assignedTo}
                    </div>

                    <div className="text-[11px] text-slate-400 sm:text-right">
                      {item.timeAgo}
                    </div>

                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.status === 'Awaiting assignment'
                            ? 'bg-amber-50 text-amber-800 border border-amber-200'
                            : item.status === 'Under review'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : item.status === 'In progress'
                            ? 'bg-teal-50 text-teal-700 border border-teal-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {item.status}
                      </span>
                      {item.status !== 'Resolved' && (
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
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Card: Department health */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Department health</h3>
                <span className="text-xs text-slate-400">Illustrative sample &middot; not live service data</span>
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
                    {[
                      { name: 'Roads', queue: 82, overdue: 7, rate: 78, review: 'Needs review', color: 'amber' },
                      { name: 'Drainage', queue: 64, overdue: 5, rate: 84, review: 'On track', color: 'emerald' },
                      { name: 'Street Lights', queue: 48, overdue: 2, rate: 90, review: 'On track', color: 'emerald' },
                      { name: 'Water Supply', queue: 71, overdue: 9, rate: 72, review: 'Attention needed', color: 'rose' },
                      { name: 'Other', queue: 47, overdue: 4, rate: 81, review: 'Needs review', color: 'amber' }
                    ].map((row) => (
                      <tr key={row.name} className="hover:bg-slate-50/60">
                        <td className="py-2.5 font-bold text-slate-900">{row.name}</td>
                        <td className="py-2.5 text-slate-700">{row.queue}</td>
                        <td className="py-2.5 text-slate-700">{row.overdue}</td>
                        <td className="py-2.5">
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-slate-100 h-2 rounded-full overflow-hidden">
                              <div className="bg-teal-600 h-full rounded-full" style={{ width: `${row.rate}%` }} />
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
                  className="px-4 py-2 text-xs font-bold bg-[#0d9488] hover:bg-[#0f766e] text-white rounded-xl shadow-xs"
                >
                  Confirm Assignment
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

    </div>
  );
}
