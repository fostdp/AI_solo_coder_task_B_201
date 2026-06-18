from typing import Dict, Any, List, Tuple
import math
import uuid
from datetime import datetime
import numpy as np


SIMPLE_MODE_PRESETS = {
    "delicate": {
        "id": "delicate",
        "name": "精致小巧",
        "description": "体型小巧，纹饰细腻，适合把玩观赏",
        "icon": "✨",
        "scaling_factors": {
            "height": 0.7,
            "diameter": 0.7,
            "wall_thickness": 0.8,
            "pattern_count": 1.2,
        },
    },
    "balanced": {
        "id": "balanced",
        "name": "经典均衡",
        "description": "比例协调，庄重典雅，仿古标准样式",
        "icon": "⚖️",
        "scaling_factors": {
            "height": 1.0,
            "diameter": 1.0,
            "wall_thickness": 1.0,
            "pattern_count": 1.0,
        },
    },
    "grand": {
        "id": "grand",
        "name": "庄重敦厚",
        "description": "体型宏大，壁厚扎实，器型沉稳有分量",
        "icon": "🏛️",
        "scaling_factors": {
            "height": 1.3,
            "diameter": 1.3,
            "wall_thickness": 1.3,
            "pattern_count": 0.8,
        },
    },
    "intricate": {
        "id": "intricate",
        "name": "繁复华丽",
        "description": "纹饰密布，精巧绝伦，挑战工艺极限",
        "icon": "🌸",
        "scaling_factors": {
            "height": 1.0,
            "diameter": 1.0,
            "wall_thickness": 0.7,
            "pattern_count": 1.5,
        },
    },
}


SIMPLE_MODE_PARAMS = {
    "size": {
        "min": 1,
        "max": 5,
        "step": 1,
        "default": 3,
        "label": "整体尺寸",
        "hint": "1=小巧, 5=宏大",
    },
    "ornament": {
        "min": 1,
        "max": 5,
        "step": 1,
        "default": 3,
        "label": "纹饰程度",
        "hint": "1=素面, 5=繁缛",
    },
    "thickness": {
        "min": 1,
        "max": 5,
        "step": 1,
        "default": 3,
        "label": "壁厚程度",
        "hint": "1=轻薄, 5=厚重",
    },
}


