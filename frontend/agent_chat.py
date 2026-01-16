import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def show_chat_page():
    st.markdown("## 🤖 Multilingual Book Agent")

    # --- 1. SESSION STATE SETUP ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Check Login
    user_info = st.session_state.get('user_info', {})
    if not user_info:
        st.warning("⚠️ Please login to use the Agent.")
        return

    # --- 2. KNOWLEDGE CONTEXT (MOVED TO MAIN PAGE) ---
    # We use an expander so it stays clean but accessible
    with st.expander("📚 Knowledge Context & Upload (Click to Open/Close)", expanded=True):
        
        col1, col2 = st.columns([2, 1])

        # --- A. SELECT BOOKS (Left Column) ---
        with col1:
            st.subheader("Select Books to Chat With")
            try:
                res = requests.get(f"{API_URL}/books/")
                if res.status_code == 200:
                    all_books = res.json()
                    # Filter for current user (or all if admin)
                    if user_info.get('role') == 'admin':
                        my_books = all_books
                    else:
                        my_books = [b for b in all_books if b['user_id'] == user_info['user_id']]
                    
                    # Create Map
                    book_map = {f"{b['title']} (ID: {b['book_id']})": b['book_id'] for b in my_books}
                else:
                    my_books = []
                    book_map = {}
            except Exception as e:
                st.error(f"Failed to fetch books: {e}")
                book_map = {}

            selected_titles = st.multiselect(
                "Choose documents:", 
                options=list(book_map.keys()),
                help="The AI will answer questions based on the content of these books."
            )
            selected_ids = [book_map[t] for t in selected_titles]

        # --- B. UPLOAD NEW FILE (Right Column) ---
        with col2:
            st.subheader("Upload New File")
            uploaded_file = st.file_uploader("PDF/TXT/DOCX", type=["pdf", "txt", "docx"], label_visibility="collapsed")
            
            if uploaded_file:
                if st.button("Process & Add", type="primary"):
                    with st.spinner("Uploading..."):
                        files = {"file": uploaded_file}
                        data = {
                            "title": uploaded_file.name,
                            "author": "User Upload",
                            "user_id": user_info.get('user_id', 1) 
                        }
                        try:
                            res = requests.post(f"{API_URL}/books/", data=data, files=files)
                            if res.status_code == 200:
                                st.success(f"✅ Added!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {res.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")

    st.divider()

    # --- 3. CHAT INTERFACE ---
    
    # Language Selection (Horizontal)
    lang_mode = st.radio(
        "Response Language:", 
        ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Marathi"], 
        horizontal=True
    )

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Area
    if prompt := st.chat_input("Ask a question about the selected books..."):
        # 1. Show User Message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Validation
        if not selected_ids:
            response_text = "⚠️ Please select at least one book from the 'Knowledge Context' section above."
            st.chat_message("assistant").markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            # 3. Call Backend Agent
            with st.chat_message("assistant"):
                with st.spinner("🤖 Reading & Thinking..."):
                    try:
                        payload = {
                            "query": prompt,
                            "book_ids": selected_ids,
                            "language": lang_mode
                        }
                        res = requests.post(f"{API_URL}/agent/chat", json=payload)
                        
                        if res.status_code == 200:
                            response_text = res.json().get("response", "No response.")
                        else:
                            response_text = f"Error: {res.text}"
                            
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    except Exception as e:
                        st.error(f"Connection Error: {e}")