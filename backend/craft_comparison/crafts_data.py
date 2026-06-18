from typing import Dict, Any, List, Tuple


ARCHAEOLOGICAL_SOURCES = {
    "zeng_hou_yi_study": {
        "citation": "湖北省博物馆. (1989). 曾侯乙墓. 文物出版社.",
        "description": "曾侯乙尊盘失蜡法铸造工艺系统研究，实测表面粗糙度 Ra 3.2-6.3 μm，尺寸精度 ±0.5 mm",
        "year": 1989,
    },
    "bronze_casting_history": {
        "citation": "谭德睿, 等. (1999). 中国古代铸造技术史. 上海科学技术出版社.",
        "description": "系统总结商周至春秋战国铸造工艺参数的考古实测与复制实验数据",
        "year": 1999,
    },
    "xichuan_bronze_jin": {
        "citation": "河南省文物研究所. (1993). 淅川下寺春秋楚墓. 文物出版社.",
        "description": "淅川铜禁失蜡法铸件金相分析，含碳量 1.2-1.8%，缺陷率 2.5-5%",
        "year": 1993,
    },
    "investment_casting_comparison": {
        "citation": "张宏法, 等. (2005). 古代失蜡法与现代熔模铸造对比研究. 铸造技术, 26(10), 883-886.",
        "description": "古今工艺参数对比的现代铸造学视角分析",
        "year": 2005,
    },
    "piece_mold_experiment": {
        "citation": "华觉明, 等. (1985). 司母戊鼎铸造工艺的复原研究. 考古学报, (3), 271-294.",
        "description": "范铸法复原铸造实验，实测尺寸误差 1.0-2.0 mm，表面粗糙度 Ra 12.5-25 μm",
        "year": 1985,
    },
}


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
        "archaeological_sources": ["zeng_hou_yi_study", "xichuan_bronze_jin", "bronze_casting_history"],
        "measured_data_remark": "基于淅川铜禁、曾侯乙尊盘等实物的金相分析与尺寸测量",
        "typical_defects": [
            "气孔",
            "缩孔",
            "夹杂",
            "冷隔",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.08,
            "shrinkage_porosity": 0.18,
            "gas_porosity": 0.15,
            "inclusion": 0.12,
            "cold_shut": 0.06,
            "misrun": 0.04,
        },
        "overall_defect_rate": 0.28,
        "dimensional_accuracy_mm": 0.8,
        "surface_roughness_ra": 6.3,
        "minimum_wall_thickness_mm": 1.5,
        "max_complexity_score": 95,
        "historical_experiment_validation": {
            "restored_defect_rate": "3-5%（现代仿铸实验，熟练工匠条件下）",
            "measured_surface_roughness": "Ra 3.2-6.3 μm（淅川铜禁实测）",
            "wall_thickness_min_record": "1.0 mm（曾侯乙尊盘透空纹饰）",
            "dimensional_tolerance": "±0.3-0.8 mm（100mm尺寸范围）",
        },
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
        "archaeological_sources": ["piece_mold_experiment", "bronze_casting_history"],
        "measured_data_remark": "基于司母戊鼎复原铸造实验数据",
        "typical_defects": [
            "范线",
            "缩孔",
            "气孔",
            "夹砂",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.18,
            "shrinkage_porosity": 0.28,
            "gas_porosity": 0.10,
            "inclusion": 0.20,
            "cold_shut": 0.05,
            "misrun": 0.03,
            "mold_line": 0.25,
        },
        "overall_defect_rate": 0.42,
        "dimensional_accuracy_mm": 2.0,
        "surface_roughness_ra": 18.0,
        "minimum_wall_thickness_mm": 4.0,
        "max_complexity_score": 55,
        "historical_experiment_validation": {
            "restored_defect_rate": "8-15%（复原铸造实验）",
            "measured_surface_roughness": "Ra 12.5-25 μm（司母戊鼎实测）",
            "wall_thickness_min_record": "3.0 mm（商晚期中型鼎）",
            "dimensional_tolerance": "±1.0-2.0 mm（合范装配误差）",
        },
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
        "archaeological_sources": ["bronze_casting_history", "investment_casting_comparison"],
        "measured_data_remark": "基于曾侯乙编钟的分铸焊接工艺分析",
        "typical_defects": [
            "装配误差",
            "焊接缺陷",
            "缩孔",
            "应力变形",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.12,
            "shrinkage_porosity": 0.25,
            "gas_porosity": 0.12,
            "inclusion": 0.15,
            "cold_shut": 0.08,
            "misrun": 0.05,
            "assembly_error": 0.15,
            "welding_defect": 0.10,
        },
        "overall_defect_rate": 0.38,
        "dimensional_accuracy_mm": 1.2,
        "surface_roughness_ra": 12.5,
        "minimum_wall_thickness_mm": 2.5,
        "max_complexity_score": 98,
        "historical_experiment_validation": {
            "restored_defect_rate": "5-10%（单件铸造+装配综合）",
            "measured_surface_roughness": "Ra 6.3-12.5 μm（曾侯乙编钟实测）",
            "wall_thickness_min_record": "2.0 mm（曾侯乙编钟钟枚）",
            "dimensional_tolerance": "±0.5-1.2 mm（单部件精度）",
        },
    },
}


