import { useState, useRef, useEffect } from 'react';
import { api, AP_CORPORATIONS, APCorporation, AcknowledgementReceiptData } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import AcknowledgementReceiptModal from './AcknowledgementReceiptModal';
import {
  MapPin,
  Send,
  Loader2,
  X,
  Navigation,
  Camera,
  Layers,
  ThumbsUp,
  Sparkles,
  CheckCheck,
  User,
  Building2,
  Plus,
  Download,
  Scale,
  Mic,
  MicOff,
  Video,
  RefreshCw,
  Languages,
  Square
} from 'lucide-react';

export default function ComplaintForm({ onComplaintAdded }: { onComplaintAdded: () => void }) {
  const { profile } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  
  // Language & Voice State
  const [speechLang, setSpeechLang] = useState<'te-IN' | 'en-IN'>('te-IN');
  const [isListening, setIsListening] = useState(false);
  const [activeSpeechField, setActiveSpeechField] = useState<'title' | 'description' | null>(null);
  const recognitionRef = useRef<any>(null);

  // AP Municipal Details
  const [corporations, setCorporations] = useState<APCorporation[]>(AP_CORPORATIONS);
  const [selectedCorp, setSelectedCorp] = useState(profile?.municipalCorporation || 'GVMC');
  const [ward, setWard] = useState(profile?.ward || 'Ward 12');
  const [landmark, setLandmark] = useState('');

  // Citizen Contact
  const [citizenName, setCitizenName] = useState(profile?.name || '');
  const [citizenEmail, setCitizenEmail] = useState(profile?.email || '');
  const [citizenPhone, setCitizenPhone] = useState(profile?.phone || '+91 98480 12345');

  // Multi-Photo & Camera State
  const [images, setImages] = useState<string[]>([]);
  const [cameraModalOpen, setCameraModalOpen] = useState(false);
  const [cameraFacing, setCameraFacing] = useState<'environment' | 'user'>('environment');
  const [cameraLoading, setCameraLoading] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

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

  const [receiptModalOpen, setReceiptModalOpen] = useState(false);
  const [receiptDetails, setReceiptDetails] = useState<{
    id: string;
    rawId?: string;
    refNumber: string;
    department: string;
    category: string;
    workflowType: string;
    expectedDate: string;
    sla: string;
    emailSent: boolean;
    smsSent: boolean;
    receiptData: AcknowledgementReceiptData;
  } | null>(null);

  const [location, setLocation] = useState('');
  const [locationLat, setLocationLat] = useState<number | null>(null);
  const [locationLng, setLocationLng] = useState<number | null>(null);

  // Classification & Category State (Priority Score completely removed from Citizen UI)
  const [category, setCategory] = useState('');
  const [categoryLabel, setCategoryLabel] = useState('');
  const [categoryConfidence, setCategoryConfidence] = useState<number | null>(null);
  const [zoneType, setZoneType] = useState<string>('residential');

  // Computer Vision & Duplicate States
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
  const cameraInputRef = useRef<HTMLInputElement>(null);

  // ==================== SPEECH-TO-TEXT (MICROPHONE VOICE REGISTRATION) ====================
  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        console.warn('Speech recognition stop warning:', e);
      }
    }
    setIsListening(false);
    setActiveSpeechField(null);
  };

  const startListening = (targetField: 'title' | 'description') => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or mobile browser, or type in Telugu / English.');
      return;
    }

    if (isListening) {
      stopListening();
      return;
    }

    setError('');
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = speechLang;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognitionRef.current = recognition;

      recognition.onstart = () => {
        setIsListening(true);
        setActiveSpeechField(targetField);
      };

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }

        if (targetField === 'title') {
          setTitle((prev) => {
            const trimmed = prev.trim();
            return trimmed ? `${trimmed} ${transcript}` : transcript;
          });
        } else {
          setDescription((prev) => {
            const trimmed = prev.trim();
            const updated = trimmed ? `${trimmed} ${transcript}` : transcript;
            if (updated.length >= 8) {
              runClassification(updated, images[0] || null, location, locationLat, locationLng);
            }
            return updated;
          });
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
          setError(`Microphone Notice: ${event.error === 'not-allowed' ? 'Microphone permission denied. Please allow microphone access.' : event.error}`);
        }
        stopListening();
      };

      recognition.onend = () => {
        setIsListening(false);
        setActiveSpeechField(null);
        if (targetField === 'description' && description.trim().length >= 8) {
          runClassification(description, images[0] || null, location, locationLat, locationLng);
        }
      };

      recognition.start();
    } catch (err: any) {
      console.error('Speech recognition exception:', err);
      setError('Could not initialize microphone. Please check permissions.');
      setIsListening(false);
      setActiveSpeechField(null);
    }
  };

  // ==================== CAMERA CAPTURE (WEBCAM & MOBILE CAMERA) ====================
  const openCameraModal = async () => {
    setError('');
    setCameraModalOpen(true);
    setCameraLoading(true);

    try {
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: cameraFacing,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraLoading(false);
    } catch (err: any) {
      console.warn('Live camera stream error, falling back to camera file input:', err);
      setCameraLoading(false);
      setCameraModalOpen(false);
      // Fallback directly to mobile camera capture input
      cameraInputRef.current?.click();
    }
  };

  const closeCameraModal = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraModalOpen(false);
    setCameraLoading(false);
  };

  const switchCameraFacing = async () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    const nextFacing = cameraFacing === 'environment' ? 'user' : 'environment';
    setCameraFacing(nextFacing);
    setCameraLoading(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: nextFacing },
        audio: false
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.warn('Switch camera error:', err);
    } finally {
      setCameraLoading(false);
    }
  };

  const captureSnapshot = async () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);

    closeCameraModal();

    const updated = [...images, dataUrl].slice(0, 5);
    setImages(updated);

    // Verify first photo
    try {
      setVerifyingImage(true);
      const cv = await api.verifyImage(updated[0]);
      setCvResult(cv);
    } catch (err) {
      console.warn('CV verification error:', err);
    } finally {
      setVerifyingImage(false);
    }

    runClassification(description, updated[0], location, locationLat, locationLng);
  };

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
      if (res.confidence || res.wing_confidence) {
        setCategoryConfidence(res.confidence || res.wing_confidence);
      }
      if (res.location_info) {
        setZoneType(res.location_info.zone_type || 'residential');
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
      const updatedList = [...images, ...newImages].slice(0, 5);
      setImages(updatedList);

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
    if (cameraInputRef.current) cameraInputRef.current.value = '';
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

      if (!finalCategory) {
        const res = await api.classifyComplaint(
          description,
          images[0] || undefined,
          location || undefined,
          locationLat || undefined,
          locationLng || undefined
        );
        finalCategory = res.wing || 'others';
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
        priority: 'Medium',
        image_data: images[0] || undefined,
        images: images.length > 0 ? images : undefined,
        citizen_name: citizenName || undefined,
        citizen_email: citizenEmail || undefined,
        citizen_phone: citizenPhone || undefined
      });

      const shortId = created?.grievance_ref_number || (created?.id ? `AP-${selectedCorp}-2026-NXC${created.id.slice(0, 4).toUpperCase()}` : 'AP-NXC-LIVE');
      const wfType = created?.workflow_type || 'ordinary_grievance';
      const expectedTimeline = created?.deadline_formatted || created?.expected_resolution_date || 'Within 7 AP Working Days';

      setReceiptDetails({
        id: shortId,
        rawId: created?.id,
        refNumber: shortId,
        department: created?.department || 'Municipal Services',
        category: created?.category || finalCategory,
        workflowType: wfType,
        expectedDate: expectedTimeline,
        sla: created?.municipal_sla || '24 - 48 Hours (Standard Municipal SLA)',
        emailSent: Boolean(citizenEmail && citizenEmail.includes('@')),
        smsSent: Boolean(citizenPhone && citizenPhone.trim().length >= 10),
        receiptData: {
          grievance_ref_number: shortId,
          complaint_id: created?.id || 'live-id',
          title: created?.title || title,
          citizen_name: citizenName || 'Public Citizen',
          citizen_email: citizenEmail,
          citizen_phone: citizenPhone,
          submission_time: created?.created_at || new Date().toISOString(),
          department: created?.department || 'Municipal Services',
          department_code: created?.department_code || finalCategory,
          category: created?.category || finalCategory,
          workflow_type: wfType,
          legal_source: created?.legal_source || (wfType === 'notified_service' ? 'AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)' : 'AP Municipal Citizen Charter & PGRS Guidelines'),
          go_reference: 'Standing Order No. 118',
          designated_officer: created?.designated_officer || 'Municipal Section Engineer',
          expected_resolution_date: expectedTimeline,
          timeline_calculation_method: 'working_days',
          current_status: 'pending',
          first_appellate_authority: created?.appellate_authority || 'Superintending Engineer / Commissioner',
          appeal_deadline_days: wfType === 'notified_service' ? 30 : 15,
          compensation_applicable: wfType === 'notified_service'
        }
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
      setCategoryConfidence(null);
      setImages([]);
      setCvResult(null);
      setDuplicateResult(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (cameraInputRef.current) cameraInputRef.current.value = '';
      
      if (created.is_duplicate) {
        setSuccess('Duplicate Complaint Identified & Merged! Your report added an active Citizen Endorsement (+1 Upvote) to fast-track this municipal repair.');
      } else {
        setSuccess('Civic Complaint Registered and classified to Department Command Center!');
      }

      onComplaintAdded();
      setTimeout(() => setSuccess(''), 7000);
    } catch (err: any) {
      setError(err?.message || 'Failed to submit complaint. Please check your connection.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-slate-200/80 dark:border-gray-700 p-6">
      
      {/* Header with Bilingual & Voice Helper */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100 dark:border-gray-700">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              ఫిర్యాదు నమోదు &bull; File Civic Grievance
            </h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800 flex items-center gap-1">
              <Sparkles size={11} /> AI Auto-Classifier
            </span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            మీరు <strong>తెలుగులో (Telugu)</strong> లేదా <strong>ఇంగ్లీషులో (English)</strong> మాట్లాడి లేదా టైప్ చేసి నమోదు చేయవచ్చు. కెమెరాతో ఫోటో తీయండి.
          </p>
        </div>

        {/* Voice Language Selector Pill */}
        <div className="flex items-center gap-1.5 self-start sm:self-auto bg-slate-100 dark:bg-gray-700/80 p-1 rounded-xl text-xs font-semibold">
          <Languages size={13} className="text-teal-600 ml-1" />
          <button
            type="button"
            onClick={() => setSpeechLang('te-IN')}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
              speechLang === 'te-IN'
                ? 'bg-teal-600 text-white shadow-2xs'
                : 'text-slate-600 dark:text-gray-300 hover:text-slate-900'
            }`}
          >
            తెలుగు
          </button>
          <button
            type="button"
            onClick={() => setSpeechLang('en-IN')}
            className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
              speechLang === 'en-IN'
                ? 'bg-teal-600 text-white shadow-2xs'
                : 'text-slate-600 dark:text-gray-300 hover:text-slate-900'
            }`}
          >
            English
          </button>
        </div>
      </div>

      {/* Voice Recording Active Pulsing Banner */}
      {isListening && (
        <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-700 rounded-xl flex items-center justify-between gap-3 text-rose-900 dark:text-rose-200 animate-pulse shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold">
            <span className="w-3 h-3 rounded-full bg-rose-600 animate-ping inline-block" />
            <span>
              {speechLang === 'te-IN'
                ? '🎙️ వింటున్నారు... తెలుగులో మాట్లాడండి...'
                : '🎙️ Listening... Speak now in English...'}
            </span>
          </div>
          <button
            type="button"
            onClick={stopListening}
            className="px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold flex items-center gap-1 shadow-2xs transition cursor-pointer"
          >
            <Square size={11} />
            <span>పూర్తయింది (Stop)</span>
          </button>
        </div>
      )}
      
      {error && <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300 rounded-xl text-xs">{error}</div>}
      
      {success && (
        <div className="mb-4 p-3.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200 rounded-xl text-xs font-medium border border-emerald-200 dark:border-emerald-800 flex items-start gap-2.5">
          <CheckCheck size={18} className="text-emerald-600 shrink-0 mt-0.5" />
          <span>{success}</span>
        </div>
      )}

      {/* Official Municipal Acknowledgment Receipt Banner */}
      {receiptDetails && (
        <div className="mb-4 p-5 rounded-2xl bg-gradient-to-r from-teal-50 via-emerald-50 to-slate-50 dark:from-teal-950/40 dark:via-emerald-950/40 dark:to-gray-900/60 border border-teal-300 dark:border-teal-700/80 text-slate-800 dark:text-slate-100 shadow-sm space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2.5">
              <span className="w-7 h-7 rounded-lg bg-teal-600 text-white flex items-center justify-center font-black text-xs shadow-xs">✓</span>
              <div>
                <span className="font-extrabold text-sm text-slate-900 dark:text-white block">
                  Municipal Grievance Successfully Registered
                </span>
                <span className="text-[11px] text-teal-700 dark:text-teal-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Scale size={12} />
                  {receiptDetails.workflowType === 'notified_service' ? 'Notified Public Service (Act No. 6 of 2018)' : 'Ordinary Civic Grievance (Citizen Charter)'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-xl text-xs font-mono font-black bg-teal-200/80 dark:bg-teal-900/80 text-teal-950 dark:text-teal-200 tracking-wider">
                REF: {receiptDetails.refNumber}
              </span>
              <button
                type="button"
                onClick={() => setReceiptModalOpen(true)}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
              >
                <Download size={13} />
                Download Receipt
              </button>
            </div>
          </div>

          <div className="text-xs text-slate-600 dark:text-slate-300 grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2.5 border-t border-teal-200/60 dark:border-teal-800/60">
            <div>
              <span className="text-slate-400 block text-[10px] font-bold">DEPARTMENT</span>
              <strong>{receiptDetails.department}</strong>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] font-bold">EXPECTED RESOLUTION DATE</span>
              <strong className="text-teal-800 dark:text-teal-300">{receiptDetails.expectedDate}</strong>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] font-bold">NOTIFICATION DISPATCH</span>
              <span className="font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                <CheckCheck size={13} /> SMS & Email Dispatched
              </span>
            </div>
          </div>

          {receiptDetails.rawId && (
            <div className="pt-2 border-t border-teal-200/40 dark:border-teal-800/40 flex justify-end">
              <Link
                to={`/complaint/${receiptDetails.rawId}`}
                className="text-xs text-teal-700 dark:text-teal-300 hover:underline font-bold inline-flex items-center gap-1"
              >
                <span>View Full Tracking Dossier &rarr;</span>
              </Link>
            </div>
          )}
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
                Existing ticket: <strong>"{duplicateResult.master_title}"</strong>. Submitting will register your report as a <strong>Citizen Endorsement (+1 Upvote)</strong> to fast-track municipal action.
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

        {/* Complaint Title with Voice Input */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700 dark:text-gray-300">
              ఫిర్యాదు శీర్షిక &bull; Complaint Title
            </label>
            <button
              type="button"
              onClick={() => startListening('title')}
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[11px] font-bold transition cursor-pointer ${
                isListening && activeSpeechField === 'title'
                  ? 'bg-rose-600 text-white animate-pulse'
                  : 'bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 hover:bg-teal-100 border border-teal-200 dark:border-teal-800'
              }`}
              title="Click to speak title in Telugu or English"
            >
              {isListening && activeSpeechField === 'title' ? <MicOff size={12} /> : <Mic size={12} />}
              <span>{isListening && activeSpeechField === 'title' ? 'ఆపండి (Stop)' : 'మాట్లాడండి (Speak)'}</span>
            </button>
          </div>
          <div className="relative">
            <input
              type="text"
              required
              className="w-full pl-3.5 pr-10 py-2.5 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-sm"
              placeholder="ఉదా: రోడ్డుపై పెద్ద గుంతలు / e.g. Deep road crater near Benz Circle"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <button
              type="button"
              onClick={() => startListening('title')}
              className={`absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition ${
                isListening && activeSpeechField === 'title'
                  ? 'text-rose-600 bg-rose-100 dark:bg-rose-900/50'
                  : 'text-slate-400 hover:text-teal-600'
              }`}
              title="Speak in Telugu/English"
            >
              <Mic size={15} />
            </button>
          </div>
        </div>
        
        {/* Detailed Description with Voice Input */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700 dark:text-gray-300">
              సమస్య పూర్తి వివరాలు &bull; Detailed Description
            </label>
            <button
              type="button"
              onClick={() => startListening('description')}
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg text-[11px] font-bold transition cursor-pointer ${
                isListening && activeSpeechField === 'description'
                  ? 'bg-rose-600 text-white animate-pulse'
                  : 'bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 hover:bg-teal-100 border border-teal-200 dark:border-teal-800'
              }`}
              title="Click to speak description in Telugu or English"
            >
              {isListening && activeSpeechField === 'description' ? <MicOff size={12} /> : <Mic size={12} />}
              <span>{isListening && activeSpeechField === 'description' ? 'ఆపండి (Stop)' : 'వాయిస్ మైక్ (Voice Mic)'}</span>
            </button>
          </div>
          <div className="relative">
            <textarea
              required
              rows={3}
              className="w-full pl-3.5 pr-10 py-2.5 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-xs resize-none"
              placeholder="సమస్యను వివరంగా చెప్పండి: తాగునీటి పైపులైన్ లీకేజీ, కాలువ పూడిక, వీధి లైట్లు వెలగడం లేదు, చెత్త పేరుకుపోయింది... / Describe the civic defect in detail in Telugu or English..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={handleDescriptionBlur}
            />
            <button
              type="button"
              onClick={() => startListening('description')}
              className={`absolute right-2.5 top-3 p-1.5 rounded-lg transition ${
                isListening && activeSpeechField === 'description'
                  ? 'text-rose-600 bg-rose-100 dark:bg-rose-900/50'
                  : 'text-slate-400 hover:text-teal-600'
              }`}
              title="Speak in Telugu/English"
            >
              <Mic size={16} />
            </button>
          </div>
        </div>

        {/* Multi-Photo & Camera Section */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700 dark:text-gray-300">
              ఫోటో రుజువు &bull; Photo Evidence (Upload or Capture with Camera)
            </label>
            <span className="text-[11px] text-slate-500">{images.length}/5 photos attached</span>
          </div>
          
          {/* Hidden File Inputs */}
          <input
            type="file"
            ref={fileInputRef}
            accept="image/*"
            multiple
            onChange={handleImageChange}
            className="hidden"
          />
          <input
            type="file"
            ref={cameraInputRef}
            accept="image/*"
            capture="environment"
            onChange={handleImageChange}
            className="hidden"
          />

          {/* Photo Gallery & Action Buttons */}
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
              <>
                {/* 1. Take Photo with Live Camera Button */}
                <button
                  type="button"
                  onClick={openCameraModal}
                  className="aspect-square border-2 border-dashed border-teal-300 dark:border-teal-700/80 hover:border-teal-500 rounded-xl flex flex-col items-center justify-center gap-1 text-teal-700 dark:text-teal-300 hover:bg-teal-50 dark:hover:bg-teal-950/30 transition p-2 text-center cursor-pointer bg-teal-50/40"
                >
                  <Camera size={18} className="text-teal-600" />
                  <span className="text-[10px] font-bold">కెమెరా (Camera)</span>
                </button>

                {/* 2. Choose File from Gallery Button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="aspect-square border-2 border-dashed border-slate-300 dark:border-gray-600 hover:border-teal-500 rounded-xl flex flex-col items-center justify-center gap-1 text-slate-600 dark:text-gray-400 hover:text-teal-600 transition bg-slate-50 dark:bg-gray-900/50 p-2 text-center cursor-pointer"
                >
                  <Plus size={18} className="text-teal-600" />
                  <span className="text-[10px] font-bold">గ్యాలరీ (Upload)</span>
                </button>
              </>
            )}
          </div>

          {/* Computer Vision Feedback */}
          {images.length > 0 && (
            <div className="mt-2.5 p-2.5 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl flex items-center justify-between text-xs">
              {verifyingImage ? (
                <div className="flex items-center gap-1.5 text-teal-600 font-medium">
                  <Loader2 size={13} className="animate-spin" />
                  <span>AI Computer Vision inspecting pavement defect...</span>
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
                </div>
              ) : (
                <span className="text-slate-500 text-[11px]">
                  {cvResult?.rejection_reason || `${images.length} photos attached for field verification.`}
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Location & Landmark Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              గుర్తు / వీధి పేరు &bull; Landmark / Street Name
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none text-slate-900 dark:text-white text-xs"
              placeholder="ఉదా: ప్రభుత్వ ఆస్పత్రి ఎదురుగా / Near Govt Hospital"
              value={landmark}
              onChange={(e) => setLandmark(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              GPS స్థానం &bull; Coordinates / Address
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
                className="px-3 py-2 bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-300 hover:bg-teal-100 rounded-xl text-xs font-bold flex items-center gap-1 transition border border-teal-200 dark:border-teal-800 shrink-0 cursor-pointer"
              >
                <Navigation size={13} className={detectingGps ? 'animate-spin' : ''} />
                <span>{detectingGps ? 'GPS...' : 'GPS'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Locality Type & AI Classification (Priority score completely removed) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1">
              ప్రాంతం రకం &bull; Locality / Zone Category
            </label>
            <select
              value={zoneType}
              onChange={(e) => setZoneType(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-teal-500 outline-none"
            >
              <option value="residential">Residential Colony (నివాస ప్రాంతం)</option>
              <option value="hospital">Hospital &amp; Healthcare Zone (ఆస్పత్రి ప్రాంతం)</option>
              <option value="school">School / College Zone (పాఠశాల / కళాశాల)</option>
              <option value="highway">High-Speed Corridor / Highway (హైవే / ప్రధాన రహదారి)</option>
              <option value="transit_hub">RTC Bus Station / Railway Station (బస్టాండ్ / రైల్వే స్టేషన్)</option>
              <option value="commercial">Commercial Market (వాణిజ్య మార్కెట్)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-gray-300 mb-1 flex items-center justify-between">
              <span>వర్గీకరణ శాఖ &bull; Target Municipal Department</span>
              {classifying && (
                <span className="text-[10px] text-teal-600 font-medium flex items-center gap-1">
                  <Loader2 size={10} className="animate-spin" /> AI Classifying...
                </span>
              )}
            </label>
            <div className="px-3 py-2 bg-slate-50 dark:bg-gray-900 border border-slate-200 dark:border-gray-700 rounded-xl text-xs flex items-center justify-between text-slate-800 dark:text-slate-200 font-semibold min-h-[38px]">
              <span className="flex items-center gap-1.5">
                {categoryLabel || (category ? category.replace('_', ' ').toUpperCase() : 'AI Auto-Detect')}
                {checkingDuplicate && (
                  <span className="text-[10px] text-amber-600 flex items-center gap-0.5 font-normal">
                    <Loader2 size={9} className="animate-spin" /> checking dupes
                  </span>
                )}
              </span>
              {categoryConfidence && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 dark:bg-teal-950/60 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
                  {Math.round(categoryConfidence * 100)}% Match
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
              <span>నమోదు చేస్తున్నారు... Registering Complaint...</span>
            </>
          ) : (
            <>
              <Send size={16} />
              <span>ఫిర్యాదు సమర్పించండి &bull; Submit to {selectedCorp}</span>
            </>
          )}
        </button>
      </form>

      {/* Official Downloadable Acknowledgement Receipt Modal */}
      {receiptDetails && (
        <AcknowledgementReceiptModal
          receipt={receiptDetails.receiptData}
          isOpen={receiptModalOpen}
          onClose={() => setReceiptModalOpen(false)}
        />
      )}

      {/* INTERACTIVE LIVE CAMERA CAPTURE MODAL */}
      {cameraModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 text-white rounded-3xl overflow-hidden max-w-lg w-full border border-slate-700 shadow-2xl space-y-4 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm">
                <Video size={16} className="text-teal-400" />
                <span>Take Photo with Camera &bull; ఫోటో తీయండి</span>
              </div>
              <button
                type="button"
                onClick={closeCameraModal}
                className="p-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                <X size={18} />
              </button>
            </div>

            {/* Video Viewport */}
            <div className="relative aspect-video bg-black rounded-2xl overflow-hidden flex items-center justify-center border border-slate-800">
              {cameraLoading && (
                <div className="flex items-center gap-2 text-teal-400 text-xs">
                  <Loader2 size={20} className="animate-spin" />
                  <span>కెమెరా ప్రారంభమవుతోంది... Initializing camera...</span>
                </div>
              )}
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
            </div>

            {/* Camera Controls */}
            <div className="flex items-center justify-between gap-3 pt-2">
              <button
                type="button"
                onClick={switchCameraFacing}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold flex items-center gap-1.5 transition text-slate-200"
                title="Switch front/back camera"
              >
                <RefreshCw size={14} />
                <span>Flip Camera</span>
              </button>

              <button
                type="button"
                onClick={captureSnapshot}
                className="px-6 py-2.5 rounded-full bg-teal-500 hover:bg-teal-400 text-slate-950 font-black text-sm flex items-center gap-2 shadow-lg transition active:scale-95 cursor-pointer"
              >
                <Camera size={18} />
                <span>ఫోటో తీయండి (Capture)</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  closeCameraModal();
                  cameraInputRef.current?.click();
                }}
                className="text-xs text-slate-400 hover:text-white underline"
              >
                Native App
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
