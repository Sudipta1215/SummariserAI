import React, { useState } from "react";
import {
  LayoutDashboard,
  UploadCloud,
  BookOpen,
  FileText,
  Share2,
  MessageSquare,
  Settings,
  LogOut,
  ThumbsUp,
  Activity,
  Bell,
  Search,
  PieChart as PieIcon,
} from "lucide-react";

import {
  LineChart,
  Line,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";

/* --- REUSABLE COMPONENTS --- */

const Card = ({ children, className = "" }) => (
  <div
    className={`bg-[#1E1E2E] rounded-3xl p-6 border border-white/5 shadow-xl backdrop-blur-sm ${className}`}
  >
    {children}
  </div>
);

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group
      ${
        active
          ? "bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white shadow-lg shadow-purple-500/20"
          : "text-slate-400 hover:bg-white/5 hover:text-white"
      }`}
  >
    <Icon
      size={20}
      className={`${active ? "text-white" : "text-slate-400 group-hover:text-white"}`}
    />
    <span className="font-medium">{label}</span>
    {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white shadow-glow" />}
  </button>
);

const StatBadge = ({ icon: Icon, value, label, color }) => (
  <div className="flex flex-col items-center justify-center p-5 rounded-2xl w-full bg-[#252636] border border-white/5">
    <Icon size={24} style={{ color }} className="mb-2 opacity-90" />
    <span className="text-3xl font-bold text-white mb-1">{value}</span>
    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
      {label}
    </span>
  </div>
);

/* --- SUB PAGES --- */

const Dashboard = () => {
  const trendData = [
    { id: 1, val: 2 },
    { id: 2, val: 2.2 },
    { id: 3, val: 1.8 },
    { id: 4, val: 3.5 },
    { id: 5, val: 4.8 },
    { id: 6, val: 4.2 },
    { id: 7, val: 2.5 },
    { id: 8, val: 3.0 },
    { id: 9, val: 3.8 },
    { id: 10, val: 2.2 },
    { id: 11, val: 2.5 },
  ];

  const distributionData = [
    { name: "Neutral", value: 64, color: "#6366F1" },
    { name: "Positive", value: 36, color: "#4ADE80" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
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
                <span className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
                  Positive
                </span>
                <span className="text-slate-400 font-medium text-lg">• 1.09 Score</span>
              </div>
            </div>
          </div>

          <div className="hidden md:block text-right">
            <p className="text-slate-400 text-sm mb-1">Confidence Score</p>
            <p className="text-2xl font-bold text-white">94%</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatBadge icon={Activity} value="4" label="Positive" color="#4ADE80" />
        <StatBadge icon={MessageSquare} value="7" label="Neutral" color="#6366F1" />
        <StatBadge icon={Activity} value="0" label="Negative" color="#F43F5E" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={20} className="text-[#A78BFA]" />
            <h3 className="text-lg font-semibold text-white">Conversation Trend</h3>
          </div>

          <Card className="h-80 bg-[#1A1A27]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <defs>
                  <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#A78BFA" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#A78BFA" stopOpacity={0} />
                  </linearGradient>
                </defs>

                <Line
                  type="monotone"
                  dataKey="val"
                  stroke="#A78BFA"
                  strokeWidth={4}
                  dot={{ r: 4, fill: "#1E1E2E", stroke: "#A78BFA", strokeWidth: 2 }}
                  activeDot={{ r: 8, fill: "#A78BFA" }}
                />
                <YAxis hide domain={[0, 6]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    borderColor: "#374151",
                    borderRadius: "12px",
                    color: "#fff",
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-4">
            <PieIcon size={20} className="text-[#A78BFA]" />
            <h3 className="text-lg font-semibold text-white">Distribution</h3>
          </div>

          <Card className="h-80 flex flex-col items-center justify-center bg-[#1A1A27]">
            <div className="w-full h-48 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distributionData}
                    innerRadius={60}
                    outerRadius={80}
                    startAngle={90}
                    endAngle={-270}
                    dataKey="value"
                    stroke="none"
                    paddingAngle={5}
                  >
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>

              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-3xl font-bold text-white">100%</span>
                <span className="text-xs text-slate-500">Total</span>
              </div>
            </div>

            <div className="flex w-full justify-around mt-4 px-4">
              {distributionData.map((item) => (
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

export default function MainLayout() {
  const [activePage, setActivePage] = useState("dashboard");

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "upload", label: "Upload Book", icon: UploadCloud },
    { id: "library", label: "My Library", icon: BookOpen },
    { id: "summaries", label: "Summaries", icon: FileText },
    { id: "graph", label: "Knowledge Graph", icon: Share2 },
    { id: "chat", label: "Agent Chat", icon: MessageSquare },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-[#0F1016] text-slate-200 font-sans flex overflow-hidden selection:bg-purple-500/30">
      {/* SIDEBAR */}
      <aside className="w-72 bg-[#161622] border-r border-white/5 flex flex-col hidden md:flex">
        <div className="p-8 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
              <BookOpen className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              BookAI
            </h1>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Main Menu
          </p>
          {navItems.map((item) => (
            <SidebarItem
              key={item.id}
              icon={item.icon}
              label={item.label}
              active={activePage === item.id}
              onClick={() => setActivePage(item.id)}
            />
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="bg-[#1E1E2E] p-3 rounded-2xl flex items-center gap-3 hover:bg-white/5 transition-colors cursor-pointer border border-white/5">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-white font-bold">
              JD
            </div>
            <div className="flex-1 overflow-hidden">
              <h4 className="text-sm font-bold text-white truncate">John Doe</h4>
              <p className="text-xs text-slate-400 truncate">Pro Plan</p>
            </div>
            <LogOut size={18} className="text-slate-500 hover:text-rose-400 transition-colors" />
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/80 backdrop-blur-md sticky top-0 z-50">
          <h2 className="text-xl font-bold text-white capitalize">
            {activePage.replace("-", " ")}
          </h2>

          <div className="flex items-center gap-4">
            <div className="relative hidden md:block">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                size={18}
              />
              <input
                type="text"
                placeholder="Search books..."
                className="bg-[#1E1E2E] border border-white/5 rounded-full pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-purple-500/50 w-64 transition-all"
              />
            </div>

            <button className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-full transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border border-[#0F1016]" />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 relative">
          <div className="absolute top-0 left-0 w-full h-96 bg-purple-500/5 rounded-full blur-[120px] pointer-events-none" />

          {activePage === "dashboard" && <Dashboard />}

          {activePage !== "dashboard" && (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <div className="w-20 h-20 bg-[#1E1E2E] rounded-full flex items-center justify-center mb-4 border border-white/5">
                <Settings size={32} className="opacity-50" />
              </div>
              <h3 className="text-xl font-medium text-white">Work in Progress</h3>
              <p>The {activePage} page is currently under development.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
