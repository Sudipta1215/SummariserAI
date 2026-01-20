import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

const AuthPage = () => {
  const navigate = useNavigate();
  const [authMode, setAuthMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const [formData, setFormData] = useState({ fullName: "", email: "", password: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError("");
    setIsLoading(true);

    try {
      let endpoint = "/auth/login";
      let body = {};

      // 1. CONFIGURE REQUEST BASED ON MODE
      if (authMode === "login") {
        endpoint = "/auth/login";
        body = { email: formData.email, password: formData.password };
      } 
      else if (authMode === "register") {
        endpoint = "/auth/register";
        body = { name: formData.fullName, email: formData.email, password: formData.password };
      } 
      else if (authMode === "forgot") {
        endpoint = "/auth/forgot-password";
        // ✅ CRITICAL FIX: Send 'new_password' to match Backend Schema
        body = { email: formData.email, new_password: formData.password };
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        // --- SUCCESS HANDLERS ---
        if (authMode === "login") {
          if (data.access_token) localStorage.setItem("token", data.access_token);
          const userInfo = data.user || { email: formData.email, role: "user" };
          localStorage.setItem("user_info", JSON.stringify(userInfo));
          userInfo.role === "admin" ? navigate("/role-selection") : navigate("/");
        } 
        else if (authMode === "register") {
          alert("Account created! Please log in.");
          setAuthMode("login");
          setFormData({ ...formData, password: "" });
        } 
        else if (authMode === "forgot") {
          alert("Success! Password updated. Please log in with your NEW password.");
          setAuthMode("login");
          setFormData({ ...formData, password: "" }); // Clear old input
        }
      } else {
        // --- ERROR HANDLER ---
        let msg = data.detail || "Request failed.";
        if (Array.isArray(msg)) msg = msg.map(err => err.msg).join(", ");
        setServerError(msg);
      }
    } catch (err) {
      console.error("Auth Error:", err);
      setServerError("Network error. Backend not reachable.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F1016] flex items-center justify-center p-4">
      <div className="bg-[#1E1E2E] w-full max-w-md p-8 rounded-3xl border border-white/5 shadow-2xl backdrop-blur-sm">
        <h1 className="text-3xl font-bold text-center text-white mb-2 capitalize">
          {authMode === "forgot" ? "Reset Password" : authMode}
        </h1>
        
        {serverError && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400 text-sm">
            <AlertCircle size={18} /> <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
          {authMode === "register" && (
            <div className="relative">
              <User className="absolute left-4 top-3.5 text-slate-500" size={18} />
              <input type="text" placeholder="Full Name" className="w-full bg-[#161622] border border-white/5 rounded-xl py-3 pl-12 text-white outline-none focus:border-indigo-500"
                value={formData.fullName} onChange={(e) => setFormData({ ...formData, fullName: e.target.value })} required />
            </div>
          )}

          <div className="relative">
            <Mail className="absolute left-4 top-3.5 text-slate-500" size={18} />
            <input type="email" placeholder="Email Address" className="w-full bg-[#161622] border border-white/5 rounded-xl py-3 pl-12 text-white outline-none focus:border-indigo-500"
              value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
          </div>

          <div className="relative">
            <Lock className="absolute left-4 top-3.5 text-slate-500" size={18} />
            <input 
              type={showPassword ? "text" : "password"} 
              placeholder={authMode === "forgot" ? "Enter New Password" : "Password"}
              className="w-full bg-[#161622] border border-white/5 rounded-xl py-3 pl-12 text-white outline-none focus:border-indigo-500"
              value={formData.password} 
              onChange={(e) => setFormData({ ...formData, password: e.target.value })} 
              required 
              autoComplete="new-password" // ✅ PREVENTS BROWSER AUTOFILL OF OLD PASS
            />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-3.5 text-slate-500 hover:text-white">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <button type="submit" disabled={isLoading} className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all">
            {isLoading ? <Loader2 className="animate-spin" /> : <>Continue <ArrowRight size={18} /></>}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {authMode === "login" && <button onClick={() => setAuthMode("forgot")} className="hover:text-indigo-400">Forgot Password?</button>}
          <p className="mt-2">
            {authMode === "login" ? "Need an account?" : "Back to"} 
            <button onClick={() => { setAuthMode(authMode === "login" ? "register" : "login"); setServerError(""); }} className="ml-2 text-indigo-400 font-bold hover:text-white">
              {authMode === "login" ? "Sign Up" : "Log In"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
export default AuthPage;