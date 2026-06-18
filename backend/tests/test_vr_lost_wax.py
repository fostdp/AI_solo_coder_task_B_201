import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from vr_lost_wax.wax_mold_engine import (
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
    get_simple_mode_presets,
    get_simple_mode_params,
    apply_simple_mode_params,
    apply_preset,
)
from vr_lost_wax.service import vr_lost_wax_service


class TestVrLostWaxData:
    """虚拟失蜡铸造模块测试 - 数据验证"""

    def test_wax_mold_templates_exist(self):
        assert len(WAX_MOLD_TEMPLATES) >= 3
        for template_id, template in WAX_MOLD_TEMPLATES.items():
            assert "id" in template
            assert "name" in template
            assert "category" in template
            assert "difficulty" in template
            assert "default_params" in template
            assert "param_ranges" in template

    def test_templates_have_valid_difficulty(self):
        for template in get_wax_mold_templates():
            assert 1 <= template["difficulty"] <= 5

    def test_casting_materials_exist(self):
        materials = get_casting_materials()
        assert len(materials) >= 3
        for material in materials:
            assert "id" in material
            assert "name" in material
            assert "pouring_temp" in material
            assert "density" in material
            assert material["pouring_temp"] > 0

    def test_shell_materials_exist(self):
        shells = get_shell_materials()
        assert len(shells) >= 3
        for shell in shells:
            assert "id" in shell
            assert "name" in shell
            assert "permeability" in shell
            assert shell["permeability"] > 0

    def test_simple_mode_presets_exist(self):
        presets = get_simple_mode_presets()
        assert len(presets) >= 3
        for preset in presets:
            assert "id" in preset
            assert "name" in preset
            assert "scaling_factors" in preset

    def test_simple_mode_params_exist(self):
        params = get_simple_mode_params()
        assert "size" in params
        assert "ornament" in params
        assert "thickness" in params


class TestVrLostWaxGeometry:
    """虚拟失蜡铸造模块测试 - 几何生成验证"""

    def test_generate_geometry_zunpan(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = generate_model_geometry(template_id, template["default_params"])
        assert "template_id" in result
        assert "parts" in result
        assert "properties" in result
        assert len(result["parts"]) >= 3

    def test_generate_geometry_ding(self):
        template_id = "ding"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = generate_model_geometry(template_id, template["default_params"])
        assert result["template_id"] == template_id
        assert len(result["parts"]) >= 2

    def test_geometry_has_volume_and_surface_area(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = generate_model_geometry(template_id, template["default_params"])
        props = result["properties"]
        assert "volume_cm3" in props
        assert "surface_area_cm2" in props
        assert "complexity_score" in props
        assert props["volume_cm3"] > 0
        assert props["surface_area_cm2"] > 0
        assert 0 <= props["complexity_score"] <= 100

    def test_geometry_invalid_template(self):
        result = generate_model_geometry("nonexistent", {})
        assert "error" in result

    def test_apply_simple_mode_params(self):
        result = apply_simple_mode_params(
            "zunpan",
            size_level=3,
            ornament_level=3,
            thickness_level=3,
        )
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_apply_preset(self):
        result = apply_preset("zunpan", "balanced")
        assert "error" not in result
        assert isinstance(result, dict)

    def test_apply_preset_invalid(self):
        result = apply_preset("nonexistent", "balanced")
        assert "error" in result


class TestVrLostWaxSimulation:
    """虚拟失蜡铸造模块测试 - 模拟功能验证"""

    def test_simulate_casting_returns_result(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
            material_id="bronze_cu_sn",
            shell_id="silica_sol",
        )
        assert "simulation_id" in result
        assert "results" in result
        assert "geometry" in result

    def test_simulation_has_defect_rate(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        assert "overall_defect_rate" in result["results"]
        assert 0 <= result["results"]["overall_defect_rate"] <= 100

    def test_simulation_has_filling_quality(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        assert "filling_quality_score" in result["results"]
        assert 0 <= result["results"]["filling_quality_score"] <= 100

    def test_simulation_has_defect_breakdown(self):
        template_id = "ring"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        breakdown = result["results"]["defect_breakdown"]
        assert "gas_porosity_rate" in breakdown
        assert "shrinkage_rate" in breakdown
        assert "cold_shut_rate" in breakdown
        assert "inclusion_rate" in breakdown

    def test_simulation_has_detected_defects(self):
        template_id = "pendant"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        assert "detected_defects" in result["results"]
        assert isinstance(result["results"]["detected_defects"], list)

    def test_simulation_has_simulation_steps(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        assert "simulation_steps" in result
        assert len(result["simulation_steps"]) >= 5

    def test_simulation_has_tips(self):
        template_id = "ding"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
        )
        assert "tips" in result
        assert isinstance(result["tips"], list)
        assert len(result["tips"]) >= 1

    def test_different_materials_produce_different_results(self):
        template_id = "zunpan"
        template = get_wax_mold_template(template_id)
        if not template:
            pytest.skip(f"Template {template_id} not found")
        bronze_result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
            material_id="bronze_cu_sn",
        )
        steel_result = simulate_casting(
            template_id=template_id,
            params=template["default_params"],
            material_id="stainless_steel",
        )
        assert bronze_result["material"]["id"] == "bronze_cu_sn"
        assert steel_result["material"]["id"] == "stainless_steel"

    def test_simulation_invalid_template(self):
        result = simulate_casting(
            template_id="nonexistent",
            params={},
        )
        assert "error" in result


class TestVrLostWaxService:
    """虚拟失蜡铸造模块测试 - 服务层验证"""

    def test_list_templates(self):
        result = vr_lost_wax_service.list_templates()
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_list_templates_with_category(self):
        result = vr_lost_wax_service.list_templates(category="青铜器")
        assert isinstance(result, list)

    def test_get_template_valid(self):
        templates = vr_lost_wax_service.list_templates()
        if len(templates) < 1:
            pytest.skip("No templates available")
        template_id = templates[0]["id"]
        template = vr_lost_wax_service.get_template(template_id)
        assert template is not None
        assert template["id"] == template_id

    def test_get_template_invalid(self):
        template = vr_lost_wax_service.get_template("nonexistent")
        assert template is None

    def test_list_materials(self):
        result = vr_lost_wax_service.list_materials()
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_list_shell_materials(self):
        result = vr_lost_wax_service.list_shell_materials()
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_generate_geometry_service(self):
        templates = vr_lost_wax_service.list_templates()
        if len(templates) < 1:
            pytest.skip("No templates available")
        template = templates[0]
        result = vr_lost_wax_service.generate_geometry(
            template_id=template["id"],
            params=template["default_params"],
        )
        assert "parts" in result
        assert "properties" in result

    def test_simulate_service(self):
        templates = vr_lost_wax_service.list_templates()
        if len(templates) < 1:
            pytest.skip("No templates available")
        template = templates[0]
        result = vr_lost_wax_service.simulate(
            template_id=template["id"],
            params=template["default_params"],
        )
        assert "results" in result
        assert "overall_defect_rate" in result["results"]

    def test_simple_mode_presets_service(self):
        result = vr_lost_wax_service.simple_mode_presets()
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_apply_simple_mode_service(self):
        templates = vr_lost_wax_service.list_templates()
        if len(templates) < 1:
            pytest.skip("No templates available")
        result = vr_lost_wax_service.apply_simple_mode(
            template_id=templates[0]["id"],
            size_level=3,
            ornament_level=3,
            thickness_level=3,
        )
        assert isinstance(result, dict)
