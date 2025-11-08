import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "log.db"

st.set_page_config(page_title="Log Analysis & Report Generation", layout="wide")

# TODO: Check if database exists
if not os.path.exists(DB_NAME):
    st.warning("Database not found. Please ensure 'log.db' from Week 7–11 exists.")
else:
    # TODO: Connect to database and load system_log table
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM system_log", conn)

    st.title("📊 System Log Analysis & Reporting")

    # TODO: Display key statistics (average, max, min)
    # Example: st.metric("Average CPU", f"{df['cpu'].mean():.2f}%")

    # TODO: Count how many alerts exceed thresholds (CPU>80, MEM>85, DISK>90)

    # TODO: Plot summary charts
    st.subheader("📈 CPU / Memory / Disk Trends")
    st.line_chart(df.set_index("timestamp")[["cpu", "memory", "disk"]])

    # TODO: Add export option to save summary as CSV
    # Example: st.download_button("Download CSV", csv_data, "report.csv")

    conn.close()
