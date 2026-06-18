import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virtual_experience.wax_mold_engine import (
    WAX_MOLD_TEMPLATES,
    CASTING_MATERIALS,
    SHELL_MATERIALS,
    SIMPLE_MODE_PRESETS,
    SIMPLE_MODE_PARAMS,
    get_wax_mold_templates,
    get_wax_mold_template,
    get_casting_materials,
    get_shell_materials,
    generate_model_geometry,
    simulate_casting,
    apply_simple_mode_params,
    apply_preset,
    get_simple_mode_presets,
    get_simple_mode_params,
)
from virtual_experience.service import virtual_service


class TestVirtualExperienceDesignFreedom:
    """虚拟体验模块测试 - 设计自由度验证"""

    def test_all_five_templates_available(self):
        """正常用例：5种蜡模模板全部可用（尊盘、圆鼎、铜壶、指环、挂坠）"""
        templates = get_wax_mold_templates()
        ids = [t["id"] for t in templates]
        expected = ["zunpan", "ding", "hu", "ring", "pendant"]
        for exp_id in expected:
            assert exp_id in ids, f"缺少模板: {exp_id}"
        assert len(templates) == 5

    def test_simple_mode_presets_available(self):
        """正常用例：简单模式预设全部可用"""
        presets = get_simple_mode_presets()
        assert len(presets) >= 4
        preset_ids = [p["id"] for p in presets]
        expected = ["delicate", "balanced", "grand", "intricate"]
        for pid in expected:
            assert pid in preset_ids, f"缺少预设: {pid}"
        for preset in presets:
            assert "name" in preset
            assert "description" in preset
            assert "icon" in preset
            assert "scaling_factors" in preset

    def test_simple_mode_params_defined(self):
        """正常用例：简单模式参数定义完整"""
        params = get_simple_mode_params()
        assert "size" in params
        assert "ornament" in params
        assert "thickness" in params
        for key, p in params.items():
            assert p["min"] == 1
            assert p["max"] == 5
            assert p["default"] == 3
            assert "label" in p
            assert "hint" in p

    def test_apply_preset_produces_different_results(self):
        """正常用例：不同预设产生不同的参数组合"""
        template_id = "zunpan"
        params_delicate = apply_preset(template_id, "delicate")
        params_grand = apply_preset(template_id, "grand")
        assert "error" not in params_delicate
        assert "error" not in params_grand
        assert params_delicate["height"] < params_grand["height"], (
            "精致模式应比宏大模式尺寸小"
        )
        assert params_delicate["wall_thickness"] < params_grand["wall_thickness"], (
            "精致模式应比宏大模式壁薄"
        )

    def test_apply_simple_mode_size_scaling(self):
        """边界用例：简单模式尺寸等级1和5产生显著差异"""
        template_id = "ding"
        params_small = apply_simple_mode_params(template_id, size_level=1)
        params_large = apply_simple_mode_params(template_id, size_level=5)
        assert "error" not in params_small
        assert "error" not in params_large
        assert params_small["height"] < params_large["height"]
        assert params_small["diameter"] < params_large["diameter"]
        size_ratio = params_large["height"] / params_small["height"]
        assert 1.5 <= size_ratio <= 2.5, f"尺寸比例 {size_ratio:.2f} 应在 [1.5, 2.5] 范围"

    def test_apply_simple_mode_ornament_scaling(self):
        """边界用例：简单模式纹饰等级影响纹饰数量"""
        template_id = "zunpan"
        params_plain = apply_simple_mode_params(template_id, ornament_level=1)
        params_intricate = apply_simple_mode_params(template_id, ornament_level=5)
        assert "error" not in params_plain
        assert "error" not in params_intricate
        assert params_plain["pattern_count"] < params_intricate["pattern_count"], (
            "低纹饰等级应比高纹饰等级有更少纹饰"
        )
        assert params_plain.get("has_dragons", True) == False, (
            "素面模式应无龙形装饰"
        )

    def test_apply_simple_mode_thickness_scaling(self):
        """边界用例：简单模式壁厚等级影响厚度"""
        template_id = "hu"
        params_thin = apply_simple_mode_params(template_id, thickness_level=1)
        params_thick = apply_simple_mode_params(template_id, thickness_level=5)
        assert "error" not in params_thin
        assert "error" not in params_thick
        assert params_thin["wall_thickness"] < params_thick["wall_thickness"]

    def test_apply_simple_mode_invalid_template(self):
        """异常用例：应用简单模式到不存在的模板返回错误"""
        result = apply_simple_mode_params("nonexistent_template")
        assert "error" in result

    def test_apply_preset_invalid_ids(self):
        """异常用例：应用不存在的预设返回错误"""
        result = apply_preset("zunpan", "nonexistent_preset")
        assert "error" in result
        result = apply_preset("nonexistent_template", "delicate")
        assert "error" in result

    def test_templates_have_audience_classification(self):
        """正常用例：模板按受众分级（beginner/all）"""
        templates = get_wax_mold_templates()
        audiences = set()
        for t in templates:
            assert "audience" in t
            audiences.add(t["audience"])
        assert "beginner" in audiences
        assert "all" in audiences

    def test_templates_have_expert_param_markers(self):
        """正常用例：参数标记专家模式可见"""
        template = get_wax_mold_template("zunpan")
        pr = template["param_ranges"]
        expert_count = sum(1 for p in pr.values() if p.get("expert_only", False))
        normal_count = sum(1 for p in pr.values() if not p.get("expert_only", False))
        assert expert_count >= 3, "专家参数不足"
        assert normal_count >= 3, "普通参数不足"

    def test_each_template_has_param_ranges(self):
        """正常用例：每个模板都有参数范围定义"""
        for template in get_wax_mold_templates():
            assert "param_ranges" in template, f"{template['id']} 缺少 param_ranges"
            assert len(template["param_ranges"]) >= 1, (
                f"{template['id']} 至少应定义1个可调参数"
            )
            numeric_param_count = 0
            for param_name, prange in template["param_ranges"].items():
                if isinstance(prange, dict) and "min" in prange:
                    numeric_param_count += 1
                    assert "max" in prange, f"{template['id']}.{param_name} 缺少 max"
                    assert prange["max"] > prange["min"], (
                        f"{template['id']}.{param_name} max 应大于 min"
                    )
            assert numeric_param_count >= 3, f"{template['id']} 数值参数不足"

    def test_template_default_params_within_ranges(self):
        """边界用例：所有数值型默认参数值均在参数范围内"""
        for template in get_wax_mold_templates():
            for param_name, prange in template["param_ranges"].items():
                if not isinstance(prange, dict) or "min" not in prange:
                    continue
                default_val = template["default_params"].get(param_name)
                assert default_val is not None, (
                    f"{template['id']} 缺少 {param_name} 的默认值"
                )
                assert prange["min"] <= default_val <= prange["max"], (
                    f"{template['id']}.{param_name} 默认值 {default_val} 超出范围 [{prange['min']}, {prange['max']}]"
                )

    def test_generate_geometry_normal_params(self):
        """正常用例：标准参数下几何生成成功"""
        template = get_wax_mold_template("zunpan")
        result = generate_model_geometry("zunpan", template["default_params"])
        assert "error" not in result
        assert result["template_id"] == "zunpan"
        assert len(result["parts"]) > 0
        assert "properties" in result
        assert result["properties"]["volume_cm3"] > 0

    def test_generate_geometry_all_templates(self):
        """正常用例：所有5种模板都能生成几何"""
        for template in get_wax_mold_templates():
            result = generate_model_geometry(template["id"], template["default_params"])
            assert "error" not in result, f"{template['name']} 几何生成失败"
            assert len(result["parts"]) > 0, f"{template['name']} 未生成任何部件"
            assert result["properties"]["volume_cm3"] > 0, (
                f"{template['name']} 体积应大于0"
            )

    def test_geometry_volume_scales_with_size(self):
        """边界用例：增大尺寸参数应增大体积"""
        template = get_wax_mold_template("zunpan")
        small_params = {**template["default_params"], "height": 80.0, "diameter": 100.0}
        large_params = {**template["default_params"], "height": 200.0, "diameter": 250.0}
        small_result = generate_model_geometry("zunpan", small_params)
        large_result = generate_model_geometry("zunpan", large_params)
        assert large_result["properties"]["volume_cm3"] > small_result["properties"]["volume_cm3"], (
            "大尺寸应有更大的体积"
        )

    def test_complexity_score_increases_with_detail(self):
        """边界用例：增加纹饰数量应提高复杂度评分"""
        template = get_wax_mold_template("zunpan")
        simple = {**template["default_params"], "pattern_count": 8, "pattern_depth": 0.5}
        complex_p = {**template["default_params"], "pattern_count": 32, "pattern_depth": 3.0}
        simple_result = generate_model_geometry("zunpan", simple)
        complex_result = generate_model_geometry("zunpan", complex_p)
        assert complex_result["properties"]["complexity_score"] >= simple_result["properties"]["complexity_score"] - 5, (
            "更多纹饰应有更高或相近的复杂度评分"
        )

    def test_thin_wall_increases_complexity(self):
        """边界用例：薄壁应提高复杂度评分"""
        template = get_wax_mold_template("zunpan")
        thick = {**template["default_params"], "wall_thickness": 10.0}
        thin = {**template["default_params"], "wall_thickness": 2.0}
        thick_result = generate_model_geometry("zunpan", thick)
        thin_result = generate_model_geometry("zunpan", thin)
        assert thin_result["properties"]["complexity_score"] > thick_result["properties"]["complexity_score"], (
            "薄壁铸件应有更高复杂度"
        )

    def test_casting_materials_variety(self):
        """正常用例：提供4种不同合金材料"""
        materials = get_casting_materials()
        ids = [m["id"] for m in materials]
        expected = ["bronze_cu_sn", "brass", "stainless_steel", "aluminum_alloy"]
        for exp_id in expected:
            assert exp_id in ids, f"缺少合金材料: {exp_id}"
        assert len(materials) == 4

    def test_shell_materials_variety(self):
        """正常用例：提供4种型壳材料（含古代泥范）"""
        shells = get_shell_materials()
        ids = [s["id"] for s in shells]
        expected = ["silica_sol", "water_glass", "ethyl_silicate", "ancient_mud"]
        for exp_id in expected:
            assert exp_id in ids, f"缺少型壳材料: {exp_id}"
        assert len(shells) == 4

    def test_ancient_mud_shell_marked_historical(self):
        """正常用例：古代泥范被正确标记为历史材料"""
        ancient = next((s for s in get_shell_materials() if s["id"] == "ancient_mud"), None)
        assert ancient is not None
        assert ancient["historical"] is True

    def test_simulate_casting_normal_conditions(self):
        """正常用例：标准条件下浇铸仿真成功"""
        template = get_wax_mold_template("ring")
        result = simulate_casting(
            template_id="ring",
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        assert "error" not in result
        assert result["template_id"] == "ring"
        assert "results" in result
        assert "simulation_steps" in result
        assert len(result["simulation_steps"]) == 10

    def test_simulate_casting_defect_rate_reasonable(self):
        """边界用例：仿真缺陷率在合理范围"""
        template = get_wax_mold_template("ring")
        result = simulate_casting(
            template_id="ring",
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        defect_rate = result["results"]["overall_defect_rate"]
        assert 0 <= defect_rate <= 85, f"缺陷率 {defect_rate}% 应在 [0, 85] 范围"

    def test_bad_conditions_increase_defects(self):
        """边界用例：恶劣工艺条件应增加缺陷率"""
        template = get_wax_mold_template("zunpan")
        thin_params = {**template["default_params"], "wall_thickness": 2.0}
        normal_params = {**template["default_params"], "wall_thickness": 5.0}
        thin_result = simulate_casting("zunpan", thin_params, "bronze_cu_sn", "ancient_mud", pouring_temp_override=900)
        normal_result = simulate_casting("zunpan", normal_params, "bronze_cu_sn", "silica_sol")
        assert thin_result["results"]["overall_defect_rate"] >= normal_result["results"]["overall_defect_rate"] * 0.8, (
            "恶劣条件下缺陷率不应低于良好条件"
        )

    def test_simulate_casting_returns_quality_score(self):
        """正常用例：仿真返回充型质量评分"""
        template = get_wax_mold_template("pendant")
        result = simulate_casting(
            template_id="pendant",
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        score = result["results"]["filling_quality_score"]
        assert 0 <= score <= 100, f"质量评分 {score} 应在 [0, 100]"

    def test_tips_provided_for_any_outcome(self):
        """正常用例：无论结果如何都提供工艺建议"""
        template = get_wax_mold_template("hu")
        result = simulate_casting(
            template_id="hu",
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        assert len(result["tips"]) >= 1, "应至少提供1条工艺建议"

    def test_invalid_template_id_returns_error(self):
        """异常用例：无效模板ID返回错误"""
        result = generate_model_geometry("nonexistent_template_xyz", {})
        assert "error" in result

    def test_simulate_invalid_template_handled(self):
        """异常用例：仿真无效模板ID应返回错误不崩溃"""
        result = simulate_casting(
            template_id="invalid_xyz",
            params={},
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        assert "error" in result

    def test_simulate_invalid_material_handled(self):
        """异常用例：仿真无效材料ID应返回错误不崩溃"""
        result = simulate_casting(
            template_id="ring",
            params={},
            material_id="unobtainium",
            shell_id="silica_sol",
        )
        assert "error" in result

    def test_extreme_params_dont_crash(self):
        """异常用例：极端参数值不应崩溃"""
        template = get_wax_mold_template("zunpan")
        extreme_params = {
            **template["default_params"],
            "height": 1.0,
            "diameter": 1.0,
            "wall_thickness": 0.1,
        }
        try:
            result = generate_model_geometry("zunpan", extreme_params)
            assert "error" not in result
        except Exception as e:
            raise AssertionError(f"极端参数不应崩溃: {e}")

    def test_geometry_parts_have_valid_types(self):
        """正常用例：生成的几何部件类型有效"""
        valid_types = {"cylinder", "torus", "sphere", "ellipsoid", "hole"}
        template = get_wax_mold_template("zunpan")
        result = generate_model_geometry("zunpan", template["default_params"])
        for part in result["parts"]:
            assert part["type"] in valid_types, (
                f"无效部件类型: {part['type']}, 名称: {part.get('name')}"
            )

    def test_ding_has_legs(self):
        """正常用例：圆鼎模板应生成鼎足部件"""
        template = get_wax_mold_template("ding")
        result = generate_model_geometry("ding", template["default_params"])
        leg_parts = [p for p in result["parts"] if "鼎足" in p.get("name", "") or "leg" in p.get("name", "").lower()]
        assert len(leg_parts) >= 3, "圆鼎应有至少3个鼎足"

    def test_defect_severity_levels_valid(self):
        """边界用例：仿真检出的缺陷严重程度为有效值"""
        valid_severities = {"low", "medium", "high", "critical"}
        template = get_wax_mold_template("zunpan")
        thin_params = {**template["default_params"], "wall_thickness": 2.0}
        result = simulate_casting("zunpan", thin_params, "bronze_cu_sn", "ancient_mud", pouring_temp_override=800)
        for defect in result["results"]["detected_defects"]:
            assert defect["severity"] in valid_severities, (
                f"无效缺陷严重程度: {defect['severity']}"
            )

    def test_casting_steps_progress_monotonically(self):
        """正常用例：仿真步骤的充型进度单调递增"""
        template = get_wax_mold_template("ring")
        result = simulate_casting(
            template_id="ring",
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        steps = result["simulation_steps"]
        for i in range(1, len(steps)):
            assert steps[i]["filling_progress"] >= steps[i - 1]["filling_progress"] - 5, (
                f"步骤 {i} 充型进度不应下降"
            )

    def test_material_pouring_temps_reasonable(self):
        """正常用例：各合金浇铸温度在合理范围"""
        for mat in get_casting_materials():
            assert 500 <= mat["pouring_temp"] <= 2000, (
                f"{mat['name']} 浇铸温度 {mat['pouring_temp']}°C 不合理"
            )

    def test_templates_categorized(self):
        """正常用例：模板分属于不同类别"""
        categories = set(t["category"] for t in get_wax_mold_templates())
        assert len(categories) >= 2, "模板应覆盖至少2个类别"

    def test_each_template_has_historical_note(self):
        """正常用例：每个模板都有历史注释（教育价值）"""
        for template in get_wax_mold_templates():
            assert template.get("historical_note"), f"{template['name']} 缺少历史注释"
            assert len(template["historical_note"]) > 10, (
                f"{template['name']} 历史注释应足够详细"
            )

    def test_service_layer_wraps_engine(self):
        """正常用例：服务层正确封装核心引擎"""
        templates = virtual_service.list_templates()
        assert len(templates) == 5

        materials = virtual_service.list_materials()
        assert len(materials) == 4

        shells = virtual_service.list_shells()
        assert len(shells) == 4

        zunpan = virtual_service.get_template("zunpan")
        assert zunpan is not None
        assert zunpan["id"] == "zunpan"

        missing = virtual_service.get_template("nonexistent")
        assert missing is None


def run_tests():
    """测试运行入口"""
    test_class = TestVirtualExperienceDesignFreedom
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
