from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from .service import vr_lost_wax_service


class SimulateRequest(BaseModel):
    template_id: str
    params: dict
    material_id: str = "bronze_cu_sn"
    shell_id: str = "silica_sol"
    pouring_temp: Optional[float] = None


class GeometryRequest(BaseModel):
    template_id: str
    params: dict


class SimpleModeRequest(BaseModel):
    template_id: str
    size_level: int = Field(3, ge=1, le=5)
    ornament_level: int = Field(3, ge=1, le=5)
    thickness_level: int = Field(3, ge=1, le=5)


class PresetRequest(BaseModel):
    template_id: str
    preset_id: str


router = APIRouter(prefix="/api/vr-lost-wax", tags=["VR Lost Wax"])


@router.get("/templates")
async def list_templates(
    audience: Optional[str] = None,
    category: Optional[str] = None,
):
    return vr_lost_wax_service.list_templates(audience=audience, category=category)


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    template = vr_lost_wax_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.get("/materials")
async def list_materials():
    return vr_lost_wax_service.list_materials()


@router.get("/shell-materials")
async def list_shell_materials():
    return vr_lost_wax_service.list_shell_materials()


@router.get("/simple-mode/presets")
async def simple_mode_presets():
    return vr_lost_wax_service.simple_mode_presets()


@router.get("/simple-mode/params")
async def simple_mode_params():
    return vr_lost_wax_service.simple_mode_params()


@router.post("/simple-mode/apply")
async def apply_simple_mode(req: SimpleModeRequest):
    result = vr_lost_wax_service.apply_simple_mode(
        template_id=req.template_id,
        size_level=req.size_level,
        ornament_level=req.ornament_level,
        thickness_level=req.thickness_level,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/simple-mode/preset")
async def apply_preset(req: PresetRequest):
    result = vr_lost_wax_service.apply_preset(
        template_id=req.template_id,
        preset_id=req.preset_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/geometry")
async def generate_geometry(req: GeometryRequest):
    result = vr_lost_wax_service.generate_geometry(
        template_id=req.template_id,
        params=req.params,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/simulate")
async def simulate(req: SimulateRequest):
    result = vr_lost_wax_service.simulate(
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
async def list_experiments(limit: int = 20):
    return vr_lost_wax_service.list_experiments(limit)


@router.get("/experiments/{exp_id}")
async def get_experiment(exp_id: str):
    exp = vr_lost_wax_service.get_experiment(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{exp_id}' not found")
    return exp
