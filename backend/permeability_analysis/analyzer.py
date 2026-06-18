import numpy as np
from typing import Dict, Any, List, Tuple


PERMEABILITY_RANGE = {
    "min": 10.0,
    "max": 85.0,
    "step": 5.0,
}


def calculate_permeability_impact(
    alloy_type: str = "bronze",
    pouring_temp: float = 1180.0,
    shell_thickness: int = 9,
) -> Dict[str, Any]:
    perm_values = np.arange(
        PERMEABILITY_RANGE["min"],
        PERMEABILITY_RANGE["max"] + PERMEABILITY_RANGE["step"],
        PERMEABILITY_RANGE["step"],
    )

    filling_quality = []
    defect_rates = []
    gas_porosity = []
    shrinkage = []
    filling_speed = []

    optimal_perm = 50.0
    optimal_temp = 1180.0

    temp_factor = 1.0
    if alloy_type in ("bronze", "zeng_houyi_bronze", "brass"):
        optimal_temp = 1180.0
    elif "steel" in alloy_type:
        optimal_temp = 1580.0
    elif "aluminum" in alloy_type:
        optimal_temp = 720.0
    temp_deviation = abs(pouring_temp - optimal_temp) / optimal_temp
    temp_factor = 1.0 + temp_deviation * 2.0

    thickness_factor = 9.0 / shell_thickness

    for perm in perm_values:
        perm_ratio = perm / optimal_perm

        fill_speed_score = 60.0 + 25.0 * perm_ratio
        fill_speed_score = min(100.0, fill_speed_score * thickness_factor)

        if perm < optimal_perm:
            fill_quality_base = 50.0 + 50.0 * (perm / optimal_perm)
        else:
            fill_quality_base = 100.0 - 15.0 * ((perm - optimal_perm) / (100.0 - optimal_perm))

        fill_quality = fill_quality_base / temp_factor
        fill_quality = max(20.0, min(98.0, fill_quality))

        gas_porosity_rate = 0.30 * np.exp(-0.045 * perm) * temp_factor
        gas_porosity_rate = min(0.5, max(0.02, gas_porosity_rate))

        if perm < optimal_perm:
            shrinkage_rate = 0.18 - 0.08 * (perm / optimal_perm)
        else:
            shrinkage_rate = 0.10 + 0.06 * ((perm - optimal_perm) / (100.0 - optimal_perm))
        shrinkage_rate *= temp_factor
        shrinkage_rate = max(0.03, min(0.4, shrinkage_rate))

        overall_defect = gas_porosity_rate * 0.4 + shrinkage_rate * 0.4 + (1.0 - fill_quality / 100.0) * 0.2
        overall_defect = min(0.6, max(0.05, overall_defect))

        filling_speed.append(round(fill_speed_score, 2))
        filling_quality.append(round(fill_quality, 2))
        gas_porosity.append(round(gas_porosity_rate * 100, 2))
        shrinkage.append(round(shrinkage_rate * 100, 2))
        defect_rates.append(round(overall_defect * 100, 2))

    perm_list = [round(float(p), 1) for p in perm_values]

    best_idx = int(np.argmax(filling_quality))
    worst_idx = int(np.argmin(filling_quality))

    min_defect_idx = int(np.argmin(defect_rates))

    return {
        "parameters": {
            "alloy_type": alloy_type,
            "pouring_temp": pouring_temp,
            "shell_thickness_layers": shell_thickness,
            "optimal_permeability": optimal_perm,
        },
        "permeability_values": perm_list,
        "filling_quality_scores": filling_quality,
        "filling_speed_scores": filling_speed,
        "defect_rates_percent": defect_rates,
        "gas_porosity_rates_percent": gas_porosity,
        "shrinkage_rates_percent": shrinkage,
        "analysis": {
            "best_quality_permeability": perm_list[best_idx],
            "best_quality_score": filling_quality[best_idx],
            "lowest_defect_permeability": perm_list[min_defect_idx],
            "lowest_defect_rate": defect_rates[min_defect_idx],
            "worst_quality_permeability": perm_list[worst_idx],
            "worst_quality_score": filling_quality[worst_idx],
        },
        "insights": [
            "透气性过低时，气体无法排出，易产生气孔缺陷，充型速度慢",
            "透气性过高时，散热过快，易产生缩孔缩松，型壳强度降低",
            f"该合金条件下最佳透气性约为 {optimal_perm:.0f}%",
            f"浇铸温度偏离最佳值 {optimal_temp:.0f}°C 越多，缺陷率越高",
            "型壳层数越多，透气性越低，但强度越高",
        ],
        "shell_materials_comparison": [
            {"name": "硅酸乙酯+锆英砂", "permeability": 65.0, "strength": "very_high", "cost": 5, "surface_quality": 90},
            {"name": "硅溶胶+石英砂", "permeability": 50.0, "strength": "high", "cost": 3, "surface_quality": 75},
            {"name": "水玻璃+石英砂", "permeability": 35.0, "strength": "medium", "cost": 2, "surface_quality": 60},
            {"name": "石膏型", "permeability": 20.0, "strength": "low", "cost": 1, "surface_quality": 85},
        ],
    }


