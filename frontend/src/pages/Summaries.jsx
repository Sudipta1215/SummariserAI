import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import {
  FileText, Sparkles, Copy, Check, AlignLeft, List, Loader2,
  BookOpen, AlertTriangle, History, Download, Languages,
  Headphones, Trash2, Play, Zap,
} from "lucide-react";
import SpeedReader from "../components/SpeedReader";

const API_URL = "http://127.0.0.1:8000";

const WORLD_LANGS = {
  "English 🇺🇸": "en", "Spanish 🇪🇸": "es", "French 🇫🇷": "fr", "German 🇩🇪": "de",
  "Italian 🇮🇹": "it", "Portuguese 🇵🇹": "pt", "Russian 🇷🇺": "ru", "Chinese 🇨🇳": "zh-CN",
  "Japanese 🇯🇵": "ja", "Korean 🇰🇷": "ko", "Arabic 🇸🇦": "ar", "Turkish 🇹🇷": "tr"
};

const INDIC_LANGS = {
  "Hindi 🇮🇳": "hi-IN", "Tamil 🇮🇳": "ta-IN", "Telugu 🇮🇳": "te-IN", 
  "Malayalam 🇮🇳": "ml-IN", "Kannada 🇮🇳": "kn-IN", "Marathi 🇮🇳": "mr-IN", 
  "Bengali 🇮🇳": "bn-IN", "Gujarati 🇮🇳": "gu-IN", "Punjabi 🇮🇳": "pa-IN", "Odia 🇮🇳": "od-IN"
};