WAX_MOLD_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "zunpan": {
        "id": "zunpan",
        "name": "尊盘",
        "category": "青铜器",
        "difficulty": 5,
        "audience": "all",
        "description": "曾侯乙尊盘样式，多层浮雕纹饰，工艺复杂",
        "default_params": {
            "height": 120.0,
            "diameter": 150.0,
            "wall_thickness": 5.0,
            "pattern_count": 16,
            "pattern_depth": 1.5,
            "has_rim": True,
            "has_foot": True,
            "has_dragons": True,
        },
        "param_ranges": {
            "height": {"min": 80.0, "max": 200.0, "step": 5.0, "label": "高度 (mm)", "expert_only": False},
            "diameter": {"min": 100.0, "max": 250.0, "step": 5.0, "label": "直径 (mm)", "expert_only": False},
            "wall_thickness": {"min": 2.0, "max": 10.0, "step": 0.5, "label": "壁厚 (mm)", "expert_only": False},
            "pattern_count": {"min": 8.0, "max": 32.0, "step": 2.0, "label": "纹饰数量", "expert_only": True},
            "pattern_depth": {"min": 0.5, "max": 3.0, "step": 0.5, "label": "纹饰深度 (mm)", "expert_only": True},
            "has_rim": {"expert_only": True, "label": "带口缘"},
            "has_foot": {"expert_only": True, "label": "带圈足"},
            "has_dragons": {"expert_only": True, "label": "带龙形饰"},
        },
        "historical_note": "曾侯乙尊盘是战国早期青铜器，以其繁复精美的失蜡法铸造工艺闻名于世。",
    },
    "ding": {
        "id": "ding",
        "name": "圆鼎",
        "category": "青铜器",
        "difficulty": 3,
        "audience": "all",
        "description": "三足圆鼎，典型礼器，造型庄重",
        "default_params": {
            "height": 180.0,
            "diameter": 150.0,
            "wall_thickness": 6.0,
            "leg_count": 3,
            "has_handles": True,
            "decorated_body": True,
        },
        "param_ranges": {
            "height": {"min": 100.0, "max": 300.0, "step": 10.0, "label": "高度 (mm)", "expert_only": False},
            "diameter": {"min": 80.0, "max": 200.0, "step": 5.0, "label": "口径 (mm)", "expert_only": False},
            "wall_thickness": {"min": 3.0, "max": 12.0, "step": 1.0, "label": "壁厚 (mm)", "expert_only": False},
            "leg_count": {"expert_only": True, "label": "鼎足数量"},
            "has_handles": {"expert_only": True, "label": "带立耳"},
            "decorated_body": {"expert_only": True, "label": "腹部纹饰"},
        },
        "historical_note": "鼎是古代最重要的礼器之一，象征权力与地位。司母戊鼎是迄今发现最大的青铜器。",
    },
    "hu": {
        "id": "hu",
        "name": "铜壶",
        "category": "青铜器",
        "difficulty": 3,
        "audience": "all",
        "description": "盛酒器，鼓腹长颈，造型优雅",
        "default_params": {
            "height": 200.0,
            "body_diameter": 120.0,
            "neck_diameter": 60.0,
            "wall_thickness": 4.0,
            "has_cover": True,
            "has_ring_foot": True,
        },
        "param_ranges": {
            "height": {"min": 100.0, "max": 350.0, "step": 10.0, "label": "高度 (mm)", "expert_only": False},
            "body_diameter": {"min": 60.0, "max": 180.0, "step": 5.0, "label": "腹径 (mm)", "expert_only": False},
            "wall_thickness": {"min": 2.0, "max": 8.0, "step": 0.5, "label": "壁厚 (mm)", "expert_only": False},
            "neck_diameter": {"expert_only": True, "label": "颈径 (mm)"},
            "has_cover": {"expert_only": True, "label": "带盖"},
            "has_ring_foot": {"expert_only": True, "label": "带圈足"},
        },
        "historical_note": "铜壶是古代盛酒或盛水器，常饰有精美的错金银或镶嵌工艺。",
    },
    "ring": {
        "id": "ring",
        "name": "指环",
        "category": "饰品",
        "difficulty": 1,
        "audience": "beginner",
        "description": "简单的指环造型，适合初学者体验",
        "default_params": {
            "diameter": 20.0,
            "band_width": 5.0,
            "thickness": 2.0,
            "has_pattern": True,
            "pattern_type": "twist",
        },
        "param_ranges": {
            "diameter": {"min": 15.0, "max": 25.0, "step": 0.5, "label": "内径 (mm)", "expert_only": False},
            "band_width": {"min": 3.0, "max": 12.0, "step": 0.5, "label": "戒面宽度 (mm)", "expert_only": False},
            "thickness": {"min": 1.0, "max": 4.0, "step": 0.5, "label": "厚度 (mm)", "expert_only": False},
            "has_pattern": {"expert_only": True, "label": "带纹饰"},
            "pattern_type": {"expert_only": True, "label": "纹饰类型"},
        },
        "historical_note": "指环是人类最早的饰品之一，古代指环多用玉石或金属制成。",
    },
    "pendant": {
        "id": "pendant",
        "name": "挂坠",
        "category": "饰品",
        "difficulty": 2,
        "audience": "beginner",
        "description": "带孔的小挂坠，可穿绳佩戴",
        "default_params": {
            "height": 30.0,
            "width": 20.0,
            "thickness": 3.0,
            "hole_diameter": 2.5,
            "shape": "teardrop",
            "has_pattern": True,
        },
        "param_ranges": {
            "height": {"min": 15.0, "max": 60.0, "step": 2.0, "label": "高度 (mm)", "expert_only": False},
            "width": {"min": 10.0, "max": 40.0, "step": 2.0, "label": "宽度 (mm)", "expert_only": False},
            "thickness": {"min": 1.0, "max": 6.0, "step": 0.5, "label": "厚度 (mm)", "expert_only": False},
            "hole_diameter": {"expert_only": True, "label": "穿孔直径"},
            "shape": {"expert_only": True, "label": "外形"},
            "has_pattern": {"expert_only": True, "label": "带纹饰"},
        },
        "historical_note": "挂坠是古代常见的佩饰，材质多样，常刻有吉祥图案或文字。",
    },
}


