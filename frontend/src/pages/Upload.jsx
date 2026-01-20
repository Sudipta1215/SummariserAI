import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud, FileText, X, CheckCircle2,
  Trash2, AlertCircle, Loader2, Book
} from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const Upload = () => {
  const navigate = useNavigate();

  // Form State
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");

  // UI State
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [successData, setSuccessData] = useState(null);
  const [recentUploads, setRecentUploads] = useState([]);

  // 1) HELPER TO GET AUTH HEADERS
  // Inside Upload.jsx
const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  if (!token) {
    console.error("No token found. Redirecting to login.");
    navigate("/login"); // Optional: auto-redirect if token is missing
    return {};
  }
  return { Authorization: `Bearer ${token}` };
};

  // 2) FETCH RECENT UPLOADS (with headers)
  const fetchRecent = async () => {
    try {
      const res = await fetch(`${API_URL}/books/`, {
        headers: getAuthHeaders(),
      });

      if (res.ok) {
        const data = await res.json();
        setRecentUploads(data.sort((a, b) => b.book_id - a.book_id).slice(0, 5));
      } else {
        // Optional: show message if unauthorized
        // const errData = await res.json().catch(() => ({}));
        // setError(errData.detail || "Failed to load recent uploads.");
      }
    } catch (err) {
      console.error("Failed to load recent uploads");
    }
  };

  useEffect(() => {
    fetchRecent();
  }, []);

  // 3) FILE HANDLING
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setError("");
    setSuccessData(null);

    if (!selected) return;

    // Validation
    if (selected.size > MAX_FILE_SIZE) {
      setError("File is too large (Max 10MB).");
      return;
    }
    const validTypes = [
      'application/pdf',
      'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    if (!validTypes.includes(selected.type)) {
      setError("Invalid file type. Only PDF, DOCX, and TXT allowed.");
      return;
    }

    setFile(selected);
    setTitle(selected.name.replace(/\.[^/.]+$/, ""));
  };

  const handleClearFile = () => {
    setFile(null);
    setTitle("");
    setAuthor("");
    setError("");
    setSuccessData(null);
  };

  // 4) UPLOAD ACTION (with headers; user_id NOT sent)
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !title) return;

    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("author", author || "Unknown");
    // user_id NOT appended; backend gets it from token

    try {
      const res = await fetch(`${API_URL}/books/`, {
        method: 'POST',
        headers: getAuthHeaders(), // sends Bearer token
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        setSuccessData(data);
        fetchRecent();
        setFile(null);
      } else {
        const errData = await res.json().catch(() => ({}));
        setError(errData.detail || "Upload failed. Please ensure you are logged in.");
      }
    } catch (err) {
      setError("Connection failed. Is backend running?");
    } finally {
      setUploading(false);
    }
  };

  // 5) DELETE ACTION (with headers)
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this book?")) return;
    try {
      const res = await fetch(`${API_URL}/books/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (res.ok) fetchRecent();
      else alert("Failed to delete (maybe not authorized).");
    } catch (err) {
      alert("Failed to delete.");
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">

      {/* HEADER */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
            <UploadCloud size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Upload Book</h1>
            <p className="text-xs text-slate-400">PDF, DOCX, TXT (Max 10MB)</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* LEFT: UPLOAD FORM */}
          <div className="lg:col-span-2 space-y-6">

            {/* Drop Zone */}
            {!file && !successData && (
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-white/10 rounded-3xl cursor-pointer bg-[#1E1E2E] hover:bg-[#252636] hover:border-purple-500/50 transition-all group relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="z-10 flex flex-col items-center">
                  <div className="w-16 h-16 bg-[#161622] rounded-full flex items-center justify-center mb-4 shadow-xl group-hover:scale-110 transition-transform">
                    <UploadCloud size={32} className="text-purple-400" />
                  </div>
                  <p className="text-lg font-medium text-white">Click to upload or drag and drop</p>
                  <p className="text-sm text-slate-500 mt-1">PDF, DOCX, or TXT</p>
                </div>
                <input type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.docx,.txt" />
              </label>
            )}

            {/* File Selected / Form */}
            {file && !successData && (
              <div className="bg-[#1E1E2E] rounded-3xl p-8 border border-white/5 shadow-xl animate-fade-in">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400">
                      <FileText size={24} />
                    </div>
                    <div>
                      <p className="font-bold text-white">{file.name}</p>
                      <p className="text-xs text-slate-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <button onClick={handleClearFile} className="p-2 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition-colors">
                    <X size={20} />
                  </button>
                </div>

                <form onSubmit={handleUpload} className="space-y-4">
                  <div>
                    <label className="text-xs font-bold text-slate-500 uppercase ml-1">Title</label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="w-full mt-1 bg-[#161622] text-white p-3 rounded-xl border border-white/10 focus:border-purple-500 outline-none transition-colors"
                      placeholder="Book Title"
                      required
                    />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-500 uppercase ml-1">Author (Optional)</label>
                    <input
                      type="text"
                      value={author}
                      onChange={(e) => setAuthor(e.target.value)}
                      className="w-full mt-1 bg-[#161622] text-white p-3 rounded-xl border border-white/10 focus:border-purple-500 outline-none transition-colors"
                      placeholder="Author Name"
                    />
                  </div>

                  {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2 text-red-400 text-sm">
                      <AlertCircle size={16} /> {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={uploading}
                    className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-purple-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                  >
                    {uploading ? <Loader2 className="animate-spin" /> : <UploadCloud size={20} />}
                    {uploading ? "Processing..." : "Upload & Process"}
                  </button>
                </form>
              </div>
            )}

            {/* Success State */}
            {successData && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-3xl p-8 text-center animate-fade-in">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-400">
                  <CheckCircle2 size={32} />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Upload Successful!</h2>
                <p className="text-slate-400 mb-6">Your book has been processed and is ready.</p>

                <div className="grid grid-cols-2 gap-4 mb-6 max-w-sm mx-auto">
                  <div className="bg-[#0F1016] p-3 rounded-xl border border-white/5">
                    <p className="text-xs text-slate-500 uppercase">Words</p>
                    <p className="text-xl font-bold text-white">{successData.word_count?.toLocaleString()}</p>
                  </div>
                  <div className="bg-[#0F1016] p-3 rounded-xl border border-white/5">
                    <p className="text-xs text-slate-500 uppercase">Chars</p>
                    <p className="text-xl font-bold text-white">{successData.char_count?.toLocaleString()}</p>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <button onClick={handleClearFile} className="px-6 py-2 rounded-xl bg-[#161622] hover:bg-[#252636] text-white border border-white/10 transition-colors">
                    Upload Another
                  </button>
                  <button
                    onClick={() => navigate('/summaries', { state: { selectedBookId: successData.book_id } })}
                    className="px-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white font-bold shadow-lg shadow-emerald-500/20 transition-colors"
                  >
                    Generate Summary
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: RECENT UPLOADS */}
          <div>
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Book size={18} className="text-slate-400" /> Recent Uploads
            </h3>
            <div className="space-y-3">
              {recentUploads.length === 0 ? (
                <p className="text-slate-500 text-sm italic">No uploads yet.</p>
              ) : (
                recentUploads.map(book => (
                  <div key={book.book_id} className="bg-[#1E1E2E] p-4 rounded-2xl border border-white/5 flex items-center justify-between group hover:border-white/10 transition-all">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 shrink-0">
                        <FileText size={16} />
                      </div>
                      <div className="overflow-hidden">
                        <p className="text-sm font-medium text-white truncate w-32">{book.title}</p>
                        <p className="text-[10px] text-slate-500">
                          {new Date(book.created_at || Date.now()).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(book.book_id)}
                      className="p-2 text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Upload;
