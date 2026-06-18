import { useEffect, useState, useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { permeabilityApi, type PermeabilityImpactResult } from "@/lib/api";
import { Wind, Droplets, AlertTriangle, TrendingUp, Thermometer, Layers } from "lucide-react";

const alloyOptions = [
  { value: "bronze", label: "青铜 Cu-Sn", temp: 1180 },
  { value: "brass", label: "黄铜 Cu-Zn", temp: 1060 },
  { value: "steel", label: "不锈钢 304", temp: 1580 },
  { value: "aluminum", label: "铝合金 A356", temp: 720 },
];

export default function PermeabilityAnalysisPage() {
  const [data, setData] = useState<PermeabilityImpactResult | null>(null);
  const [alloyType, setAlloyType] = useState("bronze");
  const [pouringTemp, setPouringTemp] = useState(1180);
  const [shellThickness, setShellThickness] = useState(9);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const result = await permeabilityApi.analyzeImpact(alloyType, pouringTemp, shellThickness);
        setData(result);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [alloyType, pouringTemp, shellThickness]);

  const handleAlloyChange = (value: string) => {
    setAlloyType(value);
    const opt = alloyOptions.find((o) => o.value === value);
    if (opt) setPouringTemp(opt.temp);
  };

  const qualityChartOption = useMemo(() => {
    if (!data) return {};
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(13,13,20,0.92)",
        borderColor: "#b87333",
        textStyle: { color: "#e8d5a3" },
      },
      legend: {
        data: ["充型质量", "充型速度", "缺陷率"],
        textStyle: { color: "#d4af37", fontSize: 12 },
        top: 0,
      },
      grid: { left: 48, right: 56, top: 36, bottom: 28 },
      xAxis: {
        type: "category",
        name: "型壳透气性 (%)",
        data: data.permeability_values,
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        axisLabel: { color: "#c9b27a", fontSize: 10 },
        nameTextStyle: { color: "#d4af37" },
      },
      yAxis: [
        {
          type: "value",
          name: "质量/速度 (分)",
          max: 100,
          axisLine: { lineStyle: { color: "#5a4a2a" } },
          splitLine: { lineStyle: { color: "rgba(184,115,51,0.08)" } },
          axisLabel: { color: "#c9b27a", fontSize: 10 },
          nameTextStyle: { color: "#d4af37" },
        },
        {
          type: "value",
          name: "缺陷率 (%)",
          max: 50,
          axisLine: { lineStyle: { color: "#5a4a2a" } },
          splitLine: { show: false },
          axisLabel: { color: "#c9b27a", fontSize: 10 },
          nameTextStyle: { color: "#d4af37" },
        },
      ],
      series: [
        {
          name: "充型质量",
          type: "line",
          smooth: true,
          data: data.filling_quality_scores,
          lineStyle: { color: "#d4af37", width: 2.5 },
          itemStyle: { color: "#d4af37" },
          areaStyle: {
            color: {
              type: "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(212,175,55,0.3)" },
                { offset: 1, color: "rgba(212,175,55,0)" },
              ],
            },
          },
        },
        {
          name: "充型速度",
          type: "line",
          smooth: true,
          data: data.filling_speed_scores,
          lineStyle: { color: "#4a90d9", width: 2 },
          itemStyle: { color: "#4a90d9" },
        },
        {
          name: "缺陷率",
          type: "line",
          yAxisIndex: 1,
          smooth: true,
          data: data.defect_rates_percent,
          lineStyle: { color: "#e63946", width: 2.5, type: "dashed" },
          itemStyle: { color: "#e63946" },
        },
      ],
    };
  }, [data]);

  const defectChartOption = useMemo(() => {
    if (!data) return {};
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(13,13,20,0.92)",
        borderColor: "#b87333",
        textStyle: { color: "#e8d5a3" },
      },
      legend: {
        data: ["气孔率", "缩松缩孔率"],
        textStyle: { color: "#d4af37", fontSize: 12 },
        top: 0,
      },
      grid: { left: 48, right: 20, top: 36, bottom: 28 },
      xAxis: {
        type: "category",
        name: "型壳透气性 (%)",
        data: data.permeability_values,
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        axisLabel: { color: "#c9b27a", fontSize: 10 },
        nameTextStyle: { color: "#d4af37" },
      },
      yAxis: {
        type: "value",
        name: "缺陷率 (%)",
        axisLine: { lineStyle: { color: "#5a4a2a" } },
        splitLine: { lineStyle: { color: "rgba(184,115,51,0.08)" } },
        axisLabel: { color: "#c9b27a", fontSize: 10 },
        nameTextStyle: { color: "#d4af37" },
      },
      series: [
        {
          name: "气孔率",
          type: "line",
          smooth: true,
          data: data.gas_porosity_rates_percent,
          lineStyle: { color: "#ff8a3d", width: 2.5 },
          itemStyle: { color: "#ff8a3d" },
          areaStyle: {
            color: {
              type: "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(255,138,61,0.25)" },
                { offset: 1, color: "rgba(255,138,61,0)" },
              ],
            },
          },
        },
        {
          name: "缩松缩孔率",
          type: "line",
          smooth: true,
          data: data.shrinkage_rates_percent,
          lineStyle: { color: "#9b59b6", width: 2.5 },
          itemStyle: { color: "#9b59b6" },
          areaStyle: {
            color: {
              type: "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(155,89,182,0.25)" },
                { offset: 1, color: "rgba(155,89,182,0)" },
              ],
            },
          },
        },
      ],
    };
  }, [data]);

  if (loading || !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-amber-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="mb-6">
        <h1 className="mb-2 font-serif text-2xl font-bold text-amber-300">
          <Wind className="mr-3 inline h-7 w-7" />
          型壳透气性影响分析
        </h1>
        <p className="text-sm text-amber-500/70">
          分析型壳透气性对充型质量、缺陷率和充型速度的影响规律
        </p>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-amber-900/30 bg-black/30 p-4">
          <label className="mb-2 block text-xs text-amber-400/70">合金类型</label>
          <select
            value={alloyType}
            onChange={(e) => handleAlloyChange(e.target.value)}
            className="w-full rounded-lg border border-amber-800/40 bg-black/40 px-3 py-2 text-sm text-amber-200 focus:border-amber-500 focus:outline-none"
          >
            {alloyOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="rounded-xl border border-amber-900/30 bg-black/30 p-4">
          <label className="mb-2 flex justify-between text-xs text-amber-400/70">
            <span>浇铸温度</span>
            <span className="font-mono text-amber-300">{pouringTemp}°C</span>
          </label>
          <input
            type="range"
            min={700}
            max={1650}
            step={10}
            value={pouringTemp}
            onChange={(e) => setPouringTemp(Number(e.target.value))}
            className="w-full accent-amber-500"
          />
        </div>

        <div className="rounded-xl border border-amber-900/30 bg-black/30 p-4">
          <label className="mb-2 flex justify-between text-xs text-amber-400/70">
            <span>型壳层数</span>
            <span className="font-mono text-amber-300">{shellThickness} 层</span>
          </label>
          <input
            type="range"
            min={3}
            max={15}
            step={1}
            value={shellThickness}
            onChange={(e) => setShellThickness(Number(e.target.value))}
            className="w-full accent-amber-500"
          />
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/15 to-black/30 p-4">
          <div className="mb-1 flex items-center gap-2 text-xs text-amber-500/60">
            <TrendingUp className="h-3.5 w-3.5" />
            最佳质量透气性
          </div>
          <div className="font-mono text-2xl font-bold text-amber-300">
            {data.analysis.best_quality_permeability}%
          </div>
          <div className="mt-1 text-xs text-amber-500/50">
            质量评分 {data.analysis.best_quality_score}
          </div>
        </div>

        <div className="rounded-xl border border-emerald-700/40 bg-gradient-to-br from-emerald-900/15 to-black/30 p-4">
          <div className="mb-1 flex items-center gap-2 text-xs text-emerald-400/70">
            <AlertTriangle className="h-3.5 w-3.5" />
            最低缺陷率
          </div>
          <div className="font-mono text-2xl font-bold text-emerald-300">
            {data.analysis.lowest_defect_rate}%
          </div>
          <div className="mt-1 text-xs text-emerald-400/50">
            @ {data.analysis.lowest_defect_permeability}% 透气性
          </div>
        </div>

        <div className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-4">
          <div className="mb-1 flex items-center gap-2 text-xs text-amber-500/60">
            <Thermometer className="h-3.5 w-3.5" />
            基准浇铸温度
          </div>
          <div className="font-mono text-2xl font-bold text-amber-300">
            {data.parameters.pouring_temp}°C
          </div>
          <div className="mt-1 text-xs text-amber-500/50">
            {data.parameters.alloy_type}
          </div>
        </div>

        <div className="rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-4">
          <div className="mb-1 flex items-center gap-2 text-xs text-amber-500/60">
            <Layers className="h-3.5 w-3.5" />
            型壳层数
          </div>
          <div className="font-mono text-2xl font-bold text-amber-300">
            {data.parameters.shell_thickness_layers} 层
          </div>
          <div className="mt-1 text-xs text-amber-500/50">
            最优透气 {data.parameters.optimal_permeability}%
          </div>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
          <h3 className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
            <Droplets className="h-5 w-5" />
            充型质量与缺陷率曲线
          </h3>
          <div className="h-[340px]">
            <ReactECharts option={qualityChartOption} style={{ height: "100%" }} />
          </div>
        </div>

        <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
          <h3 className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-amber-300">
            <AlertTriangle className="h-5 w-5" />
            各类缺陷变化趋势
          </h3>
          <div className="h-[340px]">
            <ReactECharts option={defectChartOption} style={{ height: "100%" }} />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-amber-900/30 bg-black/30 p-5">
        <h3 className="mb-4 font-serif text-lg font-semibold text-amber-300">
          <Wind className="mr-2 inline h-5 w-5" />
          型壳材料对比
        </h3>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {data.shell_materials_comparison.map((mat, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-amber-800/25 bg-gradient-to-br from-amber-900/10 to-black/30 p-4"
            >
              <h4 className="mb-2 font-medium text-amber-200">{mat.name}</h4>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-amber-500/60">透气性</span>
                  <span className="font-mono text-amber-300">{mat.permeability}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-500/60">强度</span>
                  <span className="text-amber-300">
                    {mat.strength === "very_high"
                      ? "极高"
                      : mat.strength === "high"
                        ? "高"
                        : mat.strength === "medium"
                          ? "中"
                          : "低"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-500/60">表面质量</span>
                  <span className="font-mono text-amber-300">{mat.surface_quality}分</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-amber-500/60">成本等级</span>
                  <span className="text-amber-300">{"¥".repeat(mat.cost)}</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="mb-1 h-1.5 w-full rounded-full bg-amber-950/50">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-amber-600 to-amber-400"
                    style={{ width: `${mat.permeability}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-amber-900/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-5">
        <h3 className="mb-4 font-serif text-lg font-semibold text-amber-300">
          <Droplets className="mr-2 inline h-5 w-5" />
          工艺洞察
        </h3>
        <div className="grid gap-3 md:grid-cols-2">
          {data.insights.map((insight, idx) => (
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
    </div>
  );
}