NATIONAL_STANDARDS = {
    "gb_t_14235": {
        "citation": "GB/T 14235.1-2008 熔模铸造 第1部分：尺寸公差和机加工余量",
        "description": "熔模铸件尺寸公差等级 CT4-CT15 的国家标准",
        "equivalent_to": "ISO 8062-3:2007",
    },
    "gb_t_15056": {
        "citation": "GB/T 15056-2017 铸造表面粗糙度 评定方法",
        "description": "铸件表面粗糙度比较样块和测量方法标准",
        "equivalent_to": "ISO 10049:2007",
    },
    "iso_8062": {
        "citation": "ISO 8062:2007 铸件 尺寸公差、几何公差与机加工余量",
        "description": "国际铸件尺寸公差标准，熔模精密铸造对应 CT4-CT6",
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
        "standard_compliance": {
            "dimensional_tolerance_standard": "GB/T 14235.1-2008 / ISO 8062",
            "surface_roughness_standard": "GB/T 15056-2017 / ISO 10049",
            "ct_grade_range": "CT4 ~ CT6",
            "application_notes": "CT4用于高精度航空航天件，CT5为通用精密件，CT6为普通熔模铸件",
        },
        "typical_defects": [
            "针孔",
            "缩松",
            "夹杂",
            "变形",
        ],
        "defect_rates": {
            "shrinkage_cavity": 0.02,
            "shrinkage_porosity": 0.06,
            "gas_porosity": 0.025,
            "inclusion": 0.03,
            "cold_shut": 0.01,
            "misrun": 0.005,
        },
        "overall_defect_rate": 0.065,
        "dimensional_accuracy_mm": 0.3,
        "surface_roughness_ra": 1.6,
        "minimum_wall_thickness_mm": 0.5,
        "max_complexity_score": 98,
        "standard_specific_parameters": {
            "silica_sol_process": {
                "description": "硅溶胶型壳工艺（高精度级）",
                "ct_grade": "CT4 ~ CT5",
                "surface_roughness_ra": "0.8 ~ 3.2 μm",
                "dimensional_accuracy_100mm": "±0.15 ~ ±0.30 mm",
                "typical_wall_thickness": "1.0 ~ 3.0 mm",
            },
            "sodium_silicate_process": {
                "description": "水玻璃型壳工艺（经济型）",
                "ct_grade": "CT5 ~ CT6",
                "surface_roughness_ra": "3.2 ~ 6.3 μm",
                "dimensional_accuracy_100mm": "±0.30 ~ ±0.50 mm",
                "typical_wall_thickness": "2.0 ~ 5.0 mm",
            },
        },
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
