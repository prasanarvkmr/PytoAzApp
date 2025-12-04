import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="Databricks Jobs Dashboard",
    page_icon="⚡",
    layout="wide"
)

# FastAPI backend URL
API_URL = os.environ.get("API_URL", "http://localhost:8001")

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-success { color: #10b981; font-weight: bold; }
    .status-failed { color: #ef4444; font-weight: bold; }
    .status-running { color: #3b82f6; font-weight: bold; }
    .status-pending { color: #f59e0b; font-weight: bold; }
    .status-cancelled { color: #6b7280; font-weight: bold; }
    .stMetric {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

def get_status_color(status):
    colors = {
        "SUCCESS": "🟢",
        "FAILED": "🔴",
        "RUNNING": "🔵",
        "PENDING": "🟡",
        "CANCELLED": "⚫"
    }
    return colors.get(status, "⚪")

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Call the FastAPI backend"""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Unknown error")}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API server"}
    except Exception as e:
        return {"error": str(e)}

# Title
st.title("⚡ Databricks Jobs Dashboard")
st.caption("Real-time monitoring of Databricks job executions")

# Sidebar
with st.sidebar:
    st.header("🔧 Controls")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # API Health Check
    st.subheader("API Status")
    health = call_api("/health")
    if "error" not in health:
        st.success("✅ API Connected")
    else:
        st.error(f"❌ {health['error']}")
    
    st.divider()
    
    # Filters
    st.subheader("🔍 Filters")
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "RUNNING", "SUCCESS", "FAILED", "PENDING", "CANCELLED"]
    )
    
    jobs_data = call_api("/jobs")
    if "error" not in jobs_data:
        job_names = ["All"] + [job["job_name"] for job in jobs_data]
        job_filter = st.selectbox("Filter by Job", job_names)
    else:
        job_filter = "All"

# Main content
# Summary metrics
st.header("📊 Summary")
summary = call_api("/summary")

if "error" not in summary:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Runs", summary["total_jobs"])
    with col2:
        st.metric("🔵 Running", summary["running"])
    with col3:
        st.metric("🟢 Success", summary["success"])
    with col4:
        st.metric("🔴 Failed", summary["failed"])
    with col5:
        st.metric("🟡 Pending", summary["pending"])
    with col6:
        st.metric("Success Rate", f"{summary['success_rate']}%")
else:
    st.error(f"Failed to load summary: {summary['error']}")

st.divider()

# Two column layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("📋 Recent Job Runs")
    
    # Build query params
    params = "?limit=30"
    if status_filter != "All":
        params += f"&status={status_filter}"
    
    runs = call_api(f"/runs{params}")
    
    if "error" not in runs and runs:
        # Convert to DataFrame
        df = pd.DataFrame(runs)
        
        # Get jobs data for schedule and owner info
        jobs_info = call_api("/jobs")
        jobs_dict = {}
        if "error" not in jobs_info:
            jobs_dict = {job["job_id"]: job for job in jobs_info}
        
        # Add schedule and owner from jobs data
        df["schedule"] = df["job_id"].apply(lambda x: jobs_dict.get(x, {}).get("schedule", "N/A"))
        df["owner"] = df["job_id"].apply(lambda x: jobs_dict.get(x, {}).get("created_by", "N/A"))
        
        # Filter by job name if selected
        if job_filter != "All":
            df = df[df["job_name"] == job_filter]
        
        # Format display
        df["status_icon"] = df["status"].apply(get_status_color)
        df["display_status"] = df["status_icon"] + " " + df["status"]
        df["start_time_formatted"] = pd.to_datetime(df["start_time"]).dt.strftime("%Y-%m-%d %H:%M")
        df["duration"] = df["duration_seconds"].apply(
            lambda x: f"{x//60}m {x%60}s" if pd.notna(x) and x else "Running..."
        )
        
        # Display table with selection
        display_df = df[["run_id", "job_name", "display_status", "start_time_formatted", "duration", "schedule", "owner", "cluster_name"]]
        display_df.columns = ["Run ID", "Job Name", "Status", "Start Time", "Duration", "Schedule", "Owner", "Cluster"]
        
        # Use data editor for row selection
        selected_job_name = st.selectbox(
            "📈 Select a job to view run history chart:",
            options=["Select a job..."] + df["job_name"].unique().tolist(),
            key="chart_job_select"
        )
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=350
        )
        
        # Time series bar chart for selected job
        if selected_job_name != "Select a job...":
            st.subheader(f"📊 Run Duration History: {selected_job_name}")
            
            job_runs_df = df[df["job_name"] == selected_job_name].copy()
            job_runs_df = job_runs_df[job_runs_df["duration_seconds"].notna()]
            
            if not job_runs_df.empty:
                # Prepare chart data
                job_runs_df["start_time_dt"] = pd.to_datetime(job_runs_df["start_time"])
                job_runs_df = job_runs_df.sort_values("start_time_dt")
                job_runs_df["duration_min"] = job_runs_df["duration_seconds"] / 60
                job_runs_df["run_label"] = job_runs_df["start_time_dt"].dt.strftime("%m/%d %H:%M")
                
                # Create color-coded bar chart using Altair
                import altair as alt
                
                # Define color based on status
                color_scale = alt.Scale(
                    domain=["SUCCESS", "FAILED", "CANCELLED", "RUNNING", "PENDING"],
                    range=["#10b981", "#ef4444", "#6b7280", "#3b82f6", "#f59e0b"]
                )
                
                chart = alt.Chart(job_runs_df).mark_bar(size=20).encode(
                    x=alt.X("run_label:N", title="Run Time", sort=None, axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("duration_min:Q", title="Duration (minutes)"),
                    color=alt.Color("status:N", scale=color_scale, title="Status"),
                    tooltip=[
                        alt.Tooltip("run_id:N", title="Run ID"),
                        alt.Tooltip("status:N", title="Status"),
                        alt.Tooltip("duration_min:Q", title="Duration (min)", format=".1f"),
                        alt.Tooltip("run_label:N", title="Start Time"),
                        alt.Tooltip("cluster_name:N", title="Cluster")
                    ]
                ).properties(
                    height=300
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=13
                )
                
                st.altair_chart(chart, use_container_width=True)
                
                # Show stats for this job
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                job_all_runs = df[df["job_name"] == selected_job_name]
                with col_s1:
                    st.metric("Total Runs", len(job_all_runs))
                with col_s2:
                    success_count = len(job_all_runs[job_all_runs["status"] == "SUCCESS"])
                    st.metric("Successful", success_count)
                with col_s3:
                    failed_count = len(job_all_runs[job_all_runs["status"] == "FAILED"])
                    st.metric("Failed", failed_count)
                with col_s4:
                    avg_duration = job_runs_df["duration_min"].mean()
                    st.metric("Avg Duration", f"{avg_duration:.1f} min")
            else:
                st.info("No completed runs with duration data available for this job.")
        
        # Show failed job details
        failed_runs = df[df["status"] == "FAILED"]
        if not failed_runs.empty:
            with st.expander("🔴 Failed Job Details", expanded=False):
                for _, run in failed_runs.iterrows():
                    st.error(f"**Run {run['run_id']}** - {run['job_name']}: {run.get('error_message', 'Unknown error')}")
    else:
        st.info("No job runs found matching the criteria")

with col_right:
    st.header("📌 Configured Jobs")
    
    jobs = call_api("/jobs")
    
    if "error" not in jobs:
        for job in jobs:
            status_icon = get_status_color(job["last_run_status"])
            
            with st.container():
                st.markdown(f"""
                **{job['job_name']}** {status_icon}
                - Job ID: `{job['job_id']}`
                - Schedule: `{job['schedule']}`
                - Owner: {job['created_by']}
                """)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("▶️ Trigger", key=f"trigger_{job['job_id']}", use_container_width=True):
                        result = call_api(f"/jobs/{job['job_id']}/trigger", method="POST")
                        if "error" not in result:
                            st.success(f"Triggered! Run ID: {result['run_id']}")
                        else:
                            st.error(result["error"])
                with col_b:
                    if st.button("📊 History", key=f"history_{job['job_id']}", use_container_width=True):
                        st.session_state[f"show_history_{job['job_id']}"] = True
                
                st.divider()
    else:
        st.error(f"Failed to load jobs: {jobs['error']}")

# Job Run History Modal
st.header("📈 Job Performance")

if "error" not in jobs:
    selected_job = st.selectbox(
        "Select Job for Detailed View",
        options=[f"{job['job_id']} - {job['job_name']}" for job in jobs]
    )
    
    if selected_job:
        job_id = int(selected_job.split(" - ")[0])
        job_runs = call_api(f"/runs/job/{job_id}?limit=10")
        
        if "error" not in job_runs and job_runs:
            # Create chart data
            chart_data = pd.DataFrame(job_runs)
            chart_data["start_time"] = pd.to_datetime(chart_data["start_time"])
            chart_data["duration_min"] = chart_data["duration_seconds"].fillna(0) / 60
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Run Duration Trend")
                st.line_chart(
                    chart_data.set_index("start_time")["duration_min"],
                    use_container_width=True
                )
            
            with col2:
                st.subheader("Status Distribution")
                status_counts = chart_data["status"].value_counts()
                st.bar_chart(status_counts, use_container_width=True)
        else:
            st.info("No run history available for this job")

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Dashboard v1.0")
