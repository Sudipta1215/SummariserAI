import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, CheckCircle2, HardDrive, Clock, 
  Type, Globe, UploadCloud, Activity,
  Sparkles, Loader2, History, AlertCircle
} from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

const Dashboard = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [latestStats, setLatestStats] = useState({
    sentence_count: "—",
    reading_time_minutes: "—",
    language: "unknown"
  });
  
  const user = JSON.parse(localStorage.getItem("user_info") || '{"name": "User"}');
  const token = localStorage.getItem("token");

  // ------------------------------------------------------
  // 1. TIME FORMATTER (Equivalent to get_relative_time)
  // ------------------------------------------------------
  const getRelativeTime = (dateStr) => {
    if (!dateStr) return "Unknown";
    try {
      const dt = new Date(dateStr.replace("Z", ""));
      const now = new Date();
      const diffInSeconds = Math.floor((now - dt) / 1000);

      if (diffInSeconds < 60) return "Just now";
      
      const diffInMinutes = Math.floor(diffInSeconds / 60);
      if (diffInMinutes < 60) return `${diffInMinutes} mins ago`;
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) return `${diffInHours} hours ago`;
      
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} days ago`;
    } catch { return "Unknown"; }
  };

  // ------------------------------------------------------
  // 2. FETCH DATA & STATS
  // ------------------------------------------------------
  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        setLoading(false);
        setError("You are not logged in.");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/books/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          setBooks(data); 
          
          // Fetch text statistics for the latest book (books[-1] equivalent)
          if (data.length > 0) {
            const latestBook = data[data.length - 1]; 
            const statsRes = await fetch(`${API_URL}/books/${latestBook.book_id}/stats`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (statsRes.ok) {
              const sData = await statsRes.json();
              setLatestStats(sData);
            }
          }
        } else if (res.status === 401) {
          navigate("/login");
        } else {
          setError("Unable to connect to the backend server.");
        }
      } catch (err) {
        setError("Unable to connect to the backend server.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, navigate]);

  // ------------------------------------------------------
  // 3. CALCULATE STATS (Equivalent to calculate_stats)
  // ------------------------------------------------------
  const totalChars = books.reduce((acc, b) => acc + (b.char_count || 0), 0);
  const storageMB = (totalChars / (1024 * 1024)).toFixed(2);
  const processedCount = books.filter(b => b.status === 'text_extracted' || b.status === 'completed').length;

  if (loading) return (
    <div className="h-full flex flex-col items-center justify-center bg-white dark:bg-[#0F1016] min-h-screen">
       <Loader2 size={40} className="animate-spin text-blue-500 mb-4" />
       <p className="text-slate-500 font-medium">Loading your dashboard...</p>
    </div>
  );

  // ------------------------------------------------------
  // 4. EMPTY STATE (Equivalent to Streamlit Hero Section)
  // ------------------------------------------------------
  if (books.length === 0) {
    return (
      <div className="p-8 space-y-8 bg-white dark:bg-[#0F1016] min-h-screen text-slate-900 dark:text-white">
        <h1 className="text-4xl font-bold">Welcome back, {user.name}!</h1>
        <div className="bg-slate-100 dark:bg-[#1E1E2E] p-12 rounded-4xl border border-slate-200 dark:border-white/5 text-center">
            <UploadCloud size={80} className="mx-auto text-blue-400 mb-6" />
            <h2 className="text-3xl font-bold mb-4">You're new here — let’s get started!</h2>
            <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-lg mx-auto text-lg">
                Upload your first book to generate AI summaries instantly and explore deeper insights.
                <br /><span className="text-sm font-semibold text-blue-500 mt-2 block">Supported Formats: PDF, DOCX, TXT</span>
            </p>
            <button 
                onClick={() => navigate('/upload')}
                className="bg-blue-600 hover:bg-blue-500 text-white px-12 py-4 rounded-2xl font-bold text-lg shadow-lg shadow-blue-500/30 transition-all"
            >
                Upload Your First Book
            </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6 bg-white dark:bg-[#0F1016] min-h-screen text-slate-900 dark:text-white">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">Welcome back, {user.name}!</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">Your personalized AI summarization dashboard.</p>
        </div>
        {error && (
          <div className="flex items-center gap-2 text-rose-500 bg-rose-50 dark:bg-rose-500/10 px-4 py-2 rounded-xl border border-rose-200 dark:border-rose-500/20">
            <AlertCircle size={18} />
            <span className="text-sm font-medium">{error}</span>
          </div>
        )}
      </div>

      {/* QUICK STATS ROW */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard icon={BookOpen} label="Total Books" value={books.length} color="text-blue-400" />
        <StatCard icon={CheckCircle2} label="Processed & Ready" value={processedCount} color="text-emerald-400" />
        <StatCard icon={HardDrive} label="Storage Used" value={`${storageMB} MB`} color="text-purple-400" />
      </div>

      {/* LATEST BOOK TEXT ANALYSIS (Equivalent to Streamlit m4, m5, m6) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard icon={Type} label="Sentences" value={latestStats.sentence_count} color="text-pink-400" />
        <StatCard icon={Clock} label="Reading Time" value={`${latestStats.reading_time_minutes} mins`} color="text-amber-400" />
        <StatCard icon={Globe} label="Language" value={latestStats.language} color="text-indigo-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-4">
        
        {/* RECENT ACTIVITY FEED (Left Column) */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-bold text-xl flex items-center gap-2 text-slate-900 dark:text-white"><History size={20} /> Recent Activity Feed</h3>
          <div className="bg-slate-50 dark:bg-[#1E1E2E] rounded-3xl border border-slate-200 dark:border-white/5 divide-y divide-slate-200 dark:divide-white/5">
            {/* sorted(books, key=lambda x: x.get("book_id", 0), reverse=True)[:5] equivalent */}
            {books.slice().sort((a, b) => b.book_id - a.book_id).slice(0, 5).map(book => {
              let message = `Processing ${book.title}`;
              if (book.status === 'completed') message = `Summary generated for ${book.title}`;
              else if (book.status === 'text_extracted') message = `Uploaded ${book.title}`;

              return (
                <div key={book.book_id} className="p-6 flex items-center justify-between hover:bg-slate-100 dark:hover:bg-white/5 transition-colors">
                  <div>
                    <p className="font-bold text-slate-900 dark:text-white">{message}</p>
                    <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest">{book.status.replace('_', ' ')}</p>
                  </div>
                  <span className="text-xs text-slate-400 font-medium">
                    {getRelativeTime(book.uploaded_at || book.created_at)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* QUICK ACTIONS & TIPS (Right Column) */}
        <div className="space-y-6">
          <div className="bg-slate-50 dark:bg-[#1E1E2E] p-8 rounded-3xl border border-slate-200 dark:border-white/5 space-y-4">
            <h3 className="font-bold text-xl mb-4 text-slate-900 dark:text-white">Quick Actions</h3>
            <button onClick={() => navigate('/upload')} className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-2xl font-bold flex items-center justify-center gap-2 shadow-md">
                <UploadCloud size={20} /> Upload New Book
            </button>
            <button onClick={() => navigate('/library')} className="w-full bg-white dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 text-slate-900 dark:text-white py-4 rounded-2xl font-bold border border-slate-200 dark:border-white/10 transition-all">
                View My Library
            </button>

            <div className="pt-6">
              <div className="bg-amber-50 dark:bg-amber-500/5 p-4 rounded-2xl border border-amber-200 dark:border-amber-500/20">
                <h4 className="font-bold text-amber-600 dark:text-amber-500 flex items-center gap-2 mb-2">
                  <Sparkles size={16}/> Daily Tips
                </h4>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Visit the <strong>Help</strong> section anytime for detailed guidance on maximizing AI insights!
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

/* --- REUSABLE SUBCOMPONENT --- */
const StatCard = ({ icon: Icon, label, value, color }) => (
  <div className="bg-white dark:bg-[#1E1E2E] p-6 rounded-3xl border border-slate-200 dark:border-white/5 group hover:translate-y-[-4px] transition-all shadow-sm">
    <div className={`w-10 h-10 bg-slate-50 dark:bg-white/5 rounded-xl flex items-center justify-center mb-4`}>
      <Icon className={color} size={20} />
    </div>
    <h3 className="text-3xl font-black text-slate-900 dark:text-white">{value}</h3>
    <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-1">{label}</p>
  </div>
);

export default Dashboard;