import streamlit as st
import re
import requests
import time

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"

# --- CUSTOM CSS FOR STYLING ---
def load_css():
    st.markdown("""
        <style>
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            font-weight: bold;
        }
        .auth-container {
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 2rem;
        }
        .error-message {
            color: #ff4b4b;
            font-size: 0.8rem;
            margin-top: -10px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- VALIDATION FUNCTIONS ---
def validate_name(name):
    """Name: not empty, only letters/spaces, min 2 chars"""
    if not name:
        return "Name is required."
    if len(name) < 2:
        return "Name must be at least 2 characters."
    if not re.match(r"^[a-zA-Z\s]+$", name):
        return "Name must contain only letters and spaces."
    return None

def validate_email(email):
    """Email: valid regex format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return "Please enter a valid email address."
    return None

def validate_password(password):
    """Password: min 8 chars, 1 upper, 1 lower, 1 number, 1 special"""
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("one special character")
    
    if errors:
        return "Password needs: " + ", ".join(errors)
    return None

# --- AUTHENTICATION PAGES ---

def register_user():
    st.header("Create an Account")
    st.markdown("Join us to start managing your library.")
    
    with st.form("register_form"):
        # Inputs
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password", type="password", help="Min 8 chars, mixed case & symbols")
        with col2:
            confirm_password = st.text_input("Confirm Password", type="password")
            
        submit_btn = st.form_submit_button("Register Now", type="primary")
        
        if submit_btn:
            # 1. Input Validation
            err_name = validate_name(full_name)
            err_email = validate_email(email)
            err_pass = validate_password(password)
            
            has_error = False
            
            if err_name:
                st.error(f"❌ Name Error: {err_name}")
                has_error = True
            if err_email:
                st.error(f"❌ Email Error: {err_email}")
                has_error = True
            if err_pass:
                st.error(f"❌ Password Error: {err_pass}")
                has_error = True
            if password != confirm_password:
                st.error("❌ Passwords do not match.")
                has_error = True
                
            # 2. Backend Submission
            if not has_error:
                with st.spinner("Creating account..."):
                    # Simulate network delay for UX
                    time.sleep(1) 
                    try:
                        payload = {
                            "name": full_name,
                            "email": email,
                            "password": password # In real app, hash this or let backend hash it
                        }
                        response = requests.post(f"{API_URL}/users/", json=payload)
                        
                        if response.status_code == 200:
                            st.success("✅ Account created successfully! Please log in.")
                            st.session_state['auth_page'] = 'login'
                            st.rerun()
                        elif response.status_code == 400:
                            st.error("⚠️ Email already registered.")
                        else:
                            st.error(f"Server Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")

    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        st.write("Already have an account?")
    with col2:
        if st.button("Log In Here"):
            st.session_state['auth_page'] = 'login'
            st.rerun()

def login_user():
    st.header("Welcome Back")
    st.markdown("Please enter your details to sign in.")
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")
        
        submit_login = st.form_submit_button("Log In", type="primary")
        
        if submit_login:
            if not email or not password:
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Verifying credentials..."):
                    time.sleep(1)
                    # NOTE: Since we haven't built a specific /login endpoint in the backend
                    # that returns a token, we will simulate a successful UI flow 
                    # if the user exists in the database.
                    # Ideally, you would POST to /login/ here.
                    
                    # For this exercise, we will just Check if user exists (Simulated Login)
                    try:
                        # We are 'cheating' slightly by checking the users list 
                        # because we haven't built the Login API endpoint in Task 2.
                        response = requests.get(f"{API_URL}/users/")
                        if response.status_code == 200:
                            users = response.json()
                            user_found = False
                            for u in users:
                                if u['email'] == email:
                                    user_found = True
                                    st.success(f"Welcome back, {u['name']}!")
                                    st.session_state['logged_in'] = True
                                    st.session_state['user_info'] = u
                                    st.rerun()
                            if not user_found:
                                st.error("User not found or incorrect password.")
                        else:
                            st.error("Could not connect to database.")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    st.markdown("---")
    col1, col2 = st.columns([1,1])
    with col1:
        st.write("Forgot Password?")
    with col2:
        if st.button("Create New Account"):
            st.session_state['auth_page'] = 'register'
            st.rerun()

# --- MAIN APP FLOW ---
def main():
    st.set_page_config(page_title="Auth System", page_icon="🔒", layout="centered")
    load_css()
    
    # Initialize Session State
    if 'auth_page' not in st.session_state:
        st.session_state['auth_page'] = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Routing
    if st.session_state['logged_in']:
        st.success(f"You are logged in as {st.session_state['user_info'].get('name')}!")
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()
        # HERE YOU WOULD NORMALLY IMPORT YOUR DASHBOARD APP
        st.write("🚀 Redirecting to Dashboard...")
        
    else:
        if st.session_state['auth_page'] == 'login':
            login_user()
        else:
            register_user()

if __name__ == "__main__":
    main()