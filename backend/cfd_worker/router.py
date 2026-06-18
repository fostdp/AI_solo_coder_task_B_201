from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel
from .service import cfd_worker_service
from .worker_manager import start_cfd_workers, get_cfd_manager


class SimulationParams(BaseModel):
    domain_size: Optional[list] = None
    base_cells: Optional[list] = None
    max_levels: int = 3
    total_time: float = 10.0
    dt: float = 0.1
    fluid_density: float = 7800.0
    fluid_viscosity: float = 4.5e-3
    pouring_velocity: Optional[list] = None
    inlet_pos: Optional[list] = None
    inlet_radius: float = 15.0


router = APIRouter(prefix="/api/cfd-worker", tags=["CFD Worker"])


@router.on_event("startup")
async def startup_event():
    start_cfd_workers(num_workers=1)


@router.post("/submit")
async def submit_simulation(params: SimulationParams):
    params_dict = params.model_dump(exclude_none=True)
    if params.domain_size:
        params_dict["domain_size"] = tuple(params.domain_size)
    if params.base_cells:
        params_dict["base_cells"] = tuple(params.base_cells)
    if params.pouring_velocity:
        params_dict["pouring_velocity"] = tuple(params.pouring_velocity)
    if params.inlet_pos:
        params_dict["inlet_pos"] = tuple(params.inlet_pos)

    return cfd_worker_service.submit_simulation(params_dict)


@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    status = cfd_worker_service.get_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return status


@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    result = cfd_worker_service.get_result(job_id)
    if not result:
        status = cfd_worker_service.get_status(job_id)
        if status:
            return status
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return result


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    result = cfd_worker_service.cancel_job(job_id)
    if not result["cancelled"]:
        raise HTTPException(status_code=400, detail=f"Job '{job_id}' cannot be cancelled")
    return result


@router.get("/jobs")
async def list_jobs(limit: int = 50):
    return cfd_worker_service.list_jobs(limit)


@router.get("/stats")
async def get_stats():
    return cfd_worker_service.get_stats()


@router.post("/run-sync")
async def run_simulation_sync(params: SimulationParams):
    params_dict = params.model_dump(exclude_none=True)
    if params.domain_size:
        params_dict["domain_size"] = tuple(params.domain_size)
    if params.base_cells:
        params_dict["base_cells"] = tuple(params.base_cells)
    if params.pouring_velocity:
        params_dict["pouring_velocity"] = tuple(params.pouring_velocity)
    if params.inlet_pos:
        params_dict["inlet_pos"] = tuple(params.inlet_pos)

    return cfd_worker_service.run_sync(params_dict)
