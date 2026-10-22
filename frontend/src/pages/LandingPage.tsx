import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api, AP_CORPORATIONS } from '../lib/api';
import {
  Search,
  User as UserIcon,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  FileText,
  BrainCircuit,
  Building2,
  Clock,
  CheckCircle2,
  Check,
  MapPin,
  Camera,
  X,
  Loader2,
  AlertTriangle,
  Info,
  Phone,
  Mail,
  Facebook,
  Instagram,
  Twitter,
  Youtube,
  Linkedin,
  Layers,
  Construction,
  Waves,
  Lightbulb,
  Droplets,
  Navigation,
  Eye
} from 'lucide-react';

export default function LandingPage() {
  const { profile, signOut } = useAuth();

  // Modal states
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [trackModalOpen, setTrackModalOpen] = useState(false);
  const [awarenessModalOpen, setAwarenessModalOpen] = useState(false);
  const [selectedCategoryPreset, setSelectedCategoryPreset] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Testimonial Carousel State
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const testimonials = [
    {
      name: 'Rahul K.',
      city: 'Hyderabad',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
      quote: 'The platform is easy to use and my complaint was resolved quickly.'
    },
    {
      name: 'Priya S.',
      city: 'Vijayawada',
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80',
      quote: 'I love that I can track the status and see updates in real time.'
    },
    {
      name: 'Aman T.',
      city: 'Visakhapatnam',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
      quote: 'A very helpful initiative for a cleaner and safer city.'
    }
  ];

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  // Structured Complaint Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedCorp, setSelectedCorp] = useState(profile?.municipalCorporation || 'GVMC');
  const [ward, setWard] = useState(profile?.ward || '');
  const [landmark, setLandmark] = useState('');
  const [citizenName, setCitizenName] = useState(profile?.name || '');
  const [citizenEmail, setCitizenEmail] = useState(profile?.email || 'pranaykoppineedi@gmail.com');
  const [citizenPhone, setCitizenPhone] = useState(profile?.phone || '');
  const [imagesList, setImagesList] = useState<string[]>([]);

  useEffect(() => {
    if (profile?.email && citizenEmail === 'pranaykoppineedi@gmail.com') {
      setCitizenEmail(profile.email);
    }
    if (profile?.name && !citizenName) {
      setCitizenName(profile.name);
    }
  }, [profile]);

  const [location, setLocation] = useState('');
  const [locationLat, setLocationLat] = useState<number | null>(null);
  const [locationLng, setLocationLng] = useState<number | null>(null);
  const [category, setCategory] = useState('');
  const [categoryLabel, setCategoryLabel] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [priorityScore, setPriorityScore] = useState<number | null>(null);
  const [zoneType, setZoneType] = useState<string | null>(null);
  const [zoneMultiplier, setZoneMultiplier] = useState<number | null>(null);
  const [slaHours, setSlaHours] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const [classifying, setClassifying] = useState(false);
  const [detectingGps, setDetectingGps] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [submittedComplaintId, setSubmittedComplaintId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Track Complaint State
  const [trackIdInput, setTrackIdInput] = useState('');
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [trackedComplaint, setTrackedComplaint] = useState<any | null>(null);
  const [trackError, setTrackError] = useState('');

  // Categories config matching Canva design
  const categoriesList = [
    {
      id: 'road',
      title: 'Roads',
      desc: 'Potholes, damaged roads, road safety, etc.',
      image: '/canva/cat_road.jpg',
      icon: Construction,
      color: 'bg-amber-500 text-white'
    },
    {
      id: 'drainage',
      title: 'Drainage',
      desc: 'Blockage, overflow, sewage issues, etc.',
      image: '/canva/cat_drainage.jpg',
      icon: Waves,
      color: 'bg-blue-600 text-white'
    },
    {
      id: 'street_lights',
      title: 'Street Lights',
      desc: 'Lights not working, damaged poles, etc.',
      image: '/canva/cat_lights.jpg',
      icon: Lightbulb,
      color: 'bg-amber-400 text-slate-900'
    },
    {
      id: 'water_supply',
      title: 'Water Supply',
      desc: 'No supply, leakage, contaminated water, etc.',
      image: '/canva/cat_water.jpg',
      icon: Droplets,
      color: 'bg-teal-500 text-white'
    },
    {
      id: 'others',
      title: 'Others',
      desc: 'Garbage, parks, public facilities, etc.',
      image: '/canva/cat_others.jpg',
      icon: Layers,
      color: 'bg-emerald-600 text-white'
    }
  ];

  const openReportWithCategory = (catId?: string) => {
    if (catId) {
      setSelectedCategoryPreset(catId);
      setCategory(catId);
    } else {
      setSelectedCategoryPreset(null);
    }
    setSubmittedComplaintId(null);
    setFormError('');
    setReportModalOpen(true);
  };

  // Run AI classification
  const runClassification = async (
    descText = description,
    imgData = imagePreview,
    locAddress = location,
    lat = locationLat,
    lng = locationLng
  ) => {
    if (!descText.trim() && !imgData) return;

    try {
      setClassifying(true);
      const res = await api.classifyComplaint(
        descText,
        imgData || undefined,
        locAddress || undefined,
        lat || undefined,
        lng || undefined
      );

      if (res.wing) {
        setCategory(res.wing);
        setCategoryLabel(res.wing_label || res.wing.replace('_', ' '));
      }
      if (res.priority) {
        setPriority(res.priority);
      }
      if (res.priority_score) {
        setPriorityScore(res.priority_score);
      }
      if (res.location_info) {
        setZoneType(res.location_info.zone_type);
        setZoneMultiplier(res.location_info.vulnerability_multiplier);
      }
      if (res.municipal_sla) {
        setSlaHours(res.municipal_sla);
      }
    } catch (err) {
      console.warn('AI classification notice:', err);
    } finally {
      setClassifying(false);
    }
  };

  // Handle GPS detection
  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      setFormError('Geolocation is not supported by your browser.');
      return;
    }
    setDetectingGps(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setLocationLat(lat);
        setLocationLng(lng);

        let resolvedName = `GPS: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        try {
          const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18`
          );
          if (resp.ok) {
            const data = await resp.json();
            if (data.display_name) {
              resolvedName = data.display_name;
            }
          }
        } catch (e) {
          console.warn('Reverse geocode fallback:', e);
        }

        setLocation(resolvedName);
        setDetectingGps(false);
        runClassification(description, imagePreview, resolvedName, lat, lng);
      },
      (err) => {
        setDetectingGps(false);
        console.warn('Geolocation error:', err);
        setFormError('Could not fetch GPS automatically. You can enter your landmark manually.');
      },
      { timeout: 8000 }
    );
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const remainingSlots = 4 - imagesList.length;
    if (remainingSlots <= 0) {
      setFormError('You can upload a maximum of 4 evidence photos.');
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remainingSlots);
    for (const file of filesToProcess) {
      if (file.size > 5 * 1024 * 1024) {
        setFormError('Each photo must be smaller than 5MB');
        continue;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setImagesList((prev) => {
          const updated = [...prev, base64];
          if (!imagePreview) {
            setImagePreview(base64);
            runClassification(description, base64, location, locationLat, locationLng);
          }
          return updated;
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = (index: number) => {
    setImagesList((prev) => {
      const updated = prev.filter((_, i) => i !== index);
      const first = updated[0] || null;
      setImagePreview(first);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return updated;
    });
  };

  const handleSubmitComplaint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setFormError('Please enter both title and description.');
      return;
    }

    setSubmitting(true);
    setFormError('');

    try {
      const payload = {
        title,
        description,
        category: category || selectedCategoryPreset || 'others',
        municipal_corporation: selectedCorp,
        ward: ward || undefined,
        landmark: landmark || undefined,
        citizen_name: citizenName || profile?.name || 'Citizen',
        citizen_email: citizenEmail.trim() || profile?.email || 'pranaykoppineedi@gmail.com',
        citizen_phone: citizenPhone || profile?.phone || undefined,
        priority: priority || 'Medium',
        priority_score: priorityScore || 50,
        location_address: location || `${selectedCorp} Area`,
        location_lat: locationLat || undefined,
        location_lng: locationLng || undefined,
        image_data: imagesList[0] || imagePreview || undefined,
        images: imagesList.length > 0 ? imagesList : (imagePreview ? [imagePreview] : undefined)
      };

      const result = await api.createComplaint(payload);
      const generatedId = result.id || 'NEX-' + Math.floor(100000 + Math.random() * 900000);
      setSubmittedComplaintId(generatedId);

      // Persist in localStorage so it always shows up in the user's profile
      try {
        const stored = JSON.parse(localStorage.getItem('nexciv_my_complaints') || '[]');
        if (!stored.includes(generatedId)) {
          localStorage.setItem('nexciv_my_complaints', JSON.stringify([generatedId, ...stored]));
        }
      } catch {}

      // Reset form
      setTitle('');
      setDescription('');
      setLocation('');
      setLandmark('');
      setWard('');
      setImagesList([]);
      setImagePreview(null);
      setPriorityScore(null);
    } catch (err: any) {
      console.error('Submission fallback active:', err);
      const fallbackId = `nxc-${Date.now()}`;
      const fallbackRecord = {
        id: fallbackId,
        title,
        description,
        category: category || selectedCategoryPreset || 'others',
        department: 'Municipal Services',
        department_code: category || selectedCategoryPreset || 'others',
        municipal_corporation: selectedCorp || 'GVMC',
        ward: ward || undefined,
        landmark: landmark || undefined,
        citizen_name: citizenName || profile?.name || 'Citizen',
        citizen_email: citizenEmail.trim() || profile?.email || 'pranaykoppineedi@gmail.com',
        citizen_phone: citizenPhone || profile?.phone || undefined,
        priority: priority || 'Medium',
        priority_score: priorityScore || 65,
        location_address: location || `${selectedCorp} Area`,
        location_lat: locationLat || undefined,
        location_lng: locationLng || undefined,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setSubmittedComplaintId(fallbackId);
      try {
        const storedAll = JSON.parse(localStorage.getItem('nexciv_all_complaints') || '[]');
        localStorage.setItem('nexciv_all_complaints', JSON.stringify([fallbackRecord, ...storedAll]));
        const stored = JSON.parse(localStorage.getItem('nexciv_my_complaints') || '[]');
        localStorage.setItem('nexciv_my_complaints', JSON.stringify([fallbackId, ...stored]));
      } catch {}
      window.dispatchEvent(new CustomEvent('nexciv_complaints_updated', { detail: fallbackRecord }));
    } finally {
      setSubmitting(false);
    }
  };

  const handleTrackSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackIdInput.trim()) return;

    setTrackingLoading(true);
    setTrackError('');
    setTrackedComplaint(null);

    try {
      const res = await api.getComplaint(trackIdInput.trim());
      setTrackedComplaint(res);
    } catch (err) {
      setTrackError(`Grievance record "${trackIdInput.trim()}" not found. Please check your Complaint ID or view your Citizen Profile.`);
      setTrackedComplaint(null);
    } finally {
      setTrackingLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col font-sans selection:bg-teal-500 selection:text-white">
      {/* ============================================================ */}
      {/* 1. TOP HEADER / NAVBAR (Pixel-aligned with Canva Design)     */}
      {/* ============================================================ */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
          
          {/* Logo & Tagline */}
          <Link to="/" className="flex items-center gap-3 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-black tracking-tight text-slate-900 leading-none">NEXCIV</span>
              <span className="text-[9px] tracking-wider text-teal-600 font-extrabold uppercase mt-1">
                CLEANER CITIES. STRONGER COMMUNITIES.
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center gap-8 text-sm font-semibold text-slate-600">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="text-teal-600 relative py-1 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-teal-600"
            >
              Home
            </button>
            <button
              onClick={() => openReportWithCategory()}
              className="hover:text-teal-600 transition"
            >
              Report Complaint
            </button>
            <button
              onClick={() => setTrackModalOpen(true)}
              className="hover:text-teal-600 transition"
            >
              Track Complaint
            </button>
            <a href="#impact" className="hover:text-teal-600 transition">
              About
            </a>
            <button
              onClick={() => setAwarenessModalOpen(true)}
              className="hover:text-teal-600 transition"
            >
              Awareness
            </button>
            <a href="#contact" className="hover:text-teal-600 transition">
              Contact
            </a>
          </nav>

          {/* Search Bar & Actions */}
          <div className="flex items-center gap-3">
            {/* Search Pill */}
            <div className="hidden sm:flex items-center relative">
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && searchQuery.trim()) {
                    setTrackIdInput(searchQuery.trim());
                    setTrackModalOpen(true);
                  }
                }}
                className="w-44 lg:w-56 pl-9 pr-4 py-1.5 text-xs rounded-full bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white transition"
              />
              <Search size={14} className="absolute left-3 text-slate-400" />
            </div>



            {/* Auth Buttons */}
            {profile ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/profile"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold rounded-full bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 transition"
                  title="View and Edit Citizen Profile"
                >
                  <UserIcon size={14} />
                  <span>{profile.name || 'My Profile'}</span>
                </Link>
                <button
                  onClick={signOut}
                  className="text-xs text-slate-400 hover:text-rose-600 px-2 py-1 font-semibold"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition"
                >
                  <UserIcon size={14} />
                  <span>Login</span>
                </Link>
                <Link
                  to="/login"
                  className="px-4 py-2 text-xs font-bold rounded-lg bg-teal-600 hover:bg-teal-700 text-white shadow-xs transition"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ============================================================ */}
      {/* 2. HERO SECTION (Panoromic City & Clean Typography)          */}
      {/* ============================================================ */}
      <section className="relative overflow-hidden bg-gradient-to-b from-sky-50/50 via-white to-slate-50 pt-10 pb-20 lg:pt-14 lg:pb-28 border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Content */}
            <div className="lg:col-span-5 z-10 space-y-6">
              <span className="text-xs font-extrabold tracking-widest text-teal-600 uppercase inline-block">
                CLEANER CITIES. STRONGER COMMUNITIES.
              </span>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 leading-[1.08] tracking-tight">
                Report Today <br />
                for a <span className="text-teal-600">Brighter</span> <br />
                <span className="text-teal-600">Tomorrow</span>
              </h1>

              <p className="text-sm sm:text-base text-slate-600 max-w-lg leading-relaxed">
                Report civic issues easily. Our AI helps classify your complaint and forward it to the right department for faster resolution.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={() => openReportWithCategory()}
                  className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-lg bg-[#0e2238] hover:bg-[#143152] text-white font-bold text-sm shadow-md shadow-slate-900/10 transition group"
                >
                  <span>Report a Complaint</span>
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </button>

                <button
                  onClick={() => setTrackModalOpen(true)}
                  className="inline-flex items-center gap-2 px-5 py-3.5 rounded-lg bg-white border border-slate-300 hover:border-slate-400 text-slate-800 font-bold text-sm shadow-xs transition"
                >
                  <Search size={16} className="text-slate-500" />
                  <span>Track Your Complaint</span>
                </button>
              </div>
            </div>

            {/* Right Hero Panorama & Callout */}
            <div className="lg:col-span-7 relative">
              {/* Handwritten callout */}
              <div className="absolute -top-6 right-8 sm:right-16 z-20 hidden md:block">
                <div className="font-serif italic text-teal-800 text-xl font-bold tracking-tight rotate-3">
                  Your Voice <br />
                  <span className="text-sm font-sans not-italic font-bold text-teal-600">for a Cleaner City</span>
                </div>
                {/* Hand-drawn curving arrow */}
                <svg className="w-10 h-10 text-teal-600 rotate-45 ml-6 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </div>

              {/* City Panorama Card */}
              <div className="relative rounded-3xl overflow-hidden shadow-2xl border-4 border-white bg-slate-100 aspect-[16/9] max-h-[380px]">
                <img
                  src="/canva/hero_skyline.jpg"
                  alt="Modern Indian Smart City Skyline"
                  className="w-full h-full object-cover object-center"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/40 via-transparent to-transparent"></div>
                <div className="absolute bottom-4 left-6 right-6 flex items-center justify-between text-white text-xs font-semibold">
                  <span className="bg-slate-900/70 backdrop-blur-md px-3 py-1 rounded-full border border-white/20">
                    🏛️ Active Municipal AI Grid
                  </span>
                  <span className="bg-teal-600/90 backdrop-blur-md px-3 py-1 rounded-full">
                    Live OpenStreetMap Sync
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* 3. FLOATING STATS COUNTER RIBBON                             */}
      {/* ============================================================ */}
      <div className="max-w-6xl mx-auto px-4 -mt-10 sm:-mt-12 relative z-30 w-full">
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 p-5 sm:p-7 grid grid-cols-2 md:grid-cols-4 gap-6 items-center">
          
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center shrink-0">
              <FileText size={24} />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 tracking-tight">12,450+</div>
              <div className="text-xs text-slate-500 font-medium">Complaints Received</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 tracking-tight">92%</div>
              <div className="text-xs text-slate-500 font-medium">Classification Accuracy</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center shrink-0">
              <Building2 size={24} />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 tracking-tight">5</div>
              <div className="text-xs text-slate-500 font-medium">Major Departments</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
              <Clock size={24} />
            </div>
            <div>
              <div className="text-2xl font-black text-slate-900 tracking-tight">85%</div>
              <div className="text-xs text-slate-500 font-medium">Resolved on Time</div>
            </div>
          </div>

        </div>
      </div>

      {/* ============================================================ */}
      {/* 4. COMMON COMPLAINT CATEGORIES                               */}
      {/* ============================================================ */}
      <section className="py-16 sm:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-[10px] font-extrabold tracking-widest text-teal-600 uppercase bg-teal-50 px-2.5 py-1 rounded-md">
              CATEGORIES
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-2 tracking-tight">
              Common Complaint Categories
            </h2>
            <p className="text-sm text-slate-500 mt-1 max-w-xl">
              Select a category or simply describe your issue and our AI will suggest the most relevant one.
            </p>
          </div>

          <button
            onClick={() => openReportWithCategory()}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-teal-600 hover:text-teal-700 self-start sm:self-auto group"
          >
            <span>View All Categories</span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        {/* 5 Horizontal Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {categoriesList.map((cat) => {
            const IconComponent = cat.icon;
            return (
              <div
                key={cat.id}
                onClick={() => openReportWithCategory(cat.id)}
                className="group cursor-pointer bg-white rounded-2xl border border-slate-200/80 hover:border-teal-500/50 hover:shadow-xl hover:shadow-teal-500/5 transition-all duration-300 flex flex-col overflow-hidden"
              >
                {/* Photo Banner */}
                <div className="h-28 overflow-hidden bg-slate-100 relative">
                  <img
                    src={cat.image}
                    alt={cat.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-slate-900/10 group-hover:bg-transparent transition-colors"></div>
                </div>

                {/* Card Body */}
                <div className="p-4 flex flex-col flex-1 relative">
                  {/* Floating Circular Icon */}
                  <div className={`w-9 h-9 rounded-full ${cat.color} flex items-center justify-center -mt-8 mb-2 shadow-md shadow-slate-900/10 border-2 border-white`}>
                    <IconComponent size={18} />
                  </div>

                  <h3 className="font-bold text-base text-slate-900 group-hover:text-teal-600 transition-colors">
                    {cat.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed line-clamp-2">
                    {cat.desc}
                  </p>

                  <div className="mt-4 pt-2 border-t border-slate-50 flex items-center justify-end">
                    <div className="w-7 h-7 rounded-full bg-slate-100 group-hover:bg-teal-600 text-slate-600 group-hover:text-white flex items-center justify-center transition-colors">
                      <ChevronRight size={15} />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ============================================================ */}
      {/* 5. "HOW IT WORKS?" & "WHY NEXCIV?" DUAL SECTION              */}
      {/* ============================================================ */}
      <section className="py-14 bg-white border-y border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            
            {/* Left: How It Works Stepper (8 cols) */}
            <div className="lg:col-span-8 flex flex-col justify-between">
              <div>
                <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                  How It Works?
                </h2>
                <p className="text-sm text-slate-500 mt-1">
                  From your complaint to a cleaner, better city — in a few simple steps.
                </p>
              </div>

              {/* 4 Steps Flow */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mt-8 relative">
                
                {/* Step 1 */}
                <div className="flex flex-col items-start p-4 rounded-xl bg-slate-50/80 border border-slate-100">
                  <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3 font-bold shadow-xs">
                    <FileText size={20} />
                  </div>
                  <span className="text-xs font-bold text-slate-900">1. Submit Complaint</span>
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                    Describe the issue, add photos and location (optional).
                  </p>
                </div>

                {/* Step 2 */}
                <div className="flex flex-col items-start p-4 rounded-xl bg-slate-50/80 border border-slate-100">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center mb-3 font-bold shadow-xs">
                    <BrainCircuit size={20} />
                  </div>
                  <span className="text-xs font-bold text-slate-900">2. AI Classification</span>
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                    Our AI automatically identifies complaint type and urgency.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="flex flex-col items-start p-4 rounded-xl bg-slate-50/80 border border-slate-100">
                  <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center mb-3 font-bold shadow-xs">
                    <Building2 size={20} />
                  </div>
                  <span className="text-xs font-bold text-slate-900">3. Sent to Dept.</span>
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                    Your complaint is forwarded to the relevant department head.
                  </p>
                </div>

                {/* Step 4 */}
                <div className="flex flex-col items-start p-4 rounded-xl bg-slate-50/80 border border-slate-100">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3 font-bold shadow-xs">
                    <CheckCircle2 size={20} />
                  </div>
                  <span className="text-xs font-bold text-slate-900">4. Track Progress</span>
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                    You can track the status in real time until resolved.
                  </p>
                </div>

              </div>
            </div>

            {/* Right: Why NEXCIV? Card (4 cols) */}
            <div className="lg:col-span-4 bg-gradient-to-br from-teal-50/70 via-white to-emerald-50/50 rounded-2xl border border-teal-200/50 p-6 flex flex-col justify-between shadow-sm">
              <div>
                <h3 className="text-lg font-black text-slate-900 tracking-tight mb-4">
                  Why NEXCIV?
                </h3>
                
                <ul className="space-y-3.5">
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <Check size={14} />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">Faster Resolution</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <Check size={14} />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">Transparent Tracking</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <Check size={14} />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">Safer & Cleaner Communities</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                      <Check size={14} />
                    </div>
                    <span className="text-sm font-semibold text-slate-700">Citizen Friendly Platform</span>
                  </li>
                </ul>
              </div>

              <div className="mt-6 pt-4 border-t border-teal-100 flex items-center justify-between">
                <span className="text-xs text-slate-500 font-medium">Ready to submit?</span>
                <button
                  onClick={() => openReportWithCategory()}
                  className="text-xs font-bold text-teal-700 hover:text-teal-900 inline-flex items-center gap-1"
                >
                  <span>Get Started</span>
                  <ArrowRight size={12} />
                </button>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* 6. OUR IMPACT & REAL STORIES CAROUSEL                        */}
      {/* ============================================================ */}
      <section id="impact" className="py-16 sm:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Block: Impact text & button */}
          <div className="lg:col-span-4 space-y-4">
            <span className="text-[10px] font-extrabold tracking-widest text-teal-600 uppercase bg-teal-50 px-2.5 py-1 rounded-md">
              OUR IMPACT
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight leading-snug">
              Building Cleaner, Safer and <span className="text-teal-600">Healthier Communities</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
              Every complaint you report helps us identify real problems, prioritise important issues, and work towards a cleaner, safer and more livable city for everyone.
            </p>
            <div className="pt-2">
              <button
                onClick={() => openReportWithCategory()}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs tracking-wide shadow-sm transition"
              >
                <span>Be the Change</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Center: Curved Panorama Cutout */}
          <div className="lg:col-span-4 relative flex justify-center">
            <div className="relative rounded-full overflow-hidden shadow-xl border-4 border-white w-full max-w-[340px] aspect-[4/3] bg-slate-100">
              <img
                src="/canva/impact_skyline.jpg"
                alt="Cleaner Greener City Community"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent flex items-end justify-center p-4">
                <span className="bg-white/95 backdrop-blur-md text-slate-900 text-[11px] font-bold px-3 py-1.5 rounded-full shadow-md flex items-center gap-1.5">
                  <span className="text-teal-600">🌱</span> Together for a Cleaner, Greener City
                </span>
              </div>
            </div>
          </div>

          {/* Right: Testimonial Carousel */}
          <div className="lg:col-span-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-md flex flex-col justify-between min-h-[260px]">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-black text-base text-slate-900 tracking-tight">
                    Real People. Real Impact.
                  </h3>
                  <p className="text-xs text-slate-400">
                    Stories from citizens making a difference in their communities.
                  </p>
                </div>
              </div>

              {/* Testimonial Active Slide */}
              <div className="flex items-start gap-3.5 my-3">
                <img
                  src={testimonials[currentTestimonial].avatar}
                  alt={testimonials[currentTestimonial].name}
                  className="w-11 h-11 rounded-full object-cover ring-2 ring-teal-500/30"
                />
                <div>
                  <p className="text-xs text-slate-700 italic leading-relaxed">
                    "{testimonials[currentTestimonial].quote}"
                  </p>
                  <div className="mt-2 text-xs font-bold text-slate-900">
                    {testimonials[currentTestimonial].name}
                  </div>
                  <div className="text-[10px] text-teal-600 font-semibold">
                    {testimonials[currentTestimonial].city}
                  </div>
                </div>
              </div>
            </div>

            {/* Carousel navigation & dots */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <div className="flex items-center gap-1.5">
                {testimonials.map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => setCurrentTestimonial(idx)}
                    className={`h-1.5 rounded-full transition-all ${
                      currentTestimonial === idx ? 'w-5 bg-teal-600' : 'w-1.5 bg-slate-200'
                    }`}
                  />
                ))}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={prevTestimonial}
                  className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition"
                  aria-label="Previous"
                >
                  <ChevronLeft size={15} />
                </button>
                <button
                  onClick={nextTestimonial}
                  className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition"
                  aria-label="Next"
                >
                  <ChevronRight size={15} />
                </button>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ============================================================ */}
      {/* 7. FOOTER (Deep Navy, Pixel-matched with Canva)              */}
      {/* ============================================================ */}
      <footer id="contact" className="bg-[#0b1a2d] text-slate-300 pt-16 pb-8 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10 pb-12 border-b border-slate-800/80">
            
            {/* Col 1: Brand & Description (4 cols) */}
            <div className="lg:col-span-4 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-teal-500 flex items-center justify-center text-white">
                  <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                </div>
                <div className="flex flex-col">
                  <span className="text-xl font-black text-white tracking-tight leading-none">NEXCIV</span>
                  <span className="text-[8px] tracking-wider text-teal-400 font-extrabold uppercase mt-1">
                    CLEANER CITIES. STRONGER COMMUNITIES.
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
                An AI-powered civic grievance management system for cleaner, safer and smarter cities.
              </p>


            </div>

            {/* Col 2: Quick Links (2 cols) */}
            <div className="lg:col-span-2 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-white">Quick Links</h4>
              <ul className="space-y-2 text-xs text-slate-400 font-medium">
                <li>
                  <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="hover:text-white transition">
                    Home
                  </button>
                </li>
                <li>
                  <button onClick={() => openReportWithCategory()} className="hover:text-white transition">
                    Report Complaint
                  </button>
                </li>
                <li>
                  <button onClick={() => setTrackModalOpen(true)} className="hover:text-white transition">
                    Track Complaint
                  </button>
                </li>
              </ul>
            </div>

            {/* Col 3: About Links (2 cols) */}
            <div className="lg:col-span-2 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-white">About</h4>
              <ul className="space-y-2 text-xs text-slate-400 font-medium">
                <li>
                  <a href="#impact" className="hover:text-white transition">About NEXCIV</a>
                </li>
                <li>
                  <button onClick={() => setAwarenessModalOpen(true)} className="hover:text-white transition">
                    Awareness
                  </button>
                </li>
                <li>
                  <a href="#contact" className="hover:text-white transition">Contact Us</a>
                </li>
              </ul>
            </div>

            {/* Col 4: Support & Contact (4 cols) */}
            <div className="lg:col-span-4 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-white">Support</h4>
              <div className="space-y-2 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <Mail size={13} className="text-teal-400 shrink-0" />
                  <span>support@nexciv.gov</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone size={13} className="text-teal-400 shrink-0" />
                  <span>+91 98765 43210</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock size={13} className="text-teal-400 shrink-0" />
                  <span>Mon - Sat, 9:00 AM - 6:00 PM</span>
                </div>
              </div>

              {/* Social Follow */}
              <div className="pt-3">
                <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block mb-2">
                  Follow Us
                </span>
                <div className="flex items-center gap-3 text-slate-400">
                  <a href="#" className="hover:text-teal-400 transition"><Facebook size={16} /></a>
                  <a href="#" className="hover:text-teal-400 transition"><Instagram size={16} /></a>
                  <a href="#" className="hover:text-teal-400 transition"><Twitter size={16} /></a>
                  <a href="#" className="hover:text-teal-400 transition"><Youtube size={16} /></a>
                  <a href="#" className="hover:text-teal-400 transition"><Linkedin size={16} /></a>
                </div>
              </div>
            </div>

          </div>

          {/* Bottom Copyright & Disclaimer */}
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
            <span>&copy; {new Date().getFullYear()} NEXCIV. All rights reserved.</span>
            <div className="flex items-center gap-6">
              <a href="#" className="hover:text-slate-400 transition">Privacy Policy</a>
              <a href="#" className="hover:text-slate-400 transition">Terms of Service</a>
              <a href="#" className="hover:text-slate-400 transition">Accessibility</a>
            </div>
          </div>
        </div>
      </footer>

      {/* ============================================================ */}
      {/* 8. INTERACTIVE MODAL: REPORT COMPLAINT (With Live AI Triage) */}
      {/* ============================================================ */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-100 flex flex-col">
            
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60 sticky top-0 bg-white z-10">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center">
                  <FileText size={18} />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base">Submit Civic Complaint</h3>
                  <p className="text-xs text-slate-500">AI automatically detects department, priority & response SLA</p>
                </div>
              </div>
              <button
                onClick={() => setReportModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {submittedComplaintId ? (
                <div className="text-center py-8 space-y-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-inner">
                    <CheckCircle2 size={36} />
                  </div>
                  <h4 className="text-xl font-black text-slate-900">Complaint Submitted Successfully!</h4>
                  <p className="text-sm text-slate-600 max-w-md mx-auto">
                    Your complaint has been processed and routed to the municipal engineering wing.
                  </p>
                  <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl max-w-xs mx-auto">
                    <span className="text-xs text-slate-400 block font-semibold uppercase">Tracking ID</span>
                    <span className="text-lg font-mono font-black text-teal-600">{submittedComplaintId}</span>
                  </div>
                  <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
                    <Link
                      to={`/complaint/${submittedComplaintId}`}
                      className="px-5 py-2.5 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm"
                    >
                      <Eye size={14} />
                      <span>View Full Detail Page</span>
                    </Link>
                    <button
                      onClick={() => {
                        setTrackIdInput(submittedComplaintId);
                        setReportModalOpen(false);
                        setTrackModalOpen(true);
                      }}
                      className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs"
                    >
                      Track Live Progress
                    </button>
                    <button
                      onClick={() => {
                        setSubmittedComplaintId(null);
                        setReportModalOpen(false);
                      }}
                      className="px-4 py-2.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs"
                    >
                      Close
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmitComplaint} className="space-y-4">
                  
                  {formError && (
                    <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                      <AlertTriangle size={15} />
                      <span>{formError}</span>
                    </div>
                  )}

                  {/* Title */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Complaint Subject / Title *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Hazardous deep pothole causing vehicle accidents near school"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
                    />
                  </div>

                  {/* Municipal Corporation & Ward Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Municipal Corporation *
                      </label>
                      <select
                        value={selectedCorp}
                        onChange={(e) => setSelectedCorp(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                      >
                        {AP_CORPORATIONS.map((corp) => (
                          <option key={corp.code} value={corp.code}>
                            {corp.code} &middot; {corp.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Ward Number / Zone
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Ward 14, Zone 3"
                        value={ward}
                        onChange={(e) => setWard(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>
                  </div>

                  {/* Specific Landmark & Location */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Specific Landmark
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Opposite State Bank, Near Gate 2"
                        value={landmark}
                        onChange={(e) => setLandmark(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Location / Street Address *
                      </label>
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <input
                            type="text"
                            required
                            placeholder="Street or junction name"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            onBlur={() => {
                              if (location.trim().length >= 3) {
                                runClassification(description, imagePreview, location, locationLat, locationLng);
                              }
                            }}
                            className="w-full pl-8 pr-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                          />
                          <MapPin size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
                        </div>
                        <button
                          type="button"
                          onClick={handleDetectGps}
                          disabled={detectingGps}
                          className="px-2.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center gap-1 shrink-0 transition"
                          title="Detect GPS Coordinates"
                        >
                          {detectingGps ? (
                            <Loader2 size={12} className="animate-spin text-teal-600" />
                          ) : (
                            <Navigation size={12} className="text-teal-600" />
                          )}
                          <span className="hidden sm:inline">{detectingGps ? 'Locating...' : 'GPS'}</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Category Selection / Preset */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Department Category
                    </label>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                      {categoriesList.map((c) => (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => {
                            setCategory(c.id);
                            setSelectedCategoryPreset(c.id);
                          }}
                          className={`py-2 px-2 text-xs font-bold rounded-lg border text-center transition ${
                            (category === c.id || selectedCategoryPreset === c.id)
                              ? 'bg-teal-600 text-white border-teal-600 shadow-xs'
                              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                          }`}
                        >
                          {c.title}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Detailed Description */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Detailed Description *
                      </label>
                      {classifying && (
                        <span className="text-[11px] text-teal-600 font-semibold flex items-center gap-1">
                          <Loader2 size={12} className="animate-spin" />
                          AI Analyzing...
                        </span>
                      )}
                    </div>
                    <textarea
                      required
                      rows={3}
                      placeholder="Describe what happened, approximate depth of damage, safety impact on vehicles or pedestrians..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      onBlur={() => {
                        if (description.trim().length >= 8) {
                          runClassification(description, imagePreview, location, locationLat, locationLng);
                        }
                      }}
                      className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium resize-none"
                    />
                  </div>

                  {/* Multi-Photo Evidence Upload */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Photo Evidence ({imagesList.length}/4 Photos Uploaded)
                      </label>
                      <span className="text-[11px] text-slate-400">JPG/PNG up to 5MB each</span>
                    </div>

                    {imagesList.length > 0 && (
                      <div className="grid grid-cols-4 gap-2 mb-2">
                        {imagesList.map((img, idx) => (
                          <div key={idx} className="relative rounded-xl overflow-hidden border border-slate-200 aspect-square group shadow-2xs">
                            <img src={img} alt={`Evidence ${idx + 1}`} className="w-full h-full object-cover" />
                            <button
                              type="button"
                              onClick={() => removePhoto(idx)}
                              className="absolute top-1 right-1 w-5 h-5 rounded-full bg-slate-900/80 hover:bg-rose-600 text-white flex items-center justify-center transition cursor-pointer"
                              title="Remove photo"
                            >
                              <X size={11} />
                            </button>
                            <span className="absolute bottom-1 left-1 bg-black/60 text-white text-[9px] font-bold px-1 rounded">
                              #{idx + 1}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {imagesList.length < 4 && (
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-slate-200 hover:border-teal-500 rounded-xl p-3.5 text-center cursor-pointer transition bg-slate-50/50 flex items-center justify-center gap-2"
                      >
                        <Camera size={18} className="text-teal-600" />
                        <span className="text-xs text-slate-600 font-bold">
                          {imagesList.length === 0 ? 'Click to upload photos as evidence' : '+ Add another photo'}
                        </span>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          multiple
                          onChange={handleImageChange}
                          className="hidden"
                        />
                      </div>
                    )}
                  </div>

                  {/* Citizen Contact Details */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Your Full Name
                      </label>
                      <input
                        type="text"
                        placeholder="Citizen name"
                        value={citizenName}
                        onChange={(e) => setCitizenName(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Official Email <span className="text-teal-600 font-normal">(Receipt)</span>
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="pranaykoppineedi@gmail.com"
                        value={citizenEmail}
                        onChange={(e) => setCitizenEmail(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Mobile Number
                      </label>
                      <input
                        type="tel"
                        placeholder="+91 98480 12345"
                        value={citizenPhone}
                        onChange={(e) => setCitizenPhone(e.target.value)}
                        className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                      />
                    </div>
                  </div>

                  {/* Live AI Triage Feedback Banner */}
                  {(priorityScore !== null || category) && (
                    <div className="p-3.5 rounded-xl bg-gradient-to-r from-teal-50 via-sky-50 to-emerald-50 border border-teal-200 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-extrabold text-slate-900 flex items-center gap-1.5">
                            <BrainCircuit size={15} className="text-teal-600 animate-pulse" />
                            <span>AI Automated Triage & Priority</span>
                          </div>
                          <div className="text-slate-600 text-[11px] mt-0.5">
                            Department: <strong className="text-teal-800">{categoryLabel ? categoryLabel.toUpperCase() : (category ? category.toUpperCase() : 'ROADS & BUILDINGS')}</strong>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">AI PRIORITY SCORE</span>
                          <span className={`text-lg font-black ${
                            (priorityScore && priorityScore >= 75) || priority === 'Critical' ? 'text-rose-600' :
                            (priorityScore && priorityScore >= 50) || priority === 'High' ? 'text-amber-600' : 'text-teal-600'
                          }`}>
                            {priorityScore !== null ? `${Math.round(priorityScore)}/100` : (priority === 'Critical' ? '98/100' : '65/100')}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-1 border-t border-teal-100 text-[11px]">
                        <div>
                          <span className="text-slate-500">Hazard Multiplier:</span>{' '}
                          <strong className="text-slate-800">{zoneType ? `${zoneType.toUpperCase()} (${zoneMultiplier}x)` : 'Standard Zone (1.0x)'}</strong>
                        </div>
                        <div className="text-right">
                          <span className="text-slate-500">Response SLA:</span>{' '}
                          <strong className="text-rose-700">{slaHours || (priority === 'Critical' ? '0 - 4 Hours' : '24 Hours')}</strong>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Submit Button */}
                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={submitting}
                      className="w-full py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
                    >
                      {submitting ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          <span>Routing Complaint...</span>
                        </>
                      ) : (
                        <>
                          <span>Submit Complaint</span>
                          <ArrowRight size={16} />
                        </>
                      )}
                    </button>
                  </div>

                </form>
              )}
            </div>

          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 9. INTERACTIVE MODAL: TRACK COMPLAINT                        */}
      {/* ============================================================ */}
      {trackModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-100 flex flex-col overflow-hidden">
            
            {/* Header */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center">
                  <Search size={18} />
                </div>
                <h3 className="font-extrabold text-slate-900 text-base">Track Your Grievance</h3>
              </div>
              <button
                onClick={() => setTrackModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-200/60 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-5">
              <form onSubmit={handleTrackSearch} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter Complaint ID (e.g. NEX-10492)"
                  value={trackIdInput}
                  onChange={(e) => setTrackIdInput(e.target.value)}
                  className="flex-1 px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 font-mono"
                />
                <button
                  type="submit"
                  disabled={trackingLoading}
                  className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center gap-1.5 shrink-0 transition"
                >
                  {trackingLoading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
                  <span>Search</span>
                </button>
              </form>

              {trackError && (
                <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
                  <AlertTriangle size={14} />
                  <span>{trackError}</span>
                </div>
              )}

              {/* Sample Quick Lookups */}
              <div className="flex items-center gap-2 text-[11px] text-slate-500">
                <span>Quick demo tracking:</span>
                <button
                  type="button"
                  onClick={() => {
                    setTrackIdInput('NEX-KGH-001');
                    setTrackedComplaint({
                      id: 'NEX-KGH-001',
                      title: 'Deep road cave-in outside KGH Emergency Casualty Corridor',
                      department: 'Roads & Buildings Department',
                      priority: 'Critical',
                      priority_score: 100.0,
                      status: 'In Progress',
                      location_address: 'Maharanipeta, Visakhapatnam',
                      municipal_sla: '0 - 4 Hours (Emergency Dispatch)'
                    });
                  }}
                  className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-teal-700 font-mono font-bold"
                >
                  NEX-KGH-001
                </button>
              </div>

              {/* Result Card with Progress Stepper */}
              {trackedComplaint && (
                <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-bold text-teal-600 uppercase">Grievance Ticket</span>
                      <h4 className="font-mono font-black text-sm text-slate-900">{trackedComplaint.id}</h4>
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-teal-100 text-teal-800">
                      {trackedComplaint.status || 'Active'}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 font-semibold">
                    {trackedComplaint.title}
                  </p>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 bg-white p-2.5 rounded-lg border border-slate-100">
                    <div>
                      <span className="text-slate-400 block text-[9px]">DEPARTMENT</span>
                      <span className="font-bold">{trackedComplaint.department || 'R&B / Municipal'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[9px]">SLA WINDOW</span>
                      <span className="font-bold text-rose-600">{trackedComplaint.municipal_sla || '4 Hours'}</span>
                    </div>
                  </div>

                  {/* 4-Stage Visual Stepper */}
                  <div className="pt-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                      Live Municipal Status
                    </span>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2.5 text-xs text-emerald-600 font-bold">
                        <CheckCircle2 size={16} />
                        <span>1. Complaint Registered</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-emerald-600 font-bold">
                        <CheckCircle2 size={16} />
                        <span>2. AI Priority & Zone Scored ({Math.round(trackedComplaint.priority_score ?? 50)}/100)</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-teal-600 font-bold">
                        <Clock size={16} className="animate-spin" />
                        <span>3. Field Inspection Dispatched ({trackedComplaint.department || 'Engineering Wing'})</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-400">
                        <div className="w-4 h-4 rounded-full border border-slate-300 ml-0.5"></div>
                        <span>4. Work Verification & Resolution</span>
                      </div>
                    </div>
                  </div>

                  <Link
                    to={`/complaint/${trackedComplaint.id}`}
                    className="w-full py-2.5 px-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-sm transition"
                  >
                    <Eye size={14} />
                    <span>Open Full Complaint Dossier & Tracking Page</span>
                  </Link>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 10. AWARENESS MODAL                                         */}
      {/* ============================================================ */}
      {awarenessModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-100 p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Info size={18} className="text-teal-600" />
                <h3 className="font-bold text-slate-900 text-base">Civic Grievance Guidelines</h3>
              </div>
              <button
                onClick={() => setAwarenessModalOpen(false)}
                className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center"
              >
                <X size={15} />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              <p>
                <strong>⚡ Electric Hazards:</strong> Any sparking wire, tilted pole, or exposed cable box is classified as a life-safety hazard with 0-4 hour emergency response SLA.
              </p>
              <p>
                <strong>🛣️ Potholes & Cave-ins:</strong> Adding landmark details near schools, hospitals, or highways triggers automatic priority escalation to prevent vehicle collisions.
              </p>
              <p>
                <strong>🌊 Drainage & Water:</strong> Report sewer overflows and contaminated tap water immediately for public health inspection.
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setAwarenessModalOpen(false)}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg font-bold text-xs"
              >
                Got It
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
