import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

def show_my_books_page():
    st.title("My Books")
    st.markdown("Manage your uploaded documents and generate summaries.")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Refresh List", use_container_width=True):
            st.rerun()

    try:
        res = requests.get(f"{API_URL}/books/")
        if res.status_code == 200:
            books = res.json()
        else:
            st.error("Failed to fetch books.")
            return
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return

    if not books:
        st.info("No books found. Go to the Dashboard to upload one!")
        return

    # Sort newest first
    books = sorted(books, key=lambda x: x.get('book_id', 0), reverse=True)

    for book in books:
        book_id = book['book_id']
        title = book['title']
        author = book.get('author') or "Unknown Author"
        status = book.get('status', 'pending')
        
        # --- SHOW COUNTS HERE (Task 8 Updates) ---
        word_count = book.get('word_count', 0)
        char_count = book.get('char_count', 0)
        
        # Calculate Reading Time on the fly (Avg 200 words/min)
        read_time = max(1, round(word_count / 200))
        
        with st.expander(f"{title}  |  {author}", expanded=False):
            
            c1, c2, c3 = st.columns([2, 2, 2])
            
            with c1:
                st.caption("Metadata")
                st.write(f"**Status:** {status.replace('_', ' ').title()}")
                st.write(f"**Words:** {word_count:,}") 
                st.write(f"**Chars:** {char_count:,}") 
                # NEW: Show Reading Time
                st.caption(f"⏱️ ~{read_time} min read")

            with c2:
                st.caption("Actions")
                if status == 'text_extracted':
                    # Task 9: This button redirects to Summaries page where they choose Length
                    if st.button("✨ Generate Summary", key=f"sum_{book_id}", type="primary", use_container_width=True):
                        st.session_state['selected_book_id'] = book_id
                        st.session_state['current_page'] = "Summaries"
                        st.rerun()
                        
                elif status == 'completed':
                    if st.button("📄 View Summary", key=f"view_{book_id}", type="primary", use_container_width=True):
                        st.session_state['selected_book_id'] = book_id
                        st.session_state['current_page'] = "Summaries"
                        st.rerun()
                        
                elif status == 'processing':
                    st.info("Processing...")
                elif status == 'failed':
                    st.error("Extraction failed.")

            with c3:
                st.caption("Manage")
                if st.button("Delete Book", key=f"del_{book_id}", use_container_width=True):
                    try:
                        requests.delete(f"{API_URL}/books/{book_id}")
                        st.success("Deleted!")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Delete failed.")