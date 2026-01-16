import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000"

def show_admin_page():
    # --- HEADER & STYLE ---
    st.markdown("""
    <style>
        .metric-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #eee;
        }
        .metric-label { font-size: 15px; color: #6c757d; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 32px; color: #272838; font-weight: 700; margin: 8px 0; }
        .metric-sub { font-size: 13px; color: #28a745; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🚀 Admin Command Center")
    st.markdown("Real-time monitoring and deep analytics.")
    
    # Check Admin Access
    user_info = st.session_state.get('user_info', {})
    if user_info.get('role') != 'admin':
        st.error("⛔ Access Denied. Admin privileges required.")
        return

    # --- TABS ---
    tab_overview, tab_users, tab_health = st.tabs(["📊 Overview & Analytics", "👥 User Management", "⚙️ System Health"])

    # ==================================================
    # 1. OVERVIEW TAB
    # ==================================================
    with tab_overview:
        try:
            with st.spinner("Crunching numbers..."):
                # Fetch Data
                overview = requests.get(f"{API_URL}/admin/analytics/overview").json()
                daily = requests.get(f"{API_URL}/admin/analytics/daily").json()
                dists = requests.get(f"{API_URL}/admin/analytics/distributions").json()
                top_users = requests.get(f"{API_URL}/admin/analytics/top-users").json()

            # --- TOP METRICS ROW ---
            c1, c2, c3, c4 = st.columns(4)
            
            def metric_box(col, label, value, subtext):
                col.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-sub">{subtext}</div>
                </div>
                """, unsafe_allow_html=True)

            metric_box(c1, "Total Users", overview['total_users'], "👥 Active Community")
            metric_box(c2, "Total Books", overview['total_books'], "📚 Knowledge Base")
            metric_box(c3, "Summaries", overview['total_summaries'], f"⚡ {overview['completion_rate']}% Completion")
            metric_box(c4, "Avg Process Time", f"{overview['avg_processing_time']}s", "⏱️ Performance")

            st.write("") # Spacer

            # --- ROW 2: ACTIVITY GRAPHS ---
            g1, g2 = st.columns([2, 1])
            
            with g1:
                st.subheader("📈 Daily Activity Trends")
                df_daily = pd.DataFrame({
                    "Date": daily['dates'],
                    "New Users": daily['new_users'],
                    "Books Uploaded": daily['books_uploaded'],
                    "Summaries Generated": daily['summaries_generated']
                })
                # Melt for multi-line chart
                df_melted = df_daily.melt('Date', var_name='Metric', value_name='Count')
                fig_line = px.line(df_melted, x="Date", y="Count", color="Metric", markers=True, template="plotly_white")
                fig_line.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), legend_title_text="")
                
                # ✅ Updated param for new Streamlit
                st.plotly_chart(fig_line, use_container_width=True) 

            with g2:
                st.subheader("🏆 Most Active Users")
                if top_users:
                    df_top = pd.DataFrame(top_users)
                    fig_bar = px.bar(df_top, x="count", y="name", orientation='h', color="count", 
                                     color_continuous_scale="Viridis", text_auto=True)
                    fig_bar.update_layout(height=380, xaxis_title="Summaries Generated", yaxis_title=None, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Not enough user activity yet.")

            st.divider()

            # --- ROW 3: DISTRIBUTION PIE CHARTS ---
            st.subheader("🧩 Deep Dive Analytics")
            d1, d2 = st.columns(2)
            
            with d1:
                st.markdown("**Summary Styles Preference**")
                df_style = pd.DataFrame(dists['summary_styles'])
                if not df_style.empty:
                    fig_pie1 = px.pie(df_style, names="name", values="value", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_pie1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_pie1, use_container_width=True)
                else:
                    st.info("No style data.")

            with d2:
                st.markdown("**Processing Time Analysis**")
                df_proc = pd.DataFrame(dists['processing_times'])
                fig_pie2 = px.pie(df_proc, names="name", values="value", hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
                fig_pie2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie2, use_container_width=True)

        except Exception as e:
            st.error(f"Failed to load analytics: {e}")

    # ==================================================
    # 2. USER MANAGEMENT TAB
    # ==================================================
    with tab_users:
        st.subheader("👥 All Users Database")
        try:
            users_data = requests.get(f"{API_URL}/admin/analytics/users-table").json()
            if users_data:
                df_users = pd.DataFrame(users_data)
                
                # Reorder columns for better view
                cols = ["id", "name", "email", "role", "books", "summaries", "last_book", "joined"]
                
                st.dataframe(
                    df_users[cols], 
                    use_container_width=True, 
                    column_config={
                        "joined": st.column_config.DateColumn("Joined Date"),
                        "books": st.column_config.ProgressColumn("Books Uploaded", min_value=0, max_value=20, format="%d"),
                        "summaries": st.column_config.NumberColumn("Summaries"),
                        "email": st.column_config.LinkColumn("Email"),
                    }
                )
            else:
                st.info("No users found.")
        except Exception as e:
            st.error(f"Error loading user table: {e}")

    # ==================================================
    # 3. SYSTEM HEALTH TAB
    # ==================================================
    with tab_health:
        st.subheader("❤️ System Health Monitor")
        
        try:
            # Mocking real-time health for visuals
            h1, h2, h3 = st.columns(3)
            h1.metric("Database Size", f"{overview['db_size_mb']} MB", "+0.2 MB today", delta_color="inverse")
            h2.metric("Failed Books", overview['failed_books'], "Needs Review" if overview['failed_books'] > 0 else "All Good", delta_color="inverse")
            h3.metric("Total Records", overview['total_records'], "Rows in DB")
            
            st.markdown("### 🛡️ Actions")
            c_a, c_b = st.columns(2)
            with c_a:
                if st.button("🧹 Clear Failed Jobs", type="primary"):
                    st.toast("Failed jobs cleared (Mock)")
            with c_b:
                if st.button("📦 Export Full Database Backup"):
                    st.toast("Backup started...")
                
        except:
            st.error("Health check service unavailable.")