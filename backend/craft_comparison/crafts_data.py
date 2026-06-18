from typing import Dict, Any, List, Tuple


ANCIENT_CRAFTS: Dict[str, Dict[str, Any]] = {
    "lost_wax": {
        "id": "lost_wax",
        "name": "失蜡法",
        "english_name": "Lost Wax Casting",
        "dynasty": "商代 - 春秋战国",
        "period": "约公元前1600年 - 公元前221年",
        "description": "用蜂蜡、牛油等制成蜡模，外敷泥料制成型壳，加热使蜡熔化流出形成空腔，再浇注铜液。",
        "representative_artifacts": ["曾侯乙尊盘", "淅川铜禁", "四羊方尊"],
        "complexity": 5,
        "skill_required": 5,
        "production_cycle_days": 30,
        "material_cost": 4,
        "typical_defects": [
            "气孔",
            "缩孔",
            "夹杂",
            "冷隔",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.12,
            "shrinkage_porosity": 0.25,
            "gas_porosity": 0.18,
            "inclusion": 0.15,
            "cold_shut": 0.08,
            "misrun": 0.05,
        },
        "overall_defect_rate": 0.35,
        "dimensional_accuracy_mm": 1.5,
        "surface_roughness_ra": 12.5,
        "minimum_wall_thickness_mm": 3.0,
        "max_complexity_score": 85,
    },
    "piece_mold": {
        "id": "piece_mold",
        "name": "范铸法",
        "english_name": "Piece Mold Casting",
        "dynasty": "商代 - 周代",
        "period": "约公元前1600年 - 公元前256年",
        "description": "用泥料制成内范与外范，合范后浇注铜液，是商周青铜器的主要铸造方法。",
        "representative_artifacts": ["司母戊鼎", "大克鼎", "毛公鼎"],
        "complexity": 3,
        "skill_required": 4,
        "production_cycle_days": 20,
        "material_cost": 2,
        "typical_defects": [
            "范线",
            "缩孔",
            "气孔",
            "夹砂",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.20,
            "shrinkage_porosity": 0.30,
            "gas_porosity": 0.12,
            "inclusion": 0.22,
            "cold_shut": 0.06,
            "misrun": 0.04,
        },
        "overall_defect_rate": 0.45,
        "dimensional_accuracy_mm": 3.0,
        "surface_roughness_ra": 25.0,
        "minimum_wall_thickness_mm": 5.0,
        "max_complexity_score": 55,
    },
    "sectional_casting": {
        "id": "sectional_casting",
        "name": "分铸法",
        "english_name": "Sectional Casting",
        "dynasty": "商代晚期 - 春秋战国",
        "period": "约公元前1300年 - 公元前221年",
        "description": "将复杂器物分成多个部件分别铸造，再通过榫卯、焊接等方式组装成完整器物。",
        "representative_artifacts": ["曾侯乙编钟", "莲鹤方壶", "错金银铜方案"],
        "complexity": 4,
        "skill_required": 5,
        "production_cycle_days": 45,
        "material_cost": 3,
        "typical_defects": [
            "装配误差",
            "焊接缺陷",
            "缩孔",
            "应力变形",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.15,
            "shrinkage_porosity": 0.28,
            "gas_porosity": 0.15,
            "inclusion": 0.18,
            "cold_shut": 0.10,
            "misrun": 0.06,
            "assembly_error": 0.12,
            "welding_defect": 0.08,
        },
        "overall_defect_rate": 0.42,
        "dimensional_accuracy_mm": 2.5,
        "surface_roughness_ra": 18.0,
        "minimum_wall_thickness_mm": 4.0,
        "max_complexity_score": 95,
    },
}


MODERN_CRAFTS: Dict[str, Dict[str, Any]] = {
    "modern_investment_casting": {
        "id": "modern_investment_casting",
        "name": "现代熔模铸造",
        "english_name": "Modern Investment Casting",
        "era": "现代工业",
        "description": "采用石蜡或塑料模料，硅溶胶或水玻璃型壳，真空浇铸等现代技术，可实现高精度复杂铸件。",
        "applications": ["航空航天", "医疗器械", "精密机械", "汽车工业"],
        "complexity": 5,
        "skill_required": 4,
        "production_cycle_days": 14,
        "material_cost": 5,
        "typical_defects": [
            "针孔",
            "缩松",
            "夹杂",
            "变形",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.02,
            "shrinkage_porosity": 0.08,
            "gas_porosity": 0.03,
            "inclusion": 0.04,
            "cold_shut": 0.01,
            "misrun": 0.005,
        },
        "overall_defect_rate": 0.08,
        "dimensional_accuracy_mm": 0.1,
        "surface_roughness_ra": 1.6,
        "minimum_wall_thickness_mm": 0.5,
        "max_complexity_score": 98,
    },
}


def get_ancient_crafts() -> List[Dict[str, Any]]:
    return list(ANCIENT_CRAFTS.values())


def get_modern_crafts() -> List[Dict[str, Any]]:
    return list(MODERN_CRAFTS.values())


def get_all_crafts() -> List[Dict[str, Any]]:
    return list(ANCIENT_CRAFTS.values()) + list(MODERN_CRAFTS.values())


def get_craft_by_id(craft_id: str) -> Dict[str, Any] | None:
    return ANCIENT_CRAFTS.get(craft_id) or MODERN_CRAFTS.get(craft_id)


