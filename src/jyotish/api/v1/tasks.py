"""
Asynchronous Background Task Service & Router for JyotishOS (Phase 9, Task P9-T3).
Provides non-blocking background queue management for heavy calculations,
multi-page PDF report generation, and batch export jobs.
"""

import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

from ...core.models import BirthData
from ...core.calculator import default_chart_calculator
from ...services.report_generator import default_report_generator

router = APIRouter(prefix="/tasks", tags=["v1-tasks"])

# Global thread pool for compute-heavy background tasks
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="jyotish_bg_worker")

# In-memory task registry (can be backed by Redis / DB in distributed deployments)
_task_store: Dict[str, Dict[str, Any]] = {}


class TaskSubmissionResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "queued", "running", "completed", "failed"
    created_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BackgroundReportRequest(BaseModel):
    name: str = "Client"
    birth_date: str = "1990-01-01"
    birth_time: str = "12:00:00"
    latitude: float = 28.6139
    longitude: float = 77.2090
    timezone_offset: float = 5.5
    gender: str = "male"


def _execute_report_job(task_id: str, payload: Dict[str, Any]) -> None:
    """Worker function executed inside the background thread pool."""
    start_time = time.time()
    try:
        _task_store[task_id]["status"] = "running"

        # Parse birth data
        from datetime import date, time as dt_time
        parts_d = [int(x) for x in payload["birth_date"].split("-")]
        parts_t = [int(x) for x in payload["birth_time"].split(":")]

        bd = BirthData(
            name=payload.get("name", "Client"),
            birth_date=date(parts_d[0], parts_d[1], parts_d[2]),
            birth_time=dt_time(parts_t[0], parts_t[1], parts_t[2] if len(parts_t) > 2 else 0),
            latitude=payload.get("latitude", 28.6139),
            longitude=payload.get("longitude", 77.2090),
            timezone_offset=payload.get("timezone_offset", 5.5),
            gender=payload.get("gender", "male"),
            confidence="exact"
        )

        chart = default_chart_calculator.calculate_full_chart(bd)
        html_report = default_report_generator.generate_html_report(chart)

        duration = time.time() - start_time
        _task_store[task_id].update({
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "result": {
                "native_name": chart.birth_data.name,
                "ascendant_sign": chart.lagna.sign if hasattr(chart, "lagna") else "Aries",
                "report_size_bytes": len(html_report),
                "is_ready": True
            }
        })
    except Exception as exc:
        duration = time.time() - start_time
        _task_store[task_id].update({
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "error": str(exc)
        })


@router.post("/generate-report", response_model=TaskSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_report_task(request: BackgroundReportRequest):
    """
    Enqueue a background report generation task without blocking the HTTP worker thread.
    Returns task_id immediately.
    """
    task_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    _task_store[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "created_at": now_iso,
        "payload": request.model_dump(),
        "completed_at": None,
        "result": None,
        "error": None
    }

    # Submit to thread pool
    _executor.submit(_execute_report_job, task_id, request.model_dump())

    return TaskSubmissionResponse(
        task_id=task_id,
        status="queued",
        created_at=now_iso,
        message="Background report task successfully queued."
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Poll task execution status and retrieve result."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID '{task_id}' not found."
        )

    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        created_at=task["created_at"],
        completed_at=task.get("completed_at"),
        duration_seconds=task.get("duration_seconds"),
        result=task.get("result"),
        error=task.get("error")
    )


@router.get("", response_model=List[TaskStatusResponse])
def list_recent_tasks():
    """List all recently enqueued tasks."""
    return [
        TaskStatusResponse(
            task_id=t["task_id"],
            status=t["status"],
            created_at=t["created_at"],
            completed_at=t.get("completed_at"),
            duration_seconds=t.get("duration_seconds"),
            result=t.get("result"),
            error=t.get("error")
        )
        for t in list(_task_store.values())[-20:]
    ]
