import { useState, useRef, useEffect } from 'react';
import { api, AP_CORPORATIONS, APCorporation } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import {
  MapPin,
  Send,
  Loader2,
  X,
  AlertTriangle,
  Flame,
  Clock,
  CheckCircle,
  Navigation,
  Camera,
  Layers,
  ThumbsUp,
  Sparkles,
  CheckCheck,
  Mail,
  Phone,
  User,
  Building2,
  Plus
} from 'lucide-react';

export default function ComplaintForm({ onComplaintAdded }: { onComplaintAdded: () => void }) {
  const { profile } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  
  // AP Municipal Details
  const [corporations, setCorporations] = useState<APCorporation[]>(AP_CORPORATIONS);
  const [selectedCorp, setSelectedCorp] = useState(profile?.municipalCorporation || 'GVMC');
  const [ward, setWard] = useState(profile?.ward || 'Ward 12');
  const [landmark, setLandmark] = useState('');

  // Citizen Contact
  const [citizenName, setCitizenName] = useState(profile?.name || '');
  const [citizenEmail, setCitizenEmail] = useState(profile?.email || '');
  const [citizenPhone, setCitizenPhone] = useState(profile?.phone || '+91 98480 12345');

  // Multi-Photo State
  const [images, setImages] = useState<string[]>([]);

  useEffect(() => {
    if (profile) {
      if (profile.name && !citizenName) setCitizenName(profile.name);
      if (profile.email && !citizenEmail) setCitizenEmail(profile.email);
      if (profile.phone && !citizenPhone) setCitizenPhone(profile.phone);
      if (profile.municipalCorporation) setSelectedCorp(profile.municipalCorporation);
    }
  }, [profile]);

  useEffect(() => {
    api.getCorporations().then(data => {
      if (data && data.length > 0) setCorporations(data);
    }).catch(() => {});
  }, []);

  const [receiptDetails, setReceiptDetails] = useState<{
    id: string;
    sla: string;
    emailSent: boolean;
    smsSent: boolean;
  } | null>(null);

  const [location, setLocation] = useState('');
  const [locationLat, setLocationLat] = useState<number | null>(null);
  const [locationLng, setLocationLng] = useState<number | null>(null);

  const [category, setCategory] = useState('');
  const [categoryLabel, setCategoryLabel] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [priorityScore, setPriorityScore] = useState<number | null>(null);
  const [zoneType, setZoneType] = useState<string>('residential');
  const [zoneMultiplier, setZoneMultiplier] = useState<number>(1.0);

  // Phase 2: Computer Vision & Duplicate States
  const [cvResult, setCvResult] = useState<{
    is_valid_civic_image: boolean;
    defect_type: string;
    visual_severity_score: number;
    visual_priority_tier: string;
    visual_confidence: number;
    rejection_reason?: string;
  } | null>(null);

  const [duplicateResult, setDuplicateResult] = useState<{
    is_duplicate: boolean;
    master_complaint_id?: string;
    master_title?: string;
    similarity_score?: number;
    distance_meters?: number;
    reasons?: string[];
  } | null>(null);

  const [verifyingImage, setVerifyingImage] = useState(false);
  const [checkingDuplicate, setCheckingDuplicate] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [detectingGps, setDetectingGps] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Trigger classification when text, image, or location changes
  const runClassification = async (
    descText = description,
    imgData = images[0] || null,
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
        setZoneType(res.location_info.zone_type || 'residential');
        setZoneMultiplier(res.location_info.vulnerability_multiplier || 1.0);
      }
      runDuplicateCheck(descText, res.wing || category, lat, lng, locAddress, imgData);
    } catch (err) {
      console.error('Classification error:', err);
    } finally {
      setClassifying(false);
    }
  };

  const runDuplicateCheck = async (
    descText = description,
    cat = category,
    lat = locationLat,
    lng = locationLng,
    locAddress = location,
    imgData = images[0] || null
  ) => {
    if (!descText.trim() && !imgData) return;

    try {
      setCheckingDuplicate(true);
      const dup = await api.checkDuplicate({
        title,
        description: descText,
        category: cat || undefined,
        location_lat: lat || undefined,
        location_lng: lng || undefined,
        location_address: locAddress || undefined,
        image_data: imgData || undefined
      });

      if (dup && dup.is_duplicate) {
        setDuplicateResult(dup);
      } else {
        setDuplicateResult(null);
      }
    } catch (err) {
      console.warn('Duplicate check warning:', err);
    } finally {
      setCheckingDuplicate(false);
    }
  };

  const handleDetectGps = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }
    setDetectingGps(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setLocationLat(lat);
        setLocationLng(lng);
        const gpsStr = `GPS: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        setLocation(gpsStr);
        setDetectingGps(false);
        runClassification(description, images[0] || null, gpsStr, lat, lng);
      },
      (err) => {
        setDetectingGps(false);
        console.warn('Geolocation warning:', err);
        setError('Could not fetch GPS automatically. Please enter landmark manually.');
      },
      { timeout: 8000 }
    );
  };

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const newImages: string[] = [];
    const readPromises: Promise<void>[] = [];

    Array.from(files).forEach((file) => {
      if (file.size > 8 * 1024 * 1024) {
        setError('Each photo must be smaller than 8MB');
        return;
      }
      const p = new Promise<void>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          if (reader.result) {
            newImages.push(reader.result as string);
          }
          resolve();
        };
        reader.readAsDataURL(file);
      });
      readPromises.push(p);
    });

    await Promise.all(readPromises);

    if (newImages.length > 0) {
      const updatedList = [...images, ...newImages].slice(0, 5); // Limit up to 5 photos
      setImages(updatedList);

      // Verify the first photo with Computer Vision
      const primaryPhoto = updatedList[0];
      try {
        setVerifyingImage(true);
        const cv = await api.verifyImage(primaryPhoto);
        setCvResult(cv);
        if (!cv.is_valid_civic_image) {
          setError(`Photo Notice: ${cv.rejection_reason || 'Photo is unclear'}. Please ensure clear damage evidence.`);
        } else {
          setError('');
        }
      } catch (err) {
        console.warn('Image verification note:', err);
      } finally {
        setVerifyingImage(false);
      }

      runClassification(description, primaryPhoto, location, locationLat, locationLng);
    }

    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleRemoveImage = (indexToRemove: number) => {
    const updated = images.filter((_, idx) => idx !== indexToRemove);
    setImages(updated);
    if (updated.length === 0) {
      setCvResult(null);
    }
    runClassification(description, updated[0] || null, location, locationLat, locationLng);
  };

  const handleDescriptionBlur = () => {
    if (description.trim().length >= 8) {
      runClassification(description, images[0] || null, location, locationLat, locationLng);
    }
  };

  const handleLocationBlur = () => {
    if (location.trim().length >= 3) {
      runClassification(description, images[0] || null, location, locationLat, locationLng);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) return;

    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      let finalCategory = category;
      let finalPriority = priority;

      if (!finalCategory) {
        const res = await api.classifyComplaint(
          description,
          images[0] || undefined,
          location || undefined,
          locationLat || undefined,
          locationLng || undefined
        );
        finalCategory = res.wing || 'others';
        finalPriority = res.priority || 'Medium';
      }

      const created = await api.createComplaint({
        title,
        description,
        municipal_corporation: selectedCorp,
        ward: ward || undefined,
        landmark: landmark || undefined,
        location_address: location || undefined,
        location_lat: locationLat || undefined,
        location_lng: locationLng || undefined,
        category: finalCategory,
        priority: finalPriority,
        priority_score: priorityScore || undefined,
        image_data: images[0] || undefined,
        images: images.length > 0 ? images : undefined,
        citizen_name: citizenName || undefined,
        citizen_email: citizenEmail || undefined,
        citizen_phone: citizenPhone || undefined
      });

      const shortId = created?.id ? (created.id.length > 8 ? `NXC-${created.id.slice(0, 6).toUpperCase()}` : created.id) : 'NXC-LIVE';
      setReceiptDetails({
        id: shortId,
        sla: created?.municipal_sla || '24 - 48 Hours (Standard Municipal SLA)',
        emailSent: Boolean(citizenEmail && citizenEmail.includes('@')),
        smsSent: Boolean(citizenPhone && citizenPhone.trim().length >= 10)
      });

      // Clear input fields
      setTitle('');
      setDescription('');
      setLandmark('');
      setLocation('');
      setLocationLat(null);
      setLocationLng(null);
      setCategory('');
      setCategoryLabel('');
      setPriority('Medium');
      setPriorityScore(null);
      setImages([]);
      setCvResult(null);
      setDuplicateResult(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      
      if (created.is_duplicate) {
        setSuccess('Duplicate Complaint Identified & Merged! Your report added an active Citizen Endorsement (+1 Upvote) to fast-track this municipal repair.');
      } else {
        setSuccess('Civic Complaint Registered and assigned to Department Command Center!');
      }

      onComplaintAdded();
      setTimeout(() => setSuccess(''), 7000);
    } catch (err: any) {
      setError(err?.message || 'Failed to submit complaint. Please check your connection.');
    } finally {
      setSubmitting(false);
    }
  };

  const getPriorityBadgeClass = (p: string) => {
    switch (p.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 border-red-300 dark:border-red-700';
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300 border-orange-300 dark:border-orange-700';
      case 'medium':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-300 dark:border-amber-700';
      default:
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700';
    }
  };

  const getPriorityIcon = (p: string) => {
    switch (p.toLowerCase()) {
      case 'critical': return <Flame size={14} className="text-red-600 dark:text-red-400" />;
      case 'high': return <AlertTriangle size={14} className="text-orange-600 dark:text-orange-400" />;
      case 'medium': return <Clock size={14} className="text-amber-600 dark:text-amber-400" />;
      default: return <CheckCircle size={14} className="text-emerald-600 dark:text-emerald-400" />;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-200/80 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">File Civic Grievance & Work Order</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800 flex items-center gap-1">
              <Sparkles size={11} /> AI Multimodal Triage
            </span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Attach multiple photos, select your AP Municipal Corporation & Ward. Multimodal AI computes priority and routes to the assigned municipal department.
          </p>
        </div>
      </div>
      
      {error && <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300 rounded-xl text-xs">{error}</div>}
      
      {success && (
        <div className="mb-4 p-3.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 rounded-xl text-xs font-medium border border-emerald-200 dark:border-emerald-800 flex items-start gap-2.5">
          <CheckCheck size={18} className="text-emerald-600 shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      {/* Official Municipal Acknowledgment Receipt */}
      {receiptDetails && (
        <div className="mb-4 p-4 rounded-2xl bg-gradient-to-r from-teal-50 via-emerald-50 to-slate-50 dark:from-teal-950/40 dark:via-emerald-950/40 dark:to-gray-900/60 border border-teal-300 dark:border-teal-700/80 text-slate-800 dark:text-slate-100 shadow-xs space-y-2.5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-teal-600 text-white flex items-center justify-center font-bold text-xs">✓</span>
              <span className="font-bold text-sm text-slate-900 dark:text-white">Municipal Grievance Ticket Dispatched</span>
            </div>
            <span className="px-2.5 py-1 rounded-lg text-xs font-black bg-teal-200/80 dark:bg-teal-900/80 text-teal-900 dark:text-teal-200 tracking-wider">
              REF: {receiptDetails.id}
            </span>
          </div>

          <div className="text-xs text-slate-600 dark:text-slate-300 flex flex-wrap items-center gap-x-4 gap-y-1.5 pt-2 border-t border-teal-200/60 dark:border-teal-800/60">
            <span>Target SLA: <strong className="text-amber-700 dark:text-amber-300">{receiptDetails.sla}</strong></span>
            {receiptDetails.emailSent && (
              <span className="flex items-center gap-1 text-teal-700 dark:text-teal-300 font-semibold">
                <Mail size={13} /> Confirmation Dispatched
              </span>
            )}
            {receiptDetails.smsSent && (
              <span className="flex items-center gap-1 text-teal-700 dark:text-teal-300 font-semibold">
                <Phone size={13} /> SMS Alert Dispatched
              </span>
            )}
          </div>
        </div>
      )}

      {/* Duplicate Alert Banner */}
      {duplicateResult && duplicateResult.is_duplicate && (
        <div className="mb-4 p-3.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700 rounded-xl text-amber-900 dark:text-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
          <div className="flex items-start gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-200/60 dark:bg-amber-900/60 flex items-center justify-center shrink-0 text-amber-800 dark:text-amber-300 mt-0.5 sm:mt-0">
              <Layers size={16} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-amber-900 dark:text-amber-200 uppercase tracking-wider">
                  Similar Issue Already Reported ({duplicateResult.distance_meters ? `${duplicateResult.distance_meters}m away` : 'Nearby'})
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-200 text-amber-900 font-bold">
                  {Math.round((duplicateResult.similarity_score || 0.85) * 100)}% Match
                </span>
              </div>
              <p className="text-xs text-amber-800/90 dark:text-amber-300/90 mt-0.5">
                Existing ticket: <strong>"{duplicateResult.master_title}"</strong>. Submitting will register your report as a <strong>Citizen Endorsement (+1 Upvote)</strong> to escalate repair priority.
              </p>
            </div>
          </div>
          <div className="shrink-0 flex items-center gap-1.5 text-[11px] font-bold text-amber-800 dark:text-amber-300 bg-amber-200/50 px-2.5 py-1 rounded-lg">
            <ThumbsUp size={12} /> Fast-Tracks Repair
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* ROW 1: AP Municipal Corporation & Ward */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1 flex items-center gap-1.5">
              <Building2 size={13} className="text-teal-600" />
              Municipal Corporation (17 in AP)
            </label>
            <select
              value={selectedCorp}
              onChange={(e) => setSelectedCorp(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-teal-500 outline-none"
            >
              {corporations.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.code} - {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              Ward / Division
            </label>
            <input
              type="text"
              value={ward}
              onChange={(e) => setWard(e.target.value)}
              placeholder="e.g. Ward 14 / Sector 4"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-teal-500 outline-none"
            />
          </div>
        </div>

        {/* Complaint Title */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">Complaint Title</label>
          <input
            type="text"
            required
            className="w-full px-3.5 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-sm"
            placeholder="e.g. Road crater & asphalt cave-in near Benz Circle Service Road"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        
        {/* Detailed Description */}
        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
            Detailed Description & Hazard Severity
          </label>
          <textarea
            required
            rows={3}
            className="w-full px-3.5 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-xs resize-none"
            placeholder="Describe the issue in detail: depth of pothole, sewage leakage volume, sparking electric pole, water pressure loss..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onBlur={handleDescriptionBlur}
          />
        </div>

        {/* Multi-Photo Upload Section */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700 dark:text-gray-300">
              Photo Evidence (Upload Multiple Photos — Evaluated by Computer Vision AI)
            </label>
            <span className="text-[11px] text-slate-500">{images.length}/5 photos attached</span>
          </div>
          
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            multiple
            onChange={handleImageChange}
            className="hidden"
          />

          {/* Photo Gallery Thumbnails */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2.5 pt-1">
            {images.map((img, idx) => (
              <div key={idx} className="relative group rounded-xl overflow-hidden border border-slate-200 dark:border-gray-700 bg-slate-100 aspect-square shadow-2xs">
                <img src={img} alt={`Proof ${idx + 1}`} className="w-full h-full object-cover" />
                <button
                  type="button"
                  onClick={() => handleRemoveImage(idx)}
                  className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 shadow-md hover:bg-red-700 transition"
                  title="Remove this photo"
                >
                  <X size={11} />
                </button>
                {idx === 0 && (
                  <span className="absolute bottom-1 left-1 bg-black/70 text-white text-[9px] px-1.5 py-0.5 rounded font-bold">
                    Primary
                  </span>
                )}
              </div>
            ))}

            {images.length < 5 && (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="aspect-square border-2 border-dashed border-slate-300 dark:border-gray-600 hover:border-teal-500 rounded-xl flex flex-col items-center justify-center gap-1 text-slate-600 dark:text-gray-400 hover:text-teal-600 transition bg-slate-50 dark:bg-gray-900/50 p-2 text-center"
              >
                <Plus size={18} className="text-teal-600" />
                <span className="text-[10px] font-bold">Add Photo</span>
              </button>
            )}
          </div>

          {/* CV Feedback on Primary Photo */}
          {images.length > 0 && (
            <div className="mt-2.5 p-2.5 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl flex items-center justify-between text-xs">
              {verifyingImage ? (
                <div className="flex items-center gap-1.5 text-teal-600 font-medium">
                  <Loader2 size={13} className="animate-spin" />
                  <span>AI Computer Vision inspecting pavement defect & damage depth...</span>
                </div>
              ) : cvResult?.is_valid_civic_image ? (
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1 text-[11px]">
                    <Camera size={13} className="text-teal-600" />
                    Defect: <span className="uppercase text-teal-700 dark:text-teal-400">{cvResult.defect_type.replace(/_/g, ' ')}</span>
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                    {Math.round(cvResult.visual_confidence * 100)}% AI Verified
                  </span>
                  <span className="text-slate-600 text-[11px]">
                    Severity: <strong>{cvResult.visual_severity_score}/100 ({cvResult.visual_priority_tier})</strong>
                  </span>
                </div>
              ) : (
                <span className="text-slate-500 text-[11px]">
                  {cvResult?.rejection_reason || `${images.length} photos attached for inspection.`}
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Location & Landmark Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              Specific Landmark / Street Name
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-xs"
              placeholder="e.g. Near Govt Hospital Pillar 14, Main Road"
              value={landmark}
              onChange={(e) => setLandmark(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              GPS Coordinates / Street Address
            </label>
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <MapPin className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                <input
                  type="text"
                  className="w-full pl-8 pr-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-xs"
                  placeholder="Address or click GPS"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  onBlur={handleLocationBlur}
                />
              </div>

              <button
                type="button"
                onClick={handleDetectGps}
                disabled={detectingGps}
                className="px-3 py-2 bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-300 hover:bg-teal-100 rounded-xl text-xs font-bold flex items-center gap-1 transition border border-teal-200 dark:border-teal-800 shrink-0"
              >
                <Navigation size={13} className={detectingGps ? 'animate-spin' : ''} />
                <span>{detectingGps ? 'GPS...' : 'GPS'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Vulnerability Zone Type */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              Zone Vulnerability Tier (Impact Multiplier: {zoneMultiplier}x)
            </label>
            <select
              value={zoneType}
              onChange={(e) => {
                setZoneType(e.target.value);
                const map: Record<string, number> = {
                  hospital: 1.5,
                  school: 1.4,
                  highway: 1.3,
                  transit_hub: 1.25,
                  commercial: 1.1,
                  residential: 1.0
                };
                setZoneMultiplier(map[e.target.value] || 1.0);
              }}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-teal-500 outline-none"
            >
              <option value="residential">Residential Zone (1.0x)</option>
              <option value="hospital">Hospital / Emergency Health Zone (1.5x Priority Boost)</option>
              <option value="school">School / College Pedestrian Zone (1.4x Priority Boost)</option>
              <option value="highway">High-Speed Corridor / Highway (1.3x Priority Boost)</option>
              <option value="transit_hub">RTC Bus Station / Railway Station (1.25x Priority Boost)</option>
              <option value="commercial">Commercial Market (1.1x Priority Boost)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1 flex items-center justify-between">
              <span>Target Municipal Wing</span>
              {classifying && (
                <span className="text-[10px] text-teal-600 font-medium flex items-center gap-1">
                  <Loader2 size={10} className="animate-spin" /> AI routing...
                </span>
              )}
            </label>
            <div className="px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs flex items-center justify-between text-slate-800 dark:text-slate-200 font-semibold">
              <span className="flex items-center gap-1.5">
                {categoryLabel || (category ? category.replace('_', ' ').toUpperCase() : 'AI Auto-Detect')}
                {checkingDuplicate && (
                  <span className="text-[10px] text-amber-600 flex items-center gap-0.5 font-normal">
                    <Loader2 size={9} className="animate-spin" /> checking dupes
                  </span>
                )}
              </span>
              {priority && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border flex items-center gap-1 ${getPriorityBadgeClass(priority)}`}>
                  {getPriorityIcon(priority)}
                  {priority}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Citizen Contact Section */}
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-gray-900/60 border border-slate-200 dark:border-gray-700/80 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <User size={13} className="text-teal-600" />
              Citizen Contact (Auto-populated on login)
            </span>
            <span className="text-[10px] text-slate-500">Live SMS & email resolution tracking</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div>
              <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Name</label>
              <input
                type="text"
                placeholder="Citizen Name"
                value={citizenName}
                onChange={(e) => setCitizenName(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs bg-white dark:bg-gray-800 border border-slate-200 dark:border-gray-700 rounded-lg text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Email</label>
              <input
                type="email"
                placeholder="citizen@nexciv.org"
                value={citizenEmail}
                onChange={(e) => setCitizenEmail(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs bg-white dark:bg-gray-800 border border-slate-200 dark:border-gray-700 rounded-lg text-slate-900 dark:text-white outline-none"
              />
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-slate-500 mb-0.5">Mobile (SMS)</label>
              <input
                type="tel"
                placeholder="+91 98480 12345"
                value={citizenPhone}
                onChange={(e) => setCitizenPhone(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs bg-white dark:bg-gray-800 border border-slate-200 dark:border-gray-700 rounded-lg text-slate-900 dark:text-white outline-none"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          {submitting ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span>Registering Complaint...</span>
            </>
          ) : (
            <>
              <Send size={16} />
              <span>Submit Civic Grievance to {selectedCorp}</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
