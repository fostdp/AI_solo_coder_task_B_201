from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from .service import permeability_analyzer_service


class ScenarioRequest(BaseModel):
    name: str
    alloy_type: str = "bronze"
    pouring_temp: float = 1180.0
    shell_thickness: int = 9


class CompareScenariosRequest(BaseModel):
    scenarios: List[ScenarioRequest]


router = APIRouter(prefix="/api/permeability-analyzer", tags=["Permeability Analyzer"])


@router.get("/impact")
async def analyze_permeability_impact(
    alloy_type: str = Query("bronze", description="Alloy type"),
    pouring_temp: float = Query(1180.0, description="Pouring temperature in °C"),
    shell_thickness: int = Query(9, description="Shell layers count"),
):
    return permeability_analyzer_service.analyze_impact(
        alloy_type=alloy_type,
        pouring_temp=pouring_temp,
        shell_thickness=shell_thickness,
    )


@router.get("/historical/{casting_id}")
async def analyze_historical(casting_id: str):
    result = permeability_analyzer_service.analyze_historical(casting_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/compare")
async def compare_scenarios(req: CompareScenariosRequest):
    scenarios = [s.model_dump() for s in req.scenarios]
    return permeability_analyzer_service.compare_scenarios(scenarios)
