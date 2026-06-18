import { useEffect, useState, useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { craftsApi, type CraftInfo, type AncientVsModernResult } from "@/lib/api";
import { Scale, Clock, ShieldAlert, Gauge, Layers, Sparkles } from "lucide-react";

const craftColors: Record<string, string> = {
  lost_wax: "#d4af37",
  piece_mold: "#8b7355",
  sectional_casting: "#cd853f",
  modern_investment_casting: "#4a90d9",
};

const defectNameMap: Record<string, string> = {
  shrinkage_cavity: "缩孔",
  shrinkage_porosity: "缩松",
  gas_porosity: "气孔",
  inclusion: "夹杂",
  cold_shut: "冷隔",
  misrun: "浇不足",
  assembly_error: "装配误差",
  welding_defect: "焊接缺陷",
};

export default function CraftComparisonPage() {
  const [ancientCrafts, setAncientCrafts] = useState<CraftInfo[]>([]);
  const [vsModern, setVsModern] = useState<AncientVsModernResult | null>(null);
  const [selectedCrafts, setSelectedCrafts] = useState<string[]>(["lost_wax", "piece_mold", "sectional_casting"]);
  const [activeTab, setActiveTab] = useState<"ancient" | "vs-modern">("ancient");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [ancient, vsMod] = await Promise.all([
          craftsApi.getAncientCrafts(),
          craftsApi.getAncientVsModern(),
        ]);
        setAncientCrafts(ancient);
        setVsModern(vsMod);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const toggleCraft = (craftId: string) => {
    setSelectedCrafts((prev) =>
      prev.includes(craftId)
        ? prev.filter((id) => id !== craftId)
        : [...prev, craftId]
    );
  };

  const selectedCraftData = useMemo(
    () => ancientCrafts.filter((c) => selectedCrafts.includes(c.id)),
    [ancientCrafts, selectedCrafts]
  );

  const defectRadarOption = useMemo(() => {
    const allDefectTypes = new Set<string>();
    selectedCraftData.forEach((c) => Object.keys(c.defect_rates).forEach((d) => allDefectTypes.add(d)));
    const indicators = Array.from(allDefectTypes).map((d) => ({
      name: defectNameMap[d] || d,
      max: 40,
    }));

    const series = selectedCraftData.map((craft) => ({
      name: craft.name,
      value: indicators.map((ind) => {
        const defectKey = Object.keys(defectNameMap).find((k) => defectNameMap[k] === ind.name) || "";
        return (craft.defect_rates[defectKey] || 0) * 100;
      }),
      lineStyle: { color: craftColors[craft.id] || "#d4af37", width: 2 },
      itemStyle: { color: craftColors[craft.id] || "#d4af37" },
      areaStyle: {
        color: craftColors[craft.id] + "30",
      },
    }));

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(13,13,20,0.92)",
        borderColor: "#b87333",
        textStyle: { color: "#e8d5a3" },
      },
      legend: {
        data: selectedCraftData.map((c) => c.name),
        textStyle: { color: "#d4af37", fontSize: 12 },
        top: 0,
      },
      radar: {
        indicator: indicators,
        axisName: { color: "#c9b27a", fontSize: 11 },
        splitLine: { lineStyle: { color: "rgba(184,115,51,0.15)" } },
        splitArea: {
          areaStyle: { color: ["rgba(184,115,51,0.03)", "rgba(184,115,51,0.06)"] },
        },
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        center: ["50%", "55%"],
        radius: "65%",
      },
      series: [{ type: "radar", data: series }],
    };
  }, [selectedCraftData]);

  const metricBarOption = useMemo(() => {
    const metrics = [
      { key: "overall_defect_rate", label: "缺陷率", unit: "%", multiplier: 100, lowerBetter: true },
      { key: "dimensional_accuracy_mm", label: "尺寸精度", unit: "mm", multiplier: 1, lowerBetter: true },
      { key: "surface_roughness_ra", label: "表面粗糙度", unit: "μm", multiplier: 1, lowerBetter: true },
      { key: "minimum_wall_thickness_mm", label: "最小壁厚", unit: "mm", multiplier: 1, lowerBetter: true },
      { key: "max_complexity_score", label: "复杂度评分", unit: "分", multiplier: 1, lowerBetter: false },
      { key: "production_cycle_days", label: "生产周期", unit: "天", multiplier: 1, lowerBetter: true },
    ];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(13,13,20,0.92)",
        borderColor: "#b87333",
        textStyle: { color: "#e8d5a3" },
      },
      legend: {
        data: selectedCraftData.map((c) => c.name),
        textStyle: { color: "#d4af37", fontSize: 12 },
        top: 0,
      },
      grid: { left: 56, right: 20, top: 40, bottom: 60 },
      xAxis: {
        type: "category",
        data: metrics.map((m) => m.label),
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        axisLabel: { color: "#c9b27a", fontSize: 11, rotate: 20 },
      },
      yAxis: {
        type: "value",
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        splitLine: { lineStyle: { color: "rgba(184,115,51,0.08)" } },
        axisLabel: { color: "#c9b27a", fontSize: 10 },
      },
      series: selectedCraftData.map((craft) => ({
        name: craft.name,
        type: "bar",
        data: metrics.map((m) => (craft[m.key as keyof CraftInfo] as number) * m.multiplier),
        itemStyle: {
          color: craftColors[craft.id] || "#d4af37",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: Math.max(8, 32 / selectedCraftData.length),
      })),
    };
  }, [selectedCraftData]);

  const vsModernBarOption = useMemo(() => {
    if (!vsModern) return null;

    const allCrafts = [...vsModern.ancient_crafts, ...vsModern.modern_crafts];
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(13,13,20,0.92)",
        borderColor: "#b87333",
        textStyle: { color: "#e8d5a3" },
        axisPointer: { type: "shadow" },
      },
      grid: { left: 120, right: 40, top: 20, bottom: 30 },
      xAxis: {
        type: "value",
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        splitLine: { lineStyle: { color: "rgba(184,115,51,0.08)" } },
        axisLabel: { color: "#c9b27a", fontSize: 10 },
      },
      yAxis: {
        type: "category",
        data: allCrafts.map((c) => c.name),
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        axisLabel: { color: "#c9b27a", fontSize: 12 },
      },
      series: [
        {
          name: "综合缺陷率 (%)",
          type: "bar",
          data: allCrafts.map((c) => ({
            value: (c.overall_defect_rate * 100).toFixed(1),
            itemStyle: {
              color: craftColors[c.id] || "#d4af37",
              borderRadius: [0, 4, 4, 0],
            },
          })),
          label: {
            show: true,
            position: "right",
            color: "#d4af37",
            fontSize: 12,
            formatter: "{c}%",
          },
          barWidth: 24,
        },
      ],
    };
  }, [vsModern]);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-amber-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="mb-6">
        <h1 className="mb-2 font-serif text-2xl font-bold text-amber-300">铸造工艺对比分析</h1>
        <p className="text-sm text-amber-500/70">
          对比不同古代铸造工艺的缺陷率、精度、复杂度等核心指标，探索古代匠人的智慧
        </p>
      </div>

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setActiveTab("ancient")}
          className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
            activeTab === "ancient"
              ? "bg-gradient-to-r from-amber-700/40 to-amber-900/20 text-amber-200 shadow-[inset_0_-2px_0_0_#d4af37]"
              : "border border-amber-800/40 text-amber-400/70 hover:border-amber-600/50 hover:text-amber-300"
          }`}
        >
          <Scale className="mr-2 inline h-4 w-4" />
          古代工艺对比
        </button>
        <button
          onClick={() => setActiveTab("vs-modern")}
          className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
            activeTab === "vs-modern"
              ? "bg-gradient-to-r from-amber-700/40 to-amber-900/20 text-amber-200 shadow-[inset_0_-2px_0_0_#d4af37]"
              : "border border-amber-800/40 text-amber-400/70 hover:border-amber-600/50 hover:text-amber-300"
          }`}
        >
          <Clock className="mr-2 inline h-4 w-4" />
          古今精度对比
        </button>
      </div>

      {activeTab === "ancient" && (
        <>
          <div className="mb-5 flex flex-wrap gap-3">
            {ancientCrafts.map((craft) => (
              <button
                key={craft.id}
                onClick={() => toggleCraft(craft.id)}
                className={`rounded-lg border px-4 py-2.5 text-sm transition-all ${
                  selectedCrafts.includes(craft.id)
                    ? "border-amber-500/60 bg-amber-900/20 text-amber-200"
                    : "border-amber-900/40 text-amber-500/70 hover:border-amber-700/50"
                }`}
              >
                <span
                  className="mr-2 inline-block h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: craftColors[craft.id] }}
                />
                {craft.name}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-5 xl:grid-cols-4">
            {selectedCraftData.map((craft) => (
              <div
                key={craft.id}
                className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-4"
              >
                <div className="mb-2 flex items-center gap-2">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: craftColors[craft.id] }}
                  />
                  <h3 className="font-serif text-lg font-semibold text-amber-200">{craft.name}</h3>
                </div>
                <p className="mb-3 text-xs text-amber-500/60">{craft.english_name}</p>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-amber-500/60">年代</span>
                    <span className="text-amber-300">{craft.dynasty}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-amber-500/60">缺陷率</span>
                    <span className="font-mono text-amber-300">
                      {(craft.overall_defect_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-amber-500/60">尺寸精度</span>
                    <span className="font-mono text-amber-300">
                      {craft.dimensional_accuracy_mm}mm
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-amber-500/60">复杂度</span>
                    <span className="font-mono text-amber-300">{craft.max_complexity_score}分</span>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-amber-900/20">
                  <p className="text-xs text-amber-400/60 leading-relaxed">{craft.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-2">
            <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
              <h3 className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
                <ShieldAlert className="h-5 w-5" />
                缺陷雷达图
              </h3>
              <div className="h-[380px]">
                <ReactECharts option={defectRadarOption} style={{ height: "100%" }} />
              </div>
            </div>

            <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
              <h3 className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
                <Gauge className="h-5 w-5" />
                核心指标对比
              </h3>
              <div className="h-[380px]">
                <ReactECharts option={metricBarOption} style={{ height: "100%" }} />
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-amber-900/30 bg-black/30 p-5">
            <h3 className="mb-4 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
              <Sparkles className="h-5 w-5" />
              各工艺详细对比
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-amber-900/40">
                    <th className="px-3 py-2 text-left text-amber-400/80">指标</th>
                    {selectedCraftData.map((c) => (
                      <th
                        key={c.id}
                        className="px-3 py-2 text-center font-medium"
                        style={{ color: craftColors[c.id] }}
                      >
                        {c.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-amber-200/80">
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">综合缺陷率</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {(c.overall_defect_rate * 100).toFixed(1)}%
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">尺寸精度</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {c.dimensional_accuracy_mm} mm
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">表面粗糙度 Ra</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {c.surface_roughness_ra} μm
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">最小壁厚</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {c.minimum_wall_thickness_mm} mm
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">最高复杂度</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {c.max_complexity_score} 分
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">生产周期</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center font-mono">
                        {c.production_cycle_days} 天
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-amber-900/20">
                    <td className="px-3 py-2 text-amber-400/70">工艺复杂度</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center">
                        {"★".repeat(c.complexity)}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-3 py-2 text-amber-400/70">技艺要求</td>
                    {selectedCraftData.map((c) => (
                      <td key={c.id} className="px-3 py-2 text-center">
                        {"★".repeat(c.skill_required)}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {activeTab === "vs-modern" && vsModern && (
        <>
          <div className="mb-6 grid grid-cols-3 gap-4">
            <div className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/15 to-black/30 p-5">
              <div className="mb-1 text-xs text-amber-500/60">古代平均缺陷率</div>
              <div className="font-mono text-3xl font-bold text-amber-300">
                {vsModern.summary.avg_ancient_defect_rate}%
              </div>
              <div className="mt-1 text-xs text-amber-500/50">
                失蜡法 / 范铸法 / 分铸法
              </div>
            </div>
            <div className="rounded-xl border border-emerald-700/40 bg-gradient-to-br from-emerald-900/20 to-black/30 p-5">
              <div className="mb-1 text-xs text-emerald-400/70">现代平均缺陷率</div>
              <div className="font-mono text-3xl font-bold text-emerald-300">
                {vsModern.summary.avg_modern_defect_rate}%
              </div>
              <div className="mt-1 text-xs text-emerald-400/50">
                现代熔模精密铸造
              </div>
            </div>
            <div className="rounded-xl border border-blue-700/40 bg-gradient-to-br from-blue-900/20 to-black/30 p-5">
              <div className="mb-1 text-xs text-blue-400/70">缺陷率降低</div>
              <div className="font-mono text-3xl font-bold text-blue-300">
                {vsModern.summary.defect_reduction_percent}%
              </div>
              <div className="mt-1 text-xs text-blue-400/50">
                工艺进步带来的质量提升
              </div>
            </div>
          </div>

          <div className="mb-6 grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-5">
              <div className="mb-1 text-xs text-amber-500/60">古代平均尺寸精度</div>
              <div className="font-mono text-2xl font-bold text-amber-300">
                {vsModern.summary.avg_ancient_accuracy_mm} mm
              </div>
            </div>
            <div className="rounded-xl border border-emerald-700/40 bg-gradient-to-br from-emerald-900/15 to-black/30 p-5">
              <div className="mb-1 text-xs text-emerald-400/70">现代平均尺寸精度</div>
              <div className="font-mono text-2xl font-bold text-emerald-300">
                {vsModern.summary.avg_modern_accuracy_mm} mm
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
            <h3 className="mb-3 font-serif text-lg font-semibold text-amber-300">
              <Layers className="mr-2 inline h-5 w-5" />
              各工艺缺陷率对比
            </h3>
            <div className="h-[320px]">
              {vsModernBarOption && (
                <ReactECharts option={vsModernBarOption} style={{ height: "100%" }} />
              )}
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-5">
            <h3 className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
              <Sparkles className="h-5 w-5" />
              跨时代工艺洞察
            </h3>
            <div className="grid gap-3 md:grid-cols-2">
              {vsModern.key_insights.map((insight, idx) => (
                <div
                  key={idx}
                  className="flex gap-3 rounded-lg border border-amber-800/20 bg-black/20 p-3"
                >
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-700/30 text-sm font-bold text-amber-300">
                    {idx + 1}
                  </div>
                  <p className="text-sm text-amber-200/80">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
