from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from arq.jobs import Job as ArqJob
from ...core.utils import queue
from ...api.dependencies import rate_limiter_dependency
from ...schemas.job import Job

task_router = APIRouter(prefix="/jobs", tags=["job_tasks"])

async def _check_queue() -> Any:
    q = queue.pool
    if q is None:
        raise HTTPException(status_code=503, detail="Queue not initialized")
    return q

@task_router.post("/enqueue", response_model=Job, status_code=201, dependencies=[Depends(rate_limiter_dependency)])
async def add_job_to_queue(task_message: str):
    q = await _check_queue()
    new_job = await q.enqueue_job("sample_background_task", task_message)
    if new_job is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue task")
    return {"id": new_job.job_id}

@task_router.get("/status/{job_id}")
async def get_job_info(job_id: str):
    q = await _check_queue()
    job_instance = ArqJob(job_id, q)
    job_data = await job_instance.info()
    return job_data.__dict__ if job_data else None
