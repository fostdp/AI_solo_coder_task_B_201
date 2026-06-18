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
)


class VirtualExperienceService:
    def __init__(self):
        pass

    def list_templates(self) -> List[Dict[str, Any]]:
        return get_wax_mold_templates()

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return get_wax_mold_template(template_id)

    def list_materials(self) -> List[Dict[str, Any]]:
        return get_casting_materials()

    def list_shells(self) -> List[Dict[str, Any]]:
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

    def save_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        return save_virtual_experiment(experiment)

    def list_experiments(self, limit: int = 20) -> List[Dict[str, Any]]:
        return list_virtual_experiments(limit)

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        return get_virtual_experiment(exp_id)


virtual_service = VirtualExperienceService()
