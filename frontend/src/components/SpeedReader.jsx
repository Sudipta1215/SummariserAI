import React, { useEffect, useMemo, useRef, useState } from "react";
import { Play, Pause, RotateCcw, X, Zap } from "lucide-react";

// Helper to keep index within bounds
const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

const SpeedReader = ({ text = "", onClose }) => {
  // 1. Prepare Text (Memoized for performance)
  const words = useMemo(() => {
    return (text || "").split(/[\s\n]+/).filter((s) => s.length > 0);
  }, [text]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [wpm, setWpm] = useState(300);

  const timerRef = useRef(null);

  // Reset when new text is loaded
  useEffect(() => {
    setCurrentIndex(0);
    setIsPlaying(false);
  }, [text]);

  // 2. RSVP Engine (Recursive setTimeout for better precision)
  useEffect(() => {
    if (!isPlaying) return;

    if (currentIndex >= words.length - 1) {
      setIsPlaying(false);
      return;
    }

    const msPerWord = 60000 / wpm;

    timerRef.current = setTimeout(() => {
      setCurrentIndex((prev) => {
        if (prev >= words.length - 1) return prev;
        return prev + 1;
      });
    }, msPerWord);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, currentIndex, wpm, words.length]);

  // 3. Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === "Space") {
        e.preventDefault();
        setIsPlaying((p) => !p);
      }
      if (e.code === "Escape") onClose?.();
      // Step backward/forward manually
      if (e.code === "ArrowLeft") setCurrentIndex((i) => clamp(i - 1, 0, words.length - 1));
      if (e.code === "ArrowRight") setCurrentIndex((i) => clamp(i + 1, 0, words.length - 1));
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose, words.length]);

  const progressPct = words.length ? (currentIndex / words.length) * 100 : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-xl animate-in fade-in duration-200">
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-8 right-8 text-slate-500 hover:text-white transition-colors bg-white/5 p-2 rounded-full hover:bg-white/10"
      >
        <X size={24} />
      </button>

      <div className="w-full max-w-3xl px-6 flex flex-col items-center">
        
        {/* DISPLAY AREA */}
        <div className="w-full h-80 flex items-center justify-center mb-12 relative">
          {/* Optical Alignment Guides (Reticle) */}
          <div className="absolute top-4 bottom-4 left-1/2 w-0.5 bg-rose-500/30 -translate-x-1/2 rounded-full" />
          <div className="absolute left-4 right-4 top-1/2 h-0.5 bg-rose-500/30 -translate-y-1/2 rounded-full" />

          <h1 className="text-7xl md:text-9xl font-black text-white tracking-tight text-center select-none drop-shadow-2xl">
            {words[currentIndex] || "Ready"}
          </h1>
        </div>

        {/* CONTROLS UI */}
        <div className="bg-[#1E1E2E] p-8 rounded-3xl border border-white/10 shadow-2xl w-full max-w-xl">
          
          {/* Progress Scrubber */}
          <div
            className="w-full bg-slate-800 h-3 rounded-full overflow-hidden mb-8 cursor-pointer group"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const ratio = (e.clientX - rect.left) / rect.width;
              setCurrentIndex(clamp(Math.floor(ratio * words.length), 0, Math.max(words.length - 1, 0)));
            }}
          >
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-full transition-all duration-100 ease-linear group-hover:brightness-110"
              style={{ width: `${progressPct}%` }}
            />
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            {/* Stats */}
            <div className="text-slate-400 text-xs font-bold uppercase tracking-wider w-32 text-center md:text-left">
              {words.length ? currentIndex + 1 : 0} / {words.length}
              <br />
              <span className="text-slate-600">Words</span>
            </div>

            {/* Play/Pause Buttons */}
            <div className="flex items-center gap-6">
              <button
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentIndex(0);
                }}
                className="text-slate-500 hover:text-white transition-colors p-2"
                title="Reset"
              >
                <RotateCcw size={20} />
              </button>

              <button
                onClick={() => setIsPlaying((p) => !p)}
                className="w-16 h-16 bg-white text-black rounded-full flex items-center justify-center hover:scale-105 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={words.length === 0}
                title="Play/Pause"
              >
                {isPlaying ? (
                  <Pause size={28} fill="currentColor" />
                ) : (
                  <Play size={28} fill="currentColor" className="ml-1" />
                )}
              </button>
            </div>

            {/* Speed Control */}
            <div className="flex items-center gap-3 w-44 justify-end">
              <div className="flex-1 flex flex-col items-end">
                <span className="text-white font-bold text-lg leading-none">{wpm}</span>
                <span className="text-[10px] text-slate-500 font-bold uppercase">WPM</span>
              </div>
              <div className="h-8 w-[2px] bg-white/10 mx-2" />
              <Zap size={20} className="text-yellow-400" />

              <input
                type="range"
                min="200"
                max="1000"
                step="50"
                value={wpm}
                onChange={(e) => setWpm(Number(e.target.value))}
                className="w-24 accent-white h-1 bg-slate-700 rounded-lg cursor-pointer"
                title="Adjust speed"
              />
            </div>
          </div>
        </div>

        <p className="mt-8 text-slate-600 text-xs font-medium uppercase tracking-widest">
          Space = Play/Pause • Esc = Close • ←/→ = Step
        </p>
      </div>
    </div>
  );
};

export default SpeedReader;