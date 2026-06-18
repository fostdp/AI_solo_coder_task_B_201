import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from craft_comparison.crafts_data import (
    ANCIENT_CRAFTS,
    MODERN_CRAFTS,
    get_ancient_crafts,
    get_modern_crafts,
    get_all_crafts,
    get_craft_by_id,
    compare_crafts,
    calculate_defect_rate_for_conditions,
)
from craft_comparison.service import craft_service


class TestCraftComparisonDefectRates:
    """工艺对比模块测试 - 缺陷率验证"""

    def test_ancient_crafts_contains_all_three(self):
        """正常用例：古代工艺包含失蜡法、范铸法、分铸法三种"""
        ancient = get_ancient_crafts()
        ids = [c["id"] for c in ancient]
        assert "lost_wax" in ids
        assert "piece_mold" in ids
        assert "sectional_casting" in ids
        assert len(ancient) == 3

    def test_each_craft_has_required_fields(self):
        """正常用例：每个工艺都包含必需的缺陷率字段"""
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
        """边界用例：所有缺陷率均在 [0, 1] 有效范围内"""
        all_crafts = get_all_crafts()
        for craft in all_crafts:
            overall = craft["overall_defect_rate"]
            assert 0 <= overall <= 1, (
                f"{craft['id']} 综合缺陷率 {overall} 超出 [0,1] 范围"
            )
            for defect_type, rate in craft["defect_rates"].items():
                assert 0 <= rate <= 1, (
                    f"{craft['id']} 的 {defect_type} 缺陷率 {rate} 超出 [0,1] 范围"
                )

    def test_lost_wax_defect_rate_lower_than_piece_mold(self):
        """正常用例：失蜡法综合缺陷率应低于范铸法（历史事实）"""
        lost_wax = get_craft_by_id("lost_wax")
        piece_mold = get_craft_by_id("piece_mold")
        assert lost_wax is not None
        assert piece_mold is not None
        assert lost_wax["overall_defect_rate"] < piece_mold["overall_defect_rate"], (
            f"失蜡法缺陷率({lost_wax['overall_defect_rate']}) 应低于范铸法({piece_mold['overall_defect_rate']})"
        )

    def test_compare_crafts_returns_valid_structure(self):
        """正常用例：工艺对比返回完整结构"""
        result = compare_crafts(["lost_wax", "piece_mold"])
        assert "crafts" in result
        assert "comparison_metrics" in result
        assert "defect_radar" in result
        assert "defect_type_comparison" in result
        assert len(result["crafts"]) == 2

    def test_compare_crafts_single_craft_returns_error(self):
        """异常用例：仅提供一个工艺ID应返回错误提示"""
        result = compare_crafts(["lost_wax"])
        assert "error" in result

    def test_compare_crafts_empty_list_returns_error(self):
        """异常用例：空工艺列表应返回错误提示"""
        result = compare_crafts([])
        assert "error" in result

    def test_compare_crafts_invalid_id_handled_gracefully(self):
        """异常用例：无效工艺ID应被过滤不崩溃"""
        result = compare_crafts(["lost_wax", "invalid_craft_xyz"])
        assert len(result.get("crafts", [])) == 1

    def test_calculate_defect_rate_normal_conditions(self):
        """正常用例：标准工艺参数下的缺陷率计算"""
        result = calculate_defect_rate_for_conditions(
            craft_id="lost_wax",
            pouring_temp=1180.0,
            shell_permeability=50.0,
            alloy_type="bronze",
        )
        assert "error" not in result
        assert result["craft_id"] == "lost_wax"
        assert "adjusted_defect_rate" in result
        assert 0 <= result["adjusted_defect_rate"] <= 100

    def test_calculate_defect_rate_low_permeability_increases_gas_defects(self):
        """边界用例：低透气性应显著增加气孔缺陷率"""
        low_perm = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=1180, shell_permeability=15.0
        )
        normal_perm = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=1180, shell_permeability=50.0
        )
        assert low_perm["defect_breakdown"]["gas_porosity"] > normal_perm["defect_breakdown"]["gas_porosity"], (
            "低透气性应导致更高的气孔缺陷率"
        )

    def test_calculate_defect_rate_extreme_temperature_increases_defects(self):
        """边界用例：严重偏离最佳浇铸温度应增加缺陷率"""
        normal = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=1180, shell_permeability=50.0
        )
        too_low = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=800, shell_permeability=50.0
        )
        too_high = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=1500, shell_permeability=50.0
        )
        assert too_low["adjusted_defect_rate"] > normal["adjusted_defect_rate"]
        assert too_high["adjusted_defect_rate"] > normal["adjusted_defect_rate"]

    def test_calculate_defect_rate_invalid_craft_id(self):
        """异常用例：无效工艺ID应返回错误"""
        result = calculate_defect_rate_for_conditions(
            craft_id="nonexistent_craft",
            pouring_temp=1180,
            shell_permeability=50.0,
        )
        assert "error" in result

    def test_calculate_defect_rate_negative_permeability(self):
        """异常用例：负透气性不应崩溃（应按最低值处理）"""
        result = calculate_defect_rate_for_conditions(
            craft_id="lost_wax", pouring_temp=1180, shell_permeability=-10.0
        )
        assert "error" not in result
        assert 0 <= result["adjusted_defect_rate"] <= 100


