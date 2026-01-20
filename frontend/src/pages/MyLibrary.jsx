import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Book, Trash2, FileText, Clock, Type, 
  RefreshCw, Sparkles, AlertCircle, Loader2, Search, Eye
} from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

const MyLibrary = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // ✅ Helper to attach auth token
  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // --- 1. FETCH BOOKS (✅ Updated with Authorization header) ---
  const fetchBooks = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`${API_URL}/books/`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (res.ok) {
        const data = await res.json();
        setBooks(data.sort((a, b) => b.book_id - a.book_id));
      } else if (res.status === 401) {
        console.error("Not authenticated. Redirecting...");
        localStorage.removeItem("token");
        localStorage.removeItem("user_info");
        navigate("/"); // your app shows AuthPage at "/" when not authenticated
      } else {
        console.error("Failed to fetch books:", res.status);
      }
    } catch (error) {
      console.error("Connection error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- 2. ACTIONS (✅ Updated DELETE with Authorization header) ---
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this book?")) return;

    setDeletingId(id);
    try {
      const res = await fetch(`${API_URL}/books/${id}`, {
        method: "DELETE",
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (res.ok) {
        setBooks((prev) => prev.filter((b) => b.book_id !== id));
      } else if (res.status === 401) {
        console.error("Not authenticated. Redirecting...");
        localStorage.removeItem("token");
        localStorage.removeItem("user_info");
        navigate("/");
      } else {
        alert("Failed to delete book.");
      }
    } catch (error) {
      alert("Error deleting book.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleAction = (book) => {
    navigate('/summaries', { state: { selectedBookId: book.book_id } });
  };

  // Filter books based on search
  const filteredBooks = books.filter(b =>
    (b.title || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    ((b.author || "").toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">
      
      {/* HEADER */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
            <Book size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">My Library</h1>
            <p className="text-xs text-slate-400">Manage your uploaded documents</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Search Bar */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <input
              type="text"
              placeholder="Search library..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#1E1E2E] border border-white/5 rounded-full pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50 w-64 transition-all"
            />
          </div>

          <button
            onClick={fetchBooks}
            disabled={loading}
            className="p-2 bg-[#1E1E2E] hover:bg-white/5 rounded-full text-slate-400 hover:text-white transition-colors border border-white/5"
          >
            <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* CONTENT AREA */}
      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">

        {loading && books.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500">
            <Loader2 size={40} className="animate-spin text-blue-500 mb-4" />
            <p>Loading library...</p>
          </div>
        ) : filteredBooks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
            <Book size={64} className="mb-4" />
            <p className="text-lg font-medium">No books found</p>
            {searchTerm && <p className="text-sm">Try a different search term</p>}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
            {filteredBooks.map((book) => {
              const readTime = Math.max(1, Math.round((book.word_count || 0) / 200));

              return (
                <div
                  key={book.book_id}
                  className="bg-[#1E1E2E] rounded-3xl border border-white/5 p-6 flex flex-col group hover:border-blue-500/30 transition-all shadow-xl"
                >

                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shrink-0 font-bold text-lg">
                        {(book.title || "?").charAt(0).toUpperCase()}
                      </div>
                      <div className="overflow-hidden">
                        <h3 className="font-bold text-white truncate" title={book.title}>{book.title}</h3>
                        <p className="text-xs text-slate-400 truncate">{book.author || "Unknown Author"}</p>
                      </div>
                    </div>

                    <span
                      className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide border
                        ${book.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                          book.status === 'processing' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                          book.status === 'failed' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                          'bg-slate-500/10 text-slate-400 border-slate-500/20'}
                      `}
                    >
                      {(book.status || "unknown").replace('_', ' ')}
                    </span>
                  </div>

                  {/* Stats Row */}
                  <div className="grid grid-cols-3 gap-2 mb-6 py-4 border-y border-white/5">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-slate-500 text-xs mb-1">
                        <Type size={12} /> Words
                      </div>
                      <p className="text-white font-bold">{book.word_count?.toLocaleString() || 0}</p>
                    </div>
                    <div className="text-center border-x border-white/5">
                      <div className="flex items-center justify-center gap-1 text-slate-500 text-xs mb-1">
                        <FileText size={12} /> Chars
                      </div>
                      <p className="text-white font-bold">{book.char_count?.toLocaleString() || 0}</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-slate-500 text-xs mb-1">
                        <Clock size={12} /> Read
                      </div>
                      <p className="text-white font-bold">{readTime} min</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-auto flex gap-3">
                    {(book.status === 'text_extracted' || book.status === 'completed') ? (
                      <button
                        onClick={() => handleAction(book)}
                        className="flex-1 bg-[#2A2B3D] hover:bg-[#35364F] text-white py-2.5 rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2 border border-white/5"
                      >
                        {book.status === 'completed' ? (
                          <><Eye size={16} className="text-blue-400" /> View Summary</>
                        ) : (
                          <><Sparkles size={16} className="text-[#A78BFA]" /> Generate</>
                        )}
                      </button>
                    ) : (
                      <button
                        disabled
                        className="flex-1 bg-white/5 text-slate-500 py-2.5 rounded-xl text-sm font-semibold cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {book.status === 'failed' ? <AlertCircle size={16} /> : <Loader2 size={16} className="animate-spin" />}
                        {book.status === 'failed' ? 'Error' : 'Wait...'}
                      </button>
                    )}

                    <button
                      onClick={() => handleDelete(book.book_id)}
                      disabled={deletingId === book.book_id}
                      className="p-2.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded-xl transition-colors border border-rose-500/20"
                    >
                      {deletingId === book.book_id ? <Loader2 size={18} className="animate-spin" /> : <Trash2 size={18} />}
                    </button>
                  </div>

                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyLibrary;
