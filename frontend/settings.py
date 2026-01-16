import streamlit as st
import requests
import time
API_URL = "http://127.0.0.1:8000"

def show_settings_page():
    st.title("Account Settings")
    st.markdown("Manage your profile, security, and preferences here.")

    # Get current user info from session
    user_info = st.session_state.get('user_info', {})
    user_id = user_info.get('user_id')
    current_name = user_info.get('name', '')
    current_email = user_info.get('email', '')
    
    # Get current preferences (default to False if not set)
    # We store these in session state for now
    pref_email = st.session_state.get('pref_email', True)
    pref_dark_mode = st.session_state.get('pref_dark_mode', False)

    # --- TABS LAYOUT ---
    tab1, tab2, tab3 = st.tabs(["Profile", " Security", " Delete account"])

    # --------------------------
    # TAB 1: PROFILE SETTINGS
    # --------------------------
    with tab1:
        st.subheader("Profile Details")
        with st.form("profile_form"):
            new_name = st.text_input("Full Name", value=current_name)
            
            # FIXED: help="..." (Correct syntax)
            st.text_input("Email Address", value=current_email, disabled=True, help="Email cannot be changed.")
            
            # Preference Toggles
            st.markdown("##### Preferences")
            c1, c2 = st.columns(2)
            with c1:
                # We update the session state variable
                receive_emails = st.checkbox("Receive Email Summaries", value=pref_email)
            with c2:
                # FIXED: Removed 'disabled=True' so you can click it
                # Note: This saves the preference, but doesn't instantly change the Streamlit theme
                dark_mode = st.checkbox("Dark Mode Preference", value=pref_dark_mode, help="Saves your preference for dark mode.")

            if st.form_submit_button("Save Changes", type="primary"):
                # 1. Update Session State
                st.session_state['user_info']['name'] = new_name
                st.session_state['pref_email'] = receive_emails
                st.session_state['pref_dark_mode'] = dark_mode
                
                # 2. Show Success
                st.success(" Profile & Preferences updated successfully!")
                
                # 3. Optional: Show a message about Dark Mode
                if dark_mode:
                    st.info(" Note: To apply the Dark Theme visually, go to Settings (top-right menu) > Theme > Dark.")
                
                time.sleep(1)
                st.rerun()

    # --------------------------
    # TAB 2: SECURITY
    # --------------------------
    with tab2:
        st.subheader("Change Password")
        with st.form("password_form"):
            current_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_pwd != confirm_pwd:
                    st.error(" New passwords do not match.")
                elif not current_pwd:
                    st.error("Please enter your current password.")
                else:
                    st.success(" Password updated successfully! (Mock)")

    # --------------------------
    # TAB 3: DANGER ZONE
    # --------------------------
    # --------------------------
    # TAB 3: DANGER ZONE
    # --------------------------
    with tab3:
        st.subheader("Delete Account")
        st.warning("Once you delete your account, there is no going back. Please be certain.")
        
        with st.expander("🗑️ Delete My Account"):
            st.write("This action will permanently delete your account and all uploaded books.")
            confirm_delete = st.text_input("Type 'DELETE' to confirm")
            
            if st.button("Permanently Delete Account", type="primary"):
                if confirm_delete == "DELETE":
                    try:
                        # 1. Call Backend API to delete
                        res = requests.delete(f"{API_URL}/users/{user_id}")
                        
                        if res.status_code == 200:
                            # 2. Clear Session State (Log out)
                            st.session_state['logged_in'] = False
                            st.session_state['user_info'] = {}
                            st.success("Account deleted successfully.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to delete account: {res.text}")
                            
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
                else:
                    st.error("Please type 'DELETE' exactly to confirm.")