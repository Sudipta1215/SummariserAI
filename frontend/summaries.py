import streamlit as st
import requests
import time
import difflib

API_URL = "http://127.0.0.1:8000"

# --- 🌍 WORLD LANGUAGES (Google) ---
WORLD_LANGS = {
    "English 🇺🇸": "en", "Spanish 🇪🇸": "es", "French 🇫🇷": "fr", "German 🇩🇪": "de",
    "Italian 🇮🇹": "it", "Portuguese 🇵🇹": "pt", "Russian 🇷🇺": "ru", "Chinese 🇨🇳": "zh-CN",
    "Japanese 🇯🇵": "ja", "Korean 🇰🇷": "ko", "Arabic 🇸🇦": "ar", "Turkish 🇹🇷": "tr"
}

# --- 🇮🇳 INDIC LANGUAGES (Sarvam) ---
INDIC_LANGS = {
    "Hindi 🇮🇳": "hi-IN", "Tamil 🇮🇳": "ta-IN", "Telugu 🇮🇳": "te-IN", 
    "Malayalam 🇮🇳": "ml-IN", "Kannada 🇮🇳": "kn-IN", "Marathi 🇮🇳": "mr-IN", 
    "Bengali 🇮🇳": "bn-IN", "Gujarati 🇮🇳": "gu-IN", "Punjabi 🇮🇳": "pa-IN", "Odia 🇮🇳": "od-IN"
}

