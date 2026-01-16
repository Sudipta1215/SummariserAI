import streamlit as st
import requests
from streamlit_agraph import agraph, Node, Edge, Config

API_URL = "http://127.0.0.1:8000"

def show_graph_page():
    st.markdown("## 🕸️ Interactive Knowledge Graph")

    # 1. User & Role Check
    user_info = st.session_state.get('user_info', {})
    user_id = user_info.get('user_id')
    role = user_info.get('role', 'user')

    if not user_id:
        st.warning("⚠️ Please login to view the Knowledge Graph.")
        return

    # 2. Fetch Books
    try:
        response = requests.get(f"{API_URL}/books/")
        if response.status_code == 200:
            all_books = response.json()
            
            # ✅ FIX: If Admin, show ALL books. If User, show only theirs.
            if role == 'admin':
                my_books = all_books
            else:
                my_books = [b for b in all_books if b.get('user_id') == user_id]
            
            if not my_books:
                st.info("No books found. Upload one to get started!")
                return

            # 3. Selection UI
            col1, col2 = st.columns([3, 1])
            with col1:
                book_map = {f"{b['title']} (ID: {b['book_id']})": b['book_id'] for b in my_books}
                selected_title = st.selectbox("Select a Book to Analyze", list(book_map.keys()))
                selected_book_id = book_map[selected_title]
            
            with col2:
                st.write("") # Spacer
                st.write("") # Spacer
                generate_btn = st.button("🚀 Generate Graph", type="primary")

            # 4. Generate & Visualize
            if generate_btn:
                with st.spinner("🔍 Analyzing relationships..."):
                    res = requests.get(f"{API_URL}/graph/{selected_book_id}")
                    
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("nodes"):
                            visualize_graph(data)
                        else:
                            st.warning("No relationships found in this book text.")
                    else:
                        st.error("Backend Error: Could not generate graph.")
        else:
            st.error("Failed to load books list.")

    except Exception as e:
        st.error(f"Connection Error: {e}")

def visualize_graph(data):
    nodes = []
    edges = []

    # Create Nodes
    for n in data["nodes"]:
        nodes.append(Node(
            id=n["id"], 
            label=n["label"], 
            size=20, 
            shape="dot",
            color=n.get("color", "#F2B418") # Default Gold
        ))

    # Create Edges
    for e in data["edges"]:
        edges.append(Edge(
            source=e["source"], 
            target=e["target"], 
            label=e.get("relation", ""),
            color="#AFCBD5"
        ))

    config = Config(
        width=800,
        height=600,
        directed=True, 
        physics=True, 
        hierarchical=False
    )

    st.success(f"Graph generated with {len(nodes)} nodes and {len(edges)} connections!")
    agraph(nodes=nodes, edges=edges, config=config)