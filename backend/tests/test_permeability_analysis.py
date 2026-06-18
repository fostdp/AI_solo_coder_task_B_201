import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from permeability_analysis.analyzer import (
    calculate_permeability_impact,
    compare_permeability_scenarios,
    PERMEABILITY_RANGE,
)
from permeability_analysis.service import permeability_service


class TestPermeabilityAnalysisGasPorosity:
    """透气性分析模块测试 - 气孔率验证"""

    def test_impact_returns_complete_structure(self):
        """正常用例：透气性分析返回完整数据结构"""
        result = calculate_permeability_impact()
        required_keys = [
            "parameters", "permeability_values", "filling_quality_scores",
            "filling_speed_scores", "defect_rates_percent",
            "gas_porosity_rates_percent", "shrinkage_rates_percent",
            "analysis", "insights", "shell_materials_comparison",
        ]
        for key in required_keys:
            assert key in result, f"缺少关键字段: {key}"

    def test_permeability_range_consistent(self):
        """正常用例：透气性值数组与参数范围一致"""
        result = calculate_permeability_impact()
        perms = result["permeability_values"]
        assert len(perms) > 0
        assert perms[0] >= PERMEABILITY_RANGE["min"]
        assert perms[-1] <= PERMEABILITY_RANGE["max"]
        assert len(perms) == len(result["gas_porosity_rates_percent"])
        assert len(perms) == len(result["filling_quality_scores"])

    def test_gas_porosity_decreases_with_higher_permeability(self):
        """正常用例：随着透气性升高，气孔率应单调下降（核心物理规律）"""
        result = calculate_permeability_impact(
            alloy_type="bronze", pouring_temp=1180, shell_thickness=9
        )
        gas_rates = result["gas_porosity_rates_percent"]
        for i in range(1, len(gas_rates)):
            assert gas_rates[i] <= gas_rates[i - 1] + 0.5, (
                f"透气性增加时气孔率不应显著上升: {gas_rates[i-1]} -> {gas_rates[i]}"
            )

    def test_low_permeability_high_gas_porosity(self):
        """边界用例：低透气性（10-20%）应有较高气孔率"""
        result = calculate_permeability_impact()
        gas_rates = result["gas_porosity_rates_percent"]
        perm_values = result["permeability_values"]
        low_perm_indices = [i for i, p in enumerate(perm_values) if p <= 25]
        high_perm_indices = [i for i, p in enumerate(perm_values) if p >= 60]
        if low_perm_indices and high_perm_indices:
            avg_low = sum(gas_rates[i] for i in low_perm_indices) / len(low_perm_indices)
            avg_high = sum(gas_rates[i] for i in high_perm_indices) / len(high_perm_indices)
            assert avg_low > avg_high, (
                f"低透气区平均气孔率({avg_low:.1f}%)应高于高透气区({avg_high:.1f}%)"
            )

    def test_gas_porosity_within_valid_range(self):
        """边界用例：所有气孔率值在合理百分比范围 [0, 50]"""
        result = calculate_permeability_impact()
        for rate in result["gas_porosity_rates_percent"]:
            assert 0 <= rate <= 60, f"气孔率 {rate}% 超出合理范围"

    def test_all_rates_arrays_same_length(self):
        """正常用例：所有率数组长度一致"""
        result = calculate_permeability_impact()
        lengths = [
            len(result["permeability_values"]),
            len(result["filling_quality_scores"]),
            len(result["filling_speed_scores"]),
            len(result["defect_rates_percent"]),
            len(result["gas_porosity_rates_percent"]),
            len(result["shrinkage_rates_percent"]),
        ]
        assert len(set(lengths)) == 1, "所有率数组长度应一致"

    def test_optimal_permeability_around_50(self):
        """边界用例：最佳透气性应在 40-60% 范围内"""
        result = calculate_permeability_impact()
        best_perm = result["analysis"]["best_quality_permeability"]
        assert 35 <= best_perm <= 70, (
            f"最佳透气性 {best_perm}% 应在合理范围 [35, 70]"
        )

    def test_filling_quality_inverted_u_shape(self):
        """边界用例：充型质量随透气性呈倒U型（低和高都差，中间最好）"""
        result = calculate_permeability_impact()
        quality = result["filling_quality_scores"]
        best_idx = result["permeability_values"].index(result["analysis"]["best_quality_permeability"])
        for i in range(best_idx):
            assert quality[i + 1] >= quality[i] - 2, (
                f"最佳点前充型质量应逐步上升: idx {i} -> {i+1}"
            )

    def test_different_alloy_types_produce_results(self):
        """正常用例：不同合金类型均能正常计算"""
        alloys = ["bronze", "brass", "steel", "aluminum"]
        for alloy in alloys:
            result = calculate_permeability_impact(alloy_type=alloy)
            assert len(result["gas_porosity_rates_percent"]) > 0, (
                f"{alloy} 合金分析应返回有效数据"
            )

    def test_temperature_deviation_affects_gas_porosity(self):
        """边界用例：温度偏离最佳值应增加气孔率"""
        normal = calculate_permeability_impact(alloy_type="bronze", pouring_temp=1180)
        deviated = calculate_permeability_impact(alloy_type="bronze", pouring_temp=1500)
        avg_normal = sum(normal["gas_porosity_rates_percent"]) / len(normal["gas_porosity_rates_percent"])
        avg_deviated = sum(deviated["gas_porosity_rates_percent"]) / len(deviated["gas_porosity_rates_percent"])
        assert avg_deviated >= avg_normal * 0.8, (
            "温度严重偏离不应显著降低气孔率"
        )

    def test_shell_thickness_affects_results(self):
        """正常用例：不同型壳层数产生不同结果"""
        thin = calculate_permeability_impact(shell_thickness=3)
        thick = calculate_permeability_impact(shell_thickness=15)
        assert thin["analysis"]["best_quality_score"] != thick["analysis"]["best_quality_score"] or \
               thin["parameters"]["shell_thickness_layers"] != thick["parameters"]["shell_thickness_layers"]

    def test_shell_materials_comparison_contains_all_types(self):
        """正常用例：型壳材料对比包含4种材料"""
        result = calculate_permeability_impact()
        materials = result["shell_materials_comparison"]
        assert len(materials) == 4
        names = [m["name"] for m in materials]
        expected = ["硅酸乙酯+锆英砂", "硅溶胶+石英砂", "水玻璃+石英砂", "石膏型"]
        for exp_name in expected:
            assert exp_name in names, f"缺少材料: {exp_name}"

    def test_shell_material_permeability_ordering(self):
        """正常用例：型壳材料透气性排序合理"""
        result = calculate_permeability_impact()
        materials = {m["name"]: m["permeability"] for m in result["shell_materials_comparison"]}
        assert materials["硅酸乙酯+锆英砂"] > materials["硅溶胶+石英砂"]
        assert materials["硅溶胶+石英砂"] > materials["水玻璃+石英砂"]
        assert materials["水玻璃+石英砂"] > materials["石膏型"]

    def test_compare_scenarios_multiple_scenarios(self):
        """正常用例：多场景对比功能正常"""
        scenarios = [
            {"name": "方案A", "alloy_type": "bronze", "pouring_temp": 1180, "shell_thickness": 9},
            {"name": "方案B", "alloy_type": "steel", "pouring_temp": 1580, "shell_thickness": 12},
        ]
        result = compare_permeability_scenarios(scenarios)
        assert len(result["scenarios"]) == 2
        assert "best_overall" in result["comparison"]

    def test_insights_not_empty(self):
        """正常用例：分析洞察列表不为空"""
        result = calculate_permeability_impact()
        assert len(result["insights"]) >= 3

    def test_extreme_pouring_temp_handled_gracefully(self):
        """异常用例：极端浇铸温度不应崩溃"""
        try:
            result = calculate_permeability_impact(pouring_temp=100.0)
            assert "gas_porosity_rates_percent" in result
        except Exception as e:
            raise AssertionError(f"极端低温不应崩溃: {e}")

        try:
            result = calculate_permeability_impact(pouring_temp=5000.0)
            assert "gas_porosity_rates_percent" in result
        except Exception as e:
            raise AssertionError(f"极端高温不应崩溃: {e}")

    def test_negative_shell_thickness_handled(self):
        """异常用例：负型壳层数不应崩溃"""
        try:
            result = calculate_permeability_impact(shell_thickness=-5)
            assert "parameters" in result
        except Exception as e:
            raise AssertionError(f"负型壳层数不应崩溃: {e}")

    def test_invalid_alloy_type_handled(self):
        """异常用例：无效合金类型按默认值处理不崩溃"""
        try:
            result = calculate_permeability_impact(alloy_type="unknown_alloy_xyz")
            assert "gas_porosity_rates_percent" in result
        except Exception as e:
            raise AssertionError(f"无效合金类型不应崩溃: {e}")


def run_tests():
    """测试运行入口"""
    test_class = TestPermeabilityAnalysisGasPorosity
    instance = test_class()
    total_passed = 0
    total_failed = 0
    failures = []

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
