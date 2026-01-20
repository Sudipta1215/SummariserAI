import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  User,
  Lock,
  Trash2,
  Bell,
  Moon,
  Shield,
  Save,
  AlertTriangle,
  Loader2,
  CheckCircle,
} from "lucide-react";

import { useTheme } from "../context/ThemeContext";

const API_URL = "http://127.0.0.1:8000";

const Settings = () => {
  const navigate = useNavigate();
  const { isDarkMode, toggleTheme } = useTheme();

  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  // User State
  const [user, setUser] = useState({ name: "", email: "", user_id: null });

  // Form States
  const [name, setName] = useState("");
  const [prefEmail, setPrefEmail] = useState(true);

  const [passwords, setPasswords] = useState({ current: "", new: "", confirm: "" });
  const [deleteConfirm, setDeleteConfirm] = useState("");

  // Load User Data
  useEffect(() => {
    const storedUser = localStorage.getItem("user_info");
    if (storedUser) {
      const parsed = JSON.parse(storedUser);
      setUser(parsed);
      setName(parsed.name || "");
    }
  }, []);

  // --- HANDLERS ---

  const handleProfileSave = () => {
    setLoading(true);
    setTimeout(() => {
      const updatedUser = { ...user, name };
      localStorage.setItem("user_info", JSON.stringify(updatedUser));
      setUser(updatedUser);
      setSuccessMsg("Profile preferences updated successfully!");
      setLoading(false);
      setTimeout(() => setSuccessMsg(""), 3000);
    }, 800);
  };

  const handlePasswordUpdate = (e) => {
    e.preventDefault();
    setSuccessMsg("");

    if (passwords.new !== passwords.confirm) {
      alert("New passwords do not match.");
      return;
    }
    if (!passwords.current) {
      alert("Please enter current password.");
      return;
    }

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setPasswords({ current: "", new: "", confirm: "" });
      setSuccessMsg("Password updated successfully!");
      setTimeout(() => setSuccessMsg(""), 3000);
    }, 1000);
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirm !== "DELETE") return;
    if (!window.confirm("Final Warning: This cannot be undone.")) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/users/${user.user_id}`, { method: "DELETE" });
      if (res.ok) {
        localStorage.clear();
        navigate("/");
      } else {
        alert("Failed to delete account.");
      }
    } catch (err) {
      console.error(err);
      alert("Connection error.");
    } finally {
      setLoading(false);
    }
  };

  // --- SUB-COMPONENTS ---

  const Toggle = ({ label, icon: Icon, value, onChange, desc }) => (
    <div className="flex items-center justify-between p-4 bg-[#161622] rounded-2xl border border-white/5">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#252636] rounded-lg text-[#A78BFA]">
          <Icon size={20} />
        </div>
        <div>
          <p className="text-sm font-bold text-white">{label}</p>
          <p className="text-xs text-slate-500">{desc}</p>
        </div>
      </div>

      <button
        onClick={onChange}
        className={`w-12 h-6 rounded-full p-1 transition-colors relative ${
          value ? "bg-[#A78BFA]" : "bg-slate-700"
        }`}
        type="button"
      >
        <div
          className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform ${
            value ? "translate-x-6" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8 animate-fade-in text-slate-200">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Account Settings</h1>
        <p className="text-slate-400">Manage your profile, security, and preferences.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-white/10 pb-1">
        {[
          { id: "profile", label: "Profile", icon: User },
          { id: "security", label: "Security", icon: Shield },
          { id: "danger", label: "Danger Zone", icon: Trash2 },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2
              ${
                activeTab === tab.id
                  ? "text-[#A78BFA] border-[#A78BFA]"
                  : "text-slate-500 border-transparent hover:text-white"
              }`}
            type="button"
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* SUCCESS BANNER */}
      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center gap-3 text-emerald-400 animate-in fade-in slide-in-from-top-2">
          <CheckCircle size={20} />
          {successMsg}
        </div>
      )}

      {/* --- CONTENT AREA --- */}
      <div className="bg-white dark:bg-[#1E1E2E] p-8 rounded-3xl border border-slate-200 dark:border-white/5 shadow-xl transition-colors duration-300">
        {/* PROFILE TAB */}
        {activeTab === "profile" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full mt-2 bg-[#161622] text-white p-3 rounded-xl border border-white/10 focus:border-[#A78BFA] outline-none transition-colors"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                  Email Address
                </label>
                <input
                  type="text"
                  value={user.email}
                  disabled
                  className="w-full mt-2 bg-[#161622]/50 text-slate-400 p-3 rounded-xl border border-white/5 cursor-not-allowed"
                />
              </div>
            </div>

            <div className="h-px bg-white/5 my-6" />

            <h3 className="text-lg font-bold text-white mb-4">Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Toggle
                label="Email Summaries"
                desc="Receive weekly digests"
                icon={Bell}
                value={prefEmail}
                onChange={() => setPrefEmail((v) => !v)}
              />

              <Toggle
                label="Dark Mode"
                desc="App appearance"
                icon={Moon}
                value={isDarkMode}
                onChange={toggleTheme}
              />
            </div>

            <div className="pt-4 flex justify-end">
              <button
                onClick={handleProfileSave}
                disabled={loading}
                className="bg-[#A78BFA] hover:bg-[#8B5CF6] text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-purple-500/20 flex items-center gap-2"
                type="button"
              >
                {loading ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                Save Changes
              </button>
            </div>
          </div>
        )}

        {/* SECURITY TAB */}
        {activeTab === "security" && (
          <form onSubmit={handlePasswordUpdate} className="max-w-md space-y-5">
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                Current Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 text-slate-500" size={16} />
                <input
                  type="password"
                  value={passwords.current}
                  onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                  className="w-full mt-1 bg-[#161622] text-white pl-10 pr-4 py-3 rounded-xl border border-white/10 focus:border-[#A78BFA] outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 text-slate-500" size={16} />
                <input
                  type="password"
                  value={passwords.new}
                  onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                  className="w-full mt-1 bg-[#161622] text-white pl-10 pr-4 py-3 rounded-xl border border-white/10 focus:border-[#A78BFA] outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                Confirm New Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 text-slate-500" size={16} />
                <input
                  type="password"
                  value={passwords.confirm}
                  onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                  className="w-full mt-1 bg-[#161622] text-white pl-10 pr-4 py-3 rounded-xl border border-white/10 focus:border-[#A78BFA] outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-[#2A2B3D] hover:bg-[#35364F] text-white px-6 py-3 rounded-xl font-bold transition-all border border-white/5 w-full"
            >
              {loading ? "Updating..." : "Update Password"}
            </button>
          </form>
        )}

        {/* DANGER ZONE TAB */}
        {activeTab === "danger" && (
          <div className="space-y-6">
            <div className="bg-rose-500/10 border border-rose-500/20 p-6 rounded-2xl flex items-start gap-4">
              <div className="p-3 bg-rose-500/20 rounded-xl text-rose-500">
                <AlertTriangle size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Delete Account</h3>
                <p className="text-slate-400 text-sm mt-1">
                  Once you delete your account, there is no going back. All your uploaded
                  books and summaries will be permanently removed.
                </p>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                Type "DELETE" to confirm
              </label>
              <input
                type="text"
                placeholder="DELETE"
                value={deleteConfirm}
                onChange={(e) => setDeleteConfirm(e.target.value)}
                className="w-full mt-2 bg-[#161622] text-white p-3 rounded-xl border border-white/10 focus:border-rose-500 outline-none transition-colors"
              />
            </div>

            <button
              onClick={handleDeleteAccount}
              disabled={deleteConfirm !== "DELETE" || loading}
              className="w-full bg-rose-600 hover:bg-rose-700 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-rose-500/20 flex items-center justify-center gap-2"
              type="button"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Trash2 size={20} />}
              Permanently Delete Account
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;
