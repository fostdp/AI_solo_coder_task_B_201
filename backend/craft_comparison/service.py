from typing import Dict, Any, List, Optional
from .crafts_data import (
    get_ancient_crafts,
    get_modern_crafts,
    get_all_crafts,
    get_craft_by_id,
    compare_crafts,
    calculate_defect_rate_for_conditions,
)


class CraftComparisonService:
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

    def ancient_vs_modern_comparison(self) -> Dict[str, Any]:
        ancient = self.list_ancient_crafts()
        modern = self.list_modern_crafts()

        avg_ancient_defect = sum(c["overall_defect_rate"] for c in ancient) / len(ancient) if ancient else 0
        avg_modern_defect = sum(c["overall_defect_rate"] for c in modern) / len(modern) if modern else 0

        avg_ancient_accuracy = sum(c["dimensional_accuracy_mm"] for c in ancient) / len(ancient) if ancient else 0
        avg_modern_accuracy = sum(c["dimensional_accuracy_mm"] for c in modern) / len(modern) if modern else 0

        accuracy_improvement = (avg_ancient_accuracy / avg_modern_accuracy) if avg_modern_accuracy > 0 else 0
        defect_reduction = (avg_ancient_defect - avg_modern_defect) / avg_ancient_defect * 100 if avg_ancient_defect > 0 else 0

        return {
            "ancient_crafts": ancient,
            "modern_crafts": modern,
            "summary": {
                "avg_ancient_defect_rate": round(avg_ancient_defect * 100, 2),
                "avg_modern_defect_rate": round(avg_modern_defect * 100, 2),
                "defect_reduction_percent": round(defect_reduction, 2),
                "avg_ancient_accuracy_mm": round(avg_ancient_accuracy, 3),
                "avg_modern_accuracy_mm": round(avg_modern_accuracy, 3),
                "accuracy_improvement_factor": round(accuracy_improvement, 1),
            },
            "key_insights": [
                f"现代熔模铸造的缺陷率比古代失蜡法降低约 {defect_reduction:.1f}%",
                f"尺寸精度提升约 {accuracy_improvement:.1f} 倍（从 {avg_ancient_accuracy:.2f}mm 到 {avg_modern_accuracy:.2f}mm）",
                "古代工艺受限于手工技艺和自然条件，成品率波动较大",
                "现代工艺借助真空浇铸、温控炉等设备，大幅提升一致性",
            ],
        }


craft_service = CraftComparisonService()
