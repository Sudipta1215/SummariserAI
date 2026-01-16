import streamlit as st
import requests
import time

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Book Summarizer", page_icon="✨", layout="wide")

# ==========================================
# 📦 IMPORTS
# ==========================================
from dashboard import show_dashboard_page
from upload import show_upload_page
from my_books import show_my_books_page
from settings import show_settings_page
from summaries import show_summaries_page
from agent_chat import show_chat_page
from knowledge_graph import show_graph_page
from quiz import show_quiz_page
from admin_dashboard import show_admin_page
from workspaces import show_workspace_page

# ==========================================
# 🎨 CSS STYLING
# ==========================================
def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
        
        .stApp { background-color: #ECF8FD; }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(175, 203, 213, 0.25);
            border-right: 1px solid white;
        }
        
        /* Buttons */
        button[kind="primary"] {
            background-color: #815355 !important;
            border-radius: 20px !important;
            border: none !important;
        }
        button[kind="primary"]:hover {
            background-color: #F2B418 !important;
            color: #272838 !important;
        }
    </style>
    """, unsafe_allow_html=True)
apply_custom_style()

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'auth_page' not in st.session_state: st.session_state['auth_page'] = 'login'
if 'current_page' not in st.session_state: st.session_state['current_page'] = "Dashboard"
if 'user_info' not in st.session_state: st.session_state['user_info'] = {}

# ==========================================
# 1. AUTHENTICATION
# ==========================================
def show_login():
    st.markdown("<h1 style='text-align: center;'>Welcome Back ✨</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            # ✅ FIX: Changed use_container_width=True to width="stretch" to fix warning
            if st.form_submit_button("Sign In", type="primary", width="stretch"):
                try:
                    res = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                    if res.status_code == 200:
                        st.session_state['logged_in'] = True
                        st.session_state['user_info'] = res.json()
                        st.rerun()
                    else:
                        st.error(f"Login failed: {res.text}")
                except Exception as e:
                    st.error(f"Backend offline: {e}")
        
        if st.button("Create Account"):
            st.session_state['auth_page'] = 'register'
            st.rerun()

def show_register():
    st.markdown("<h1 style='text-align: center;'>Join Us 🌸</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        with st.form("reg"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            
            # ✅ FIX: Changed use_container_width=True to width="stretch" to fix warning
            if st.form_submit_button("Sign Up", type="primary", width="stretch"):
                try:
                    res = requests.post(f"{API_URL}/users/", json={"name":name, "email":email, "password":pwd})
                    if res.status_code == 200:
                        st.success("Created! Please login.")
                        st.session_state['auth_page'] = 'login'
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("Back to Login"):
            st.session_state['auth_page'] = 'login'
            st.rerun()

# ==========================================
# 2. MAIN APP ROUTING
# ==========================================
if not st.session_state['logged_in']:
    if st.session_state['auth_page'] == 'login': show_login()
    else: show_register()
else:
    # --- SIDEBAR ---
    with st.sidebar:
        user = st.session_state['user_info']
        role = user.get('role', 'user')
        
        st.markdown(f"### 👤 {user.get('name', 'User')}")
        st.caption(f"Role: {role.title()}")
        
        # Define Menu Options
        options = [
            "Dashboard", 
            "Upload Book", 
            "My Books", 
            "Summaries", 
            "Knowledge Graph", 
            "Quiz Mode", 
            "Collaborative Workspace", 
            "Agent Chat", 
            "Settings"
        ]
        
        if role == "admin":
            options.insert(1, "Admin Dashboard")

        try: idx = options.index(st.session_state['current_page'])
        except ValueError: idx = 0
            
        selected = st.radio("Menu", options, index=idx, label_visibility="collapsed")
        
        if selected != st.session_state['current_page']:
            st.session_state['current_page'] = selected
            st.rerun()

        st.divider()
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = {}
            st.rerun()

    # --- PAGE RENDERER ---
    page = st.session_state['current_page']
    
    if page == "Dashboard": show_dashboard_page()
    elif page == "Admin Dashboard": show_admin_page()
    elif page == "Upload Book": show_upload_page()
    elif page == "My Books": show_my_books_page()
    elif page == "Summaries": show_summaries_page()
    elif page == "Knowledge Graph": show_graph_page()
    elif page == "Quiz Mode": show_quiz_page()
    elif page == "Collaborative Workspace": show_workspace_page()
    elif page == "Agent Chat": show_chat_page()
    elif page == "Settings": show_settings_page()