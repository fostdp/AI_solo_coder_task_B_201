from typing import Dict, Any, List
from process_comparator.crafts_data import (
    get_ancient_crafts,
    get_modern_crafts,
    ANCIENT_CRAFTS,
    MODERN_CRAFTS,
    ARCHAEOLOGICAL_SOURCES,
    NATIONAL_STANDARDS,
)


ERA_INFO: Dict[str, Dict[str, Any]] = {
    "ancient": {
        "id": "ancient",
        "name": "古代",
        "english_name": "Ancient China",
        "period": "约公元前1600年 - 公元1911年",
        "description": "中国古代青铜铸造时期，以失蜡法、范铸法、分铸法为代表工艺",
        "key_technologies": [
            "失蜡法精密铸造",
            "范铸法批量生产",
            "分铸法组装复杂器物",
            "错金银镶嵌工艺",
        ],
        "representative_artifacts": [
            "曾侯乙尊盘",
            "司母戊鼎",
            "四羊方尊",
            "莲鹤方壶",
        ],
        "craftsmanship_level": "手工技艺巅峰",
        "quality_control": "依赖工匠经验",
    },
    "modern": {
        "id": "modern",
        "name": "现代",
        "english_name": "Modern Industry",
        "period": "20世纪至今",
        "description": "现代熔模精密铸造时期，采用硅溶胶、真空浇铸等先进技术",
        "key_technologies": [
            "硅溶胶型壳工艺",
            "真空感应熔炼",
            "计算机数值模拟",
            "3D打印蜡模",
        ],
        "representative_applications": [
            "航空航天涡轮叶片",
            "医疗器械植入件",
            "精密机械零件",
            "汽车工业部件",
        ],
        "craftsmanship_level": "数字化精准控制",
        "quality_control": "自动化检测 + 统计过程控制",
    },
}


def get_era_info(era_id: str) -> Dict[str, Any] | None:
    return ERA_INFO.get(era_id)


def get_all_eras() -> List[Dict[str, Any]]:
    return list(ERA_INFO.values())


def ancient_vs_modern_comparison() -> Dict[str, Any]:
    ancient = get_ancient_crafts()
    modern = get_modern_crafts()

    avg_ancient_defect = sum(c["overall_defect_rate"] for c in ancient) / len(ancient) if ancient else 0
    avg_modern_defect = sum(c["overall_defect_rate"] for c in modern) / len(modern) if modern else 0

    avg_ancient_accuracy = sum(c["dimensional_accuracy_mm"] for c in ancient) / len(ancient) if ancient else 0
    avg_modern_accuracy = sum(c["dimensional_accuracy_mm"] for c in modern) / len(modern) if modern else 0

    accuracy_improvement = (avg_ancient_accuracy / avg_modern_accuracy) if avg_modern_accuracy > 0 else 0
    defect_reduction = (avg_ancient_defect - avg_modern_defect) / avg_ancient_defect * 100 if avg_ancient_defect > 0 else 0

    avg_ancient_roughness = sum(c["surface_roughness_ra"] for c in ancient) / len(ancient) if ancient else 0
    avg_modern_roughness = sum(c["surface_roughness_ra"] for c in modern) / len(modern) if modern else 0
    roughness_improvement = (avg_ancient_roughness / avg_modern_roughness) if avg_modern_roughness > 0 else 0

    avg_ancient_wall = min(c["minimum_wall_thickness_mm"] for c in ancient) if ancient else 0
    avg_modern_wall = min(c["minimum_wall_thickness_mm"] for c in modern) if modern else 0
    wall_thinning_factor = (avg_ancient_wall / avg_modern_wall) if avg_modern_wall > 0 else 0

    return {
        "ancient_crafts": ancient,
        "modern_crafts": modern,
        "ancient_era": get_era_info("ancient"),
        "modern_era": get_era_info("modern"),
        "summary": {
            "avg_ancient_defect_rate": round(avg_ancient_defect * 100, 2),
            "avg_modern_defect_rate": round(avg_modern_defect * 100, 2),
            "defect_reduction_percent": round(defect_reduction, 2),
            "avg_ancient_accuracy_mm": round(avg_ancient_accuracy, 3),
            "avg_modern_accuracy_mm": round(avg_modern_accuracy, 3),
            "accuracy_improvement_factor": round(accuracy_improvement, 1),
            "avg_ancient_roughness_ra": round(avg_ancient_roughness, 2),
            "avg_modern_roughness_ra": round(avg_modern_roughness, 2),
            "roughness_improvement_factor": round(roughness_improvement, 1),
            "ancient_min_wall_thickness_mm": round(avg_ancient_wall, 2),
            "modern_min_wall_thickness_mm": round(avg_modern_wall, 2),
            "wall_thinning_factor": round(wall_thinning_factor, 1),
        },
        "detailed_comparison": {
            "defect_rate": {
                "ancient": round(avg_ancient_defect * 100, 2),
                "modern": round(avg_modern_defect * 100, 2),
                "improvement": f"降低约 {defect_reduction:.1f}%",
                "unit": "%",
            },
            "dimensional_accuracy": {
                "ancient": round(avg_ancient_accuracy, 2),
                "modern": round(avg_modern_accuracy, 2),
                "improvement": f"提升约 {accuracy_improvement:.1f} 倍",
                "unit": "mm",
            },
            "surface_roughness": {
                "ancient": round(avg_ancient_roughness, 1),
                "modern": round(avg_modern_roughness, 1),
                "improvement": f"提升约 {roughness_improvement:.1f} 倍",
                "unit": "μm (Ra)",
            },
        },
        "key_insights": [
            f"现代熔模铸造的缺陷率比古代失蜡法降低约 {defect_reduction:.1f}%",
            f"尺寸精度提升约 {accuracy_improvement:.1f} 倍（从 {avg_ancient_accuracy:.2f}mm 到 {avg_modern_accuracy:.2f}mm）",
            f"表面粗糙度提升约 {roughness_improvement:.1f} 倍（从 Ra {avg_ancient_roughness:.1f} 到 Ra {avg_modern_roughness:.1f} μm）",
            "古代工艺受限于手工技艺和自然条件，成品率波动较大",
            "现代工艺借助真空浇铸、温控炉等设备，大幅提升一致性",
        ],
        "technological_evolution": [
            {
                "aspect": "制模工艺",
                "ancient": "手工雕刻蜡模 / 压型",
                "modern": "3D打印蜡模 / 金属模具注射",
                "impact": "精度和复杂度大幅提升",
            },
            {
                "aspect": "型壳材料",
                "ancient": "泥范 / 石膏型",
                "modern": "硅溶胶 / 硅酸乙酯 + 锆英砂",
                "impact": "透气性和表面质量显著改善",
            },
            {
                "aspect": "熔化设备",
                "ancient": "木炭炉 / 坩埚",
                "modern": "真空感应炉 / 中频炉",
                "impact": "温度精确可控，合金成分稳定",
            },
            {
                "aspect": "质量检测",
                "ancient": "目视检查 / 经验判断",
                "modern": "X射线探伤 / 三坐标测量 / 超声波",
                "impact": "缺陷检出率大幅提高",
            },
        ],
    }
