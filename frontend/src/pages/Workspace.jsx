import React, { useState, useRef, useEffect } from 'react';
import { 
  Palette, Save, Trash2, Eraser, PenTool, Type, Download, 
  Share2, UserPlus, Check, X, FileImage, FileText, ChevronDown, AlignLeft
} from 'lucide-react';
import jsPDF from 'jspdf';

const API_URL = "http://127.0.0.1:8000";

const Workspace = () => {
  const canvasRef = useRef(null);
  const contextRef = useRef(null);
  
  // Workspace State
  const [workspaceName, setWorkspaceName] = useState("Untitled Project");
  const [notes, setNotes] = useState("");
  const [savedStatus, setSavedStatus] = useState(""); // 'saving', 'saved', 'error'

  // Drawing State
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState("pen");
  const [color, setColor] = useState("#A78BFA");
  const [brushSize, setBrushSize] = useState(3);

  // UI State
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  
  // Share State
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("viewer");
  const [sharedUsers, setSharedUsers] = useState([]);

  // --- 1. INITIALIZE CANVAS ---
  useEffect(() => {
    const canvas = canvasRef.current;
    // Set resolution to double container size for sharp rendering on retina screens
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = canvas.offsetHeight * 2;
    canvas.style.width = `${canvas.offsetWidth}px`;
    canvas.style.height = `${canvas.offsetHeight}px`;

    const context = canvas.getContext("2d");
    // Scale context to match resolution
    context.scale(2, 2);
    context.lineCap = "round";
    context.strokeStyle = color;
    context.lineWidth = brushSize;
    contextRef.current = context;
  }, []);

  useEffect(() => {
    if (contextRef.current) {
      contextRef.current.strokeStyle = tool === "eraser" ? "#1E1E2E" : color;
      contextRef.current.lineWidth = brushSize;
    }
  }, [color, brushSize, tool]);

  // --- 2. DRAWING LOGIC ---
  const startDrawing = ({ nativeEvent }) => {
    const { offsetX, offsetY } = nativeEvent;
    contextRef.current.beginPath();
    contextRef.current.moveTo(offsetX, offsetY);
    setIsDrawing(true);
  };

  const finishDrawing = () => {
    contextRef.current.closePath();
    setIsDrawing(false);
  };

  const draw = ({ nativeEvent }) => {
    if (!isDrawing) return;
    const { offsetX, offsetY } = nativeEvent;
    contextRef.current.lineTo(offsetX, offsetY);
    contextRef.current.stroke();
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    // Clear based on actual pixel dimensions
    contextRef.current.clearRect(0, 0, canvas.width, canvas.height);
  };

  // --- 3. EXPORT FUNCTIONS (UPDATED) ---
  const handleExport = (format) => {
    const canvas = canvasRef.current;
    const safeName = workspaceName.replace(/[^a-z0-9]/gi, '_').toLowerCase() || "workspace";
    
    if (format === 'png' || format === 'jpeg') {
      // --- Image Export ---
      const url = canvas.toDataURL(`image/${format}`);
      const link = document.createElement('a');
      link.download = `${safeName}_sketch.${format}`;
      link.href = url;
      link.click();
    } else if (format === 'txt') {
      // --- Notes (TXT) Export ---
      const element = document.createElement("a");
      const file = new Blob([notes], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = `${safeName}_notes.txt`;
      document.body.appendChild(element); // Required for FireFox
      element.click();
      document.body.removeChild(element);
    } else if (format === 'pdf') {
      // --- Combined PDF Export (Image + Notes) ---
      const imgData = canvas.toDataURL("image/png");
      // Use A4 portrait mode (p = portrait, mm = millimeters, a4 = page size)
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const pageWidth = pdf.internal.pageSize.getWidth();
      // const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;
      let currentY = margin;

      // 1. Title
      pdf.setFontSize(18);
      pdf.text(workspaceName, margin, currentY);
      currentY += 10;

      // 2. Image
      // Calculate image dimensions to fit width while maintaining aspect ratio
      const imgProps = pdf.getImageProperties(imgData);
      const pdfImgWidth = pageWidth - (margin * 2);
      const pdfImgHeight = (imgProps.height * pdfImgWidth) / imgProps.width;
      
      pdf.addImage(imgData, 'PNG', margin, currentY, pdfImgWidth, pdfImgHeight);
      currentY += pdfImgHeight + 15;

      // 3. Notes
      if (notes.trim()) {
          pdf.setFontSize(14);
          pdf.text("Project Notes:", margin, currentY);
          currentY += 8;

          pdf.setFontSize(11);
          // Split text into lines that fit the page width
          const splitNotes = pdf.splitTextToSize(notes, pageWidth - (margin * 2));
          pdf.text(splitNotes, margin, currentY);
      }

      pdf.save(`${safeName}_combined.pdf`);
    }
    setShowExportMenu(false);
  };

  // --- 4. SAVE WORKSPACE ---
  const saveWorkspace = async () => {
    setSavedStatus("saving");
    try {
      const canvasData = canvasRef.current.toDataURL(); // Save image as Base64 string
      const payload = {
        name: workspaceName,
        notes: notes,
        canvas_image: canvasData,
        shared_with: sharedUsers
      };

      const res = await fetch(`${API_URL}/workspaces/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSavedStatus("saved");
        setTimeout(() => setSavedStatus(""), 2000);
      } else {
        setSavedStatus("error");
      }
    } catch (e) {
      console.error(e);
      setSavedStatus("error");
    }
  };

  // --- 5. SHARE LOGIC ---
  const handleInvite = () => {
    if (inviteEmail) {
      setSharedUsers([...sharedUsers, { email: inviteEmail, role: inviteRole }]);
      setInviteEmail("");
    }
  };

  const removeUser = (email) => {
    setSharedUsers(sharedUsers.filter(u => u.email !== email));
  };

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white relative">
      
      {/* HEADER */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md sticky top-0 z-10">
         <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                <Palette size={24} />
            </div>
            <div>
               {/* Editable Title */}
               <input 
                  type="text" 
                  value={workspaceName}
                  onChange={(e) => setWorkspaceName(e.target.value)}
                  className="bg-transparent text-xl font-bold text-white focus:outline-none focus:border-b border-purple-500 w-64"
               />
               <p className="text-xs text-slate-400">
                  {savedStatus === "saving" ? "Saving..." : savedStatus === "saved" ? "All changes saved" : "Unsaved changes"}
               </p>
            </div>
         </div>

         <div className="flex gap-3">
            {/* Share Button */}
            <button onClick={() => setShowShareModal(true)} className="flex items-center gap-2 px-4 py-2 bg-[#1E1E2E] rounded-lg text-sm font-bold border border-white/10 hover:bg-white/5 transition-colors">
               <UserPlus size={16} /> Share
            </button>

            {/* Export Dropdown */}
            <div className="relative">
               <button onClick={() => setShowExportMenu(!showExportMenu)} className="flex items-center gap-2 px-4 py-2 bg-[#1E1E2E] rounded-lg text-sm font-bold border border-white/10 hover:bg-white/5 transition-colors">
                  <Download size={16} /> Export <ChevronDown size={14} />
               </button>
               {showExportMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-[#1E1E2E] border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden">
                     <div className="p-2 text-xs font-bold text-slate-500 uppercase">Image Only</div>
                     <button onClick={() => handleExport('png')} className="w-full text-left px-4 py-2 hover:bg-white/5 text-sm flex items-center gap-2 text-slate-300"><FileImage size={16}/> PNG Image</button>
                     <button onClick={() => handleExport('jpeg')} className="w-full text-left px-4 py-2 hover:bg-white/5 text-sm flex items-center gap-2 text-slate-300"><FileImage size={16}/> JPEG Image</button>
                     <div className="border-t border-white/10 my-1"></div>
                     <div className="p-2 text-xs font-bold text-slate-500 uppercase">Notes & Combined</div>
                     <button onClick={() => handleExport('txt')} className="w-full text-left px-4 py-2 hover:bg-white/5 text-sm flex items-center gap-2 text-slate-300"><AlignLeft size={16}/> Notes (TXT)</button>
                     <button onClick={() => handleExport('pdf')} className="w-full text-left px-4 py-2 hover:bg-white/5 text-sm flex items-center gap-2 text-slate-300"><FileText size={16}/> Combined PDF</button>
                  </div>
               )}
            </div>

            {/* Save Button */}
            <button onClick={saveWorkspace} className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg text-sm font-bold shadow-lg hover:shadow-purple-500/20 transition-all">
               {savedStatus === "saved" ? <Check size={16} /> : <Save size={16} />}
               {savedStatus === "saved" ? "Saved" : "Save"}
            </button>
         </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 overflow-hidden p-6 flex flex-col lg:flex-row gap-6">
         {/* NOTES */}
         <div className="w-full lg:w-1/3 flex flex-col gap-4">
            <div className="bg-[#1E1E2E] p-4 rounded-t-2xl border-b border-white/5 flex items-center justify-between">
               <div className="flex items-center gap-2 text-slate-300 font-bold"><Type size={18} /> Project Notes</div>
            </div>
            <textarea 
               value={notes} onChange={(e) => setNotes(e.target.value)}
               placeholder="Write summary notes here..."
               className="flex-1 bg-[#1E1E2E] rounded-2xl p-6 text-slate-300 resize-none outline-none border border-white/5 focus:border-purple-500/50 transition-all"
            />
         </div>

         {/* CANVAS */}
         <div className="flex-1 bg-[#1E1E2E] rounded-3xl border border-white/5 flex flex-col overflow-hidden shadow-2xl relative">
            <div className="h-16 border-b border-white/5 bg-[#161622] flex items-center justify-between px-6">
               <div className="flex items-center gap-4">
                  <div className="flex bg-[#0F1016] p-1 rounded-lg border border-white/5">
                     <button onClick={() => setTool("pen")} className={`p-2 rounded-md transition-all ${tool === 'pen' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}><PenTool size={18} /></button>
                     <button onClick={() => setTool("eraser")} className={`p-2 rounded-md transition-all ${tool === 'eraser' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'}`}><Eraser size={18} /></button>
                  </div>
                  <div className="flex items-center gap-2 border-l border-white/10 pl-4">
                     {["#A78BFA", "#34D399", "#60A5FA", "#F472B6", "#FBBF24", "#FFFFFF"].map(c => (
                        <button key={c} onClick={() => { setColor(c); setTool("pen"); }} className={`w-6 h-6 rounded-full border-2 transition-transform hover:scale-110 ${color === c && tool === 'pen' ? 'border-white' : 'border-transparent'}`} style={{ backgroundColor: c }} />
                     ))}
                  </div>
               </div>
               <button onClick={clearCanvas} className="text-slate-400 hover:text-red-400"><Trash2 size={20} /></button>
            </div>
            <div className="flex-1 relative cursor-crosshair bg-[#1E1E2E]">
               {/* Ensure canvas style matches CSS dimensions while internal resolution is higher */}
               <canvas ref={canvasRef} onMouseDown={startDrawing} onMouseUp={finishDrawing} onMouseLeave={finishDrawing} onMouseMove={draw} className="w-full h-full block touch-none" />
            </div>
         </div>
      </div>

      {/* SHARE MODAL */}
      {showShareModal && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
           <div className="bg-[#1E1E2E] w-[450px] p-6 rounded-3xl border border-white/10 shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                 <h2 className="text-xl font-bold text-white flex items-center gap-2"><Share2 size={20} /> Share Workspace</h2>
                 <button onClick={() => setShowShareModal(false)} className="text-slate-400 hover:text-white"><X size={20}/></button>
              </div>
              
              <div className="flex gap-2 mb-6">
                 <input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="Enter email address" className="flex-1 bg-[#161622] border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-purple-500" />
                 <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)} className="bg-[#161622] border border-white/10 rounded-xl px-3 text-slate-300 outline-none">
                    <option value="viewer">Viewer</option>
                    <option value="editor">Editor</option>
                 </select>
                 <button onClick={handleInvite} className="bg-purple-600 px-4 rounded-xl text-white font-bold hover:bg-purple-500">Invite</button>
              </div>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                 <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">People with access</h3>
                 <div className="flex items-center justify-between p-3 bg-[#161622] rounded-xl border border-white/5">
                    <div className="flex items-center gap-3">
                       <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">You</div>
                       <div><p className="text-sm font-bold text-white">You (Owner)</p><p className="text-xs text-slate-500">Workspace Admin</p></div>
                    </div>
                 </div>
                 {sharedUsers.map((user, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[#161622] rounded-xl border border-white/5">
                       <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">{user.email[0].toUpperCase()}</div>
                          <div><p className="text-sm font-bold text-white">{user.email}</p><p className="text-xs text-slate-500 capitalize">{user.role}</p></div>
                       </div>
                       <button onClick={() => removeUser(user.email)} className="text-slate-500 hover:text-red-400 text-xs">Remove</button>
                    </div>
                 ))}
                 {sharedUsers.length === 0 && <p className="text-center text-slate-500 text-sm py-2">No one invited yet.</p>}
              </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default Workspace;