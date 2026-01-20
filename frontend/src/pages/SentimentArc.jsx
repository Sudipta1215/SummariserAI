import React, { useState, useEffect } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from "recharts";
import { Activity, BookOpen, TrendingUp, Loader2, AlertCircle, Sparkles } from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ✅ IMPROVED TOOLTIP: Wider and clearer for reading story text
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div className="bg-[#1E1E2E]/95 backdrop-blur-md p-5 border border-white/10 rounded-2xl shadow-2xl z-50 max-w-sm">
        <div className="flex justify-between items-center mb-2">
          <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">{d.progress}% Complete</span>
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            d.sentiment > 0 ? "bg-emerald-500/20 text-emerald-400" : 
            d.sentiment < 0 ? "bg-rose-500/20 text-rose-400" : "bg-slate-500/20 text-slate-400"
          }`}>
            {d.label} ({d.sentiment})
          </span>
        </div>
        
        {/* The Story Snippet */}
        <p className="text-sm text-slate-200 leading-relaxed font-serif italic border-l-2 border-indigo-500 pl-3">
          {d.snippet}
        </p>
      </div>
    );
  }
  return null;
};

const SentimentArc = () => {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState("");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 1. Fetch User Books
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setError("");
        const res = await fetch(`${API_URL}/books/`, { headers: getAuthHeaders() });
        if (res.status === 401) throw new Error("Unauthorized. Please login again.");
        if (!res.ok) throw new Error("Failed to fetch books");
        const json = await res.json();
        setBooks(json);
        if (json.length > 0) setSelectedBookId(String(json[0].book_id));
      } catch (e) { setError(e.message); }
    };
    fetchBooks();
  }, []);

  // 2. Fetch Analysis
  const handleAnalyze = async () => {
    if (!selectedBookId) return;
    setLoading(true);
    setError("");
    setData([]);

    try {
      const res = await fetch(`${API_URL}/analytics/arc/${selectedBookId}`, {
        headers: getAuthHeaders(),
      });
      if (res.status === 401) throw new Error("Session expired. Login again.");
      if (!res.ok) throw new Error("Agent failed to analyze this document.");

      const json = await res.json();
      const arc = Array.isArray(json.data) ? json.data : [];
      setData(arc);

      if (arc.length === 0) setError("No data points found. Ensure the book has extracted text.");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">
      {/* Header */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-pink-500/20 rounded-lg text-pink-400"><Activity size={24} /></div>
          <div>
            <h1 className="text-xl font-bold text-white">Sentiment Arc</h1>
            <p className="text-xs text-slate-400">Agent-powered emotional journey mapping</p>
          </div>
        </div>
      </div>

      <div className="p-8 flex-1 overflow-y-auto">
        {/* Controls */}
        <div className="max-w-4xl mx-auto mb-8 flex flex-col sm:flex-row gap-4 bg-[#1E1E2E] p-6 rounded-3xl border border-white/5">
          <div className="flex-1">
            <label className="text-xs font-bold text-slate-500 uppercase ml-1 tracking-widest">Select Source</label>
            <div className="relative mt-2">
              <BookOpen className="absolute left-4 top-3.5 text-slate-500" size={18} />
              <select
                value={selectedBookId}
                onChange={(e) => setSelectedBookId(e.target.value)}
                className="w-full bg-[#161622] text-white pl-12 pr-10 py-3 rounded-xl border border-white/10 outline-none focus:border-pink-500 transition-all appearance-none cursor-pointer"
              >
                {books.map((b) => (
                  <option key={b.book_id} value={String(b.book_id)}>{b.title}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedBookId}
              className="h-[50px] w-full sm:w-auto bg-gradient-to-r from-pink-600 to-rose-600 px-8 rounded-xl font-bold hover:shadow-lg hover:shadow-rose-500/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Sparkles size={20} />} 
              {loading ? "Agent Analyzing..." : "Run Analysis"}
            </button>
          </div>
        </div>

        {error && (
          <div className="max-w-4xl mx-auto mb-6 p-4 rounded-xl border border-rose-500/20 bg-rose-500/10 text-rose-200 flex items-center gap-2">
            <AlertCircle size={18} /> <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Chart */}
        <div className="max-w-5xl mx-auto">
          {data.length > 0 ? (
            <div className="bg-[#1E1E2E] p-8 rounded-4xl border border-white/5 shadow-2xl h-[500px]">
              <div className="flex justify-between items-center mb-8">
                 <h3 className="font-bold text-lg flex items-center gap-2 uppercase tracking-tighter">
                   <TrendingUp size={18} className="text-pink-400" /> Narrative Trajectory
                 </h3>
                 <div className="flex gap-4 text-[10px] font-bold uppercase tracking-widest">
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-400"/> Positive</span>
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-rose-400"/> Negative</span>
                 </div>
              </div>
              
              <ResponsiveContainer width="100%" height="80%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ec4899" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="progress" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} unit="%" />
                  <YAxis domain={[-1, 1]} axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                  {/* ✅ THE TOOLTIP IS NOW ENABLED HERE */}
                  <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#ec4899', strokeWidth: 1 }} />
                  <ReferenceLine y={0} stroke="rgba(255,255,255,0.1)" />
                  <Area type="monotone" dataKey="sentiment" stroke="#ec4899" strokeWidth={4} fillOpacity={1} fill="url(#colorSentiment)" animationDuration={2000} />
                </AreaChart>
              </ResponsiveContainer>
              <p className="text-center text-slate-500 text-xs mt-4">Narrative Timeline (Beginning to End)</p>
            </div>
          ) : !loading && (
            <div className="h-[400px] flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-white/5 rounded-4xl">
              <Activity size={48} className="mb-4 opacity-20" />
              <p className="text-lg font-medium">No trajectory mapped yet.</p>
              <p className="text-sm">Select a book and let the Agent plot the emotional peaks.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SentimentArc;