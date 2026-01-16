import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ===============================
# HELPERS
# ===============================
def validate_file(uploaded_file):
    if uploaded_file.size == 0:
        st.error("⚠️ File is empty.")
        return False
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("⚠️ File too large (Max 10MB).")
        return False
    return True

def get_file_metadata(uploaded_file):
    size_mb = uploaded_file.size / (1024 * 1024)
    size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{uploaded_file.size / 1024:.2f} KB"

    if uploaded_file.type == "application/pdf":
        ftype = "PDF"
    elif "word" in uploaded_file.type:
        ftype = "DOCX"
    elif "text" in uploaded_file.type:
        ftype = "TXT"
    else:
        ftype = "Unknown"

    return {
        "filename": uploaded_file.name,
        "size": size_str,
        "type": ftype
    }

def delete_book(book_id):
    try:
        res = requests.delete(f"{API_URL}/books/{book_id}")
        if res.status_code == 200:
            st.success("Book deleted.")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to delete.")
    except Exception as e:
        st.error(str(e))

# ===============================
# MAIN UPLOAD PAGE
# ===============================
def show_upload_page():
    st.markdown("## 📤 Upload a Book")
    st.markdown("Upload **PDF, DOCX, or TXT** files (Max 10MB).")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"],
        help="Text must be selectable (not scanned images)."
    )

    if uploaded_file and validate_file(uploaded_file):
        meta = get_file_metadata(uploaded_file)

        # -----------------------
        # FILE PREVIEW
        # -----------------------
        st.markdown("### 📄 File Preview")
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**Filename:** {meta['filename']}")
            c2.markdown(f"**Size:** {meta['size']}")
            c3.markdown(f"**Type:** {meta['type']}")

        # -----------------------
        # METADATA FORM
        # -----------------------
        st.markdown("### 🏷️ Book Details")
        with st.form("upload_form"):
            c1, c2, c3 = st.columns(3)
            default_title = uploaded_file.name.rsplit(".", 1)[0]

            with c1:
                title = st.text_input(
                    "📖 Title",
                    value=default_title,
                    help="This name will appear in your dashboard."
                )
            with c2:
                author = st.text_input(
                    "✍️ Author",
                    help="Optional but useful for organization."
                )
            with c3:
                chapter = st.text_input(
                    "📑 Chapter",
                    help="Optional (e.g. Chapter 1)"
                )

            submitted = st.form_submit_button(
                "🚀 Upload & Process",
                type="primary",
                use_container_width=True
            )

        # -----------------------
        # UPLOAD ACTION
        # -----------------------
        if submitted:
            if not title.strip():
                st.error("⚠️ Title is required.")
                return

            user_id = st.session_state.get("user_info", {}).get("user_id")
            if not user_id:
                st.error("User not authenticated.")
                return

            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"title": title, "author": author, "user_id": user_id}
            if chapter:
                data["chapter"] = chapter

            with st.spinner("Processing document..."):
                try:
                    res = requests.post(f"{API_URL}/books/", data=data, files=files)

                    if res.status_code == 200:
                        book = res.json()
                        st.balloons()
                        st.success("✅ Book uploaded successfully!")

                        m1, m2, m3 = st.columns(3)
                        m1.metric("Status", "Processed")
                        m2.metric("Word Count", f"{book.get('word_count', 0):,}")
                        m3.metric("Char Count", f"{book.get('char_count', 0):,}")

                        if st.button("📘 Generate Summary Now", type="primary", use_container_width=True):
                            st.session_state["selected_book_id"] = book["book_id"]
                            st.session_state["current_page"] = "Summaries"
                            st.rerun()

                    elif res.status_code == 409:
                        st.warning("⚠️ This file was already uploaded.")
                    else:
                        st.error(res.text)

                except Exception as e:
                    st.error(f"Connection error: {e}")

    # ===============================
    # RECENT UPLOADS
    # ===============================
    st.markdown("---")
    st.subheader("📚 Recent Uploads")

    try:
        res = requests.get(f"{API_URL}/books/")
        if res.status_code == 200:
            books = res.json()

            if not books:
                st.info("No books uploaded yet.")
                return

            for b in books:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                    c1.write(b.get("title"))
                    c2.write(b.get("status", "unknown"))
                    c3.write(b.get("uploaded_at", "")[:10])
                    if c4.button("🗑️ Delete", key=f"del_{b['book_id']}"):
                        delete_book(b["book_id"])
    except:
        pass
