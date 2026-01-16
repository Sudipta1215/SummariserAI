import streamlit as st
import requests
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
import io

API_URL = "http://127.0.0.1:8000"

# --- PDF GENERATOR HELPER ---
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # Handle unicode/latin-1 issues
    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_content)
    
    return pdf.output(dest="S").encode("latin-1")

def show_workspace_page():
    st.title("🎨 Creative Workspace")
    st.markdown("Collaborate, Draw, and Export your notes.")

    if 'user_info' not in st.session_state:
        st.error("Please login first.")
        return

    USER_ID = st.session_state['user_info']['user_id']

    # ==========================================
    # 1. SIDEBAR: SELECT OR CREATE WORKSPACE
    # ==========================================
    with st.sidebar:
        st.header("🗂️ Manage Workspaces")
        
        # Create New
        with st.expander("➕ New Workspace"):
            new_title = st.text_input("Title", key="new_ws_title")
            if st.button("Create"):
                try:
                    res = requests.post(f"{API_URL}/workspaces/", json={"user_id": USER_ID, "title": new_title})
                    if res.status_code == 200:
                        st.success("Created!")
                        st.rerun()
                except:
                    st.error("Backend offline.")

        # Load Existing
        try:
            res = requests.get(f"{API_URL}/workspaces/user/{USER_ID}")
            if res.status_code == 200:
                data = res.json()
                all_ws = data.get('owned', []) + data.get('shared', [])
                
                if not all_ws:
                    st.info("No workspaces found.")
                    return

                # Dropdown Selector
                ws_map = {f"{w['title']} (ID: {w['workspace_id']})": w['workspace_id'] for w in all_ws}
                selected_name = st.selectbox("📂 Open Workspace", list(ws_map.keys()))
                current_id = ws_map[selected_name]
            else:
                st.error("Could not fetch workspaces.")
                return
        except Exception as e:
            st.error("Backend connection failed.")
            return

    # ==========================================
    # 2. MAIN WORKSPACE LOGIC
    # ==========================================
    try:
        # Fetch current workspace data
        ws_res = requests.get(f"{API_URL}/workspaces/{current_id}", params={"user_id": USER_ID})
        if ws_res.status_code != 200:
            st.error("Access Denied.")
            return
        
        ws_data = ws_res.json()
        permission = ws_data['permission']
        is_view_only = (permission == 'view')

        # Header
        c1, c2 = st.columns([3, 1])
        c1.subheader(f"📝 {ws_data['title']}")
        c1.caption(f"Role: {permission.upper()}")
        
        # --- EXPORT BUTTON ---
        with c2:
            if st.button("📥 Download PDF"):
                pdf_bytes = create_pdf(ws_data['title'], ws_data['content'])
                st.download_button(
                    label="Click to Save",
                    data=pdf_bytes,
                    file_name=f"{ws_data['title']}.pdf",
                    mime="application/pdf"
                )

        # --- TABS: EDITOR vs CANVAS ---
        tab_text, tab_canvas, tab_invite = st.tabs(["✍️ Text Editor", "🎨 Whiteboard", "👥 Invite"])

        # ------------------------------------------
        # TAB A: TEXT EDITOR
        # ------------------------------------------
        with tab_text:
            new_content = st.text_area(
                "Shared Notes", 
                value=ws_data['content'], 
                height=400,
                disabled=is_view_only
            )
            
            if not is_view_only:
                if st.button("💾 Save Text Notes", type="primary"):
                    save_res = requests.put(
                        f"{API_URL}/workspaces/{current_id}", 
                        json={"user_id": USER_ID, "content": new_content}
                    )
                    if save_res.status_code == 200:
                        st.success("✅ Saved to Database!")
                    else:
                        st.error("Save failed.")

        # ------------------------------------------
        # TAB B: MS PAINT CANVAS
        # ------------------------------------------
        with tab_canvas:
            st.markdown("### 🎨 Drawing Tools")
            
            col_tool, col_color, col_width = st.columns(3)
            with col_tool:
                drawing_mode = st.selectbox(
                    "Drawing Tool:",
                    ("freedraw", "line", "rect", "circle", "transform")
                )
            with col_color:
                stroke_color = st.color_picker("Stroke Color", "#000000")
            with col_width:
                stroke_width = st.slider("Stroke Width", 1, 25, 3)

            st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="#ffffff",
                update_streamlit=True,
                height=500,
                width=800,
                drawing_mode=drawing_mode,
                key=f"canvas_{current_id}_v2",
            )
            
            st.info("ℹ️ Note: Drawings are for visualization and do not currently save to the database.")

        # ------------------------------------------
        # TAB C: INVITE SYSTEM
        # ------------------------------------------
        with tab_invite:
            st.markdown("### Invite Team Members")
            if permission == 'owner':
                i1, i2 = st.columns([2, 1])
                email_input = i1.text_input("Friend's Email")
                role_input = i2.selectbox("Permission", ["view", "edit"])
                
                if st.button("Send Invite Email"):
                    res = requests.post(
                        f"{API_URL}/workspaces/{current_id}/invite",
                        json={
                            "owner_id": USER_ID,
                            "target_email": email_input,
                            "permission": role_input
                        }
                    )
                    if res.status_code == 200:
                        st.success(f"Invite sent to {email_input}!")
                    else:
                        st.error(res.json().get('detail'))
            else:
                st.warning("Only the owner can invite collaborators.")

    except Exception as e:
        st.error(f"Error loading workspace: {e}")