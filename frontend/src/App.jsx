import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";
import {
  LayoutDashboard, BookOpen, FileText, Share2, MessageSquare,
  Settings, LogOut, Activity, Bell, Search, BrainCircuit,
  UploadCloud, Palette, ThumbsUp, AlertTriangle, RefreshCw
} from "lucide-react";
import {
  LineChart, Line, YAxis, ResponsiveContainer, Tooltip, PieChart, Pie, Cell
} from "recharts";
import { ThemeProvider } from "./context/ThemeContext";

/* --- PAGE IMPORTS --- */
import AuthPage from "./pages/AuthPage";
import AgentChat from "./pages/AgentChat";
import MyLibrary from "./pages/MyLibrary";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import QuizPage from "./pages/QuizPage";
import SettingsPage from "./pages/Settings";
import Summaries from "./pages/Summaries";
import UploadPage from "./pages/Upload";
import Workspace from "./pages/Workspace";
// REMOVED: import SentimentArc from "./pages/SentimentArc";

/* --- ADMIN IMPORTS --- */
import RoleSelection from "./pages/RoleSelection";
import AdminDashboard from "./pages/AdminDashboard";

const API_URL = "http://127.0.0.1:8000";

/* --- REUSABLE UI COMPONENTS --- */
const Card = ({ children, className = "" }) => (
  <div className={`bg-[#1E1E2E] rounded-3xl p-6 border border-white/5 shadow-xl backdrop-blur-sm ${className}`}>
    {children}
  </div>
);

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group
      ${active 
        ? "bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white shadow-lg shadow-purple-500/20" 
        : "text-slate-400 hover:bg-white/5 hover:text-white"}`}
  >
    <Icon size={20} className={`${active ? "text-white" : "text-slate-400 group-hover:text-white"}`} />
    <span className="font-medium">{label}</span>
    {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white shadow-glow" />}
  </button>
);

const StatBadge = ({ icon: Icon, value, label, color }) => (
  <div className="flex flex-col items-center justify-center p-5 rounded-2xl w-full bg-[#252636] border border-white/5">
    <Icon size={24} style={{ color }} className="mb-2 opacity-90" />
    <span className="text-3xl font-bold text-white mb-1">{value}</span>
    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
  </div>
);

const ProtectedRoute = ({ children, requireAdmin, user }) => {
  const isAdmin = user?.role === "admin";
  if (requireAdmin && !isAdmin) return <Navigate to="/" replace />;
  return children;
};

/* --- DASHBOARD COMPONENT --- */
const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/dashboard/data`)
      .then(async (res) => {
        if (!res.ok) throw new Error("API Connection Failed");
        return res.json();
      })
      .then((realData) => {
        setData(realData);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard Error:", err);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div className="flex flex-col items-center justify-center h-full text-slate-500 animate-pulse">
      <Activity className="text-indigo-500 mb-4" size={40} />
      <p>Connecting to BookAI Brain...</p>
    </div>
  );

  if (error || !data || !data.stats) return (
    <div className="flex flex-col items-center justify-center h-full text-rose-400">
      <div className="p-6 bg-rose-500/10 rounded-full mb-4 border border-rose-500/20 shadow-lg"><AlertTriangle size={48} /></div>
      <h3 className="text-2xl font-bold text-white mb-2">Connection Issue</h3>
      <p className="mb-8 text-center max-w-md text-slate-400">We couldn't fetch the dashboard data.</p>
      <button onClick={() => window.location.reload()} className="flex items-center gap-2 bg-white text-black px-8 py-3 rounded-full font-bold hover:bg-slate-200 transition-colors">
        <RefreshCw size={18} /> Retry Connection
      </button>
    </div>
  );

  const { stats, trend_data, distribution } = data;

  return (
    <div className="space-y-6 animate-fade-in p-8">
      {/* Top Welcome Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#2A2B3D] to-[#1E1E2E] p-8 border border-white/10 shadow-2xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="p-4 bg-emerald-500/10 rounded-2xl border border-emerald-500/20">
              <ThumbsUp className="text-emerald-400" size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">Overall Sentiment</h1>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">Positive</span>
                <span className="text-slate-400 font-medium text-lg">• {stats.positive_score} Score</span>
              </div>
            </div>
          </div>
          <div className="hidden md:block text-right">
            <p className="text-slate-400 text-sm mb-1">Confidence Score</p>
            <p className="text-2xl font-bold text-white">{stats.confidence}%</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatBadge icon={Activity} value={stats.positive_count} label="Positive" color="#4ADE80" />
        <StatBadge icon={MessageSquare} value={stats.neutral_count} label="Neutral" color="#6366F1" />
        <StatBadge icon={Activity} value={stats.negative_count} label="Negative" color="#F43F5E" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={20} className="text-[#A78BFA]" />
            <h3 className="text-lg font-semibold text-white">Conversation Trend</h3>
          </div>
          <Card className="h-80 bg-[#1A1A27]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend_data}>
                <Line type="monotone" dataKey="val" stroke="#A78BFA" strokeWidth={4} dot={{ r: 4, fill: "#1E1E2E" }} />
                <YAxis hide domain={[0, 6]} />
                <Tooltip contentStyle={{ backgroundColor: "#1F2937", borderColor: "#374151", borderRadius: "12px", color: "#fff" }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-4">
            <PieChart size={20} className="text-[#A78BFA]" />
            <h3 className="text-lg font-semibold text-white">Distribution</h3>
          </div>
          <Card className="h-80 flex flex-col items-center justify-center bg-[#1A1A27]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distribution} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="flex w-full justify-around mt-4 px-4">
              {distribution.map((item) => (
                <div key={item.name} className="flex flex-col items-center">
                  <span className="text-xs text-slate-400 mb-1">{item.name}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-lg font-bold text-white">{item.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

/* --- MAIN APP --- */
export default function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const [isAuthenticated, setIsAuthenticated] = useState(() => localStorage.getItem("token") !== null);
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user_info") || "{}"); } catch { return {}; }
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
      try { setUser(JSON.parse(localStorage.getItem("user_info") || "{}")); } catch { setUser({}); }
    } else {
      setIsAuthenticated(false);
    }
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_info");
    setIsAuthenticated(false);
    navigate("/");
  };

  return (
    <ThemeProvider>
      {!isAuthenticated ? (
        <AuthPage />
      ) : (
        <>
          {(() => {
            const path = location.pathname.replace(/\/+$/, ""); 

            // 1. STANDALONE PAGES (No Sidebar)
            if (path === "/role-selection" || path === "/admin-dashboard") {
              return (
                <Routes>
                  <Route 
                    path="/role-selection" 
                    element={<ProtectedRoute requireAdmin={true} user={user}><RoleSelection /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/admin-dashboard" 
                    element={<ProtectedRoute requireAdmin={true} user={user}><AdminDashboard /></ProtectedRoute>} 
                  />
                  <Route path="*" element={<Navigate to="/" />} />
                </Routes>
              );
            }

            // 2. DASHBOARD PAGES (With Sidebar)
            const activePage = location.pathname === "/" ? "dashboard" : location.pathname.substring(1);
            
            return (
              <div className="min-h-screen bg-[#0F1016] text-slate-200 font-sans flex overflow-hidden">
                <aside className="w-72 bg-[#161622] border-r border-white/5 flex flex-col hidden md:flex">
                  <div className="p-8 pb-4">
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">BookAI</h1>
                  </div>
                  <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
                    {[
                      { id: "dashboard", label: "Dashboard", path: "/", icon: LayoutDashboard },
                      { id: "upload", label: "Upload Book", path: "/upload", icon: UploadCloud },
                      { id: "library", label: "My Library", path: "/library", icon: BookOpen },
                      { id: "workspace", label: "Workspace", path: "/workspace", icon: Palette },
                      { id: "summaries", label: "Summarizer", path: "/summaries", icon: FileText },
                      { id: "chat", label: "Agent Chat", path: "/chat", icon: MessageSquare },
                      { id: "graph", label: "Knowledge Graph", path: "/graph", icon: Share2 },
                      // REMOVED: { id: "sentiment", label: "Sentiment Arc", path: "/sentiment", icon: Activity },
                      { id: "quiz", label: "Knowledge Quiz", path: "/quiz", icon: BrainCircuit },
                      { id: "settings", label: "Settings", path: "/settings", icon: Settings },
                    ].map(item => (
                      <SidebarItem key={item.id} icon={item.icon} label={item.label} active={activePage === item.id} onClick={() => navigate(item.path)} />
                    ))}
                  </nav>
                  <div className="p-4 border-t border-white/5">
                    <button onClick={handleLogout} className="w-full bg-[#1E1E2E] p-3 rounded-2xl flex items-center gap-3 hover:bg-rose-500/10 transition-colors">
                      <LogOut size={18} /> Log Out
                    </button>
                  </div>
                </aside>

                <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
                  <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-50">
                    <h2 className="text-xl font-bold text-white capitalize">{activePage}</h2>
                    <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold">
                      {user.name ? user.name.substring(0, 1).toUpperCase() : "U"}
                    </div>
                  </header>

                  <div className="flex-1 overflow-y-auto p-6">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/upload" element={<UploadPage />} />
                      <Route path="/library" element={<MyLibrary />} />
                      <Route path="/workspace" element={<Workspace />} />
                      <Route path="/summaries" element={<Summaries />} />
                      <Route path="/chat" element={<AgentChat />} />
                      <Route path="/graph" element={<KnowledgeGraph />} />
                      {/* REMOVED: <Route path="/sentiment" element={<SentimentArc />} /> */}
                      <Route path="/quiz" element={<QuizPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                      <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                  </div>
                </main>
              </div>
            );
          })()}
        </>
      )}
    </ThemeProvider>
  );
}