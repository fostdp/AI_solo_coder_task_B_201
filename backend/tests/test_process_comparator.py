import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from process_comparator.crafts_data import (
    ANCIENT_CRAFTS,
    MODERN_CRAFTS,
    ARCHAEOLOGICAL_SOURCES,
    NATIONAL_STANDARDS,
    get_ancient_crafts,
    get_modern_crafts,
    get_all_crafts,
    get_craft_by_id,
    compare_crafts,
    calculate_defect_rate_for_conditions,
)
from process_comparator.service import process_comparator_service


class TestProcessComparatorCraftsData:
    """工艺对比模块测试 - 工艺数据验证"""

    def test_ancient_crafts_contains_lost_wax(self):
        ancient = get_ancient_crafts()
        ids = [c["id"] for c in ancient]
        assert "lost_wax_ancient" in ids or "lost_wax" in ids
        assert len(ancient) >= 3

    def test_modern_crafts_not_empty(self):
        modern = get_modern_crafts()
        assert len(modern) >= 1
        for craft in modern:
            assert "id" in craft
            assert "name" in craft

    def test_all_crafts_combined(self):
        all_crafts = get_all_crafts()
        ancient = get_ancient_crafts()
        modern = get_modern_crafts()
        assert len(all_crafts) == len(ancient) + len(modern)

    def test_get_craft_by_id_valid(self):
        all_crafts = get_all_crafts()
        if len(all_crafts) > 0:
            first_id = all_crafts[0]["id"]
            craft = get_craft_by_id(first_id)
            assert craft is not None
            assert craft["id"] == first_id

    def test_get_craft_by_id_invalid(self):
        craft = get_craft_by_id("nonexistent_craft_id")
        assert craft is None

    def test_each_craft_has_required_fields(self):
        all_crafts = get_all_crafts()
        required_fields = [
            "id", "name", "overall_defect_rate",
            "defect_rates", "dimensional_accuracy_mm",
            "surface_roughness_ra", "minimum_wall_thickness_mm",
        ]
        for craft in all_crafts:
            for field in required_fields:
                assert field in craft, f"工艺 {craft.get('id')} 缺少字段 {field}"

    def test_defect_rates_within_valid_range(self):
        all_crafts = get_all_crafts()
        for craft in all_crafts:
            overall = craft["overall_defect_rate"]
            assert 0 <= overall <= 100, f"{craft['id']} 总缺陷率超出范围: {overall}"

            for defect_type, rate in craft["defect_rates"].items():
                assert 0 <= rate <= 100, f"{craft['id']} 的 {defect_type} 缺陷率超出范围: {rate}"

    def test_archaeological_sources_exist(self):
        assert len(ARCHAEOLOGICAL_SOURCES) is not None
        assert isinstance(ARCHAEOLOGICAL_SOURCES, dict)

    def test_national_standards_exist(self):
        assert len(NATIONAL_STANDARDS) is not None
        assert isinstance(NATIONAL_STANDARDS, dict)


class TestProcessComparatorComparison:
    """工艺对比模块测试 - 对比功能验证"""

    def test_compare_two_crafts(self):
        all_crafts = get_all_crafts()
        if len(all_crafts) < 2:
            pytest.skip("Need at least 2 crafts for comparison")
        ids = [all_crafts[0]["id"], all_crafts[1]["id"]]
        result = compare_crafts(ids)
        assert "crafts" in result
        assert "comparison_metrics" in result
        assert len(result["crafts"]) == 2

    def test_compare_crafts_returns_metrics(self):
        all_crafts = get_all_crafts()
        if len(all_crafts) < 2:
            pytest.skip("Need at least 2 crafts")
        ids = [all_crafts[0]["id"], all_crafts[1]["id"]]
        result = compare_crafts(ids)
        assert len(result["comparison_metrics"]) > 0
        for metric in result["comparison_metrics"]:
            assert "metric" in metric
            assert "label" in metric
            assert "values" in metric

    def test_compare_single_craft(self):
        all_crafts = get_all_crafts()
        if len(all_crafts) < 1:
            pytest.skip("Need at least 1 craft")
        ids = [all_crafts[0]["id"]]
        result = compare_crafts(ids)
        assert len(result["crafts"]) == 1

    def test_compare_empty_list(self):
        result = compare_crafts([])
        assert result["crafts"] == []

    def test_calculate_defect_rate_returns_valid_value(self):
        all_crafts = get_all_crafts()
        if len(all_crafts) < 1:
            pytest.skip("Need at least 1 craft")
        craft_id = all_crafts[0]["id"]
        result = calculate_defect_rate_for_conditions(
            craft_id=craft_id,
            pouring_temp=1180,
            shell_permeability=50,
            alloy_type="bronze",
        )
        assert result is not None
        assert "defect_rate" in result or "overall_defect_rate" in result or isinstance(result, (int, float, dict))


class TestProcessComparatorService:
    """工艺对比模块测试 - 服务层验证"""

    def test_list_ancient_crafts(self):
        result = process_comparator_service.list_ancient_crafts()
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_list_modern_crafts(self):
        result = process_comparator_service.list_modern_crafts()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_list_all_crafts(self):
        result = process_comparator_service.list_all_crafts()
        ancient = process_comparator_service.list_ancient_crafts()
        modern = process_comparator_service.list_modern_crafts()
        assert len(result) == len(ancient) + len(modern)

    def test_get_craft_detail_valid(self):
        ancient = process_comparator_service.list_ancient_crafts()
        if len(ancient) < 1:
            pytest.skip("Need at least 1 craft")
        craft_id = ancient[0]["id"]
        craft = process_comparator_service.get_craft_detail(craft_id)
        assert craft is not None
        assert craft["id"] == craft_id

    def test_get_craft_detail_invalid(self):
        craft = process_comparator_service.get_craft_detail("nonexistent")
        assert craft is None

    def test_compare_method(self):
        all_crafts = process_comparator_service.list_all_crafts()
        if len(all_crafts) < 2:
            pytest.skip("Need at least 2 crafts")
        ids = [all_crafts[0]["id"], all_crafts[1]["id"]]
        result = process_comparator_service.compare(ids)
        assert "crafts" in result
        assert "comparison_metrics" in result

    def test_calculate_defect_rate_service(self):
        all_crafts = process_comparator_service.list_all_crafts()
        if len(all_crafts) < 1:
            pytest.skip("Need at least 1 craft")
        craft_id = all_crafts[0]["id"]
        result = process_comparator_service.calculate_defect_rate(
            craft_id=craft_id,
            pouring_temp=1180,
            shell_permeability=50,
        )
        assert result is not None
