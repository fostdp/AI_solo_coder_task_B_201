from typing import Dict, Any, List, Optional
from .era_data import (
    ancient_vs_modern_comparison,
    get_era_info,
    get_all_eras,
)


class EraComparatorService:
    def __init__(self):
        pass

    def list_eras(self) -> List[Dict[str, Any]]:
        return get_all_eras()

    def get_era(self, era_id: str) -> Optional[Dict[str, Any]]:
        return get_era_info(era_id)

    def compare_ancient_vs_modern(self) -> Dict[str, Any]:
        return ancient_vs_modern_comparison()


era_comparator_service = EraComparatorService()
