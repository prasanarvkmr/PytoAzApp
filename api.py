from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

app = FastAPI(title="Databricks Jobs Tracker API", description="REST API for tracking Databricks job status")

# Simulated job data (in production, this would connect to Databricks API)
class JobRun(BaseModel):
    run_id: int
    job_id: int
    job_name: str
    status: str  # PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    cluster_name: str
    triggered_by: str
    error_message: Optional[str] = None

class JobSummary(BaseModel):
    total_jobs: int
    running: int
    success: int
    failed: int
    pending: int
    cancelled: int
    success_rate: float

class Job(BaseModel):
    job_id: int
    job_name: str
    schedule: str
    last_run_status: str
    next_run_time: Optional[datetime] = None
    created_by: str

# Simulated data store
def generate_sample_jobs() -> List[Job]:
    jobs = [
        Job(job_id=101, job_name="ETL_Sales_Daily", schedule="0 6 * * *", last_run_status="SUCCESS", 
            next_run_time=datetime.now() + timedelta(hours=2), created_by="data_team"),
        Job(job_id=102, job_name="ML_Model_Training", schedule="0 0 * * 0", last_run_status="RUNNING",
            next_run_time=datetime.now() + timedelta(days=3), created_by="ml_team"),
        Job(job_id=103, job_name="Data_Quality_Check", schedule="0 */4 * * *", last_run_status="FAILED",
            next_run_time=datetime.now() + timedelta(hours=1), created_by="data_team"),
        Job(job_id=104, job_name="Customer_Segmentation", schedule="0 12 * * *", last_run_status="SUCCESS",
            next_run_time=datetime.now() + timedelta(hours=8), created_by="analytics_team"),
        Job(job_id=105, job_name="Report_Generation", schedule="0 8 * * 1-5", last_run_status="SUCCESS",
            next_run_time=datetime.now() + timedelta(hours=12), created_by="bi_team"),
        Job(job_id=106, job_name="Log_Aggregation", schedule="*/30 * * * *", last_run_status="PENDING",
            next_run_time=datetime.now() + timedelta(minutes=15), created_by="devops_team"),
        Job(job_id=107, job_name="Inventory_Sync", schedule="0 */2 * * *", last_run_status="CANCELLED",
            next_run_time=datetime.now() + timedelta(hours=1), created_by="supply_chain"),
        Job(job_id=108, job_name="Fraud_Detection", schedule="*/15 * * * *", last_run_status="RUNNING",
            next_run_time=datetime.now() + timedelta(minutes=10), created_by="security_team"),
    ]
    return jobs

def generate_sample_runs() -> List[JobRun]:
    statuses = ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "RUNNING", "PENDING", "CANCELLED"]
    clusters = ["etl-cluster", "ml-cluster", "analytics-cluster", "general-cluster"]
    users = ["scheduler", "admin", "data_engineer", "analyst"]
    
    runs = []
    base_time = datetime.now()
    
    for i in range(50):
        status = random.choice(statuses)
        start_time = base_time - timedelta(hours=random.randint(1, 72))
        duration = random.randint(60, 7200) if status in ["SUCCESS", "FAILED", "CANCELLED"] else None
        end_time = start_time + timedelta(seconds=duration) if duration else None
        
        run = JobRun(
            run_id=10000 + i,
            job_id=101 + (i % 8),
            job_name=generate_sample_jobs()[i % 8].job_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            cluster_name=random.choice(clusters),
            triggered_by=random.choice(users),
            error_message="Task failed due to cluster timeout" if status == "FAILED" else None
        )
        runs.append(run)
    
    return sorted(runs, key=lambda x: x.start_time, reverse=True)

# API Endpoints
@app.get("/")
def root():
    return {"message": "Databricks Jobs Tracker API", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/jobs", response_model=List[Job])
def get_jobs():
    """Get all configured Databricks jobs"""
    return generate_sample_jobs()

@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
    """Get a specific job by ID"""
    jobs = generate_sample_jobs()
    for job in jobs:
        if job.job_id == job_id:
            return job
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

@app.get("/runs", response_model=List[JobRun])
def get_runs(limit: int = 20, status: Optional[str] = None, job_id: Optional[int] = None):
    """Get recent job runs with optional filtering"""
    runs = generate_sample_runs()
    
    if status:
        runs = [r for r in runs if r.status == status.upper()]
    if job_id:
        runs = [r for r in runs if r.job_id == job_id]
    
    return runs[:limit]

@app.get("/runs/{run_id}", response_model=JobRun)
def get_run(run_id: int):
    """Get a specific job run by run ID"""
    runs = generate_sample_runs()
    for run in runs:
        if run.run_id == run_id:
            return run
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

@app.get("/summary", response_model=JobSummary)
def get_summary():
    """Get summary statistics of job runs"""
    runs = generate_sample_runs()
    
    total = len(runs)
    running = len([r for r in runs if r.status == "RUNNING"])
    success = len([r for r in runs if r.status == "SUCCESS"])
    failed = len([r for r in runs if r.status == "FAILED"])
    pending = len([r for r in runs if r.status == "PENDING"])
    cancelled = len([r for r in runs if r.status == "CANCELLED"])
    
    completed = success + failed
    success_rate = (success / completed * 100) if completed > 0 else 0
    
    return JobSummary(
        total_jobs=total,
        running=running,
        success=success,
        failed=failed,
        pending=pending,
        cancelled=cancelled,
        success_rate=round(success_rate, 2)
    )

@app.get("/runs/job/{job_id}", response_model=List[JobRun])
def get_runs_by_job(job_id: int, limit: int = 10):
    """Get runs for a specific job"""
    runs = generate_sample_runs()
    job_runs = [r for r in runs if r.job_id == job_id]
    return job_runs[:limit]

@app.post("/jobs/{job_id}/trigger")
def trigger_job(job_id: int):
    """Trigger a job run manually"""
    jobs = generate_sample_jobs()
    for job in jobs:
        if job.job_id == job_id:
            return {
                "message": f"Job '{job.job_name}' triggered successfully",
                "run_id": random.randint(20000, 29999),
                "status": "PENDING"
            }
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

@app.post("/runs/{run_id}/cancel")
def cancel_run(run_id: int):
    """Cancel a running job"""
    return {
        "message": f"Run {run_id} cancellation requested",
        "status": "CANCELLING"
    }
