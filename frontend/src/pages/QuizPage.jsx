import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, CheckCircle2, XCircle, Trophy, 
  RefreshCw, Play, Loader2, BookOpen, Lightbulb
} from 'lucide-react';
import confetti from 'canvas-confetti';

const API_URL = "http://127.0.0.1:8000";

const LANG_CODES = {
  "English": "en-IN",
  "Hindi": "hi-IN",
  "Tamil": "ta-IN",
  "Marathi": "mr-IN",
  "Bengali": "bn-IN"
};

const QuizPage = () => {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState("");
  const [language, setLanguage] = useState("English");
  
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userAnswers, setUserAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  // --- 1. FETCH BOOKS (Auth Token সহ) ---
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_URL}/books/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setBooks(data);
          if (data.length > 0) setSelectedBookId(data[0].book_id);
        }
      } catch (err) { console.error("Failed to fetch books"); }
    };
    fetchBooks();
  }, []);

  // --- 2. GENERATE QUIZ ---
  const handleGenerate = async () => {
    if (!selectedBookId) return;
    setLoading(true);
    setQuizData(null);
    setSubmitted(false);
    setUserAnswers({});
    setScore(0);

    try {
      const token = localStorage.getItem("token");
      const langCode = LANG_CODES[language];
      const res = await fetch(`${API_URL}/quiz/generate/${selectedBookId}?lang=${langCode}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setQuizData(data.quiz); 
      } else {
        alert("Failed to generate quiz.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // --- 3. HANDLE SELECTION ---
  const handleSelectOption = (qIndex, option) => {
    if (submitted) return; 
    setUserAnswers(prev => ({ ...prev, [qIndex]: option }));
  };

  // --- 4. SUBMIT & SCORE ---
  const handleSubmit = () => {
    let newScore = 0;
    quizData.forEach((q, idx) => {
      if (userAnswers[idx] === q.answer) newScore += 1;
    });
    setScore(newScore);
    setSubmitted(true);

    if (newScore > quizData.length / 2) {
      confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">
      {/* HEADER অংশ আগের মতোই থাকবে */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
             <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                <BrainCircuit size={24} />
             </div>
             <div>
                <h1 className="text-xl font-bold text-white">Knowledge Quiz</h1>
                <p className="text-xs text-slate-400">Test your understanding</p>
             </div>
          </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {!quizData && (
            <div className="max-w-2xl mx-auto bg-[#1E1E2E] rounded-3xl p-8 border border-white/5 shadow-2xl text-center">
               <Trophy size={48} className="mx-auto text-yellow-400 mb-4" />
               <h2 className="text-2xl font-bold mb-2">Ready to Challenge Yourself?</h2>
               <p className="text-slate-400 mb-8">Select a book and language to generate a custom AI quiz.</p>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left">
                  <div>
                     <label className="text-xs font-bold text-slate-500 uppercase ml-1">Select Book</label>
                     <div className="relative mt-2">
                        <BookOpen className="absolute left-4 top-3.5 text-slate-500" size={18} />
                        <select 
                           value={selectedBookId}
                           onChange={(e) => setSelectedBookId(e.target.value)}
                           className="w-full bg-[#161622] text-white pl-12 pr-4 py-3 rounded-xl border border-white/10 outline-none focus:border-purple-500 transition-colors"
                        >
                           {books.map(b => <option key={b.book_id} value={b.book_id}>{b.title}</option>)}
                        </select>
                     </div>
                  </div>
                  <div>
                     <label className="text-xs font-bold text-slate-500 uppercase ml-1">Language</label>
                     <select 
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="w-full mt-2 bg-[#161622] text-white p-3 rounded-xl border border-white/10 outline-none focus:border-purple-500 transition-colors"
                     >
                        {Object.keys(LANG_CODES).map(lang => <option key={lang} value={lang}>{lang}</option>)}
                     </select>
                  </div>
               </div>

               <button 
                  onClick={handleGenerate}
                  disabled={loading || books.length === 0}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-purple-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
               >
                  {loading ? <Loader2 className="animate-spin" /> : <Play size={20} fill="currentColor" />}
                  {loading ? "Generating Questions..." : "Start Quiz"}
               </button>
            </div>
          )}

          {quizData && (
            <div className="max-w-3xl mx-auto space-y-6 animate-fade-in pb-20">
              {/* Score Header */}
              {submitted && (
                  <div className="bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 rounded-2xl p-6 flex items-center justify-between shadow-lg shadow-emerald-500/10">
                    <div>
                       <h3 className="text-xl font-bold text-emerald-400">Quiz Completed!</h3>
                       <p className="text-slate-300">You scored <span className="text-white font-bold text-lg">{score}</span> out of {quizData.length}</p>
                    </div>
                    <div className="text-5xl font-black text-white drop-shadow-lg">
                       {Math.round((score / quizData.length) * 100)}%
                    </div>
                  </div>
              )}

              {quizData.map((q, idx) => {
                  const isCorrectAnswer = userAnswers[idx] === q.answer;
                  return (
                    <div key={idx} className="bg-[#1E1E2E] rounded-2xl p-6 border border-white/5 shadow-xl">
                       <h3 className="text-lg font-semibold text-white mb-4 flex gap-3">
                          <span className="text-slate-500 font-mono">Q{idx + 1}.</span> {q.question}
                       </h3>
                       <div className="space-y-2">
                          {q.options.map((opt, oIdx) => {
                              // ✅ FIX: 'resulting =' মুছে ফেলা হয়েছে
                              const isSelected = userAnswers[idx] === opt;
                              const isCorrectOption = q.answer === opt;
                              
                              let cardClass = "border-white/5 hover:bg-white/5 text-slate-300"; 
                              if (!submitted && isSelected) {
                                 cardClass = "border-purple-500 bg-purple-500/10 text-white ring-1 ring-purple-500";
                              }
                              if (submitted) {
                                 if (isCorrectOption) {
                                    cardClass = "border-emerald-500 bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500 font-bold";
                                 } else if (isSelected && !isCorrectOption) {
                                    cardClass = "border-rose-500 bg-rose-500/10 text-rose-400 ring-1 ring-rose-500 opacity-50";
                                 } else {
                                    cardClass = "opacity-40 border-white/5"; 
                                 }
                              }
                              return (
                                 <div 
                                    key={oIdx}
                                    onClick={() => handleSelectOption(idx, opt)}
                                    className={`p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${cardClass}`}
                                 >
                                    <span>{opt}</span>
                                    {submitted && isCorrectOption && <CheckCircle2 size={18} className="text-emerald-400" />}
                                    {submitted && isSelected && !isCorrectOption && <XCircle size={18} className="text-rose-400" />}
                                 </div>
                              );
                          })}
                       </div>
                       {submitted && (
                          <div className={`mt-4 p-4 rounded-xl flex gap-3 items-start border ${isCorrectAnswer ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-rose-500/5 border-rose-500/20'}`}>
                              <div className={`mt-1 ${isCorrectAnswer ? 'text-emerald-400' : 'text-rose-400'}`}>
                                 <Lightbulb size={20} />
                              </div>
                              <div>
                                 <p className={`text-xs font-bold uppercase mb-1 ${isCorrectAnswer ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {isCorrectAnswer ? "Correct!" : "Explanation"}
                                 </p>
                                 <p className="text-sm text-slate-300 leading-relaxed">
                                    {q.explanation}
                                 </p>
                              </div>
                          </div>
                       )}
                    </div>
                  );
              })}
              <div className="flex gap-4 pt-4">
                  {!submitted ? (
                    <button 
                       onClick={handleSubmit}
                       disabled={Object.keys(userAnswers).length !== quizData.length}
                       className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                       Submit Answers
                    </button>
                  ) : (
                    <button 
                       onClick={handleGenerate}
                       className="flex-1 bg-[#2A2B3D] hover:bg-[#35364F] text-white font-bold py-4 rounded-xl transition-all border border-white/10 flex items-center justify-center gap-2"
                    >
                       <RefreshCw size={18} /> Generate New Quiz
                    </button>
                  )}
              </div>
            </div>
          )}
      </div>
    </div>
  );
};

export default QuizPage;