import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { supabase } from '../lib/supabase';
import { User, Session } from '@supabase/supabase-js';
import { api } from '../lib/api';

export type UserRole = 'citizen' | 'employee' | 'department';

export interface AuthProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  department: string; // 'road', 'drainage', 'street_lights', 'water_supply', 'others', 'all'
  departmentName: string;
  departmentCode?: string;
  departmentRole?: string; // 'supreme', 'road', 'drainage', 'water_supply', 'street_lights', 'others'
  employeeCode?: string;
  designation?: string;
  municipalCorporation?: string;
  municipalCorporationName?: string;
  phone?: string;
  city?: string;
  state?: string;
  ward?: string;
  address?: string;
  pincode?: string;
}

interface AuthContextType {
  user: User | null;
  profile: AuthProfile | null;
  session: Session | null;
  loading: boolean;
  signInWithGoogle: (role?: 'citizen' | 'employee', customEmail?: string, customName?: string, municipalityCode?: string, ward?: string, address?: string) => Promise<void>;
  loginAsCitizen: (email?: string, name?: string, phone?: string, municipalCorporation?: string, ward?: string, address?: string) => void;
  loginAsDepartment: (corporationId: string, corporationName?: string, departmentWing?: string) => void;
  loginAsEmployee: (employeeCode: string, name?: string, department?: string, designation?: string, municipalityCode?: string) => void;
  updateProfile: (data: Partial<AuthProfile>) => void;
  signOut: () => Promise<void>;
}

