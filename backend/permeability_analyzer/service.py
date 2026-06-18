from typing import Dict, Any, List
from .analyzer import (
    calculate_permeability_impact,
    analyze_historical_data,
    compare_permeability_scenarios,
)


class PermeabilityAnalyzerService:
    def __init__(self):
        pass

    def analyze_impact(
        self,
        alloy_type: str = "bronze",
        pouring_temp: float = 1180.0,
        shell_thickness: int = 9,
    ) -> Dict[str, Any]:
        return calculate_permeability_impact(
            alloy_type=alloy_type,
            pouring_temp=pouring_temp,
            shell_thickness=shell_thickness,
        )

    def analyze_historical(self, casting_id: str) -> Dict[str, Any]:
        return analyze_historical_data(casting_id)

    def compare_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        return compare_permeability_scenarios(scenarios)


permeability_analyzer_service = PermeabilityAnalyzerService()
