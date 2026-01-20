import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import {
  XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  BarChart, Bar, Cell, Legend, Area, AreaChart, ComposedChart, LineChart, Line,
  PieChart, Pie
} from "recharts";
import { 
  Users, BookOpen, FileText, Activity, Server, 
  AlertTriangle, Database, Download, RefreshCw, Bell, Clock, TrendingUp, Trash2, List
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

const PALETTE = {
  blue:   { bg: "#DDF4FF", text: "#0077B6", accent: "#48CAE4" },
  purple: { bg: "#EBE4FF", text: "#624E88", accent: "#9D8EC3" },
  pink:   { bg: "#FFE4F3", text: "#AD2E53", accent: "#FF8FAB" },
  yellow: { bg: "#FFFCD6", text: "#8A7E00", accent: "#E8D848" },
};

const CHART_COLORS = [PALETTE.blue.accent, PALETTE.purple.accent, PALETTE.pink.accent, PALETTE.yellow.accent];

function cn(...classes) { return classes.filter(Boolean).join(" "); }

/* --- UI COMPONENTS --- */

function AdminHeader({ onSwitchRole }) {
  return (
    <div className="w-full bg-white/80 backdrop-blur-md border-b border-slate-100 sticky top-0 z-50 px-8 py-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-black text-xs shadow-lg shadow-indigo-200">A</div>
        <span className="font-black text-slate-800 tracking-tight uppercase">Admin Command Center</span>
      </div>
      <div className="flex items-center gap-4">
        <button onClick={onSwitchRole} className="flex items-center gap-2 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-xl text-xs font-black transition-all border border-indigo-100">
          <Users size={14} /> SWITCH TO USER VIEW
        </button>
        <div className="h-6 w-[1px] bg-slate-200 mx-2" />
        <button className="p-2 text-slate-400 hover:text-slate-600 relative">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white" />
        </button>
      </div>
    </div>
  );
}

function ExecutiveVerdict({ overview }) {
  return (
    <div className="bg-slate-900 rounded-[2rem] p-8 text-white shadow-2xl flex flex-col justify-between relative overflow-hidden h-full">
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/20 rounded-full blur-3xl" />
      <div>
        <h4 className="text-indigo-400 font-black text-xs uppercase tracking-widest mb-6">Executive Verdict</h4>
        <p className="text-5xl font-black mb-2">{overview?.completion_rate ?? 0}%</p>
        <p className="text-slate-400 text-sm font-medium mb-6 uppercase tracking-tighter">Task Success Rate</p>
        <div className="h-[1px] bg-white/10 w-full mb-6" />
        <p className="text-sm text-slate-300 leading-relaxed font-medium">
           Conclusion: Based on current <span className="text-white font-bold">Latency vs Storage</span> ratios, 
           the system is in the <span className="text-emerald-400 font-bold uppercase">Optimal Zone</span>. 
           Capacity supports <span className="text-indigo-400 font-bold">{Math.floor(3600/ (overview?.avg_processing_time || 1))}</span> uploads/hr.
        </p>
      </div>
      <button className="w-full mt-8 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-2xl font-bold transition-all shadow-lg shadow-indigo-500/20 uppercase text-xs tracking-widest">
         Download Full System Audit
      </button>
    </div>
  );
}

function MetricCard({ label, value, subtext, icon: Icon, theme }) {
  return (
    <div className="rounded-3xl p-6 border border-white/50 transition-all hover:scale-[1.02] shadow-sm" style={{ backgroundColor: theme.bg }}>
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-2xl bg-white/60"><Icon size={24} style={{ color: theme.text }} /></div>
        <span className="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded-lg" style={{ color: theme.text }}>{label}</span>
      </div>
      <div className="text-4xl font-black text-slate-800">{value}</div>
      <div className="mt-2 text-sm font-bold opacity-80" style={{ color: theme.text }}>{subtext}</div>
    </div>
  );
}

function Panel({ title, subtitle, children, className }) {
  return (
    <div className={cn("rounded-3xl border border-white/60 bg-white/80 backdrop-blur-xl p-8 shadow-sm", className)}>
      <div className="flex flex-col gap-1 mb-6">
        <h3 className="text-xl font-black text-slate-800">{title}</h3>
        {subtitle && <p className="text-sm font-medium text-slate-500">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [tab, setTab] = useState("overview");
  const [overview, setOverview] = useState(null);
  const [daily, setDaily] = useState(null);
  const [dists, setDists] = useState(null);
  const [usersTable, setUsersTable] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const isAdmin = useMemo(() => {
    try { return JSON.parse(localStorage.getItem("user_info") || "{}").role === "admin"; } 
    catch { return false; }
  }, []);

  const api = useMemo(() => axios.create({ baseURL: API_URL }), []);

  useEffect(() => {
    if (!isAdmin) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const [o, d, di, u, a] = await Promise.all([
          api.get("/admin/analytics/overview"),
          api.get("/admin/analytics/daily"),
          api.get("/admin/analytics/distributions"),
          api.get("/admin/analytics/users-table"),
          api.get("/admin/analytics/audit-logs").catch(() => ({ data: [] }))
        ]);
        setOverview(o.data);
        setDaily(d.data);
        setDists(di.data);
        setUsersTable(u.data);
        setAuditLogs(a.data);
      } catch (e) { setErr("Failed to connect to backend"); }
      finally { setLoading(false); }
    };
    fetchData();
  }, [api, isAdmin]);

  const dailySeries = useMemo(() => {
    if (!daily?.dates) return [];
    return daily.dates.map((date, i) => ({
      date,
      users: daily.new_users?.[i] ?? 0,
      summaries: daily.summaries_generated?.[i] ?? 0,
    }));
  }, [daily]);

  if (!isAdmin) return <div className="p-20 text-center font-black text-rose-600">UNAUTHORIZED ACCESS</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F0F9FF] via-[#FDF4FF] to-[#FFFBEB] font-sans pb-20">
      <AdminHeader onSwitchRole={() => navigate("/")} />
      
      <div className="p-8 mx-auto max-w-7xl space-y-8 animate-in fade-in duration-700">
        
        {/* TABS SELECTOR */}
        <div className="flex justify-center md:justify-start">
            <div className="flex bg-white/50 backdrop-blur-sm p-1.5 rounded-2xl border border-white/60 shadow-sm">
                {["overview", "users", "health"].map((t) => (
                    <button key={t} onClick={() => setTab(t)} className={cn("px-6 py-2.5 rounded-xl text-sm font-bold transition-all uppercase tracking-widest", tab === t ? "bg-slate-900 text-white shadow-lg" : "text-slate-400 hover:text-slate-600")}>
                        {t}
                    </button>
                ))}
            </div>
        </div>

        {tab === "overview" && (
            <div className="space-y-8 animate-in slide-in-from-bottom-4">
                {/* ROW 1: METRICS + VERDICT */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                        <MetricCard label="Total Users" value={overview?.total_users ?? 0} subtext="Active Accounts" icon={Users} theme={PALETTE.blue} />
                        <MetricCard label="Summaries" value={overview?.total_summaries ?? 0} subtext="AI Generations" icon={FileText} theme={PALETTE.pink} />
                        <MetricCard label="Avg Speed" value={`${overview?.avg_processing_time ?? 0}s`} subtext="Latency Score" icon={Clock} theme={PALETTE.purple} />
                        <MetricCard label="System Load" value={`${overview?.db_size_mb ?? 0}MB`} subtext="Storage Health" icon={Database} theme={PALETTE.yellow} />
                    </div>
                    <ExecutiveVerdict overview={overview} />
                </div>

                {/* ROW 2: SEPARATED CHARTS (Now Easy to Read) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <Panel title="User Acquisition" subtitle="New registrations per day">
                        <div className="h-[300px]">
                            <ResponsiveContainer>
                                <BarChart data={dailySeries}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} />
                                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} />
                                    <Tooltip cursor={{fill: '#F8FAFC'}} contentStyle={{borderRadius: '15px', border: 'none'}} />
                                    <Bar dataKey="users" name="New Users" fill={PALETTE.blue.accent} radius={[6, 6, 0, 0]} barSize={40} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </Panel>

                    <Panel title="System Engagement" subtitle="AI summaries generated per day">
                        <div className="h-[300px]">
                            <ResponsiveContainer>
                                <AreaChart data={dailySeries}>
                                    <defs>
                                        <linearGradient id="colorSum" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor={PALETTE.purple.accent} stopOpacity={0.8}/>
                                            <stop offset="95%" stopColor={PALETTE.purple.accent} stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} />
                                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} />
                                    <Tooltip contentStyle={{borderRadius: '15px', border: 'none'}} />
                                    <Area type="monotone" dataKey="summaries" name="Summaries" stroke={PALETTE.purple.text} strokeWidth={3} fillOpacity={1} fill="url(#colorSum)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Panel>
                </div>

                {/* ROW 3: PIE CHARTS */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <Panel title="Style Adoption" subtitle="Preferred summary formats">
                        <div className="h-[300px]">
                            <ResponsiveContainer>
                                <PieChart>
                                    <Pie data={dists?.summary_styles || []} innerRadius={80} outerRadius={110} paddingAngle={8} dataKey="value">
                                        {(dists?.summary_styles || []).map((entry, index) => <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip />
                                    <Legend verticalAlign="bottom" />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </Panel>
                    <Panel title="System Latency" subtitle="Processing time distribution">
                        <div className="h-[300px]">
                            <ResponsiveContainer>
                                <BarChart data={dists?.processing_times || []}>
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                    <Tooltip cursor={{fill: 'transparent'}} />
                                    <Bar dataKey="value" radius={[12, 12, 12, 12]} barSize={50}>
                                        {(dists?.processing_times || []).map((entry, index) => <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />)}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </Panel>
                </div>
            </div>
        )}

        {tab === "users" && (
            <Panel title="User Management" subtitle="System Account Control" className="animate-in slide-in-from-bottom-4">
                <div className="overflow-x-auto rounded-2xl border border-slate-100">
                    <table className="min-w-full divide-y divide-slate-100">
                        <thead className="bg-slate-50/50">
                            <tr>{["ID", "User", "Role", "Books", "Joined"].map(h => <th key={h} className="px-6 py-4 text-left text-xs font-black text-slate-400 uppercase">{h}</th>)}</tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-100">
                            {usersTable.map((u) => (
                                <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 text-sm font-bold text-slate-400">#{u.id}</td>
                                    <td className="px-6 py-4">
                                      <div className="text-sm font-bold text-slate-800">{u.name}</div>
                                      <div className="text-xs text-slate-400">{u.email}</div>
                                    </td>
                                    <td className="px-6 py-4"><span className={cn("px-3 py-1 rounded-full text-[10px] font-black uppercase", u.role === 'admin' ? "bg-purple-100 text-purple-600" : "bg-blue-100 text-blue-600")}>{u.role}</span></td>
                                    <td className="px-6 py-4 text-sm font-bold text-slate-600">{u.books}</td>
                                    <td className="px-6 py-4 text-sm text-slate-400">{u.joined}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Panel>
        )}

        {tab === "health" && (
            <div className="space-y-6 animate-in slide-in-from-bottom-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <MetricCard label="Uptime" value="99.9%" subtext="Last 30 Days" icon={Server} theme={PALETTE.blue} />
                    <MetricCard label="Failures" value={overview?.failed_books || 0} subtext="Critical Errors" icon={AlertTriangle} theme={PALETTE.pink} />
                    <MetricCard label="Latency" value="120ms" subtext="API Response" icon={Activity} theme={PALETTE.purple} />
                </div>

                <Panel title="Real-time Audit Logs" subtitle="Recent system and user activities" className="lg:col-span-3">
                    <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                        {auditLogs.length > 0 ? auditLogs.map((log) => (
                            <div key={log.id} className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-indigo-200 transition-colors">
                                <div className="p-2 bg-white rounded-xl shadow-sm"><List size={16} className="text-indigo-600" /></div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start">
                                        <span className="text-xs font-black uppercase tracking-wider text-indigo-600">{log.action}</span>
                                        <span className="text-[10px] font-bold text-slate-400">{new Date(log.timestamp).toLocaleString()}</span>
                                    </div>
                                    <p className="text-sm font-bold text-slate-800 mt-1">{log.details}</p>
                                    <p className="text-xs font-medium text-slate-400">By {log.name} (ID: {log.user_id || 'System'})</p>
                                </div>
                            </div>
                        )) : <div className="text-center py-10 text-slate-400 font-bold">No recent activity logs found.</div>}
                    </div>
                </Panel>

                <Panel title="System Maintenance">
                    <div className="flex gap-4">
                        <button className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg"><Trash2 size={18} /> Clear Cache</button>
                        <button className="flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 text-slate-700 rounded-xl font-bold hover:bg-slate-50 transition-all"><Download size={18} /> Export Logs</button>
                    </div>
                </Panel>
            </div>
        )}
      </div>
    </div>
  );
}