def analyze_historical_data(casting_id: str) -> Dict[str, Any]:
    from common.mongo_client import get_db

    db = get_db()
    sensors = list(
        db.sensors.find({"casting_id": casting_id}, {"_id": 0})
        .sort("timestamp", 1)
        .limit(200)
    )

    if not sensors:
        return {"error": "No sensor data found for this casting", "casting_id": casting_id}

    perm_values = [s.get("shell_permeability", 0) for s in sensors]
    filling_progress = [s.get("filling_progress", 0) for s in sensors]
    pouring_temps = [s.get("pouring_temperature", 0) for s in sensors]

    avg_perm = sum(perm_values) / len(perm_values)
    min_perm = min(perm_values)
    max_perm = max(perm_values)

    defects = list(db.defects.find({"casting_id": casting_id}, {"_id": 0}))
    total_defect_volume = sum(d.get("volume", 0) for d in defects)
    defect_count = len(defects)

    quality_score = max(20.0, min(95.0, 100.0 - total_defect_volume * 3.0))

    return {
        "casting_id": casting_id,
        "data_points": len(sensors),
        "permeability_stats": {
            "average": round(avg_perm, 2),
            "min": round(min_perm, 2),
            "max": round(max_perm, 2),
            "fluctuation": round(max_perm - min_perm, 2),
        },
        "defect_stats": {
            "total_defects": defect_count,
            "total_volume_cm3": round(total_defect_volume, 3),
            "quality_score": round(quality_score, 1),
        },
        "correlation": {
            "permeability_vs_defect_correlation": round((avg_perm - 40) / 40 * 0.3 + 0.5, 3),
            "low_perm_period_count": sum(1 for p in perm_values if p < 35),
            "high_perm_period_count": sum(1 for p in perm_values if p > 65),
        },
        "recommendations": _generate_recommendations(avg_perm, total_defect_volume, defect_count),
    }


def _generate_recommendations(avg_perm: float, total_volume: float, defect_count: int) -> List[str]:
    recommendations = []

    if avg_perm < 35:
        recommendations.append("当前透气性偏低，建议增加型壳层数间的干燥时间")
        recommendations.append("可考虑使用透气性更好的型壳材料（如硅溶胶换为硅酸乙酯）")
    elif avg_perm > 65:
        recommendations.append("当前透气性偏高，需注意型壳强度是否足够")
        recommendations.append("高透气性可能导致散热过快，建议适当提高浇铸温度")
    else:
        recommendations.append("透气性处于较佳范围，继续保持当前工艺参数")

    if total_volume > 3.0:
        recommendations.append("缺陷总体积较大，建议优化浇铸系统和冒口设计")

    if defect_count > 10:
        recommendations.append("缺陷数量较多，建议排查型壳干燥工艺和浇铸速度")

    if not recommendations:
        recommendations.append("工艺参数良好，无需特殊调整")

    return recommendations


def compare_permeability_scenarios(
    scenarios: List[Dict[str, Any]],
) -> Dict[str, Any]:
    results = []
    for scenario in scenarios:
        result = calculate_permeability_impact(
            alloy_type=scenario.get("alloy_type", "bronze"),
            pouring_temp=scenario.get("pouring_temp", 1180.0),
            shell_thickness=scenario.get("shell_thickness", 9),
        )
        results.append({
            "scenario_name": scenario.get("name", f"Scenario {len(results)+1}"),
            "parameters": result["parameters"],
            "key_metrics": {
                "best_quality_permeability": result["analysis"]["best_quality_permeability"],
                "best_quality_score": result["analysis"]["best_quality_score"],
                "lowest_defect_rate": result["analysis"]["lowest_defect_rate"],
            },
        })

    return {
        "scenarios": results,
        "comparison": {
            "best_overall": min(results, key=lambda r: r["key_metrics"]["lowest_defect_rate"])["scenario_name"],
        },
    }
