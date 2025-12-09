import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "log.db"

st.set_page_config(page_title="Log Analysis & Report Generation", layout="wide")

# Custom CSS for animated background and styling
st.markdown("""
<style>
    /* Animated Gradient Background - Deeper, richer colors */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #141E30);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Glassmorphism Card Style for Containers - Darker for better text visibility */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background: rgba(0, 0, 0, 0.6); /* Darker background */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Input Fields Styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9); /* Lighter background */
        color: black; /* Black text/dots */
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stTextInput > div > div > input:focus {
        border-color: #00c6ff; /* Cyan focus border */
        box-shadow: 0 0 10px rgba(0, 198, 255, 0.5);
        color: black;
    }
    
    /* Button Styling - New Colors (Purple/Blue) */
    .stButton > button {
        background: linear-gradient(45deg, #8E2DE2 0%, #4A00E0 100%); /* Purple to Blue */
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 0, 224, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 0, 224, 0.6);
        background: linear-gradient(45deg, #9b42f5 0%, #5d11f7 100%); /* Lighter on hover */
    }

    /* Download Button Styling - Green */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(45deg, #11998e 0%, #38ef7d 100%); /* Green Gradient */
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.4);
    }

    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 239, 125, 0.6);
        background: linear-gradient(45deg, #16a085 0%, #2ecc71 100%);
    }
    
    /* Text Colors & Visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #00c6ff !important; /* Cyan Headers */
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    p, label, .stMarkdown, .stText {
        color: #e0e0e0 !important; /* Off-white for body text */
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Dataframe Styling */
    div[data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Footer Styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        backdrop-filter: blur(5px);
        z-index: 1000;
    }
    
</style>
<div class="footer">
    <p>© 2025 Indrasena. All Rights Reserved.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# Initialize thresholds in session state
if "cpu_threshold" not in st.session_state:
    st.session_state.cpu_threshold = 80
if "memory_threshold" not in st.session_state:
    st.session_state.memory_threshold = 85
if "disk_threshold" not in st.session_state:
    st.session_state.disk_threshold = 90

def check_password():
    """Checks if the password is correct using the database."""
    username = st.session_state["username"]
    password = st.session_state["password"]
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Ensure users table exists or handle error
    try:
        c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
    except sqlite3.OperationalError:
        st.error("Table 'users' not found in database. Please ensure the database is set up correctly.")
        user = None
    finally:
        conn.close()
    
    if user:
        st.session_state.logged_in = True
        st.session_state.role = user[0]
        del st.session_state["password"]  # don't store password
    else:
        st.session_state.logged_in = False
        st.error("😕 User not known or password incorrect")

if not st.session_state.logged_in:
    st.title("🔐 Login to Access Dashboard")
    
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password", on_change=check_password)
    st.button("Login", on_click=check_password)

else:
    # Navigation
    st.sidebar.title(f"📂 Navigation ({st.session_state.role})")
    
    options = ["Dashboard", "Logout"]
    if st.session_state.role == "admin":
        options.insert(1, "Configuration")
        
    page = st.sidebar.radio("Select Page", options)

    if page == "Dashboard":
        # Check if database exists
        if not os.path.exists(DB_NAME):
            st.warning("Database not found. Please ensure 'log.db' from Week 7–11 exists.")
        else:
            # Connect to database and load system_log table
            try:
                conn = sqlite3.connect(DB_NAME)
                df = pd.read_sql_query("SELECT * FROM system_log", conn)
                conn.close()
        
                if df.empty:
                    st.warning("The database is empty. No logs to analyze.")
                else:
                    st.title("📊 System Log Analysis & Reporting")
        
                    # Ensure timestamp is datetime
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
                    # --- Statistics Calculation ---
                    avg_cpu = df['cpu'].mean()
                    avg_memory = df['memory'].mean()
                    avg_disk = df['disk'].mean()
        
                    # Use dynamic thresholds from session state
                    cpu_alerts = df[df['cpu'] > st.session_state.cpu_threshold].shape[0]
                    memory_alerts = df[df['memory'] > st.session_state.memory_threshold].shape[0]
                    disk_alerts = df[df['disk'] > st.session_state.disk_threshold].shape[0]
        
                    # --- Display Key Statistics ---
                    st.subheader("Key Metrics")

                    def metric_card(label, value, color):
                        st.markdown(f"""
                        <div style="
                            background-color: rgba(255, 255, 255, 0.05);
                            padding: 15px;
                            border-radius: 10px;
                            border-left: 5px solid {color};
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                            text-align: center;
                            margin-bottom: 10px;
                        ">
                            <p style="color: #e0e0e0; margin: 0; font-size: 16px; font-weight: bold;">{label}</p>
                            <p style="color: {color}; margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">{value}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        metric_card("Average CPU", f"{avg_cpu:.2f}%", "#00c6ff") # Cyan
                    with col2:
                        metric_card("Average Memory", f"{avg_memory:.2f}%", "#8E2DE2") # Purple
                    with col3:
                        metric_card("Average Disk", f"{avg_disk:.2f}%", "#FF416C") # Pink/Red

                    col4, col5, col6 = st.columns(3)
                    with col4:
                        color = "#FF4B2B" if cpu_alerts > 0 else "#00b09b" # Red if alerts, else Green
                        metric_card(f"CPU Alerts (>{st.session_state.cpu_threshold}%)", cpu_alerts, color)
                    with col5:
                        color = "#FF4B2B" if memory_alerts > 0 else "#00b09b"
                        metric_card(f"Memory Alerts (>{st.session_state.memory_threshold}%)", memory_alerts, color)
                    with col6:
                        color = "#FF4B2B" if disk_alerts > 0 else "#00b09b"
                        metric_card(f"Disk Alerts (>{st.session_state.disk_threshold}%)", disk_alerts, color)
        
                    # --- Charts ---
                    st.subheader("📈 System Resource Trends")
                    if 'timestamp' in df.columns:
                        chart_data = df.set_index("timestamp")[["cpu", "memory", "disk"]]
                        st.line_chart(chart_data)
                    else:
                        st.line_chart(df[["cpu", "memory", "disk"]])
        
                    # --- Report Generation ---
                    st.subheader("📝 Generate Report")
                    
                    report_data = {
                        "Metric": [
                            "Average CPU", "Average Memory", "Average Disk",
                            "CPU Alerts", "Memory Alerts", "Disk Alerts"
                        ],
                        "Value": [
                            f"{avg_cpu:.2f}%", f"{avg_memory:.2f}%", f"{avg_disk:.2f}%",
                            str(cpu_alerts), str(memory_alerts), str(disk_alerts)
                        ]
                    }
                    report_df = pd.DataFrame(report_data)
                    
                    st.table(report_df)
        
                    csv = report_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Report as CSV",
                        data=csv,
                        file_name="system_report.csv",
                        mime="text/csv",
                    )
        
                    # --- Bonus: Alert History ---
                    st.subheader("⚠️ Alert History (Last 24 Hours)")
                    # Assuming 'timestamp' exists and is datetime
                    if 'timestamp' in df.columns:
                         # Filter for alerts
                        alerts_df = df[
                            (df['cpu'] > 80) | 
                            (df['memory'] > 85) | 
                            (df['disk'] > 90)
                        ].copy()
                        
                        if not alerts_df.empty:
                            st.dataframe(alerts_df.sort_values(by="timestamp", ascending=False))
                        else:
                            st.info("No alerts found in the logs.")
        
            except Exception as e:
                st.error(f"An error occurred: {e}")

    elif page == "Configuration":
        if st.session_state.role != "admin":
            st.error("Access Denied")
        else:
            st.title("⚙️ Configuration Panel")
            st.write("Adjust the alert thresholds for system metrics.")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.cpu_threshold = st.slider(
                    "CPU Alert Threshold (%)", 0, 100, st.session_state.cpu_threshold
                )
            with col2:
                st.session_state.memory_threshold = st.slider(
                    "Memory Alert Threshold (%)", 0, 100, st.session_state.memory_threshold
                )
            with col3:
                st.session_state.disk_threshold = st.slider(
                    "Disk Alert Threshold (%)", 0, 100, st.session_state.disk_threshold
                )
            
            st.success("Configuration saved automatically!")

    elif page == "Logout":
        st.title("Log out")
        st.write("Are you sure you want to log out?")
        if st.button("Confirm Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
