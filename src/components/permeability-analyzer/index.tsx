import React, { useState, useEffect } from "react";
import * as echarts from "echarts";
import {
  permeabilityAnalyzerApi,
  PermeabilityImpactResult,
} from "../../lib/api";

interface PermeabilityAnalyzerProps {
  defaultAlloyType?: string;
  defaultPouringTemp?: number;
  defaultShellThickness?: number;
  onAnalysisComplete?: (result: PermeabilityImpactResult) => void;
}

const PermeabilityAnalyzer: React.FC<PermeabilityAnalyzerProps> = ({
  defaultAlloyType = "bronze",
  defaultPouringTemp = 1180,
  defaultShellThickness = 9,
  onAnalysisComplete,
}) => {
  const [alloyType, setAlloyType] = useState(defaultAlloyType);
  const [pouringTemp, setPouringTemp] = useState(defaultPouringTemp);
  const [shellThickness, setShellThickness] = useState(defaultShellThickness);
  const [result, setResult] = useState<PermeabilityImpactResult | null>(null);
  const [loading, setLoading] = useState(false);
  const chartRef = React.useRef<HTMLDivElement>(null);
  const chartInstance = React.useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    runAnalysis();
  }, [alloyType, pouringTemp, shellThickness]);

  useEffect(() => {
    if (chartRef.current && result) {
      renderChart();
    }
    return () => {
      chartInstance.current?.dispose();
    };
  }, [result]);

  const runAnalysis = async () => {
    try {
      setLoading(true);
      const data = await permeabilityAnalyzerApi.analyzeImpact(
        alloyType,
        pouringTemp,
        shellThickness
      );
      setResult(data);
      onAnalysisComplete?.(data);
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const renderChart = () => {
    if (!chartRef.current || !result) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const option: echarts.EChartsOption = {
      title: { text: "透气性对充型质量的影响", left: "center" },
      tooltip: { trigger: "axis" },
      legend: {
        data: ["充型质量", "缺陷率", "气孔率", "缩孔率"],
        bottom: 0,
      },
      grid: { left: "10%", right: "10%", top: "15%", bottom: "15%" },
      xAxis: {
        type: "category",
        name: "透气性 (%)",
        data: result.permeability_values,
      },
      yAxis: [
        {
          type: "value",
          name: "质量评分",
          min: 0,
          max: 100,
        },
        {
          type: "value",
          name: "缺陷率 (%)",
          min: 0,
          max: 60,
        },
      ],
      series: [
        {
          name: "充型质量",
          type: "line",
          yAxisIndex: 0,
          data: result.filling_quality_scores,
          smooth: true,
          lineStyle: { width: 3 },
          itemStyle: { color: "#52c41a" },
        },
        {
          name: "缺陷率",
          type: "line",
          yAxisIndex: 1,
          data: result.defect_rates_percent,
          smooth: true,
          lineStyle: { width: 2 },
          itemStyle: { color: "#ff4d4f" },
        },
        {
          name: "气孔率",
          type: "line",
          yAxisIndex: 1,
          data: result.gas_porosity_rates_percent,
          smooth: true,
          lineStyle: { width: 2, type: "dashed" },
          itemStyle: { color: "#fa8c16" },
        },
        {
          name: "缩孔率",
          type: "line",
          yAxisIndex: 1,
          data: result.shrinkage_rates_percent,
          smooth: true,
          lineStyle: { width: 2, type: "dotted" },
          itemStyle: { color: "#722ed1" },
        },
      ],
    };

    chartInstance.current.setOption(option);
  };

  const analyzeHistorical = async (castingId: string) => {
    return await permeabilityAnalyzerApi.analyzeHistorical(castingId);
  };

  const compareScenarios = async (scenarios: any[]) => {
    return await permeabilityAnalyzerApi.compareScenarios(scenarios);
  };

  const alloyOptions = [
    { value: "bronze", label: "青铜" },
    { value: "brass", label: "黄铜" },
    { value: "stainless_steel", label: "不锈钢" },
    { value: "aluminum", label: "铝合金" },
  ];

  return (
    <div className="permeability-analyzer">
      <div className="analyzer-controls">
        <h3>透气性分析</h3>

        <div className="control-group">
          <label>合金类型</label>
          <select
            value={alloyType}
            onChange={(e) => setAlloyType(e.target.value)}
          >
            {alloyOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>浇铸温度: {pouringTemp}°C</label>
          <input
            type="range"
            min="700"
            max="1650"
            step="10"
            value={pouringTemp}
            onChange={(e) => setPouringTemp(Number(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label>型壳层数: {shellThickness} 层</label>
          <input
            type="range"
            min="5"
            max="12"
            step="1"
            value={shellThickness}
            onChange={(e) => setShellThickness(Number(e.target.value))}
          />
        </div>
      </div>

      {loading && <div className="loading">分析中...</div>}

      <div ref={chartRef} className="permeability-chart" style={{ height: 400 }} />

      {result && (
        <>
          <div className="analysis-summary">
            <h4>分析结果摘要</h4>
            <div className="summary-cards">
              <div className="summary-card best">
                <span className="label">最佳透气性</span>
                <span className="value">
                  {result.analysis.best_quality_permeability}%
                </span>
                <span className="sub">
                  质量评分 {result.analysis.best_quality_score}
                </span>
              </div>
              <div className="summary-card good">
                <span className="label">最低缺陷率透气性</span>
                <span className="value">
                  {result.analysis.lowest_defect_permeability}%
                </span>
                <span className="sub">
                  缺陷率 {result.analysis.lowest_defect_rate}%
                </span>
              </div>
              <div className="summary-card worst">
                <span className="label">最差透气性</span>
                <span className="value">
                  {result.analysis.worst_quality_permeability}%
                </span>
                <span className="sub">
                  质量评分 {result.analysis.worst_quality_score}
                </span>
              </div>
            </div>
          </div>

          <div className="shell-materials-section">
            <h4>型壳材料对比</h4>
            <div className="materials-grid">
              {result.shell_materials_comparison.map((mat) => (
                <div key={mat.name} className="material-card">
                  <h5>{mat.name}</h5>
                  <div className="material-stats">
                    <div>
                      <span className="stat-label">透气性</span>
                      <span className="stat-value">{mat.permeability}%</span>
                    </div>
                    <div>
                      <span className="stat-label">表面质量</span>
                      <span className="stat-value">{mat.surface_quality}</span>
                    </div>
                    <div>
                      <span className="stat-label">强度</span>
                      <span className="stat-value">{mat.strength}</span>
                    </div>
                    <div>
                      <span className="stat-label">成本</span>
                      <span className="stat-value">{"¥".repeat(mat.cost)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="insights-section">
            <h4>分析洞察</h4>
            <ul className="insights-list">
              {result.insights.map((insight, idx) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default PermeabilityAnalyzer;
