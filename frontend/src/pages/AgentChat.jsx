import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, Book, Globe, UploadCloud, 
  Bot, User, Sparkles, X, Menu, Loader2, CheckCircle2
} from 'lucide-react';

/* --- API CONFIG --- */
const API_URL = "https://summariserai2.onrender.com";

const AgentChat = () => {
  const navigate = useNavigate();

  // --- STATE ---
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Context State
  const [books, setBooks] = useState([]);
  const [selectedBookIds, setSelectedBookIds] = useState([]);
  const [language, setLanguage] = useState("English");
  
  // UI State
  const [showSidebar, setShowSidebar] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef(null);

  // Helper: attach auth token
  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // --- 1. FETCH BOOKS ON LOAD ---
  useEffect(() => {
    fetchBooks();
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchBooks = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      const res = await fetch(`${API_URL}/books/`, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      if (res.ok) {
        const data = await res.json();
        const sorted = (data || []).sort((a, b) => b.book_id - a.book_id);
        setBooks(sorted);
      } else if (res.status === 401) {
        navigate("/");
      }
    } catch (err) {
      console.error("Failed to fetch books:", err);
    }
  };

  // --- 2. HANDLERS ---

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // ✅ FIXED: Removed the "selectedBookIds.length === 0" check.
    // Now the agent will use web search or general knowledge if no book is selected.

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`${API_URL}/agent/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          query: userMsg.content,
          book_ids: selectedBookIds, // Will be [] if none selected
          language: language
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else if (res.status === 401) {
        navigate("/");
      } else {
        setMessages(prev => [...prev, { role: 'system', content: `Error: ${res.statusText}` }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: "Failed to connect to the agent." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);
    formData.append("author", "User Upload");

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/books/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData
      });

      if (res.ok) {
        await fetchBooks();
        alert("File uploaded successfully!");
      } else {
        alert("Upload failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading file.");
    } finally {
      setIsUploading(false);
    }
  };

  const toggleBookSelection = (id) => {
    setSelectedBookIds(prev =>
      prev.includes(id) ? prev.filter(b => b !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex h-screen bg-[#0F1016] text-slate-200 overflow-hidden font-sans">
      
      {/* --- SIDEBAR --- */}
      <aside className={`
        fixed md:relative z-20 h-full w-80 bg-[#161622] border-r border-white/5 flex flex-col transition-transform duration-300
        ${showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-0 md:opacity-0 md:overflow-hidden'}
      `}>
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Book className="text-[#A78BFA]" size={20} />
            Context
          </h2>
          <button onClick={() => setShowSidebar(false)} className="md:hidden text-slate-400">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Select Documents</p>
          {books.map(book => (
            <div
              key={book.book_id}
              onClick={() => toggleBookSelection(book.book_id)}
              className={`
                p-3 rounded-xl border cursor-pointer transition-all flex items-start gap-3
                ${selectedBookIds.includes(book.book_id)
                  ? 'bg-[#A78BFA]/10 border-[#A78BFA]/50 shadow-[0_0_15px_rgba(167,139,250,0.1)]'
                  : 'bg-[#1E1E2E] border-white/5 hover:border-white/10'}
              `}
            >
              <div className={`mt-1 w-4 h-4 rounded-full border flex items-center justify-center ${selectedBookIds.includes(book.book_id) ? 'bg-[#A78BFA] border-[#A78BFA]' : 'border-slate-500'}`}>
                {selectedBookIds.includes(book.book_id) && <CheckCircle2 size={10} className="text-[#161622]" />}
              </div>
              <div className="overflow-hidden">
                <h4 className={`text-sm font-semibold truncate ${selectedBookIds.includes(book.book_id) ? 'text-white' : 'text-slate-300'}`}>
                  {book.title}
                </h4>
                <p className="text-xs text-slate-500 truncate">{book.author}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-white/5 bg-[#13131D]">
          <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-white/10 rounded-2xl cursor-pointer hover:border-[#A78BFA]/50 hover:bg-white/5 transition-all group">
            {isUploading ? <Loader2 className="animate-spin text-[#A78BFA]" /> : (
              <>
                <UploadCloud className="text-slate-500 group-hover:text-[#A78BFA] mb-2" size={24} />
                <span className="text-xs text-slate-400 group-hover:text-white">Upload PDF/TXT</span>
              </>
            )}
            <input type="file" className="hidden" onChange={handleFileUpload} disabled={isUploading} />
          </label>
        </div>
      </aside>

      {/* --- MAIN CHAT AREA --- */}
      <main className="flex-1 flex flex-col relative w-full">
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0F1016]/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <button onClick={() => setShowSidebar(!showSidebar)} className="p-2 rounded-lg hover:bg-white/5 text-slate-400">
              <Menu size={20} />
            </button>
            <div className="flex items-center gap-2">
              <Sparkles className="text-[#A78BFA]" size={20} />
              <h1 className="text-lg font-bold text-white">Agent Chat</h1>
            </div>
          </div>

          <div className="flex items-center bg-[#1E1E2E] rounded-lg p-1 border border-white/5">
            <Globe size={14} className="ml-2 mr-2 text-slate-400" />
            {["English", "Hindi", "Tamil"].map(lang => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${language === lang ? 'bg-[#A78BFA] text-white' : 'text-slate-400 hover:text-white'}`}
              >
                {lang}
              </button>
            ))}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-60">
              <Bot size={48} className="mb-4 text-[#A78BFA]" />
              <p className="text-lg font-medium">How can I help you today?</p>
              <p className="text-sm">Ask about your books or search the web!</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 
                ${msg.role === 'user' ? 'bg-gradient-to-br from-emerald-400 to-cyan-500' : 'bg-gradient-to-br from-[#6366F1] to-[#8B5CF6]'}`}>
                {msg.role === 'user' ? <User size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
              </div>
              <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed shadow-xl border
                ${msg.role === 'user' 
                  ? 'bg-[#1E1E2E] border-emerald-500/20 text-white rounded-tr-none' 
                  : 'bg-[#1E1E2E] border-purple-500/20 text-slate-200 rounded-tl-none'}
                ${msg.role === 'system' ? 'border-red-500/50 bg-red-500/10 text-red-200' : ''}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-[#1E1E2E] flex items-center justify-center border border-white/10">
                <Bot size={14} className="text-slate-400" />
              </div>
              <div className="bg-[#1E1E2E] p-4 rounded-2xl rounded-tl-none border border-white/5 flex gap-2">
                <div className="w-2 h-2 bg-[#A78BFA] rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-[#A78BFA] rounded-full animate-bounce delay-75" />
                <div className="w-2 h-2 bg-[#A78BFA] rounded-full animate-bounce delay-150" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* ✅ FIXED INPUT AREA: Disabled state removed for book selection */}
        <div className="p-4 border-t border-white/5 bg-[#0F1016]">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              // Unified placeholder
              placeholder="Ask anything, search the web, or discuss a book..."
              // Enabled by default (unless loading)
              disabled={isLoading}
              className="w-full bg-[#1E1E2E] text-white rounded-full pl-6 pr-14 py-4 border border-white/10 focus:outline-none focus:border-[#A78BFA] focus:ring-1 focus:ring-[#A78BFA] transition-all disabled:opacity-50 placeholder-slate-500"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2.5 bg-[#A78BFA] hover:bg-[#8B5CF6] text-white rounded-full transition-colors disabled:bg-slate-700"
            >
              <Send size={18} />
            </button>
          </form>
          <p className="text-center text-[10px] text-slate-600 mt-2">
            AI can make mistakes. Please review responses.
          </p>
        </div>
      </main>
    </div>
  );
};

export default AgentChat;
