from typing import Dict, Any, List, Optional
from .worker_manager import get_cfd_manager, CFDJob


class CFDWorkerService:
    def __init__(self):
        pass

    def submit_simulation(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        manager = get_cfd_manager()
        job_id = manager.submit_job(params)

        job = manager.get_job(job_id)
        return {
            "job_id": job_id,
            "status": job.status.value if job else "pending",
            "params": params,
            "created_at": job.created_at if job else None,
        }

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        manager = get_cfd_manager()
        return manager.get_job_status(job_id)

    def get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        manager = get_cfd_manager()
        result = manager.get_job_result(job_id)
        if result is None:
            return None
        return {
            "job_id": job_id,
            "status": "completed",
            "result": result,
        }

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        manager = get_cfd_manager()
        success = manager.cancel_job(job_id)
        return {
            "job_id": job_id,
            "cancelled": success,
        }

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        manager = get_cfd_manager()
        return manager.list_jobs(limit)

    def get_stats(self) -> Dict[str, Any]:
        manager = get_cfd_manager()
        return manager.get_stats()

    def run_sync(
        self,
        params: Dict[str, Any],
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        from .amr_simulator import run_amr_simulation

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
        )

        return {
            "job_id": "sync_" + str(hash(str(params))),
            "status": "completed",
            "result": result,
        }


cfd_worker_service = CFDWorkerService()
