import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Controls, Background, useNodesState, useEdgesState, 
  MarkerType, ReactFlowProvider 
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { BookOpen, Share2, Network, GitMerge, Loader2 } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

// --- LAYOUT ALGORITHM (Auto-arrange nodes) ---
const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  const nodeWidth = 172;
  const nodeHeight = 40; // Slightly increased for padding
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: direction === 'LR' ? 'left' : 'top',
      sourcePosition: direction === 'LR' ? 'right' : 'bottom',
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

const KnowledgeGraph = () => {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState("");
  const [graphType, setGraphType] = useState("mindmap");
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // ✅ FIX 1: Add Auth Token to Book Fetching
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_URL}/books/`, {
          headers: {
            'Authorization': `Bearer ${token}` //
          }
        });
        if (res.ok) {
          const data = await res.json();
          setBooks(data);
          if (data.length > 0) setSelectedBookId(data[0].book_id);
        }
      } catch (err) {
        console.error("Failed to fetch books", err);
      }
    };
    fetchBooks();
  }, []);

  // ✅ FIX 2: Add Auth Token to Graph Generation
  const handleGenerate = async () => {
    if (!selectedBookId) return;
    setLoading(true);
    setSelectedNode(null);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/graph/generate/${selectedBookId}?type=${graphType}`, {
        headers: {
          'Authorization': `Bearer ${token}` //
        }
      });
      
      const data = await res.json();

      if (data && data.nodes) {
        const flowNodes = data.nodes.map((n) => ({
          id: n.id.toString(),
          data: { label: n.label, details: n.details, type: n.type },
          position: { x: 0, y: 0 },
          style: { 
            background: n.type === 'Character' ? '#E0E7FF' : '#F3E8FF',
            border: '1px solid #6366F1',
            borderRadius: '8px',
            fontSize: '11px',
            fontWeight: 'bold',
            padding: '10px',
            width: 150,
            color: '#1E1E2E',
            textAlign: 'center'
          },
        }));

        const flowEdges = data.edges.map((e, i) => ({
          id: `e${i}`,
          source: e.source.toString(),
          target: e.target.toString(),
          label: e.relation,
          type: 'smoothstep',
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: '#A78BFA' },
          style: { stroke: '#A78BFA' },
          labelStyle: { fill: '#94A3B8', fontSize: 10 }
        }));

        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
          flowNodes, 
          flowEdges, 
          graphType === 'mindmap' ? 'TB' : 'LR'
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      }
    } catch (err) {
      console.error("Graph Generation Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node.data);
  }, []);

  return (
    <div className="h-full flex flex-col bg-[#0F1016] text-white">
      {/* Header code remains same */}
      <div className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-[#0F1016]/90 backdrop-blur-md z-10">
         <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400"><Share2 size={24} /></div>
            <div>
                <h1 className="text-xl font-bold text-white">Interactive Knowledge Graph</h1>
                <p className="text-xs text-slate-400">Visualize complex relationships</p>
            </div>
         </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Controls */}
        <div className="w-80 bg-[#161622] border-r border-white/5 p-6 flex flex-col gap-6 z-20 shadow-2xl">
           <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">Source Material</label>
              <div className="relative mt-2">
                 <BookOpen className="absolute left-4 top-3.5 text-slate-500" size={18} />
                 <select 
                    value={selectedBookId}
                    onChange={(e) => setSelectedBookId(e.target.value)}
                    className="w-full bg-[#1E1E2E] text-white pl-12 pr-4 py-3 rounded-xl border border-white/10 outline-none focus:border-blue-500"
                 >
                    <option value="">Select a book...</option>
                    {books.map(b => <option key={b.book_id} value={b.book_id}>{b.title}</option>)}
                 </select>
              </div>
           </div>

           <div>
              <label className="text-xs font-bold text-slate-500 uppercase ml-1">Visualization Mode</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                 <button 
                    onClick={() => setGraphType('mindmap')}
                    className={`py-3 rounded-xl text-xs font-bold flex flex-col items-center gap-2 border transition-all ${graphType === 'mindmap' ? 'bg-blue-600 border-blue-500 text-white' : 'bg-[#1E1E2E] border-white/5 text-slate-400'}`}
                 >
                    <GitMerge size={20} /> Mind Map
                 </button>
                 <button 
                    onClick={() => setGraphType('network')}
                    className={`py-3 rounded-xl text-xs font-bold flex flex-col items-center gap-2 border transition-all ${graphType === 'network' ? 'bg-purple-600 border-purple-500 text-white' : 'bg-[#1E1E2E] border-white/5 text-slate-400'}`}
                 >
                    <Network size={20} /> Network
                 </button>
              </div>
           </div>

           <button 
              onClick={handleGenerate}
              disabled={loading || !selectedBookId}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
           >
              {loading ? <Loader2 className="animate-spin" /> : <Share2 size={20} />}
              {loading ? "Analyzing..." : "Generate Graph"}
           </button>

           {selectedNode && (
              <div className="mt-auto bg-[#1E1E2E] p-4 rounded-xl border border-white/10 animate-fade-in">
                 <h3 className="font-bold text-lg text-white mb-1">{selectedNode.label}</h3>
                 <span className="text-[10px] uppercase bg-white/10 px-2 py-1 rounded text-blue-300 font-bold tracking-wider">{selectedNode.type}</span>
                 <p className="text-sm text-slate-400 mt-3 leading-relaxed">
                    {selectedNode.details}
                 </p>
              </div>
           )}
        </div>

        {/* Right Canvas Area */}
        <div className="flex-1 bg-[#0F1016] relative" style={{ width: '100%', height: '100%' }}>
           <ReactFlowProvider>
              <ReactFlow
                 nodes={nodes}
                 edges={edges}
                 onNodesChange={onNodesChange}
                 onEdgesChange={onEdgesChange}
                 onNodeClick={onNodeClick}
                 fitView
                 className="bg-[#0F1016]"
              >
                 <Background color="#1E1E2E" gap={20} />
                 <Controls />
              </ReactFlow>
           </ReactFlowProvider>
           
           {!nodes.length && !loading && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 pointer-events-none">
                 <Share2 size={64} className="mb-4 opacity-20" />
                 <p>Select a book and click generate to visualize.</p>
              </div>
           )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;