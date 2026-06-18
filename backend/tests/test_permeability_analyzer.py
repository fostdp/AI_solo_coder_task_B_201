import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from permeability_analyzer.analyzer import (
    PERMEABILITY_MEASUREMENT_REFERENCES,
    PERMEABILITY_RANGE,
    SHELL_MATERIAL_PERMEABILITY,
    GAS_POROSITY_MODEL_COEFFICIENTS,
    calculate_permeability_impact,
    compare_permeability_scenarios,
)
from permeability_analyzer.service import permeability_analyzer_service


class TestPermeabilityAnalyzerData:
    """透气性分析模块测试 - 数据验证"""

    def test_permeability_range_valid(self):
        assert PERMEABILITY_RANGE["min"] < PERMEABILITY_RANGE["max"]
        assert PERMEABILITY_RANGE["step"] > 0
        assert PERMEABILITY_RANGE["min"] >= 0

    def test_shell_materials_exist(self):
        assert len(SHELL_MATERIAL_PERMEABILITY) >= 2
        for key, material in SHELL_MATERIAL_PERMEABILITY.items():
            assert "name" in material
            assert "permeability" in material
            assert material["permeability"] > 0

    def test_gas_porosity_coefficients_exist(self):
        assert len(GAS_POROSITY_MODEL_COEFFICIENTS) >= 3
        for alloy, coeff in GAS_POROSITY_MODEL_COEFFICIENTS.items():
            assert "A" in coeff
            assert "k" in coeff
            assert "B" in coeff
            assert "R_squared" in coeff
            assert coeff["R_squared"] > 0.8

    def test_measurement_references_exist(self):
        assert "measurements" in PERMEABILITY_MEASUREMENT_REFERENCES
        assert len(PERMEABILITY_MEASUREMENT_REFERENCES["measurements"]) >= 2
        assert "uncertainty_statement" in PERMEABILITY_MEASUREMENT_REFERENCES


class TestPermeabilityAnalyzerCalculation:
    """透气性分析模块测试 - 计算功能验证"""

    def test_calculate_permeability_impact_returns_result(self):
        result = calculate_permeability_impact()
        assert result is not None
        assert "parameters" in result
        assert "permeability_values" in result
        assert "filling_quality_scores" in result
        assert "defect_rates_percent" in result

    def test_permeability_values_have_correct_length(self):
        result = calculate_permeability_impact()
        n_values = len(result["permeability_values"])
        assert len(result["filling_quality_scores"]) == n_values
        assert len(result["defect_rates_percent"]) == n_values
        assert len(result["gas_porosity_rates_percent"]) == n_values
        assert len(result["shrinkage_rates_percent"]) == n_values

    def test_filling_quality_within_range(self):
        result = calculate_permeability_impact()
        for score in result["filling_quality_scores"]:
            assert 0 <= score <= 100, f"充型质量评分超出范围: {score}"

    def test_defect_rates_positive(self):
        result = calculate_permeability_impact()
        for rate in result["defect_rates_percent"]:
            assert rate >= 0, f"缺陷率不能为负: {rate}"

    def test_analysis_contains_best_and_worst(self):
        result = calculate_permeability_impact()
        assert "analysis" in result
        analysis = result["analysis"]
        assert "best_quality_permeability" in analysis
        assert "best_quality_score" in analysis
        assert "lowest_defect_permeability" in analysis
        assert "lowest_defect_rate" in analysis
        assert "worst_quality_permeability" in analysis
        assert "worst_quality_score" in analysis

    def test_best_quality_higher_than_worst(self):
        result = calculate_permeability_impact()
        analysis = result["analysis"]
        assert analysis["best_quality_score"] >= analysis["worst_quality_score"]

    def test_insights_not_empty(self):
        result = calculate_permeability_impact()
        assert "insights" in result
        assert len(result["insights"]) >= 3

    def test_shell_materials_comparison_exists(self):
        result = calculate_permeability_impact()
        assert "shell_materials_comparison" in result
        assert len(result["shell_materials_comparison"]) >= 3

    def test_different_alloy_types(self):
        bronze_result = calculate_permeability_impact(alloy_type="bronze")
        steel_result = calculate_permeability_impact(alloy_type="stainless_steel")
        assert bronze_result["parameters"]["alloy_type"] == "bronze"
        assert steel_result["parameters"]["alloy_type"] == "stainless_steel"

    def test_parameters_reflected_in_result(self):
        result = calculate_permeability_impact(
            alloy_type="bronze",
            pouring_temp=1200,
            shell_thickness=8,
        )
        assert result["parameters"]["alloy_type"] == "bronze"
        assert result["parameters"]["pouring_temp"] == 1200
        assert result["parameters"]["shell_thickness_layers"] == 8

    def test_compare_scenarios_multiple(self):
        scenarios = [
            {"name": "场景1", "alloy_type": "bronze", "pouring_temp": 1150, "shell_thickness": 9},
            {"name": "场景2", "alloy_type": "bronze", "pouring_temp": 1200, "shell_thickness": 9},
        ]
        result = compare_permeability_scenarios(scenarios)
        assert "scenarios" in result
        assert len(result["scenarios"]) == 2
        assert "comparison" in result

    def test_compare_scenarios_best_overall_exists(self):
        scenarios = [
            {"name": "场景1", "alloy_type": "bronze", "pouring_temp": 1150, "shell_thickness": 9},
            {"name": "场景2", "alloy_type": "bronze", "pouring_temp": 1200, "shell_thickness": 9},
        ]
        result = compare_permeability_scenarios(scenarios)
        assert "best_overall" in result["comparison"]
        assert result["comparison"]["best_overall"] in ["场景1", "场景2"]


class TestPermeabilityAnalyzerService:
    """透气性分析模块测试 - 服务层验证"""

    def test_analyze_impact(self):
        result = permeability_analyzer_service.analyze_impact(
            alloy_type="bronze",
            pouring_temp=1180,
            shell_thickness=9,
        )
        assert "parameters" in result
        assert "permeability_values" in result
        assert "filling_quality_scores" in result

    def test_compare_scenarios_service(self):
        scenarios = [
            {"name": "场景A", "alloy_type": "bronze", "pouring_temp": 1100, "shell_thickness": 7},
            {"name": "场景B", "alloy_type": "stainless_steel", "pouring_temp": 1580, "shell_thickness": 10},
        ]
        result = permeability_analyzer_service.compare_scenarios(scenarios)
        assert "scenarios" in result
        assert len(result["scenarios"]) == 2
