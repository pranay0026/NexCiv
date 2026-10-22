import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import HeroSlider from '../components/HeroSlider';
import ComplaintForm from '../components/ComplaintForm';
import ComplaintList from '../components/ComplaintList';
import { api, ComplaintRecord } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Shield } from 'lucide-react';

const DEPT_CODE_TO_CATEGORY: Record<string, string> = {
  road: 'Road',
  drainage: 'Drainage',
  street_lights: 'Street Lights',
  water_supply: 'Water Supply',
  others: 'Others'
};

export default function Dashboard() {
  const { profile } = useAuth();
  const isEmployee = profile?.role === 'employee';

  const defaultCategory = (isEmployee && profile?.department && DEPT_CODE_TO_CATEGORY[profile.department])
    ? DEPT_CODE_TO_CATEGORY[profile.department]
    : 'All';

  const [selectedCategory, setSelectedCategory] = useState(defaultCategory);
  const [selectedPriority, setSelectedPriority] = useState('All');
  const [complaints, setComplaints] = useState<ComplaintRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const data = await api.getComplaints({
        category: selectedCategory,
        priority: selectedPriority
      });
      setComplaints(data);
    } catch (error) {
      console.error('Error fetching complaints:', error);
      setComplaints([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [selectedCategory, selectedPriority]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          selectedPriority={selectedPriority}
          onSelectPriority={setSelectedPriority}
        />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <div className="max-w-5xl mx-auto space-y-8">
            
            {/* Officer Banner if logged in as municipal employee */}
            {isEmployee ? (
              <div className="bg-gradient-to-r from-[#0b1a2d] via-[#0e2238] to-[#122b46] rounded-3xl p-6 text-white border border-slate-700/60 shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center text-teal-300 shrink-0 shadow-sm">
                    <Shield size={24} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-extrabold uppercase tracking-widest text-teal-400">
                        Municipal Officer Workspace
                      </span>
                    </div>
                    <h2 className="text-xl font-black mt-0.5 tracking-tight">{profile?.departmentName}</h2>
                    <p className="text-xs text-slate-300 mt-1">
                      Viewing grievances routed by the AI engine. Use the buttons on each card to dispatch teams and mark resolved.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <HeroSlider />
            )}

            {/* Citizen Complaint Registration Form */}
            <ComplaintForm onComplaintAdded={fetchComplaints} />

            {/* Complaint List with real-time status updates */}
            <ComplaintList
              complaints={complaints}
              loading={loading}
              onStatusUpdated={fetchComplaints}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
