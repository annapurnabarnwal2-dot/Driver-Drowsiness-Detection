
from datetime import datetime
import subprocess
import sys
import csv
import io
import os
import html
import streamlit as st


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Driver Drowsiness Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.title("Driver Drowsiness Detection")
st.caption("Monitoring Dashboard | Event History")


# ---------------- PROJECT PATHS ----------------

project_root = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(
    project_root,
    "drowsiness_log.csv"
)


# ---------------- SESSION STATE ----------------

if "monitor_process" not in st.session_state:
    st.session_state.monitor_process = None

if "session_start" not in st.session_state:
    st.session_state.session_start = None

if "session_stop" not in st.session_state:
    st.session_state.session_stop = None


# ---------------- MONITORING CONTROL ----------------

st.subheader("Monitoring Control")

col_start, col_stop = st.columns(2)

with col_start:
    if st.button("Start Monitoring", use_container_width=True):
        process = st.session_state.monitor_process

        if process is None or process.poll() is not None:
            try:
                process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=project_root
                )

                st.session_state.monitor_process = process
                st.session_state.session_start = datetime.now()
                st.session_state.session_stop = None

                st.success("Monitoring program started.")

            except (OSError, ValueError) as error:
                st.error(f"Could not start monitoring: {error}")

        else:
            st.info("Monitoring is already running.")

with col_stop:
    if st.button("Stop Monitoring", use_container_width=True):
        process = st.session_state.monitor_process

        if process is not None and process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            st.session_state.monitor_process = None
            st.session_state.session_stop = datetime.now()

            st.success("Monitoring program stopped.")

        else:
            st.info("Monitoring program is not running.")


# ---------------- LIVE MONITORING STATUS ----------------

st.subheader("Live Monitoring Status")

monitor_process = st.session_state.monitor_process

if monitor_process is not None and monitor_process.poll() is None:
    st.success("MONITORING IS RUNNING")
else:
    st.warning("MONITORING IS STOPPED")


# ---------------- SESSION REPORT ----------------

st.subheader("Session Report")

session_start = st.session_state.session_start
session_stop = st.session_state.session_stop

if session_start is not None:
    st.write(
        "Session started:",
        session_start.strftime("%Y-%m-%d %H:%M:%S")
    )

    if session_stop is not None:
        st.write(
            "Session stopped:",
            session_stop.strftime("%Y-%m-%d %H:%M:%S")
        )

        duration = (session_stop - session_start).total_seconds()
        st.metric("Session Duration", f"{duration:.1f} seconds")

    elif monitor_process is not None and monitor_process.poll() is None:
        duration = (datetime.now() - session_start).total_seconds()
        st.metric("Session Duration", f"{duration:.1f} seconds")
        st.info("Monitoring session is currently running.")

    else:
        st.info("The monitoring process has stopped.")

else:
    st.info("Start monitoring to begin a session.")


# ---------------- LOAD EVENT LOG ----------------

st.divider()
st.subheader("Monitoring Summary")

rows = []
ear_values = []

if os.path.exists(log_file):
    try:
        with open(
            log_file,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

    except (OSError, csv.Error, UnicodeError) as error:
        st.error(f"Could not read event log: {error}")

else:
    st.info(
        "Event log nahi mili. Monitoring start karo aur "
        "drowsiness event record hone do."
    )


# Extract EAR values safely

for row in rows:
    try:
        ear = float(row.get("EAR", ""))
        ear_values.append(ear)
    except (ValueError, TypeError):
        pass


# ---------------- METRICS ----------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Alert Events",
    len(rows)
)

if ear_values:
    average_ear = sum(ear_values) / len(ear_values)
    col2.metric("Average EAR", f"{average_ear:.3f}")
else:
    col2.metric("Average EAR", "N/A")

if rows:
    latest_event = rows[-1].get("Time", "N/A")
else:
    latest_event = "N/A"

col3.metric("Latest Event", latest_event)

