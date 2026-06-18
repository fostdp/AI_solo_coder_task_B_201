import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from era_comparator.era_data import (
    ERA_INFO,
    get_era_info,
    get_all_eras,
    ancient_vs_modern_comparison,
)
from era_comparator.service import era_comparator_service


class TestEraComparatorData:
    """跨时代对比模块测试 - 数据验证"""

    def test_era_info_contains_ancient_and_modern(self):
        assert "ancient" in ERA_INFO
        assert "modern" in ERA_INFO
        assert len(ERA_INFO) >= 2

    def test_each_era_has_required_fields(self):
        required_fields = ["id", "name", "period", "key_technologies"]
        for era_id, era in ERA_INFO.items():
            for field in required_fields:
                assert field in era, f"时代 {era_id} 缺少字段 {field}"

    def test_get_era_info_valid(self):
        ancient = get_era_info("ancient")
        assert ancient is not None
        assert ancient["id"] == "ancient"

        modern = get_era_info("modern")
        assert modern is not None
        assert modern["id"] == "modern"

    def test_get_era_info_invalid(self):
        era = get_era_info("nonexistent_era")
        assert era is None

    def test_get_all_eras_returns_list(self):
        eras = get_all_eras()
        assert isinstance(eras, list)
        assert len(eras) >= 2

    def test_ancient_vs_modern_comparison_returns_summary(self):
        result = ancient_vs_modern_comparison()
        assert "summary" in result
        assert "ancient_crafts" in result
        assert "modern_crafts" in result

    def test_comparison_summary_has_key_metrics(self):
        result = ancient_vs_modern_comparison()
        summary = result["summary"]
        assert "avg_ancient_defect_rate" in summary
        assert "avg_modern_defect_rate" in summary
        assert "defect_reduction_percent" in summary
        assert "avg_ancient_accuracy_mm" in summary
        assert "avg_modern_accuracy_mm" in summary
        assert "accuracy_improvement_factor" in summary

    def test_modern_defect_rate_lower_than_ancient(self):
        result = ancient_vs_modern_comparison()
        summary = result["summary"]
        assert summary["avg_modern_defect_rate"] < summary["avg_ancient_defect_rate"]

    def test_modern_accuracy_better_than_ancient(self):
        result = ancient_vs_modern_comparison()
        summary = result["summary"]
        assert summary["avg_modern_accuracy_mm"] < summary["avg_ancient_accuracy_mm"]

    def test_comparison_has_key_insights(self):
        result = ancient_vs_modern_comparison()
        assert "key_insights" in result
        assert isinstance(result["key_insights"], list)
        assert len(result["key_insights"]) >= 3

    def test_comparison_has_detailed_comparison(self):
        result = ancient_vs_modern_comparison()
        assert "detailed_comparison" in result

    def test_comparison_has_technological_evolution(self):
        result = ancient_vs_modern_comparison()
        assert "technological_evolution" in result
        assert isinstance(result["technological_evolution"], list)
        assert len(result["technological_evolution"]) >= 2

    def test_ancient_crafts_not_empty(self):
        result = ancient_vs_modern_comparison()
        assert len(result["ancient_crafts"]) >= 2

    def test_modern_crafts_not_empty(self):
        result = ancient_vs_modern_comparison()
        assert len(result["modern_crafts"]) >= 1

    def test_defect_reduction_is_positive(self):
        result = ancient_vs_modern_comparison()
        summary = result["summary"]
        assert summary["defect_reduction_percent"] > 0

    def test_accuracy_improvement_factor_gt_one(self):
        result = ancient_vs_modern_comparison()
        summary = result["summary"]
        assert summary["accuracy_improvement_factor"] > 1.0


class TestEraComparatorService:
    """跨时代对比模块测试 - 服务层验证"""

    def test_list_eras(self):
        result = era_comparator_service.list_eras()
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_era_valid(self):
        era = era_comparator_service.get_era("ancient")
        assert era is not None
        assert era["id"] == "ancient"

    def test_get_era_invalid(self):
        era = era_comparator_service.get_era("nonexistent")
        assert era is None

    def test_compare_ancient_vs_modern(self):
        result = era_comparator_service.compare_ancient_vs_modern()
        assert "summary" in result
        assert "ancient_crafts" in result
        assert "modern_crafts" in result
        assert "key_insights" in result