def get_simple_mode_presets() -> List[Dict[str, Any]]:
    return list(SIMPLE_MODE_PRESETS.values())


def get_simple_mode_params() -> Dict[str, Any]:
    return SIMPLE_MODE_PARAMS


def apply_simple_mode_params(
    template_id: str,
    size_level: int = 3,
    ornament_level: int = 3,
    thickness_level: int = 3,
) -> Dict[str, Any]:
    template = WAX_MOLD_TEMPLATES.get(template_id)
    if not template:
        return {"error": f"Template {template_id} not found"}

    size_factor = 0.6 + (size_level - 1) * 0.2
    ornament_factor = 0.5 + (ornament_level - 1) * 0.25
    thickness_factor = 0.6 + (thickness_level - 1) * 0.2

    defaults = template["default_params"]
    params = {}

    for key, value in defaults.items():
        if isinstance(value, bool):
            if key in ("has_pattern", "decorated_body", "has_dragons"):
                params[key] = ornament_level >= 3
            else:
                params[key] = value
        elif isinstance(value, (int, float)):
            if "height" in key or "diameter" in key or "width" in key:
                params[key] = round(value * size_factor, 1)
            elif "thickness" in key or key == "thickness":
                params[key] = round(value * thickness_factor, 1)
            elif "pattern" in key and "count" in key:
                params[key] = int(value * ornament_factor)
            elif "pattern" in key and "depth" in key:
                params[key] = round(value * (0.5 + ornament_factor * 0.5), 1)
            else:
                params[key] = value
        else:
            params[key] = value

    return params


def apply_preset(template_id: str, preset_id: str) -> Dict[str, Any]:
    template = WAX_MOLD_TEMPLATES.get(template_id)
    preset = SIMPLE_MODE_PRESETS.get(preset_id)
    if not template or not preset:
        return {"error": f"Template {template_id} or preset {preset_id} not found"}

    defaults = template["default_params"]
    factors = preset["scaling_factors"]
    params = {}

    for key, value in defaults.items():
        if isinstance(value, bool):
            params[key] = value
        elif isinstance(value, (int, float)):
            factor = factors.get(key, 1.0)
            if isinstance(value, int):
                params[key] = int(value * factor)
            else:
                params[key] = round(value * factor, 1)
        else:
            params[key] = value

    return params


CASTING_MATERIALS: Dict[str, Dict[str, Any]] = {
    "bronze_cu_sn": {
        "id": "bronze_cu_sn",
        "name": "青铜 (Cu-Sn 12%)",
        "pouring_temp": 1180.0,
        "density": 8.7,
        "viscosity": 4.5,
        "shrinkage_rate": 1.5,
        "color_hex": "#b87333",
        "historical": True,
    },
    "brass": {
        "id": "brass",
        "name": "黄铜 (Cu-Zn 30%)",
        "pouring_temp": 1060.0,
        "density": 8.5,
        "viscosity": 3.8,
        "shrinkage_rate": 1.8,
        "color_hex": "#e5c100",
        "historical": True,
    },
    "stainless_steel": {
        "id": "stainless_steel",
        "name": "不锈钢 304",
        "pouring_temp": 1580.0,
        "density": 7.9,
        "viscosity": 5.2,
        "shrinkage_rate": 2.0,
        "color_hex": "#c0c0c0",
        "historical": False,
    },
    "aluminum_alloy": {
        "id": "aluminum_alloy",
        "name": "铝合金 A356",
        "pouring_temp": 720.0,
        "density": 2.7,
        "viscosity": 2.0,
        "shrinkage_rate": 3.5,
        "color_hex": "#d4d4d4",
        "historical": False,
    },
}