def compare_crafts(craft_ids: List[str]) -> Dict[str, Any]:
    crafts = []
    for cid in craft_ids:
        craft = get_craft_by_id(cid)
        if craft:
            crafts.append(craft)

    if len(crafts) < 2:
        return {"error": "At least 2 crafts are required for comparison", "crafts": crafts}

    defect_radar = {}
    for craft in crafts:
        defect_radar[craft["id"]] = craft["defect_rates"]

    comparison_metrics = [
        {
            "metric": "overall_defect_rate",
            "label": "综合缺陷率",
            "unit": "%",
            "values": {c["id"]: round(c["overall_defect_rate"] * 100, 2) for c in crafts},
        },
        {
            "metric": "dimensional_accuracy_mm",
            "label": "尺寸精度",
            "unit": "mm",
            "values": {c["id"]: c["dimensional_accuracy_mm"] for c in crafts},
            "lower_is_better": True,
        },
        {
            "metric": "surface_roughness_ra",
            "label": "表面粗糙度",
            "unit": "μm (Ra)",
            "values": {c["id"]: c["surface_roughness_ra"] for c in crafts},
            "lower_is_better": True,
        },
        {
            "metric": "minimum_wall_thickness_mm",
            "label": "最小壁厚",
            "unit": "mm",
            "values": {c["id"]: c["minimum_wall_thickness_mm"] for c in crafts},
            "lower_is_better": True,
        },
        {
            "metric": "max_complexity_score",
            "label": "最高复杂度评分",
            "unit": "分",
            "values": {c["id"]: c["max_complexity_score"] for c in crafts},
        },
        {
            "metric": "production_cycle_days",
            "label": "生产周期",
            "unit": "天",
            "values": {c["id"]: c["production_cycle_days"] for c in crafts},
            "lower_is_better": True,
        },
        {
            "metric": "complexity",
            "label": "工艺复杂度",
            "unit": "级",
            "values": {c["id"]: c["complexity"] for c in crafts},
        },
        {
            "metric": "skill_required",
            "label": "技艺要求",
            "unit": "级",
            "values": {c["id"]: c["skill_required"] for c in crafts},
        },
    ]

    defect_type_comparison = []
    all_defect_types = set()
    for craft in crafts:
        all_defect_types.update(craft["defect_rates"].keys())

    defect_name_map = {
        "shrinkage_cavity": "缩孔",
        "shrinkage_porosity": "缩松",
        "gas_porosity": "气孔",
        "inclusion": "夹杂",
        "cold_shut": "冷隔",
        "misrun": "浇不足",
        "assembly_error": "装配误差",
        "welding_defect": "焊接缺陷",
    }

    for defect_type in sorted(all_defect_types):
        defect_type_comparison.append({
            "type": defect_type,
            "label": defect_name_map.get(defect_type, defect_type),
            "values": {c["id"]: round(c["defect_rates"].get(defect_type, 0) * 100, 2) for c in crafts},
        })

    return {
        "crafts": crafts,
        "comparison_metrics": comparison_metrics,
        "defect_radar": defect_radar,
        "defect_type_comparison": defect_type_comparison,
    }


def calculate_defect_rate_for_conditions(
    craft_id: str,
    pouring_temp: float,
    shell_permeability: float,
    alloy_type: str = "bronze",
) -> Dict[str, Any]:
    craft = get_craft_by_id(craft_id)
    if not craft:
        return {"error": f"Craft '{craft_id}' not found"}

    base_rate = craft["overall_defect_rate"]
    base_defects = dict(craft["defect_rates"])

    temp_factor = 1.0
    if "bronze" in alloy_type or "zeng_houyi" in alloy_type:
        optimal_temp = 1180
    elif "steel" in alloy_type:
        optimal_temp = 1580
    elif "aluminum" in alloy_type:
        optimal_temp = 720
    else:
        optimal_temp = 1180

    temp_deviation = abs(pouring_temp - optimal_temp) / optimal_temp
    temp_factor = 1.0 + temp_deviation * 2.5

    perm_factor = 1.0
    if shell_permeability > 0:
        optimal_perm = 50.0
        perm_deviation = abs(shell_permeability - optimal_perm) / optimal_perm
        perm_factor = 1.0 + perm_deviation * 1.5
        if shell_permeability < 20:
            perm_factor *= 1.3

    adjusted_defects = {}
    for d_type, d_rate in base_defects.items():
        factor = temp_factor
        if d_type in ("gas_porosity", "inclusion"):
            factor = perm_factor
        elif d_type in ("cold_shut", "misrun"):
            factor = temp_factor * 0.8 + perm_factor * 0.2
        adjusted_defects[d_type] = min(1.0, d_rate * factor)

    adjusted_overall = min(1.0, base_rate * (temp_factor * 0.6 + perm_factor * 0.4))

    return {
        "craft_id": craft_id,
        "craft_name": craft["name"],
        "base_defect_rate": round(base_rate * 100, 2),
        "adjusted_defect_rate": round(adjusted_overall * 100, 2),
        "temperature_factor": round(temp_factor, 3),
        "permeability_factor": round(perm_factor, 3),
        "defect_breakdown": {
            k: round(v * 100, 2) for k, v in adjusted_defects.items()
        },
        "conditions": {
            "pouring_temp": pouring_temp,
            "shell_permeability": shell_permeability,
            "alloy_type": alloy_type,
        },
    }
