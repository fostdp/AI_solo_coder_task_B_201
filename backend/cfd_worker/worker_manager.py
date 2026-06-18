import multiprocessing as mp
from multiprocessing import Process, Queue, Manager
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CFDJob:
    job_id: str
    params: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


def _cfd_worker_process(job_queue: Queue, result_queue: Queue, worker_id: int):
    from .amr_simulator import run_amr_simulation

    logger.info(f"CFD Worker {worker_id} started")

    while True:
        try:
            job_data = job_queue.get(timeout=10)
        except Exception:
            continue

        if job_data is None:
            break

        job_id = job_data["job_id"]
        params = job_data["params"]

        result_queue.put({
            "job_id": job_id,
            "status": JobStatus.RUNNING.value,
            "progress": 0.0,
            "timestamp": time.time(),
        })

        try:
            def progress_callback(progress: float, info: Dict[str, Any]):
                result_queue.put({
                    "job_id": job_id,
                    "status": JobStatus.RUNNING.value,
                    "progress": progress,
                    "info": info,
                    "timestamp": time.time(),
                })

            result = run_amr_simulation(
                domain_size=tuple(params.get("domain_size", (200.0, 200.0))),
                base_cells=tuple(params.get("base_cells", (40, 40))),
                max_levels=params.get("max_levels", 3),
                total_time=params.get("total_time", 10.0),
                dt=params.get("dt", 0.1),
                fluid_density=params.get("fluid_density", 7800.0),
                fluid_viscosity=params.get("fluid_viscosity", 4.5e-3),
                pouring_velocity=tuple(params.get("pouring_velocity", (0.0, -1.5))),
                inlet_pos=tuple(params.get("inlet_pos", (100.0, 200.0))),
                inlet_radius=params.get("inlet_radius", 15.0),
                progress_callback=progress_callback,
            )

            result_queue.put({
                "job_id": job_id,
                "status": JobStatus.COMPLETED.value,
                "progress": 1.0,
                "result": result,
                "timestamp": time.time(),
            })

        except Exception as e:
            logger.exception(f"CFD job {job_id} failed")
            result_queue.put({
                "job_id": job_id,
                "status": JobStatus.FAILED.value,
                "progress": 0.0,
                "error": str(e),
                "timestamp": time.time(),
            })

    logger.info(f"CFD Worker {worker_id} stopped")


class CFDWorkerManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._manager = Manager()
        self._job_queue: Queue = self._manager.Queue()
        self._result_queue: Queue = self._manager.Queue()

        self._jobs: Dict[str, CFDJob] = {}
        self._jobs_lock = threading.Lock()

        self._workers: List[Process] = []
        self._num_workers = 1

        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

        self._callbacks: Dict[str, Callable] = {}

    def start(self, num_workers: int = 1):
        if self._running:
            return

        self._num_workers = num_workers
        self._running = True

        for i in range(num_workers):
            worker = Process(
                target=_cfd_worker_process,
                args=(self._job_queue, self._result_queue, i),
                daemon=True,
            )
            worker.start()
            self._workers.append(worker)
            logger.info(f"Started CFD worker process {i} (PID: {worker.pid})")

        self._monitor_thread = threading.Thread(target=self._monitor_results, daemon=True)
        self._monitor_thread.start()

        logger.info(f"CFD Worker Manager started with {num_workers} workers")

    def stop(self):
        self._running = False

        for _ in range(self._num_workers):
            try:
                self._job_queue.put(None)
            except Exception:
                pass

        for worker in self._workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=2)

        self._workers.clear()
        logger.info("CFD Worker Manager stopped")

    def _monitor_results(self):
        while self._running:
            try:
                result = self._result_queue.get(timeout=1)
            except Exception:
                continue

            job_id = result.get("job_id")
            if not job_id:
                continue

            with self._jobs_lock:
                job = self._jobs.get(job_id)
                if not job:
                    continue

                status = result.get("status")
                if status == JobStatus.RUNNING.value:
                    if job.status != JobStatus.RUNNING:
                        job.status = JobStatus.RUNNING
                        job.started_at = result.get("timestamp", time.time())
                    job.progress = result.get("progress", 0.0)

                elif status == JobStatus.COMPLETED.value:
                    job.status = JobStatus.COMPLETED
                    job.progress = 1.0
                    job.result = result.get("result")
                    job.completed_at = result.get("timestamp", time.time())

                elif status == JobStatus.FAILED.value:
                    job.status = JobStatus.FAILED
                    job.error = result.get("error")
                    job.completed_at = result.get("timestamp", time.time())

                callback = self._callbacks.get(job_id)
                if callback:
                    try:
                        callback(job)
                    except Exception:
                        logger.exception(f"Error in callback for job {job_id}")

    def submit_job(
        self,
        params: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> str:
        job_id = str(uuid.uuid4())

        job = CFDJob(
            job_id=job_id,
            params=params,
        )

        with self._jobs_lock:
            self._jobs[job_id] = job
            if callback:
                self._callbacks[job_id] = callback

        self._job_queue.put({
            "job_id": job_id,
            "params": params,
        })

        logger.info(f"Submitted CFD job {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Optional[CFDJob]:
        with self._jobs_lock:
            return self._jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.get_job(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "has_result": job.result is not None,
            "has_error": job.error is not None,
            "error": job.error,
        }

    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.get_job(job_id)
        if not job or job.status != JobStatus.COMPLETED:
            return None
        return job.result

    def cancel_job(self, job_id: str) -> bool:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return False
            job.status = JobStatus.CANCELLED
            return True

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._jobs_lock:
            jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
            return [
                {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                }
                for job in jobs[:limit]
            ]

    def get_stats(self) -> Dict[str, Any]:
        with self._jobs_lock:
            total = len(self._jobs)
            pending = sum(1 for j in self._jobs.values() if j.status == JobStatus.PENDING)
            running = sum(1 for j in self._jobs.values() if j.status == JobStatus.RUNNING)
            completed = sum(1 for j in self._jobs.values() if j.status == JobStatus.COMPLETED)
            failed = sum(1 for j in self._jobs.values() if j.status == JobStatus.FAILED)

        return {
            "num_workers": self._num_workers,
            "total_jobs": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "is_running": self._running,
        }


_cfd_manager: Optional[CFDWorkerManager] = None


def get_cfd_manager() -> CFDWorkerManager:
    global _cfd_manager
    if _cfd_manager is None:
        _cfd_manager = CFDWorkerManager()
    return _cfd_manager


def start_cfd_workers(num_workers: int = 1):
    manager = get_cfd_manager()
    manager.start(num_workers=num_workers)


def stop_cfd_workers():
    global _cfd_manager
    if _cfd_manager is not None:
        _cfd_manager.stop()
        _cfd_manager = None