SHELL_MATERIALS: Dict[str, Dict[str, Any]] = {
    "silica_sol": {
        "id": "silica_sol",
        "name": "硅溶胶+石英砂",
        "permeability": 50.0,
        "thermal_conductivity": 1.2,
        "strength": 3,
        "cost": 2,
        "layers": 9,
        "historical": False,
    },
    "water_glass": {
        "id": "water_glass",
        "name": "水玻璃+石英砂",
        "permeability": 35.0,
        "thermal_conductivity": 0.8,
        "strength": 2,
        "cost": 1,
        "layers": 7,
        "historical": False,
    },
    "ethyl_silicate": {
        "id": "ethyl_silicate",
        "name": "硅酸乙酯+锆英砂",
        "permeability": 65.0,
        "thermal_conductivity": 1.5,
        "strength": 4,
        "cost": 3,
        "layers": 10,
        "historical": False,
    },
    "ancient_mud": {
        "id": "ancient_mud",
        "name": "古代泥范",
        "permeability": 25.0,
        "thermal_conductivity": 0.6,
        "strength": 1,
        "cost": 0,
        "layers": 1,
        "historical": True,
    },
}


def get_wax_mold_templates() -> List[Dict[str, Any]]:
    return list(WAX_MOLD_TEMPLATES.values())


def get_wax_mold_template(template_id: str) -> Dict[str, Any] | None:
    return WAX_MOLD_TEMPLATES.get(template_id)


def get_casting_materials() -> List[Dict[str, Any]]:
    return list(CASTING_MATERIALS.values())


def get_shell_materials() -> List[Dict[str, Any]]:
    return list(SHELL_MATERIALS.values())


