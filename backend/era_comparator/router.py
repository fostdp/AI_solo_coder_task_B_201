from fastapi import APIRouter, HTTPException
from .service import era_comparator_service


router = APIRouter(prefix="/api/era-comparator", tags=["Era Comparator"])


@router.get("/eras")
async def list_eras():
    return era_comparator_service.list_eras()


@router.get("/eras/{era_id}")
async def get_era(era_id: str):
    era = era_comparator_service.get_era(era_id)
    if not era:
        raise HTTPException(status_code=404, detail=f"Era '{era_id}' not found")
    return era


@router.get("/ancient-vs-modern")
async def ancient_vs_modern():
    return era_comparator_service.compare_ancient_vs_modern()