col4.metric(
    "Logged Alert Events",
    len(rows)
)

st.caption(
    "Logged alert events are CSV records, not necessarily "
    "the total number of separate drowsiness episodes."
)


# ---------------- EVENT DATES ----------------

if rows:
    session_dates = [
        row.get("Date", "")
        for row in rows
        if row.get("Date", "")
    ]

    if session_dates:
        st.write("First recorded date:", session_dates[0])
        st.write("Latest recorded date:", session_dates[-1])


# ---------------- EAR TREND GRAPH ----------------

st.divider()
st.subheader("Drowsiness Alert Trend")

chart_rows = []

for row in rows:
    try:
        chart_rows.append({
            "Time": row.get("Time", ""),
            "EAR": float(row.get("EAR", ""))
        })
    except (ValueError, TypeError):
        pass

if chart_rows:
    chart_width = 700
    chart_height = 250
    margin = 40

    values = [item["EAR"] for item in chart_rows]
    max_value = max(max(values), 0.1)

    points = []
    count = len(values)

    for index, value in enumerate(values):
        x = margin + index * (
            (chart_width - 2 * margin) / max(count - 1, 1)
        )

        y = chart_height - margin - (
            value / max_value
        ) * (chart_height - 2 * margin)

        points.append(f"{x:.1f},{y:.1f}")

    points_string = " ".join(points)

    chart_html = f"""
    <svg viewBox="0 0 {chart_width} {chart_height}"
         style="width:100%; max-width:700px;
                border:1px solid #ddd; border-radius:8px;"
         role="img" aria-label="EAR trend graph">
        <line x1="{margin}" y1="{margin}"
              x2="{margin}" y2="{chart_height - margin}"
              stroke="gray" stroke-width="1"/>
        <line x1="{margin}" y1="{chart_height - margin}"
              x2="{chart_width - margin}"
              y2="{chart_height - margin}"
              stroke="gray" stroke-width="1"/>
        <polyline points="{points_string}"
                  fill="none" stroke="#16803c"
                  stroke-width="3"/>
        <text x="10" y="20" font-size="12">EAR Trend</text>
        <text x="{margin}" y="{chart_height - 10}"
              font-size="12">Older</text>
        <text x="{chart_width - 85}" y="{chart_height - 10}"
              font-size="12">Latest</text>
    </svg>
    """

    st.markdown(chart_html, unsafe_allow_html=True)

else:
    st.info("EAR trend graph will appear when valid EAR records exist.")


# ---------------- EVENT HISTORY TABLE ----------------

st.divider()
st.subheader("Drowsiness Event History")

if rows:
    headers = ["Date", "Time", "Event", "EAR"]

    table_html = """
    <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse;">
    <thead><tr>
    """

    for header in headers:
        table_html += (
            '<th style="text-align:left;padding:10px;'
            'border-bottom:1px solid #888;">'
            + html.escape(header)
            + "</th>"
        )

    table_html += "</tr></thead><tbody>"

    for row in rows:
        table_html += "<tr>"

        for header in headers:
            value = html.escape(str(row.get(header, "")))
            table_html += (
                '<td style="padding:10px;'
                'border-bottom:1px solid #ccc;">'
                + value
                + "</td>"
            )

        table_html += "</tr>"

    table_html += "</tbody></table></div>"

    st.markdown(table_html, unsafe_allow_html=True)

else:
    st.info("No drowsiness events have been recorded yet.")


# ---------------- CSV DOWNLOAD ----------------

st.divider()
st.subheader("Download Report")

if rows:
    output = io.StringIO()

    fieldnames = list(rows[0].keys())

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )

    writer.writeheader()
    writer.writerows(rows)

    st.download_button(
        label="Download Event History CSV",
        data=output.getvalue().encode("utf-8"),
        file_name="drowsiness_log.csv",
        mime="text/csv"
    )

else:
    st.caption("CSV download will be available after events are recorded.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Academic prototype only. This system is not validated "
    "for real-world driving safety."
)