def generate_model_geometry(template_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    template = WAX_MOLD_TEMPLATES.get(template_id)
    if not template:
        return {"error": f"Template '{template_id}' not found"}

    p = {**template["default_params"], **params}

    if template_id == "zunpan":
        parts = _generate_zunpan_geometry(p)
    elif template_id == "ding":
        parts = _generate_ding_geometry(p)
    elif template_id == "hu":
        parts = _generate_hu_geometry(p)
    elif template_id == "ring":
        parts = _generate_ring_geometry(p)
    elif template_id == "pendant":
        parts = _generate_pendant_geometry(p)
    else:
        parts = []

    volume = _calculate_volume(template_id, p)
    surface_area = _calculate_surface_area(template_id, p)
    complexity_score = _calculate_complexity_score(template_id, p)

    return {
        "template_id": template_id,
        "template_name": template["name"],
        "params": p,
        "parts": parts,
        "properties": {
            "volume_cm3": round(volume, 2),
            "surface_area_cm2": round(surface_area, 2),
            "estimated_weight_g": round(volume * 8.7, 2),
            "complexity_score": round(complexity_score, 1),
            "difficulty": template["difficulty"],
        },
    }


def _generate_zunpan_geometry(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts = []
    h = p["height"]
    d = p["diameter"]
    r = d / 2

    parts.append({
        "type": "cylinder",
        "name": "器身",
        "top_radius": r * 0.9,
        "bottom_radius": r * 0.75,
        "height": h * 0.5,
        "y_offset": -h * 0.1,
    })

    if p.get("has_rim", True):
        parts.append({
            "type": "torus",
            "name": "口缘",
            "radius": r,
            "tube_radius": h * 0.06,
            "y_offset": h * 0.15,
        })

    if p.get("has_foot", True):
        parts.append({
            "type": "cylinder",
            "name": "圈足",
            "top_radius": r * 0.5,
            "bottom_radius": r * 0.65,
            "height": h * 0.25,
            "y_offset": -h * 0.45,
        })

    pattern_count = int(p.get("pattern_count", 16))
    for i in range(pattern_count):
        angle = (i / pattern_count) * math.pi * 2
        parts.append({
            "type": "sphere",
            "name": f"蟠龙饰_{i+1}",
            "radius": h * 0.06,
            "x": math.cos(angle) * r * 0.92,
            "z": math.sin(angle) * r * 0.92,
            "y": h * 0.1,
        })

    return parts


def _generate_ding_geometry(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts = []
    h = p["height"]
    d = p["diameter"]
    r = d / 2

    parts.append({
        "type": "cylinder",
        "name": "鼎腹",
        "top_radius": r,
        "bottom_radius": r * 0.85,
        "height": h * 0.6,
        "y_offset": 0,
    })

    leg_count = int(p.get("leg_count", 3))
    for i in range(leg_count):
        angle = (i / leg_count) * math.pi * 2 + math.pi / leg_count
        parts.append({
            "type": "cylinder",
            "name": f"鼎足_{i+1}",
            "top_radius": h * 0.05,
            "bottom_radius": h * 0.04,
            "height": h * 0.4,
            "x": math.cos(angle) * r * 0.6,
            "z": math.sin(angle) * r * 0.6,
            "y_offset": -h * 0.5,
        })

    return parts


def _generate_hu_geometry(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts = []
    h = p["height"]
    bd = p.get("body_diameter", 120.0)
    nd = p.get("neck_diameter", 60.0)

    parts.append({
        "type": "cylinder",
        "name": "壶腹",
        "top_radius": bd / 2 * 0.8,
        "bottom_radius": bd / 2 * 0.6,
        "height": h * 0.55,
        "y_offset": 0,
    })

    parts.append({
        "type": "cylinder",
        "name": "壶颈",
        "top_radius": nd / 2,
        "bottom_radius": bd / 2 * 0.5,
        "height": h * 0.25,
        "y_offset": h * 0.4,
    })

    if p.get("has_ring_foot", True):
        parts.append({
            "type": "cylinder",
            "name": "圈足",
            "top_radius": bd / 2 * 0.5,
            "bottom_radius": bd / 2 * 0.55,
            "height": h * 0.15,
            "y_offset": -h * 0.4,
        })

    return parts


def _generate_ring_geometry(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts = []
    d = p["diameter"]
    bw = p["band_width"]
    r_med = d / 2 + bw / 2

    parts.append({
        "type": "torus",
        "name": "戒身",
        "radius": r_med,
        "tube_radius": bw / 3,
        "y_offset": 0,
    })

    return parts


def _generate_pendant_geometry(p: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts = []
    h = p["height"]
    w = p["width"]
    t = p["thickness"]

    parts.append({
        "type": "ellipsoid",
        "name": "坠身",
        "x_radius": w / 2,
        "y_radius": h / 2,
        "z_radius": t / 2,
        "y_offset": 0,
    })

    if p.get("hole_diameter", 2.5) > 0:
        parts.append({
            "type": "hole",
            "name": "穿绳孔",
            "diameter": p.get("hole_diameter", 2.5),
            "y_offset": h / 2 - h * 0.1,
        })

    return parts


def _calculate_volume(template_id: str, p: Dict[str, Any]) -> float:
    wt = p.get("wall_thickness", 5.0)

    if template_id == "zunpan":
        h = p["height"]
        d = p["diameter"]
        volume = math.pi * (d/2)**2 * h * 0.5 * (wt / (d/2)) * 3
    elif template_id == "ding":
        h = p["height"]
        d = p["diameter"]
        volume = math.pi * (d/2)**2 * h * 0.45 * (wt / (d/2)) * 3
    elif template_id == "hu":
        h = p["height"]
        bd = p.get("body_diameter", 120.0)
        volume = math.pi * (bd/2)**2 * h * 0.4 * (wt / (bd/2)) * 3
    elif template_id == "ring":
        d = p["diameter"]
        bw = p["band_width"]
        th = p["thickness"]
        volume = math.pi * (d + bw) * bw * th
    elif template_id == "pendant":
        h = p["height"]
        w = p["width"]
        t = p["thickness"]
        volume = math.pi * (w/2) * (h/2) * t * 0.7
    else:
        volume = 100.0

    return volume / 1000.0


def _calculate_surface_area(template_id: str, p: Dict[str, Any]) -> float:
    if template_id == "zunpan":
        h = p["height"]
        d = p["diameter"]
        pattern_count = p.get("pattern_count", 16)
        base_area = math.pi * d * h * 0.6
        pattern_area = pattern_count * h * 0.06 * 4
        return (base_area + pattern_area) / 100.0
    elif template_id == "ring":
        d = p["diameter"]
        bw = p["band_width"]
        return 2 * math.pi * (d/2 + bw/2) * bw / 100.0
    elif template_id == "pendant":
        h = p["height"]
        w = p["width"]
        return math.pi * (w/2) * (h/2) * 2 / 100.0
    else:
        return 50.0


def _calculate_complexity_score(template_id: str, p: Dict[str, Any]) -> float:
    template = WAX_MOLD_TEMPLATES.get(template_id)
    base = float(template["difficulty"] * 15) if template else 40.0

    wt = p.get("wall_thickness", p.get("thickness", 5.0))
    if wt < 2.0:
        base += 25
    elif wt < 3.0:
        base += 18
    elif wt < 4.0:
        base += 10
    elif wt < 5.0:
        base += 4

    pattern_count = p.get("pattern_count", 0)
    if pattern_count > 0:
        base += min(25, pattern_count * 0.6)

    h = p.get("height", 0)
    d = p.get("diameter", p.get("width", 0))
    if h > 0 and d > 0 and h / d > 1.8:
        base += 8

    return min(100, base)


def simulate_casting(
    template_id: str,
    params: Dict[str, Any],
    material_id: str = "bronze_cu_sn",
    shell_id: str = "silica_sol",
    pouring_temp_override: float | None = None,
) -> Dict[str, Any]:
    template = WAX_MOLD_TEMPLATES.get(template_id)
    material = CASTING_MATERIALS.get(material_id)
    shell = SHELL_MATERIALS.get(shell_id)

    if not template or not material or not shell:
        return {"error": "Invalid template, material, or shell type"}

    geometry = generate_model_geometry(template_id, params)
    if "error" in geometry:
        return geometry

    p = {**template["default_params"], **params}

    pouring_temp = pouring_temp_override or material["pouring_temp"]
    optimal_temp = material["pouring_temp"]
    temp_deviation = abs(pouring_temp - optimal_temp) / optimal_temp

    complexity = geometry["properties"]["complexity_score"]
    wall_thickness = p.get("wall_thickness", p.get("thickness", 5.0))

    base_defect_rate = 0.15 + complexity * 0.004

    if wall_thickness < 3.0:
        base_defect_rate += 0.15
    elif wall_thickness < 4.0:
        base_defect_rate += 0.08

    temp_factor = 1.0 + temp_deviation * 3.0

    perm = shell["permeability"]
    optimal_perm = 50.0
    perm_factor = 1.0 + abs(perm - optimal_perm) / optimal_perm * 0.8
    if perm < 25:
        perm_factor += 0.15

    overall_defect_rate = min(0.85, base_defect_rate * temp_factor * perm_factor)

    gas_porosity = min(0.4, overall_defect_rate * 0.35 * (1.0 + (50 - perm) / 50.0))
    shrinkage = min(0.35, overall_defect_rate * 0.3 * temp_factor)
    cold_shut = min(0.25, overall_defect_rate * 0.2 * temp_factor)
    inclusion = min(0.2, overall_defect_rate * 0.15)

    filling_quality = max(20, 100 - overall_defect_rate * 80)

    shrinkage_cavities = []
    num_defects = int(overall_defect_rate * 15) + 1

    import random
    random.seed(hash(template_id + str(wall_thickness) + str(pouring_temp)) & 0x7fffffff)

    for i in range(min(num_defects, 12)):
        rx = random.uniform(-0.4, 0.4)
        ry = random.uniform(-0.4, 0.4)
        rz = random.uniform(-0.4, 0.4)
        volume = random.uniform(0.05, 0.8) * (overall_defect_rate / 0.3)
        severity = "low"
        if volume > 0.4:
            severity = "medium"
        if volume > 0.7:
            severity = "high"
        if volume > 1.0:
            severity = "critical"

        shrinkage_cavities.append({
            "id": str(uuid.uuid4()),
            "position": {"x": 0.5 + rx, "y": 0.5 + ry, "z": 0.5 + rz},
            "volume_cm3": round(volume, 3),
            "severity": severity,
            "type": "shrinkage_cavity" if volume > 0.3 else "shrinkage_porosity",
        })

    steps = []
    total_steps = 10
    for step in range(1, total_steps + 1):
        progress = step / total_steps
        temp_at_front = pouring_temp * (1.0 - progress * 0.3)
        steps.append({
            "step": step,
            "filling_progress": round(progress * 100, 1),
            "avg_temperature": round(pouring_temp * (1.0 - progress * 0.4), 1),
            "front_temperature": round(temp_at_front, 1),
        })

    return {
        "simulation_id": str(uuid.uuid4()),
        "template_id": template_id,
        "template_name": template["name"],
        "material": material,
        "shell": shell,
        "geometry": geometry,
        "casting_parameters": {
            "pouring_temp": pouring_temp,
            "optimal_temp": optimal_temp,
            "temp_deviation_percent": round(temp_deviation * 100, 1),
        },
        "results": {
            "overall_defect_rate": round(overall_defect_rate * 100, 2),
            "filling_quality_score": round(filling_quality, 1),
            "defect_breakdown": {
                "gas_porosity_rate": round(gas_porosity * 100, 2),
                "shrinkage_rate": round(shrinkage * 100, 2),
                "cold_shut_rate": round(cold_shut * 100, 2),
                "inclusion_rate": round(inclusion * 100, 2),
            },
            "detected_defects": shrinkage_cavities,
            "total_defect_volume": round(sum(d["volume_cm3"] for d in shrinkage_cavities), 3),
        },
        "simulation_steps": steps,
        "tips": _generate_casting_tips(
            overall_defect_rate, wall_thickness, perm, pouring_temp, optimal_temp, complexity
        ),
        "created_at": datetime.now().isoformat(),
    }


def _generate_casting_tips(
    defect_rate: float,
    wall_thickness: float,
    permeability: float,
    pouring_temp: float,
    optimal_temp: float,
    complexity: float,
) -> List[str]:
    tips = []

    if wall_thickness < 3.0:
        tips.append("壁厚较薄，极易产生浇不足缺陷，建议适当提高浇铸温度或增加壁厚")

    if permeability < 30:
        tips.append("型壳透气性偏低，建议增加型壳层数间的干燥时间，或改用透气性更好的材料")
    elif permeability > 70:
        tips.append("型壳透气性偏高，需注意防止金属液渗透和表面粗糙问题")

    if pouring_temp < optimal_temp * 0.95:
        tips.append("浇铸温度偏低，流动性下降，容易产生冷隔和浇不足")
    elif pouring_temp > optimal_temp * 1.08:
        tips.append("浇铸温度偏高，会增加缩孔缩松倾向，且晶粒粗大")

    if defect_rate > 0.5:
        tips.append("缺陷率较高，建议优化工艺参数：调整浇温、改善型壳透气性、增设冒口")

    if complexity > 70:
        tips.append("铸件结构复杂，建议在热节处设置冷铁或冒口，防止缩孔")

    if not tips:
        tips.append("工艺参数良好，预期铸件质量较好")

    return tips


def save_virtual_experiment(experiment: Dict[str, Any]) -> Dict[str, Any]:
    from common.mongo_client import get_db
    db = get_db()

    if "id" not in experiment:
        experiment["id"] = str(uuid.uuid4())
    if "created_at" not in experiment:
        experiment["created_at"] = datetime.now()

    db.virtual_experiments.insert_one(experiment)
    return experiment


def list_virtual_experiments(limit: int = 20) -> List[Dict[str, Any]]:
    from common.mongo_client import get_db
    db = get_db()
    return list(
        db.virtual_experiments.find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )


def get_virtual_experiment(exp_id: str) -> Dict[str, Any] | None:
    from common.mongo_client import get_db
    db = get_db()
    return db.virtual_experiments.find_one({"id": exp_id}, {"_id": 0})
