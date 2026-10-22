import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface APCorporation {
  code: string;
  name: string;
  short_name: string;
  district: string;
  headquarters: string;
  contact_email: string;
  contact_phone: string;
  wards_count: number;
  population: string;
}

export interface ComplaintRecord {
  id: string;
  user_id?: string;
  title: string;
  description: string;
  category: string;
  status: 'pending' | 'in_progress' | 'resolved';
  department?: string;
  department_code?: string;
  municipal_corporation?: string;
  ward?: string;
  landmark?: string;
  confidence?: number;
  priority?: 'Critical' | 'High' | 'Medium' | 'Low';
  priority_score?: number;
  location_lat?: number;
  location_lng?: number;
  location_address?: string;
  image_url?: string;
  image_data?: string;
  images?: string[];
  zone_type?: string;
  vulnerability_multiplier?: number;
  municipal_sla?: string;
  assigned_team?: string;
  assigned_employee_id?: string;
  citizen_name?: string;
  citizen_email?: string;
  citizen_phone?: string;
  is_duplicate?: boolean;
  master_complaint_id?: string;
  duplicate_count?: number;
  upvote_count?: number;
  image_hash?: string;
  defect_type?: string;
  visual_score?: number;
  cluster_id?: string;
  resolution_notes?: string;
  resolution_proof_url?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeRecord {
  id: string;
  employee_code: string;
  name: string;
  initials: string;
  email: string;
  phone?: string;
  department: string;
  department_name: string;
  designation: string;
  zone: string;
  status: string;
  assigned_count: number;
  completed_count: number;
  pending_count: number;
  overdue_count: number;
  avg_resolution_days: number;
  completion_rate: number;
  rating: number;
  performance: 'On track' | 'Needs review' | 'Attention needed';
  skills?: string;
}

export interface HotspotCluster {
  cluster_id: string;
  department: string;
  count: number;
  latitude: number;
  longitude: number;
  location: string;
  radius_meters: number;
  sample_titles: string[];
}

export const AP_CORPORATIONS: APCorporation[] = [
  { code: 'GVMC', name: 'Greater Visakhapatnam Municipal Corporation', short_name: 'Visakhapatnam', district: 'Visakhapatnam', headquarters: 'Asilmetta, Visakhapatnam', contact_email: 'commissioner_gvmc@yahoo.co.in', contact_phone: '0891-2746300', wards_count: 98, population: '23.5 Lakhs' },
  { code: 'VMC', name: 'Vijayawada Municipal Corporation', short_name: 'Vijayawada', district: 'NTR', headquarters: 'Canal Road, Vijayawada', contact_email: 'ourvmc@yahoo.com', contact_phone: '0866-2422400', wards_count: 64, population: '14.8 Lakhs' },
  { code: 'GMC', name: 'Guntur Municipal Corporation', short_name: 'Guntur', district: 'Guntur', headquarters: 'Opp. Collectorate, Guntur', contact_email: 'commissionerguntur@gmail.com', contact_phone: '0863-2224202', wards_count: 57, population: '10.2 Lakhs' },
  { code: 'TMC', name: 'Tirupati Municipal Corporation', short_name: 'Tirupati', district: 'Tirupati', headquarters: 'Tilak Road, Tirupati', contact_email: 'commr_tirupati@yahoo.com', contact_phone: '0877-2256789', wards_count: 50, population: '6.8 Lakhs' },
  { code: 'KMC', name: 'Kurnool Municipal Corporation', short_name: 'Kurnool', district: 'Kurnool', headquarters: 'Near Raj Vihar, Kurnool', contact_email: 'commr_kurnool@yahoo.com', contact_phone: '08518-220033', wards_count: 52, population: '7.5 Lakhs' },
  { code: 'RMC', name: 'Rajamahendravaram Municipal Corporation', short_name: 'Rajahmundry', district: 'East Godavari', headquarters: 'Subba Rao Peta, Rajamahendravaram', contact_email: 'commr_rmc@yahoo.co.in', contact_phone: '0883-2471676', wards_count: 50, population: '5.6 Lakhs' },
  { code: 'NMC', name: 'Nellore Municipal Corporation', short_name: 'Nellore', district: 'SPSR Nellore', headquarters: 'Pogathota, Nellore', contact_email: 'commissionernellore@gmail.com', contact_phone: '0861-2326555', wards_count: 54, population: '6.5 Lakhs' },
  { code: 'KADA', name: 'Kadapa Municipal Corporation', short_name: 'Kadapa', district: 'YSR Kadapa', headquarters: 'Main Road, Kadapa', contact_email: 'commr_kadapa@yahoo.co.in', contact_phone: '08562-241515', wards_count: 50, population: '4.8 Lakhs' },
  { code: 'KKD', name: 'Kakinada Municipal Corporation', short_name: 'Kakinada', district: 'Kakinada', headquarters: 'Cinema Road, Kakinada', contact_email: 'commr_kkd@yahoo.com', contact_phone: '0884-2376677', wards_count: 50, population: '5.2 Lakhs' },
  { code: 'ELR', name: 'Eluru Municipal Corporation', short_name: 'Eluru', district: 'Eluru', headquarters: 'Near Fire Station, Eluru', contact_email: 'commr_elr@yahoo.co.in', contact_phone: '08812-230303', wards_count: 50, population: '4.1 Lakhs' },
  { code: 'ATP', name: 'Anantapur Municipal Corporation', short_name: 'Anantapur', district: 'Anantapur', headquarters: 'Subhash Road, Anantapur', contact_email: 'commr_atp@yahoo.com', contact_phone: '08554-220025', wards_count: 50, population: '4.5 Lakhs' },
  { code: 'VZM', name: 'Vizianagaram Municipal Corporation', short_name: 'Vizianagaram', district: 'Vizianagaram', headquarters: 'Cantonment, Vizianagaram', contact_email: 'commr_vzm@yahoo.co.in', contact_phone: '08922-224422', wards_count: 50, population: '3.8 Lakhs' },
  { code: 'ONG', name: 'Ongole Municipal Corporation', short_name: 'Ongole', district: 'Prakasam', headquarters: 'Trunk Road, Ongole', contact_email: 'commr_ongole@yahoo.co.in', contact_phone: '08592-233444', wards_count: 50, population: '3.2 Lakhs' },
  { code: 'NDL', name: 'Nandyal Municipal Corporation', short_name: 'Nandyal', district: 'Nandyal', headquarters: 'Sanjeeva Nagar, Nandyal', contact_email: 'commr_ndl@yahoo.co.in', contact_phone: '08514-242200', wards_count: 42, population: '2.9 Lakhs' },
  { code: 'MCT', name: 'Machilipatnam Municipal Corporation', short_name: 'Machilipatnam', district: 'Krishna', headquarters: 'Fort Road, Machilipatnam', contact_email: 'commr_mct@yahoo.co.in', contact_phone: '08672-222333', wards_count: 50, population: '2.8 Lakhs' },
  { code: 'CTR', name: 'Chittoor Municipal Corporation', short_name: 'Chittoor', district: 'Chittoor', headquarters: 'Church Street, Chittoor', contact_email: 'commr_chittoor@yahoo.co.in', contact_phone: '08572-232444', wards_count: 50, population: '2.6 Lakhs' },
  { code: 'SKLM', name: 'Srikakulam Municipal Corporation', short_name: 'Srikakulam', district: 'Srikakulam', headquarters: 'Seven Road Junction, Srikakulam', contact_email: 'commr_sklm@yahoo.co.in', contact_phone: '08942-222555', wards_count: 50, population: '2.5 Lakhs' }
];

async function getAuthHeaders() {
  const localToken = localStorage.getItem('nexciv_token');
  if (localToken) {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localToken}`
    };
  }

  const { data: { session } } = await supabase.auth.getSession();
  return {
    'Content-Type': 'application/json',
    ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {})
  };
}

export const api = {
  async getCorporations(): Promise<APCorporation[]> {
    try {
      const res = await fetch(`${API_URL}/api/auth/corporations`);
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback to local list
    }
    return AP_CORPORATIONS;
  },

  async loginDepartment(corporationId: string, departmentWing = 'all', password = 'admin@123') {
    const res = await fetch(`${API_URL}/api/auth/department-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ corporation_id: corporationId, department_wing: departmentWing, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Department authentication failed');
    }
    return res.json();
  },

  async loginEmployee(employeeCode: string, password = 'emp@123') {
    const res = await fetch(`${API_URL}/api/auth/employee-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employee_code: employeeCode, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Employee authentication failed');
    }
    return res.json();
  },

  async classifyComplaint(
    text: string,
    imageData?: string,
    locationAddress?: string,
    locationLat?: number,
    locationLng?: number
  ) {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/classify`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        text,
        image_data: imageData,
        location_address: locationAddress,
        location_lat: locationLat,
        location_lng: locationLng
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Classification failed');
    }
    return res.json();
  },

  async createComplaint(data: {
    title: string;
    description: string;
    category?: string;
    department?: string;
    department_code?: string;
    municipal_corporation?: string;
    ward?: string;
    landmark?: string;
    priority?: string;
    priority_score?: number;
    location_address?: string;
    location_lat?: number;
    location_lng?: number;
    image_url?: string;
    image_data?: string;
    images?: string[];
    citizen_name?: string;
    citizen_email?: string;
    citizen_phone?: string;
  }): Promise<ComplaintRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create complaint');
    }
    return res.json();
  },

  async getComplaints(filters?: {
    category?: string;
    priority?: string;
    status?: string;
    department?: string;
    municipal_corporation?: string;
    assigned_employee_id?: string;
    citizen_email?: string;
    search?: string;
  }): Promise<ComplaintRecord[]> {
    const headers = await getAuthHeaders();
    const params = new URLSearchParams();
    if (filters?.category && filters.category !== 'All') {
      params.append('category', filters.category.toLowerCase().replace(' ', '_'));
    }
    if (filters?.department && filters.department !== 'All' && filters.department !== 'All departments') {
      params.append('department', filters.department.toLowerCase().replace(' ', '_'));
    }
    if (filters?.priority && filters.priority !== 'All') {
      params.append('priority', filters.priority);
    }
    if (filters?.status && filters.status !== 'All' && filters.status !== 'All statuses') {
      params.append('status', filters.status.toLowerCase());
    }
    if (filters?.municipal_corporation && filters.municipal_corporation !== 'All') {
      params.append('municipal_corporation', filters.municipal_corporation.toUpperCase());
    }
    if (filters?.assigned_employee_id && filters.assigned_employee_id !== 'All') {
      params.append('assigned_employee_id', filters.assigned_employee_id);
    }
    if (filters?.citizen_email && filters.citizen_email !== 'All') {
      params.append('citizen_email', filters.citizen_email);
    }
    if (filters?.search && filters.search.trim()) {
      params.append('search', filters.search.trim());
    }

    const queryString = params.toString();
    const url = `${API_URL}/api/complaints${queryString ? `?${queryString}` : ''}`;
    const res = await fetch(url, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch complaints');
    }
    return res.json();
  },

  async getComplaint(id: string): Promise<ComplaintRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/${id}`, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch complaint');
    }
    return res.json();
  },

  async upvoteComplaint(id: string): Promise<{ id: string; upvote_count: number }> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/${id}/upvote`, {
      method: 'POST',
      headers
    });
    if (!res.ok) {
      return { id, upvote_count: 2 };
    }
    return res.json();
  },

  async updateComplaintStatus(
    id: string,
    status: string,
    notes?: string,
    resolutionProofUrl?: string,
    resolvedByEmployeeId?: string
  ): Promise<ComplaintRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/${id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({
        status,
        notes,
        resolution_proof_url: resolutionProofUrl,
        resolved_by_employee_id: resolvedByEmployeeId
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update complaint status');
    }
    return res.json();
  },

  async assignComplaint(complaintId: string, employeeId: string, assignedTeam?: string): Promise<ComplaintRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/${complaintId}/assign`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({
        employee_id: employeeId,
        assigned_team: assignedTeam
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to assign complaint');
    }
    return res.json();
  },

  async getAnalytics(municipalCorporation?: string) {
    const headers = await getAuthHeaders();
    const url = municipalCorporation && municipalCorporation !== 'All'
      ? `${API_URL}/api/complaints/analytics?municipal_corporation=${municipalCorporation}`
      : `${API_URL}/api/complaints/analytics`;
    const res = await fetch(url, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch analytics');
    }
    return res.json();
  },

  async getEmployees(filters?: { department?: string; status?: string; search?: string }): Promise<EmployeeRecord[]> {
    const headers = await getAuthHeaders();
    const params = new URLSearchParams();
    if (filters?.department && filters.department !== 'All' && filters.department !== 'All departments') {
      params.append('department', filters.department.toLowerCase().replace(' ', '_'));
    }
    if (filters?.status && filters.status !== 'All' && filters.status !== 'All statuses') {
      params.append('status', filters.status.toLowerCase());
    }
    if (filters?.search && filters.search.trim()) {
      params.append('search', filters.search.trim());
    }
    const queryString = params.toString();
    const url = `${API_URL}/api/employees${queryString ? `?${queryString}` : ''}`;
    const res = await fetch(url, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch employees');
    }
    return res.json();
  },

  async getEmployee(idOrCode: string): Promise<EmployeeRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/employees/${idOrCode}`, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch employee');
    }
    return res.json();
  },

  async createEmployee(data: {
    employee_code: string;
    name: string;
    email: string;
    department: string;
    department_name?: string;
    designation: string;
    zone: string;
    phone?: string;
    skills?: string;
  }): Promise<EmployeeRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/employees`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to register employee');
    }
    return res.json();
  },

  async checkDuplicate(data: {
    title?: string;
    description: string;
    category?: string;
    location_lat?: number;
    location_lng?: number;
    location_address?: string;
    image_data?: string;
  }) {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/check-duplicate`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      return { is_duplicate: false };
    }
    return res.json();
  },

  async verifyImage(imageData: string) {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/verify-image`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ image_data: imageData })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Image verification failed');
    }
    return res.json();
  },

  async getHotspots(radiusMeters = 100) {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_URL}/api/complaints/hotspots?radius_meters=${radiusMeters}`, { headers });
    if (!res.ok) {
      return { total_hotspots: 0, hotspots: [] };
    }
    return res.json();
  }
};
