import React, { useState } from 'react';
import { 
  Youtube, Video, Send, UploadCloud, 
  Loader2, FileText, Sparkles, Mic, Play, 
  AlertCircle, ExternalLink 
} from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

const MediaSummarizer = () => {
  const [activeTab, setActiveTab] = useState('youtube'); // 'youtube' or 'meeting'
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const resetState = (tab) => {
    setActiveTab(tab);
    setData(null);
    setError(null);
    setUrl('');
    setFile(null);
  };

  const handleProcess = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      if (activeTab === 'youtube') {
        if (!url.trim()) return;
        const response = await fetch(`${API_URL}/youtube/summarize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
        if (!response.ok) throw new Error("Invalid YouTube link or no captions found.");
        setData(await response.json());
      } else {
        if (!file) throw new Error("Please upload a file first.");
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`${API_URL}/meeting/process-meeting`, {
          method: 'POST',
          body: formData
        });
        if (!response.ok) throw new Error("Failed to process meeting file.");
        setData(await response.json());
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0F1016] text-slate-200 overflow-hidden font-sans">
      
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <Sparkles className="text-[#A78BFA]" size={24} />
          <h1 className="text-lg font-bold text-white">Media Intelligence</h1>
        </div>
        
        {/* Tab Switcher */}
        <div className="flex bg-[#1E1E2E] p-1 rounded-xl border border-white/5">
          <button 
            onClick={() => resetState('youtube')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'youtube' ? 'bg-[#A78BFA] text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
          >
            <Youtube size={14} /> YouTube
          </button>
          <button 
            onClick={() => resetState('meeting')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'meeting' ? 'bg-[#A78BFA] text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
          >
            <Video size={14} /> Meeting File
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
        <div className="max-w-5xl mx-auto space-y-8">
          
          {/* Input Card */}
          <section className="bg-[#161622] p-8 rounded-3xl border border-white/5 shadow-2xl transition-all">
            {activeTab === 'youtube' ? (
              <form onSubmit={handleProcess} className="space-y-4">
                <h2 className="text-xl font-semibold text-white">YouTube Summarizer</h2>
                <p className="text-sm text-slate-400">Generate instant notes from any video using Gemini Pro.</p>
                <div className="relative group">
                  <input 
                    type="text" 
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full bg-[#1E1E2E] text-white rounded-2xl pl-6 pr-40 py-5 border border-white/10 outline-none focus:border-[#A78BFA] transition-all"
                  />
                  <button 
                    disabled={isLoading || !url.trim()} 
                    className="absolute right-3 top-3 bottom-3 px-6 bg-[#A78BFA] hover:bg-[#8B5CF6] rounded-xl text-white font-bold flex items-center gap-2 transition-all disabled:opacity-50"
                  >
                    {isLoading ? <Loader2 className="animate-spin" size={18} /> : <Play size={16} />} 
                    Summarize
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Meeting Minutes Generator</h2>
                <p className="text-sm text-slate-400">Upload recording to transcribe with Whisper and summarize with LLaMA 3.</p>
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-white/10 rounded-2xl cursor-pointer hover:border-indigo-500/50 hover:bg-white/5 transition-all">
                  <UploadCloud className="text-slate-500 mb-2" size={32} />
                  <span className="text-xs text-slate-400">{file ? file.name : "Drag and drop or click to upload MP4, MP3, or WAV"}</span>
                  <input type="file" className="hidden" onChange={(e) => setFile(e.target.files[0])} accept="video/*,audio/*" />
                </label>
                <button 
                  onClick={handleProcess}
                  disabled={isLoading || !file}
                  className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Video size={20} />}
                  {isLoading ? "Processing Media..." : "Generate Meeting Minutes"}
                </button>
              </div>
            )}
            {error && (
              <div className="mt-4 flex items-center gap-2 text-red-400 text-sm bg-red-400/10 p-3 rounded-lg border border-red-400/20">
                <AlertCircle size={16} /> <span>{error}</span>
              </div>
            )}
          </section>

          {/* Result Area */}
          {data && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Media Info / Transcript */}
              <div className="space-y-6">
                {activeTab === 'youtube' && (
                  <div className="bg-[#161622] p-4 rounded-3xl border border-white/5 shadow-xl">
                    <img src={data.thumbnail} alt="Thumbnail" className="w-full rounded-2xl aspect-video object-cover mb-4" />
                    <a href={url} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-2 text-sm bg-white/5 py-2 rounded-lg hover:bg-white/10 transition-all">
                      Watch Video <ExternalLink size={14} />
                    </a>
                  </div>
                )}
                <div className="bg-[#161622] rounded-3xl border border-white/5 h-[400px] flex flex-col shadow-xl">
                  <div className="p-4 border-b border-white/5 font-bold flex items-center gap-2">
                    <Mic size={16} className="text-indigo-400" /> Source Transcript
                  </div>
                  <div className="p-6 overflow-y-auto text-sm text-slate-400 leading-relaxed custom-scrollbar whitespace-pre-line">
                    {data.transcript || "Transcript generated successfully."}
                  </div>
                </div>
              </div>

              {/* AI Summary Section */}
              <div className="bg-[#161622] rounded-3xl border border-white/5 flex flex-col h-full shadow-xl">
                <div className="p-4 border-b border-white/5 font-bold flex items-center gap-2 text-[#A78BFA]">
                  <FileText size={18} /> AI Detailed Notes
                </div>
                <div className="p-8 overflow-y-auto text-slate-200 custom-scrollbar">
                  <div className="prose prose-invert max-w-none text-base leading-loose whitespace-pre-line">
                    {data.summary}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="p-4 bg-[#0F1016] border-t border-white/5 text-center text-[10px] text-slate-600">
        Media Intelligence Portal | Powered by Gemini & Groq
      </footer>
    </div>
  );
};

export default MediaSummarizer;