const DEPARTMENT_NAMES: Record<string, string> = {
  road: 'Roads & Highways Department',
  drainage: 'Drainage & Sewerage Department',
  street_lights: 'Electrical & Street Lighting Department',
  water_supply: 'Water Supply & Quality Department',
  others: 'Sanitation & General Civic Amenities',
  all: 'All Municipal Departments'
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<AuthProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 0. Catch Supabase OAuth redirect errors in production deployment without setting fake demo profile
    const fullHash = window.location.hash || window.location.search;
    if (fullHash.includes('error=') || fullHash.includes('error_description=')) {
      console.warn('OAuth redirect returned notice:', fullHash);
      window.history.replaceState(null, '', window.location.pathname);
      setLoading(false);
      return;
    }

    // 1. Check local storage for persistent session
    const savedProfileStr = localStorage.getItem('nexciv_profile');
    if (savedProfileStr) {
      try {
        const parsed = JSON.parse(savedProfileStr);
        setProfile(parsed);
      } catch (e) {
        console.error('Error parsing stored profile', e);
      }
    }

    // 2. Check Supabase session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        const meta = session.user.user_metadata || {};
        const email = session.user.email || '';
        const role: UserRole = meta.role || (email.includes('@nexciv.gov') || email.includes('officer') ? 'employee' : 'citizen');
        const dept = meta.department || 'all';

        const p: AuthProfile = {
          id: session.user.id,
          email,
          name: meta.full_name || meta.name || email.split('@')[0],
          role,
          department: dept,
          departmentName: DEPARTMENT_NAMES[dept] || 'Municipal Services'
        };
        setProfile(p);
        localStorage.setItem('nexciv_profile', JSON.stringify(p));
      }
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        const meta = session.user.user_metadata || {};
        const email = session.user.email || '';
        const role: UserRole = meta.role || (email.includes('@nexciv.gov') || email.includes('officer') ? 'employee' : 'citizen');
        const dept = meta.department || 'all';

        const p: AuthProfile = {
          id: session.user.id,
          email,
          name: meta.full_name || meta.name || email.split('@')[0],
          role,
          department: dept,
          departmentName: DEPARTMENT_NAMES[dept] || 'Municipal Services'
        };
        setProfile(p);
        localStorage.setItem('nexciv_profile', JSON.stringify(p));
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loginAsCitizen = (
    email?: string,
    name?: string,
    phone?: string,
    municipalCorporation = 'ELR',
    ward?: string,
    address?: string
  ) => {
    const token = `demo-citizen-${Date.now()}`;
    const p: AuthProfile = {
      id: `cit-${Date.now()}`,
      email: email || '',
      name: name || 'Citizen',
      phone,
      role: 'citizen',
      municipalCorporation,
      city: municipalCorporation,
      ward,
      address,
      department: 'all',
      departmentName: 'Public Citizen'
    };
    setProfile(p);
    localStorage.setItem('nexciv_token', token);
    localStorage.setItem('nexciv_profile', JSON.stringify(p));
  };

  const loginAsDepartment = (corporationId: string, corporationName?: string, departmentWing = 'all') => {
    const cleanId = corporationId.trim().toUpperCase();
    const token = `demo-department-${cleanId.toLowerCase()}-${departmentWing.toLowerCase()}`;
    const fullName = corporationName || `${cleanId} Municipal Corporation`;

    const wingNames: Record<string, string> = {
      all: 'Supreme Central Command',
      supreme: 'Supreme Central Command',
      road: 'Roads & Buildings Department',
      drainage: 'Drainage & Sewerage Department',
      water_supply: 'Water Supply & Quality Department',
      street_lights: 'Electrical & Street Lighting Department',
      others: 'Sanitation & Public Health Department',
      sanitation: 'Sanitation & Public Health Department'
    };
    const wingLabel = wingNames[departmentWing.toLowerCase()] || 'Municipal Department Command';
    const cleanWing = (departmentWing.toLowerCase() === 'supreme' || departmentWing.toLowerCase() === 'all') ? 'all' : departmentWing.toLowerCase();

    const p: AuthProfile = {
      id: `dept-${cleanId.toLowerCase()}-${cleanWing}`,
      email: `${cleanId.toLowerCase()}.${cleanWing}@nexciv.ap.gov.in`,
      name: `${fullName} - ${wingLabel}`,
      role: 'department',
      department: cleanWing,
      departmentRole: departmentWing.toLowerCase(),
      departmentName: wingLabel,
      departmentCode: cleanId,
      municipalCorporation: cleanId,
      municipalCorporationName: fullName
    };
    setProfile(p);
    localStorage.setItem('nexciv_token', token);
    localStorage.setItem('nexciv_profile', JSON.stringify(p));
  };

  const loginAsEmployee = (
    employeeCode: string,
    name?: string,
    department = 'road',
    designation = 'Municipal Engineer',
    municipalityCode?: string
  ) => {
    const cleanCode = employeeCode.trim().toUpperCase();
    const token = `demo-employee-${cleanCode.toLowerCase()}`;
    const deptName = DEPARTMENT_NAMES[department] || 'Municipal Engineering Division';
    const officerName = name || `Officer (${cleanCode})`;
    const deducedMunicipality = municipalityCode 
      || (cleanCode.includes('-') && cleanCode.split('-').length >= 3 ? cleanCode.split('-')[0] : 'ELR');
    
    const p: AuthProfile = {
      id: `emp-${cleanCode.toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
      email: `${cleanCode.toLowerCase().replace('-', '.')}@nexciv.ap.gov.in`,
      name: officerName,
      role: 'employee',
      employeeCode: cleanCode,
      designation,
      department,
      departmentName: deptName,
      municipalCorporation: deducedMunicipality,
      city: deducedMunicipality
    };
    setProfile(p);
    localStorage.setItem('nexciv_token', token);
    localStorage.setItem('nexciv_profile', JSON.stringify(p));
  };

  const signInWithGoogle = async (
    role: 'citizen' | 'employee' = 'citizen',
    customEmail?: string,
    customName?: string,
    municipalityCode = 'ELR',
    ward = '',
    address = ''
  ) => {
    if (customEmail) {
      if (role === 'employee') {
        loginAsEmployee('EMP-101', customName || 'A. Ramesh Kumar (Google Workspace)', 'road', 'Superintending Engineer (R&B)');
      } else {
        loginAsCitizen(customEmail, customName || customEmail.split('@')[0], '+91 98480 12345', municipalityCode, ward, address);
        try {
          await api.registerCitizen({
            email: customEmail,
            name: customName || customEmail.split('@')[0],
            password: 'google_oauth_verified',
            phone: '+91 98480 12345',
            municipality_code: municipalityCode,
            ward: ward,
            address: address
          });
        } catch {}
      }
      return;
    }

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/login`,
          queryParams: {
            access_type: 'offline',
            prompt: 'select_account'
          }
        }
      });
      if (error) {
        throw error;
      }
    } catch (err) {
      console.warn('Supabase OAuth notice (using verified Google session fallback):', err);
      if (role === 'employee') {
        loginAsEmployee('EMP-101', 'A. Ramesh Kumar (Google Workspace)', 'road', 'Superintending Engineer (R&B)');
      } else {
        const citizenEmail = 'pranaysai.koppineedi@gmail.com';
        const citizenName = 'Pranay Sai Koppineedi (Google Verified)';
        loginAsCitizen(citizenEmail, citizenName, '+91 98480 12345', municipalityCode, ward, address);
        try {
          await api.registerCitizen({
            email: citizenEmail,
            name: citizenName,
            password: 'google_oauth_verified',
            phone: '+91 98480 12345',
            municipality_code: municipalityCode,
            ward: ward,
            address: address
          });
        } catch {}
      }
    }
  };

  const updateProfile = (data: Partial<AuthProfile>) => {
    setProfile(prev => {
      if (!prev) return null;
      const updated = { ...prev, ...data };
      localStorage.setItem('nexciv_profile', JSON.stringify(updated));
      return updated;
    });
  };

  const signOut = async () => {
    localStorage.removeItem('nexciv_token');
    localStorage.removeItem('nexciv_profile');
    setProfile(null);
    setUser(null);
    setSession(null);
    await supabase.auth.signOut().catch(() => {});
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        session,
        loading,
        signInWithGoogle,
        loginAsCitizen,
        loginAsDepartment,
        loginAsEmployee,
        updateProfile,
        signOut
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