def show_summaries_page():
    st.markdown("<h1 style='text-align: center;'>📚 Intelligent Summarizer</h1>", unsafe_allow_html=True)

    # --- 1. BOOK SELECTION ---
    try:
        books_res = requests.get(f"{API_URL}/books/")
        books = books_res.json() if books_res.status_code == 200 else []
    except:
        st.error("⚠️ Backend offline.")
        return

    if not books:
        st.info("No books uploaded. Please upload a book first.")
        return

    book_options = {b['title']: b for b in books}
    index = 0
    if 'selected_book_id' in st.session_state:
        for i, (title, b) in enumerate(book_options.items()):
            if b['book_id'] == st.session_state['selected_book_id']:
                index = i
                break

    col_sel, _ = st.columns([3, 1])
    with col_sel:
        selected_title = st.selectbox("Select Book", list(book_options.keys()), index=index)
    
    selected_book = book_options[selected_title]
    book_id = selected_book['book_id']

    # --- 2. TABS INTERFACE ---
    tab_gen, tab_hist, tab_comp = st.tabs(["✨ Generate New", "📜 Version History", "⚖️ Compare Versions"])

    # --- TAB 1: GENERATE NEW ---
    with tab_gen:
        st.subheader("⚙️ Configuration")
        c1, c2, c3 = st.columns(3)
        with c1:
            length = st.select_slider("📏 Length", options=["Short", "Medium", "Long"], value="Medium")
        with c2:
            style = st.radio("🎨 Style", ["Paragraph", "Bullet Points"], horizontal=True)
        with c3:
            detail = st.select_slider("🔍 Detail", options=["Concise", "Standard", "Detailed"], value="Standard")
            
        st.divider()

        # Generate Button
        if st.button("✨ Generate Summary", type="primary", use_container_width=True):
            with st.spinner("🚀 Starting AI Agent..."):
                try:
                    # 1. Trigger Generation
                    params = {"length": length, "style": style, "detail": detail}
                    res = requests.post(f"{API_URL}/summary/{book_id}", params=params)
                    
                    if res.status_code == 200:
                        # 2. Long Polling Loop (Waits up to 5 minutes)
                        progress_bar = st.progress(0, text="Analyzing text structure...")
                        status_placeholder = st.empty()
                        
                        for i in range(600):
                            time.sleep(0.5)
                            try:
                                status_res = requests.get(f"{API_URL}/books/{book_id}")
                                if status_res.status_code == 200:
                                    status = status_res.json().get("status")
                                    
                                    if status == "completed":
                                        progress_bar.progress(100, text="✅ Done!")
                                        time.sleep(0.5)
                                        st.rerun() # Refresh to show result
                                        break
                                    elif status == "failed":
                                        status_placeholder.error("❌ Generation failed on server.")
                                        break
                                    else:
                                        # Fake progress animation
                                        fake_prog = min(i % 90 + 10, 90)
                                        progress_bar.progress(fake_prog, text=f"Processing... (Status: {status})")
                            except: pass
                        else:
                            st.error("⚠️ Timed out. AI is taking longer than usual.")
                    else:
                        st.error(f"Failed to start: {res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        # --- SMART DISPLAY RESULT (FIXED) ---
        result_container = st.container()
        
        with result_container:
            # ✅ CHECK STATUS FIRST (Prevents 404 logs)
            try:
                book_check = requests.get(f"{API_URL}/books/{book_id}")
                if book_check.status_code == 200:
                    status = book_check.json().get("status")
                    
                    if status == "processing":
                        st.info("⏳ AI is currently analyzing this book. Please wait...")
                    elif status == "completed":
                        # ONLY fetch summary if completed
                        summary_res = requests.get(f"{API_URL}/summary/{book_id}")
                        if summary_res.status_code == 200:
                            data = summary_res.json()
                            summary_text = data.get('summary', '')
                            
                            st.divider()
                            st.success("✅ Summary Ready!")
                            st.markdown("### 📝 Summary Result")
                            st.write(summary_text)

                            # --- 🌍 HYBRID TRANSLATION ---
                            st.divider()
                            st.subheader("🌍 Translate Summary")
                            mode = st.radio("Translation Engine:", ["World (Google)", "Indic (Sarvam)"], horizontal=True)
                            
                            tc1, tc2 = st.columns([3, 1])
                            with tc1:
                                if mode == "World (Google)":
                                    t_lang = st.selectbox("Select Language", list(WORLD_LANGS.keys()))
                                    t_code = WORLD_LANGS[t_lang]
                                else:
                                    t_lang = st.selectbox("Select Indic Language", list(INDIC_LANGS.keys()))
                                    t_code = INDIC_LANGS[t_lang]
                            
                            with tc2:
                                st.write(""); st.write("")
                                if st.button("Translate 🔄", use_container_width=True):
                                    with st.spinner(f"Translating to {t_lang}..."):
                                        try:
                                            if mode == "World (Google)":
                                                res = requests.post(f"{API_URL}/translate/translate", json={"text": summary_text, "target_lang": t_code})
                                            else:
                                                res = requests.post(f"{API_URL}/translate/sarvam", json={"text": summary_text, "target_lang": t_code})
                                            
                                            if res.status_code == 200:
                                                st.success(f"Translation ({t_lang}):")
                                                st.info(res.json().get("translated_text"))
                                            else:
                                                st.error("Translation failed.")
                                        except Exception as e: st.error(f"Error: {e}")

                            # --- 🎧 AUDIO PLAYER ---
                            st.divider()
                            st.subheader("🎧 Audio Player")
                            a_mode = st.radio("Voice Engine:", ["World Voices", "Indic Voices (Sarvam)"], horizontal=True)
                            
                            if a_mode == "World Voices":
                                world_lang = st.selectbox("Select Audio Language", list(WORLD_LANGS.keys()), key="audio_world")
                                world_code = WORLD_LANGS[world_lang]

                                if st.button("▶️ Play World Audio", use_container_width=True):
                                    with st.spinner(f"Generating {world_lang} Audio..."):
                                        try:
                                            text_to_speak = summary_text
                                            if world_code != "en":
                                                res_trans = requests.post(f"{API_URL}/translate/translate", json={"text": summary_text, "target_lang": world_code})
                                                if res_trans.status_code == 200:
                                                    text_to_speak = res_trans.json()['translated_text']
                                            
                                            res = requests.post(f"{API_URL}/audio/generate", json={"text": text_to_speak[:2000], "lang": world_code})
                                            if res.status_code == 200: 
                                                st.audio(res.content, format="audio/mp3")
                                            else: st.error("Audio generation failed.")
                                        except Exception as e: st.error(f"Error: {e}")

                            else:
                                indi_lang = st.selectbox("Select Voice Language", list(INDIC_LANGS.keys()), key="audio_indi")
                                indi_code = INDIC_LANGS[indi_lang]
                                
                                if st.button("▶️ Play Indic Audio", use_container_width=True):
                                    with st.spinner("Generating High-Quality Audio..."):
                                        try:
                                            trans_res = requests.post(f"{API_URL}/translate/sarvam", json={"text": summary_text[:1000], "target_lang": indi_code})
                                            if trans_res.status_code == 200:
                                                indic_text = trans_res.json()['translated_text']
                                                aud_res = requests.post(f"{API_URL}/translate/sarvam/tts", json={"text": indic_text, "target_lang": indi_code})
                                                if aud_res.status_code == 200:
                                                    st.audio(aud_res.content, format="audio/wav")
                                                else: st.error("Audio generation failed.")
                                        except Exception as e: st.error(f"Error: {e}")
                            
                            # --- EXPORT ---
                            st.divider()
                            st.subheader("📥 Export")
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                r = requests.get(f"{API_URL}/summary/{book_id}/export?format=txt")
                                if r.status_code == 200: st.download_button("📄 Download TXT", r.text, "summary.txt")
                            with ec2:
                                r = requests.get(f"{API_URL}/summary/{book_id}/export?format=pdf")
                                if r.status_code == 200: st.download_button("📕 Download PDF", r.content, "summary.pdf")
                    else:
                        st.info("ℹ️ No summary yet. Click 'Generate Summary' to start.")

            except Exception as e:
                pass

    # --- TAB 2 & 3 (History/Compare) ---
    with tab_hist:
        if st.button("🔄 Refresh History"): st.rerun()
        try:
            history_res = requests.get(f"{API_URL}/summary/history/{book_id}")
            history = history_res.json() if history_res.status_code == 200 else []
        except: history = []
        if not history: st.info("No history available.")
        else:
            for s in history:
                with st.expander(f"📅 {str(s.get('created_at'))[:10]}"):
                    st.write(s.get('summary_text'))
                    if st.button("Delete", key=f"del_{s.get('summary_id')}"):
                        requests.delete(f"{API_URL}/summary/{s.get('summary_id')}")
                        st.rerun()

    with tab_comp:
        try:
            history_res = requests.get(f"{API_URL}/summary/history/{book_id}")
            history = history_res.json() if history_res.status_code == 200 else []
        except: history = []
        if len(history) < 2: st.warning("Need 2 versions to compare.")
        else:
            c1, c2 = st.columns(2)
            v1_idx = c1.selectbox("Ver A", range(len(history)), key="v1_c")
            v2_idx = c2.selectbox("Ver B", range(len(history)), index=1, key="v2_c")
            t1 = history[v1_idx].get('summary_text', '')
            t2 = history[v2_idx].get('summary_text', '')
            diff = difflib.ndiff(t1.splitlines(), t2.splitlines())
            for line in diff:
                if line.startswith('+ '): st.markdown(f":green[{line}]")
                elif line.startswith('- '): st.markdown(f":red[{line}]")
                else: st.markdown(line)