class TestAncientVsModernSurfaceRoughness:
    """跨时代对比测试 - 表面粗糙度验证"""

    def test_modern_craft_exists(self):
        """正常用例：现代熔模铸造工艺存在"""
        modern = get_modern_crafts()
        ids = [c["id"] for c in modern]
        assert "modern_investment_casting" in ids

    def test_ancient_vs_modern_comparison_structure(self):
        """正常用例：古今对比返回完整结构"""
        result = craft_service.ancient_vs_modern_comparison()
        assert "ancient_crafts" in result
        assert "modern_crafts" in result
        assert "summary" in result
        assert "key_insights" in result

    def test_summary_contains_surface_roughness_metrics(self):
        """正常用例：摘要包含精度相关指标"""
        result = craft_service.ancient_vs_modern_comparison()
        summary = result["summary"]
        assert "avg_ancient_accuracy_mm" in summary
        assert "avg_modern_accuracy_mm" in summary
        assert "accuracy_improvement_factor" in summary

    def test_modern_surface_roughness_better_than_ancient(self):
        """正常用例：现代工艺表面粗糙度显著优于古代"""
        ancient = get_craft_by_id("lost_wax")
        modern = get_craft_by_id("modern_investment_casting")
        assert ancient is not None
        assert modern is not None
        ancient_ra = ancient["surface_roughness_ra"]
        modern_ra = modern["surface_roughness_ra"]
        assert modern_ra < ancient_ra, (
            f"现代表面粗糙度 Ra({modern_ra}) 应优于古代({ancient_ra})"
        )

    def test_modern_roughness_within_precision_range(self):
        """边界用例：现代熔模铸造粗糙度应在精密铸造范围 Ra 0.8-3.2"""
        modern = get_craft_by_id("modern_investment_casting")
        ra = modern["surface_roughness_ra"]
        assert 0.5 <= ra <= 5.0, (
            f"现代熔模铸造粗糙度 Ra({ra}) 应在精密铸造合理范围"
        )

    def test_ancient_roughness_higher_than_modern(self):
        """边界用例：所有古代工艺粗糙度均高于现代"""
        modern_ra = get_craft_by_id("modern_investment_casting")["surface_roughness_ra"]
        for craft in get_ancient_crafts():
            assert craft["surface_roughness_ra"] > modern_ra, (
                f"{craft['name']} 粗糙度应高于现代工艺"
            )

    def test_accuracy_improvement_factor_reasonable(self):
        """边界用例：精度提升倍数应在合理范围（5-20倍）"""
        result = craft_service.ancient_vs_modern_comparison()
        factor = result["summary"]["accuracy_improvement_factor"]
        assert 3 <= factor <= 30, (
            f"精度提升倍数 {factor} 应在合理范围 [3, 30]"
        )

    def test_defect_reduction_percent_positive(self):
        """正常用例：缺陷率降低百分比应为正"""
        result = craft_service.ancient_vs_modern_comparison()
        reduction = result["summary"]["defect_reduction_percent"]
        assert reduction > 0, "现代工艺缺陷率应低于古代"
        assert reduction <= 100, "缺陷率降低不应超过100%"

    def test_modern_minimum_wall_thickness_thinner(self):
        """正常用例：现代工艺可实现更薄的壁厚"""
        ancient_min = min(c["minimum_wall_thickness_mm"] for c in get_ancient_crafts())
        modern_min = get_craft_by_id("modern_investment_casting")["minimum_wall_thickness_mm"]
        assert modern_min < ancient_min, "现代工艺最小壁厚应小于古代"

    def test_key_insights_not_empty(self):
        """正常用例：洞察结论列表不为空"""
        result = craft_service.ancient_vs_modern_comparison()
        assert len(result["key_insights"]) >= 3


def run_tests():
    """测试运行入口"""
    test_classes = [TestCraftComparisonDefectRates, TestAncientVsModernSurfaceRoughness]
    total_passed = 0
    total_failed = 0
    failures = []

    for test_class in test_classes:
        instance = test_class()
        print(f"\n{'='*60}")
        print(f"  运行测试: {test_class.__name__}")
        print(f"{'='*60}")
        test_methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in sorted(test_methods):
            method = getattr(instance, method_name)
            try:
                method()
                print(f"  ✅ {method_name}")
                total_passed += 1
            except AssertionError as e:
                print(f"  ❌ {method_name}: {e}")
                total_failed += 1
                failures.append(f"{test_class.__name__}.{method_name}: {e}")
            except Exception as e:
                print(f"  💥 {method_name}: 异常 - {type(e).__name__}: {e}")
                total_failed += 1
                failures.append(f"{test_class.__name__}.{method_name}: {type(e).__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"  测试结果: 通过 {total_passed}, 失败 {total_failed}")
    print(f"{'='*60}")
    if failures:
        print("\n失败详情:")
        for f in failures:
            print(f"  - {f}")
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