const Summaries = () => {
  const location = useLocation();
  const pollInterval = useRef(null);

  // State
  const [activeTab, setActiveTab] = useState("generate");
  const [showSpeedReader, setShowSpeedReader] = useState(false);
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(location.state?.selectedBookId || "");
  const [history, setHistory] = useState([]); // List of old summaries
  const [length, setLength] = useState("medium");
  const [format, setFormat] = useState("paragraph");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [error, setError] = useState("");

  // Compare States
  const [compareIdx1, setCompareIdx1] = useState(0);
  const [compareIdx2, setCompareIdx2] = useState(1);

  // Translation & Audio
  const [translatedText, setTranslatedText] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [transLoading, setTransLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [transEngine, setTransEngine] = useState("world");
  const [selectedLang, setSelectedLang] = useState("en");
  const [audioEngine, setAudioEngine] = useState("world");

  // 1. Fetch Books
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_URL}/books/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok) {
          const data = await res.json();
          setBooks(data);
          if (!selectedBookId && data.length > 0) setSelectedBookId(String(data[0].book_id));
        }
      } catch (err) { console.error("Failed to fetch books", err); }
    };
    fetchBooks();
    return () => { if (pollInterval.current) clearInterval(pollInterval.current); };
  }, []);

  // 2. Fetch History when Tab changes or Book changes
  useEffect(() => {
    if (activeTab === "history" || activeTab === "compare") {
      fetchHistory();
    }
  }, [activeTab, selectedBookId]);

  const fetchHistory = async () => {
    if (!selectedBookId) return;
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/summary/history/${selectedBookId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) { console.error("History fetch error", err); }
  };

  const startPolling = (bookId) => {
    if (pollInterval.current) clearInterval(pollInterval.current);
    pollInterval.current = setInterval(async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_URL}/summary/${bookId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const data = await res.json();
        if (data.status === "completed" && data.summary_text) {
          setSummary(data.summary_text);
          setLoading(false);
          setStatusMsg("Success!");
          clearInterval(pollInterval.current);
          fetchHistory(); // Refresh history after new generation
        } else {
          setStatusMsg("Agent is analyzing your document...");
        }
      } catch (err) { console.error("Polling error:", err); }
    }, 3000);
  };

  const handleGenerate = async () => {
    if (!selectedBookId) return;
    setLoading(true); setSummary(""); setTranslatedText(""); setAudioUrl(null); setError(""); setStatusMsg("Initializing...");
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/summary/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ 
          book_id: parseInt(selectedBookId, 10), 
          summary_length: length, 
          summary_format: format 
        }),
      });
      if (res.ok) {
        setStatusMsg("Agent is distilling content...");
        startPolling(selectedBookId);
      } else {
        setLoading(false);
        setError("Agent failed to start distillation.");
      }
    } catch (e) { setError("Connection failed."); setLoading(false); }
  };

  const handleTranslate = async () => {
    if (!summary) return;
    setTransLoading(true);
    setTranslatedText("");
    try {
      const token = localStorage.getItem("token");
      const endpoint = transEngine === "world" ? "/translate/translate" : "/translate/sarvam";
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ 
            text: summary, 
            target_lang: selectedLang,
            target_language_code: selectedLang 
        }),
      });
      const data = await res.json();
      if (res.ok) { setTranslatedText(data.translated_text); }
      else { alert(`Agent Error: ${data.detail || "Translation failed"}`); }
    } catch (e) { console.error("Translation Error", e); }
    finally { setTransLoading(false); }
  };

  const handleAudio = async () => {
    const textToSpeak = translatedText || summary;
    if (!textToSpeak) return;
    setAudioLoading(true);
    try {
      const token = localStorage.getItem("token");
      const endpoint = audioEngine === "indic" ? "/translate/sarvam/tts" : "/audio/generate";
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ 
          text: textToSpeak.substring(0, 2000), 
          lang: selectedLang, 
          target_lang: selectedLang,
          target_language_code: selectedLang 
        }),
      });
      if (res.ok) {
        const blob = await res.blob();
        setAudioUrl(URL.createObjectURL(blob));
      } else { alert("Agent failed to generate audio."); }
    } catch (e) { console.error("Audio Error", e); }
    finally { setAudioLoading(false); }
  };

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">
      {/* HEADER */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/20 rounded-lg text-emerald-400"><FileText size={24} /></div>
          <div>
            <h1 className="text-xl font-bold text-white">AI Summarizer</h1>
            <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Agent-powered</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 flex flex-col lg:flex-row gap-8">
        {/* LEFT PANEL */}
        <div className="w-full lg:w-1/3 space-y-6">
          <div className="bg-[#1E1E2E] rounded-3xl p-6 border border-white/5 shadow-2xl">
            <div className="flex p-1 bg-[#161622] rounded-xl mb-6">
              {['generate', 'history', 'compare'].map(tab => (
                <button 
                  key={tab} 
                  onClick={() => setActiveTab(tab)} 
                  className={`flex-1 py-2 text-xs font-bold uppercase rounded-lg transition-all ${activeTab === tab ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeTab === 'generate' && (
              <>
                <div className="mb-6">
                  <label className="text-xs font-bold text-slate-500 uppercase ml-1 tracking-widest">Target Source</label>
                  <select value={selectedBookId} onChange={(e) => setSelectedBookId(e.target.value)} className="w-full mt-2 bg-[#161622] text-white p-4 rounded-2xl border border-white/10 outline-none">
                    {books.map(b => <option key={b.book_id} value={b.book_id}>{b.title}</option>)}
                  </select>
                </div>

                <div className="mb-6">
                  <label className="text-xs font-bold text-slate-500 uppercase ml-1 tracking-widest">Distillation Length</label>
                  <div className="grid grid-cols-3 gap-2 mt-2">
                    {['short', 'medium', 'long'].map(l => (
                      <button key={l} onClick={() => setLength(l)} className={`py-2 rounded-lg text-xs font-black uppercase border transition-all ${length === l ? 'bg-[#A78BFA] text-white border-[#A78BFA]' : 'bg-[#161622] text-slate-400 border-white/5'}`}>{l}</button>
                    ))}
                  </div>
                </div>

                <div className="mb-8">
                  <label className="text-xs font-bold text-slate-500 uppercase ml-1 tracking-widest">Output Format</label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <button onClick={() => setFormat('paragraph')} className={`py-3 rounded-xl text-sm flex items-center justify-center gap-2 border transition-all ${format === 'paragraph' ? 'bg-blue-600 border-blue-500' : 'bg-[#161622] border-white/5'}`}><AlignLeft size={16}/> Paragraph</button>
                    <button onClick={() => setFormat('bullet')} className={`py-3 rounded-xl text-sm flex items-center justify-center gap-2 border transition-all ${format === 'bullet' ? 'bg-blue-600 border-blue-500' : 'bg-[#161622] border-white/5'}`}><List size={16}/> Bullets</button>
                  </div>
                </div>

                <button onClick={handleGenerate} disabled={loading || !selectedBookId} className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-2 disabled:opacity-50 transition-all">
                  {loading ? <Loader2 className="animate-spin" /> : <Sparkles size={20} />} 
                  {loading ? "Agent Distilling..." : "Generate with Agent"}
                </button>
              </>
            )}

            {activeTab === 'compare' && (
              <div className="space-y-4">
                <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">Select Versions to Compare</p>
                <div>
                  <label className="text-[10px] text-slate-500 font-bold uppercase">Version A (Newer)</label>
                  <select value={compareIdx1} onChange={(e) => setCompareIdx1(parseInt(e.target.value))} className="w-full mt-1 bg-[#161622] text-white p-3 rounded-xl border border-white/10">
                    {history.map((h, i) => <option key={i} value={i}>Version {history.length - i} ({new Date(h.created_at).toLocaleDateString()})</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 font-bold uppercase">Version B (Older)</label>
                  <select value={compareIdx2} onChange={(e) => setCompareIdx2(parseInt(e.target.value))} className="w-full mt-1 bg-[#161622] text-white p-3 rounded-xl border border-white/10">
                    {history.map((h, i) => <option key={i} value={i}>Version {history.length - i} ({new Date(h.created_at).toLocaleDateString()})</option>)}
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="flex-1 flex flex-col gap-6">
          <div className="bg-[#1E1E2E] rounded-3xl border border-white/5 shadow-2xl flex flex-col min-h-[500px] relative overflow-hidden">
            <div className="h-14 border-b border-white/5 flex items-center justify-between px-6 bg-[#161622]/50">
               <div className="flex gap-4">
                 {activeTab === 'generate' && summary && (
                   <button onClick={() => setShowSpeedReader(true)} className="text-yellow-400 flex items-center gap-1.5 text-[10px] font-black uppercase bg-yellow-400/10 px-3 py-1.5 rounded-lg border border-yellow-400/20 tracking-tighter">
                     <Zap size={14} fill="currentColor"/> Speed Read
                   </button>
                 )}
               </div>
               <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                  {activeTab} Mode
               </div>
            </div>

            <div className="flex-1 p-8 overflow-y-auto">
              {loading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
                  <Loader2 className="animate-spin text-emerald-500" size={48} />
                  <p className="animate-pulse text-emerald-400 font-medium">{statusMsg}</p>
                </div>
              ) : activeTab === 'generate' ? (
                /* GENERATE VIEW */
                <div className="space-y-8">
                  <div className="prose prose-invert max-w-none text-slate-300 leading-relaxed whitespace-pre-wrap text-lg">{summary || "Your distillation will appear here."}</div>
                  {translatedText && (
                    <div className="p-6 bg-[#161622] rounded-3xl border border-purple-500/20 shadow-inner">
                       <h4 className="text-[10px] font-black text-purple-400 mb-3 uppercase flex items-center gap-2 tracking-widest"><Languages size={14}/> Translated Summary ({selectedLang})</h4>
                       <p className="text-slate-300 text-sm whitespace-pre-wrap italic leading-relaxed">{translatedText}</p>
                    </div>
                  )}
                  {audioUrl && (
                    <div className="p-4 bg-[#161622] rounded-2xl flex items-center gap-4 border border-emerald-500/10">
                       <div className="p-3 bg-emerald-500/20 rounded-full text-emerald-400"><Headphones size={20} /></div>
                       <audio controls src={audioUrl} className="w-full h-8" />
                    </div>
                  )}
                </div>
              ) : activeTab === 'history' ? (
                /* HISTORY VIEW */
                <div className="space-y-4">
                  {history.length > 0 ? history.map((item, idx) => (
                    <div key={idx} className="p-6 bg-[#161622] rounded-3xl border border-white/5">
                      <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                        <span className="text-xs font-bold text-blue-400 uppercase">Version {history.length - idx}</span>
                        <span className="text-[10px] text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">{item.summary_text}</p>
                    </div>
                  )) : <p className="text-center text-slate-600 mt-20">No history found for this source.</p>}
                </div>
              ) : (
                /* COMPARE VIEW */
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
                  <div className="p-6 bg-[#161622] rounded-3xl border border-blue-500/20 overflow-y-auto">
                    <h4 className="text-xs font-black text-blue-400 uppercase mb-4 sticky top-0 bg-[#161622] py-2">Version A</h4>
                    <p className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
                      {history[compareIdx1]?.summary_text || "Select version A"}
                    </p>
                  </div>
                  <div className="p-6 bg-[#161622] rounded-3xl border border-purple-500/20 overflow-y-auto">
                    <h4 className="text-xs font-black text-purple-400 uppercase mb-4 sticky top-0 bg-[#161622] py-2">Version B</h4>
                    <p className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
                      {history[compareIdx2]?.summary_text || "Select version B"}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* ✅ FIXED ACTION FOOTER (Responsive Flex-Wrap) */}
            {activeTab === 'generate' && summary && (
              <div className="p-4 bg-[#161622] border-t border-white/5 grid grid-cols-1 xl:grid-cols-2 gap-4">
                
                {/* 1. Translate Controls */}
                <div className="flex flex-wrap items-center gap-2">
                  <select className="bg-[#1E1E2E] text-slate-300 text-xs p-3 rounded-xl border border-white/10 outline-none flex-shrink-0" 
                    onChange={e => {
                        setTransEngine(e.target.value);
                        setSelectedLang(e.target.value === 'world' ? 'en' : 'hi-IN');
                    }}>
                    <option value="world">Global Engine</option>
                    <option value="indic">Indic (Sarvam)</option>
                  </select>
                  
                  <select value={selectedLang} className="bg-[#1E1E2E] text-slate-300 text-xs p-3 rounded-xl border border-white/10 outline-none flex-grow min-w-[100px]" onChange={e => setSelectedLang(e.target.value)}>
                    {Object.entries(transEngine === 'world' ? WORLD_LANGS : INDIC_LANGS).map(([name, code]) => (
                      <option key={code} value={code}>{name}</option>
                    ))}
                  </select>
                  
                  <button onClick={handleTranslate} disabled={transLoading} className="p-3 bg-blue-600 rounded-xl text-white hover:bg-blue-500 disabled:opacity-50 transition-all shadow-lg shadow-blue-600/20 flex-shrink-0">
                    {transLoading ? <Loader2 size={18} className="animate-spin"/> : <Languages size={18} />}
                  </button>
                </div>

                {/* 2. Audio Controls */}
                <div className="flex flex-wrap items-center gap-2">
                  <select className="bg-[#1E1E2E] text-slate-300 text-xs p-3 rounded-xl border border-white/10 outline-none flex-grow" onChange={e => setAudioEngine(e.target.value)}>
                    <option value="world">Standard Voice</option>
                    <option value="indic">Indic Voice</option>
                  </select>
                  <button onClick={handleAudio} disabled={audioLoading} className="py-3 px-6 bg-purple-600 rounded-xl text-white text-xs font-black uppercase hover:bg-purple-500 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-purple-600/20 transition-all flex-shrink-0">
                    {audioLoading ? <Loader2 size={16} className="animate-spin"/> : <Play size={16} />} Audio Cast
                  </button>
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
      {showSpeedReader && <SpeedReader text={summary} onClose={() => setShowSpeedReader(false)} />}
    </div>
  );
};

export default Summaries;