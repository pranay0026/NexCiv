import { useState, useEffect } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function HeroSlider() {
  const slides = [
    {
      title: "Report Today for a Brighter Tomorrow",
      desc: "Our AI classifies and prioritizes complaints directly to the right municipal department."
    },
    {
      title: "Geospatial Triage with OpenStreetMap GPS",
      desc: "Emergency escalation for hazards near hospitals, schools, and high-speed arterial highways."
    },
    {
      title: "Transparent Real-Time Citizen Tracking",
      desc: "From complaint submission to field inspection and final work verification."
    },
    {
      title: "Active Civic AI Across 5 Municipal Wings",
      desc: "Roads & Buildings, Public Health, Water Supply, Electrical DISCOM & Sanitation."
    }
  ];
  
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [slides.length]);

  return (
    <div className="relative rounded-3xl overflow-hidden bg-[#0e2238] shadow-xl text-white p-6 sm:p-10 border border-slate-700/60">
      {/* City Skyline Background Overlay */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <img
          src="/canva/hero_skyline.jpg"
          alt="Skyline Backdrop"
          className="w-full h-full object-cover object-center"
        />
      </div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-xl">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-ping"></span>
            <span className="text-[10px] font-extrabold tracking-widest text-teal-400 uppercase">
              CLEANER CITIES. STRONGER COMMUNITIES.
            </span>
          </div>

          <div className="min-h-[56px] flex flex-col justify-center">
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-black tracking-tight text-white transition-opacity duration-300">
              {slides[currentSlide].title}
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
              {slides[currentSlide].desc}
            </p>
          </div>

          {/* Indicator Dots */}
          <div className="flex items-center gap-1.5 pt-2">
            {slides.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentSlide(idx)}
                className={`h-1.5 rounded-full transition-all ${
                  currentSlide === idx ? 'w-6 bg-teal-400' : 'w-2 bg-slate-600'
                }`}
              />
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row md:flex-col gap-2.5 shrink-0">
          <Link
            to="/analytics"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs shadow-md transition"
          >
            <Sparkles size={14} />
            <span>Open Dept. Analytics</span>
            <ArrowRight size={14} />
          </Link>

          <Link
            to="/"
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-200 border border-white/20 font-bold text-xs transition"
          >
            <span>Back to Portal Home</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
