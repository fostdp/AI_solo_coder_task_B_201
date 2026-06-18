import React, { useState, useEffect } from "react";
import {
  processComparatorApi,
  CraftInfo,
  ComparisonResult,
} from "../../lib/api";

interface ProcessComparatorProps {
  defaultCraftIds?: string[];
  showCraftList?: boolean;
  onCompare?: (result: ComparisonResult) => void;
}

const ProcessComparator: React.FC<ProcessComparatorProps> = ({
  defaultCraftIds = [],
  showCraftList = true,
  onCompare,
}) => {
  const [crafts, setCrafts] = useState<CraftInfo[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>(defaultCraftIds);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [eraFilter, setEraFilter] = useState<"all" | "ancient" | "modern">("all");

  useEffect(() => {
    loadCrafts();
  }, [eraFilter]);

  const loadCrafts = async () => {
    try {
      setLoading(true);
      let data: CraftInfo[];
      if (eraFilter === "ancient") {
        data = await processComparatorApi.getAncientCrafts();
      } else if (eraFilter === "modern") {
        data = await processComparatorApi.getModernCrafts();
      } else {
        data = await processComparatorApi.getAllCrafts();
      }
      setCrafts(data);
    } catch (err) {
      console.error("Failed to load crafts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (selectedIds.length < 2) return;
    try {
      setLoading(true);
      const result = await processComparatorApi.compareCrafts(selectedIds);
      setComparison(result);
      onCompare?.(result);
    } catch (err) {
      console.error("Comparison failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleCraft = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const calculateDefectRate = async (
    craftId: string,
    pouringTemp: number,
    permeability: number
  ) => {
    return await processComparatorApi.calculateDefectRate(
      craftId,
      pouringTemp,
      permeability
    );
  };

  return (
    <div className="process-comparator">
      {showCraftList && (
        <div className="craft-list-section">
          <div className="filter-bar">
            <span>时代筛选：</span>
            <button onClick={() => setEraFilter("all")} className={eraFilter === "all" ? "active" : ""}>
              全部
            </button>
            <button onClick={() => setEraFilter("ancient")} className={eraFilter === "ancient" ? "active" : ""}>
              古代
            </button>
            <button onClick={() => setEraFilter("modern")} className={eraFilter === "modern" ? "active" : ""}>
              现代
            </button>
          </div>

          <div className="craft-grid">
            {loading && <div className="loading">加载中...</div>}
            {crafts.map((craft) => (
              <div
                key={craft.id}
                className={`craft-card ${selectedIds.includes(craft.id) ? "selected" : ""}`}
                onClick={() => toggleCraft(craft.id)}
              >
                <h4>{craft.name}</h4>
                <p className="craft-era">{craft.era}</p>
                <p className="craft-desc">{craft.description}</p>
                <div className="craft-stats">
                  <span>缺陷率: {craft.overall_defect_rate?.toFixed?.(1)}%</span>
                  <span>难度: {craft.complexity}/10</span>
                </div>
              </div>
            ))}
          </div>

          <div className="compare-action">
            <button
              className="btn-primary"
              onClick={handleCompare}
              disabled={selectedIds.length < 2 || loading}
            >
              对比选中的 {selectedIds.length} 种工艺
            </button>
          </div>
        </div>
      )}

      {comparison && (
        <div className="comparison-result">
          <h3>工艺对比结果</h3>
          <div className="metrics-table">
            <table>
              <thead>
                <tr>
                  <th>指标</th>
                  {comparison.crafts.map((c) => (
                    <th key={c.id}>{c.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {comparison.comparison_metrics.map((metric) => (
                  <tr key={metric.metric}>
                    <td>
                      {metric.label} ({metric.unit})
                    </td>
                    {comparison.crafts.map((c) => (
                      <td key={c.id}>{metric.values[c.id]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="defect-radar-section">
            <h4>缺陷类型对比</h4>
            <div className="defect-chart">
              {comparison.defect_type_comparison.map((defect) => (
                <div key={defect.type} className="defect-item">
                  <span className="defect-label">{defect.label}</span>
                  <div className="defect-bars">
                    {comparison.crafts.map((c) => (
                      <div
                        key={c.id}
                        className="defect-bar"
                        style={{ width: `${(defect.values[c.id] / 50) * 100}%` }}
                        title={`${c.name}: ${defect.values[c.id]}%`}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessComparator;
