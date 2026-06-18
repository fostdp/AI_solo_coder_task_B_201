from typing import Dict, Any, List, Optional
from .wax_mold_engine import (
    get_wax_mold_templates,
    get_wax_mold_template,
    get_casting_materials,
    get_shell_materials,
    generate_model_geometry,
    simulate_casting,
    save_virtual_experiment,
    list_virtual_experiments,
    get_virtual_experiment,
    get_simple_mode_presets,
    get_simple_mode_params,
    apply_simple_mode_params,
    apply_preset,
)


class VrLostWaxService:
    def __init__(self):
        pass

    def list_templates(self, audience: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        templates = get_wax_mold_templates()
        if audience:
            templates = [t for t in templates if t["audience"] in (audience, "all")]
        if category:
            templates = [t for t in templates if t["category"] == category]
        return templates

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return get_wax_mold_template(template_id)

    def list_materials(self) -> List[Dict[str, Any]]:
        return get_casting_materials()

    def list_shell_materials(self) -> List[Dict[str, Any]]:
        return get_shell_materials()

    def generate_geometry(self, template_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return generate_model_geometry(template_id, params)

    def simulate(
        self,
        template_id: str,
        params: Dict[str, Any],
        material_id: str = "bronze_cu_sn",
        shell_id: str = "silica_sol",
        pouring_temp: Optional[float] = None,
    ) -> Dict[str, Any]:
        return simulate_casting(
            template_id=template_id,
            params=params,
            material_id=material_id,
            shell_id=shell_id,
            pouring_temp_override=pouring_temp,
        )

    def simple_mode_presets(self) -> List[Dict[str, Any]]:
        return get_simple_mode_presets()

    def simple_mode_params(self) -> Dict[str, Any]:
        return get_simple_mode_params()

    def apply_simple_mode(
        self,
        template_id: str,
        size_level: int = 3,
        ornament_level: int = 3,
        thickness_level: int = 3,
    ) -> Dict[str, Any]:
        return apply_simple_mode_params(
            template_id=template_id,
            size_level=size_level,
            ornament_level=ornament_level,
            thickness_level=thickness_level,
        )

    def apply_preset(self, template_id: str, preset_id: str) -> Dict[str, Any]:
        return apply_preset(template_id, preset_id)

    def save_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        return save_virtual_experiment(experiment)

    def list_experiments(self, limit: int = 20) -> List[Dict[str, Any]]:
        return list_virtual_experiments(limit)

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        return get_virtual_experiment(exp_id)


vr_lost_wax_service = VrLostWaxService()
