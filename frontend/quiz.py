import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def show_quiz_page():
    st.markdown("## 🧠 Knowledge Quiz")
    
    # --- BOOK SELECTION ---
    try:
        books = requests.get(f"{API_URL}/books/").json()
        book_map = {b['title']: b['book_id'] for b in books}
    except: st.error("Backend offline."); return

    if not books: st.info("Upload a book first."); return

    c1, c2 = st.columns([2, 1])
    with c1:
        sel_book = st.selectbox("Select Book for Quiz", list(book_map.keys()))
    with c2:
        # Language Selector for Quiz
        q_lang = st.selectbox("Quiz Language", ["English", "Hindi", "Tamil", "Marathi", "Bengali"])
        lang_codes = {"English": "en-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Marathi": "mr-IN", "Bengali": "bn-IN"}

    if st.button("🎲 Generate Quiz"):
        with st.spinner(f"Generating Quiz in {q_lang}..."):
            try:
                res = requests.get(f"{API_URL}/quiz/generate/{book_map[sel_book]}", params={"lang": lang_codes[q_lang]})
                if res.status_code == 200:
                    st.session_state['quiz_data'] = res.json().get("quiz", [])
                    st.session_state['quiz_answers'] = {}
                else:
                    st.error("Failed to generate quiz.")
            except: st.error("Connection failed.")

    # --- RENDER QUIZ ---
    if 'quiz_data' in st.session_state and st.session_state['quiz_data']:
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state['quiz_data']):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio(f"Select answer:", q['options'], key=f"q_{i}", label_visibility="collapsed")
                st.divider()
            
            if st.form_submit_button("Submit Answers"):
                score = 0
                for i, q in enumerate(st.session_state['quiz_data']):
                    user_ans = st.session_state.get(f"q_{i}")
                    if user_ans == q['answer']:
                        score += 1
                        st.success(f"Q{i+1}: Correct! ({q['answer']})")
                    else:
                        st.error(f"Q{i+1}: Wrong. Correct was: {q['answer']}")
                
                st.markdown(f"### 🏆 Final Score: {score} / {len(st.session_state['quiz_data'])}")