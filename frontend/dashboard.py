import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://127.0.0.1:8000"


# ------------------------------------------------------
# TIME FORMATTER
# ------------------------------------------------------
def get_relative_time(date_str):
    """Converts ISO timestamp to '2 hours ago' format."""
    if not date_str:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} days ago"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hours ago"
        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes} mins ago"
        return "Just now"
    except:
        return "Unknown"


# ------------------------------------------------------
# BASIC STATS (Books Only)
# ------------------------------------------------------
def calculate_stats(books):
    total_books = len(books)
    processed_books = len([b for b in books if b.get("status") == "text_extracted"])

    total_chars = sum(b.get("char_count", 0) for b in books)
    storage_mb = total_chars / (1024 * 1024)

    return total_books, processed_books, f"{storage_mb:.2f} MB"


# ------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------
def show_dashboard_page():

    if "user_info" not in st.session_state:
        st.error("You are not logged in.")
        return

    user_name = st.session_state["user_info"].get("name", "User")

    # HEADER
    st.title(f"Welcome back, {user_name}!")
    st.markdown("Your personalized AI summarization dashboard.")

    # FETCH BOOKS
    with st.spinner("Loading your dashboard..."):
        try:
            res = requests.get(f"{API_URL}/books/")
            books = res.json() if res.status_code == 200 else []
        except:
            books = []
            st.error("Unable to connect to the backend server.")

    # ------------------------------------------------------
    # EMPTY STATE
    # ------------------------------------------------------
    if not books:
        st.info("You're new here — let’s get started!")

        hero_col1, hero_col2 = st.columns([2, 1])

        with hero_col1:
            st.markdown("""
                ### Upload Your First Book  
                Generate AI summaries instantly and explore deeper insights.  
                **Supported Formats:** PDF, DOCX, TXT  
            """)

            if st.button("Upload Your First Book", type="primary"):
                st.session_state["current_page"] = "Upload Book"
                st.rerun()

        return

    # ------------------------------------------------------
    # QUICK STATS
    # ------------------------------------------------------
    st.markdown("### Quick Stats")

    total, processed, storage = calculate_stats(books)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Books", total)
    c2.metric("Processed & Ready", processed)
    c3.metric("Storage Used", storage)

    # ------------------------------------------------------
    # FETCH TEXT STATISTICS FOR LATEST BOOK
    # ------------------------------------------------------
    stats = {
        "sentence_count": "—",
        "reading_time_minutes": "—",
        "language": "unknown"
    }

    latest_book = books[-1]  # last uploaded book

    try:
        stats_res = requests.get(f"{API_URL}/books/{latest_book['book_id']}/stats")
        if stats_res.status_code == 200:
            stats = stats_res.json()
    except:
        pass  # stats remain default if API not found

    m4, m5, m6 = st.columns(3)
    m4.metric("Sentences", stats.get("sentence_count", "—"))
    m5.metric("Reading Time", f"{stats.get('reading_time_minutes', '—')} mins")
    m6.metric("Language", stats.get("language", "unknown"))

    st.divider()

    # ------------------------------------------------------
    # MAIN LAYOUT
    # ------------------------------------------------------
    col_left, col_right = st.columns([2, 1])

    # ------------------------------------------------------
    # RECENT ACTIVITY FEED
    # ------------------------------------------------------
    with col_left:
        st.subheader("Recent Activity Feed")

        recent_books = sorted(books, key=lambda x: x.get("book_id", 0), reverse=True)[:5]

        for book in recent_books:
            title = book.get("title", "Untitled")
            status = book.get("status", "unknown")
            time_ago = get_relative_time(book.get("uploaded_at", ""))

            if status == "completed":
                message = f"Summary generated for **{title}**"
            elif status == "text_extracted":
                message = f"Uploaded **{title}**"
            else:
                message = f"Processing **{title}**"

            with st.container():
                msg_col, time_col = st.columns([0.8, 0.2])
                msg_col.markdown(message)
                time_col.caption(time_ago)
                st.divider()

    # ------------------------------------------------------
    # QUICK ACTIONS
    # ------------------------------------------------------
    with col_right:

        st.subheader("Quick Actions")

        if st.button("Upload New Book", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Upload Book"
            st.rerun()

        if st.button("View My Library", use_container_width=True):
            st.session_state["current_page"] = "My Books"
            st.rerun()

        st.markdown("### Daily Tips")
        st.info("Visit the **Help** section anytime for detailed guidance!")


# Run page if opened directly
if __name__ == "__main__":
    show_dashboard_page()
