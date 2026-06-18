from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .service import virtual_service


class GenerateGeometryRequest(BaseModel):
    template_id: str
    params: Dict[str, Any] = {}


class SimulateCastingRequest(BaseModel):
    template_id: str
    params: Dict[str, Any] = {}
    material_id: str = "bronze_cu_sn"
    shell_id: str = "silica_sol"
    pouring_temp: Optional[float] = None


router = APIRouter(prefix="/api/virtual", tags=["Virtual Experience"])


@router.get("/templates")
async def list_templates():
    return virtual_service.list_templates()


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    template = virtual_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.get("/materials")
async def list_materials():
    return virtual_service.list_materials()


@router.get("/shells")
async def list_shells():
    return virtual_service.list_shells()


@router.post("/geometry")
async def generate_geometry(req: GenerateGeometryRequest):
    result = virtual_service.generate_geometry(req.template_id, req.params)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/simulate")
async def simulate_casting(req: SimulateCastingRequest):
    result = virtual_service.simulate(
        template_id=req.template_id,
        params=req.params,
        material_id=req.material_id,
        shell_id=req.shell_id,
        pouring_temp=req.pouring_temp,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/experiments")
async def list_experiments(limit: int = Query(20, ge=1, le=100)):
    return virtual_service.list_experiments(limit)


@router.get("/experiments/{exp_id}")
async def get_experiment(exp_id: str):
    exp = virtual_service.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.post("/experiments")
async def save_experiment(experiment: Dict[str, Any]):
    return virtual_service.save_experiment(experiment)
