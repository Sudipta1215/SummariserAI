import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User, ShieldCheck } from 'lucide-react';

export default function RoleSelection() {
  const navigate = useNavigate();

  const handleSelect = (role) => {
    if (role === 'admin') navigate('/admin-dashboard');
    else navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] p-6">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl border border-slate-100 p-8 text-center">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Welcome Back</h1>
        <p className="text-slate-500 mb-8">Select your workspace to continue.</p>

        <div className="grid grid-cols-1 gap-4">
          <button onClick={() => handleSelect('admin')} className="group flex items-center gap-4 p-4 rounded-2xl border border-slate-100 hover:border-purple-200 hover:bg-purple-50 transition-all">
            <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 group-hover:scale-110 transition-transform">
              <ShieldCheck size={24} />
            </div>
            <div className="text-left">
              <div className="font-bold text-slate-900">Admin Dashboard</div>
              <div className="text-xs text-slate-500">System analytics & user management</div>
            </div>
          </button>

          <button onClick={() => handleSelect('user')} className="group flex items-center gap-4 p-4 rounded-2xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50 transition-all">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform">
              <User size={24} />
            </div>
            <div className="text-left">
              <div className="font-bold text-slate-900">User Workspace</div>
              <div className="text-xs text-slate-500">My library & book summaries</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}