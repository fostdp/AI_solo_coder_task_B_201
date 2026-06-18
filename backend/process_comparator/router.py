from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from .service import process_comparator_service


class CalculateDefectRateRequest(BaseModel):
    craft_id: str
    pouring_temp: float
    shell_permeability: float
    alloy_type: str = "bronze"


router = APIRouter(prefix="/api/process-comparator", tags=["Process Comparator"])


@router.get("/ancient")
async def list_ancient_crafts():
    return process_comparator_service.list_ancient_crafts()


@router.get("/modern")
async def list_modern_crafts():
    return process_comparator_service.list_modern_crafts()


@router.get("/all")
async def list_all_crafts():
    return process_comparator_service.list_all_crafts()


@router.get("/{craft_id}")
async def get_craft_detail(craft_id: str):
    craft = process_comparator_service.get_craft_detail(craft_id)
    if not craft:
        raise HTTPException(status_code=404, detail=f"Craft '{craft_id}' not found")
    return craft


@router.get("/compare")
async def compare_crafts(
    craft_ids: str = Query(..., description="Comma-separated list of craft IDs")
):
    ids = [cid.strip() for cid in craft_ids.split(",") if cid.strip()]
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 craft IDs are required")
    return process_comparator_service.compare(ids)


@router.post("/calculate-defect-rate")
async def calculate_defect_rate(req: CalculateDefectRateRequest):
    result = process_comparator_service.calculate_defect_rate(
        craft_id=req.craft_id,
        pouring_temp=req.pouring_temp,
        shell_permeability=req.shell_permeability,
        alloy_type=req.alloy_type,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
