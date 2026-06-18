from typing import Dict, Any, List, Optional
from .crafts_data import (
    get_ancient_crafts,
    get_modern_crafts,
    get_all_crafts,
    get_craft_by_id,
    compare_crafts,
    calculate_defect_rate_for_conditions,
)


class ProcessComparatorService:
    def __init__(self):
        pass

    def list_ancient_crafts(self) -> List[Dict[str, Any]]:
        return get_ancient_crafts()

    def list_modern_crafts(self) -> List[Dict[str, Any]]:
        return get_modern_crafts()

    def list_all_crafts(self) -> List[Dict[str, Any]]:
        return get_all_crafts()

    def get_craft_detail(self, craft_id: str) -> Optional[Dict[str, Any]]:
        return get_craft_by_id(craft_id)

    def compare(self, craft_ids: List[str]) -> Dict[str, Any]:
        return compare_crafts(craft_ids)

    def calculate_defect_rate(
        self,
        craft_id: str,
        pouring_temp: float,
        shell_permeability: float,
        alloy_type: str = "bronze",
    ) -> Dict[str, Any]:
        return calculate_defect_rate_for_conditions(
            craft_id, pouring_temp, shell_permeability, alloy_type
        )


process_comparator_service = ProcessComparatorService()
