import React, { useState, useEffect } from "react";
import { eraComparatorApi, AncientVsModernResult } from "../../lib/api";

interface EraComparatorProps {
  autoLoad?: boolean;
  onDataLoaded?: (data: AncientVsModernResult) => void;
}

const EraComparator: React.FC<EraComparatorProps> = ({
  autoLoad = true,
  onDataLoaded,
}) => {
  const [eras, setEras] = useState<any[]>([]);
  const [comparison, setComparison] = useState<AncientVsModernResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeEra, setActiveEra] = useState<string | null>(null);

  useEffect(() => {
    if (autoLoad) {
      loadComparison();
      loadEras();
    }
  }, [autoLoad]);

  const loadEras = async () => {
    try {
      const data = await eraComparatorApi.listEras();
      setEras(data);
    } catch (err) {
      console.error("Failed to load eras:", err);
    }
  };

  const loadComparison = async () => {
    try {
      setLoading(true);
      const data = await eraComparatorApi.getAncientVsModern();
      setComparison(data);
      onDataLoaded?.(data);
    } catch (err) {
      console.error("Failed to load era comparison:", err);
    } finally {
      setLoading(false);
    }
  };

  const renderMetricCard = (
    label: string,
    ancientValue: number | string,
    modernValue: number | string,
    unit = "",
    improvementLabel?: string
  ) => (
    <div className="metric-card">
      <h4>{label}</h4>
      <div className="metric-values">
        <div className="ancient-value">
          <span className="value">{ancientValue}{unit}</span>
          <span className="label">古代</span>
        </div>
        <div className="vs-divider">VS</div>
        <div className="modern-value">
          <span className="value">{modernValue}{unit}</span>
          <span className="label">现代</span>
        </div>
      </div>
      {improvementLabel && (
        <div className="improvement-badge">{improvementLabel}</div>
      )}
    </div>
  );

  if (loading) {
    return <div className="era-comparator loading">加载中...</div>;
  }

  return (
    <div className="era-comparator">
      <div className="era-header">
        <h2>古今熔模铸造工艺对比</h2>
        <p className="subtitle">从古代失蜡法到现代精密铸造的技术演进</p>
      </div>

      {comparison && (
        <>
          <div className="summary-metrics">
            {renderMetricCard(
              "平均缺陷率",
              comparison.summary.avg_ancient_defect_rate.toFixed(1),
              comparison.summary.avg_modern_defect_rate.toFixed(1),
              "%",
              `降低 ${comparison.summary.defect_reduction_percent.toFixed(1)}%`
            )}
            {renderMetricCard(
              "尺寸精度",
              comparison.summary.avg_ancient_accuracy_mm.toFixed(1),
              comparison.summary.avg_modern_accuracy_mm.toFixed(2),
              "mm",
              `提升 ${comparison.summary.accuracy_improvement_factor.toFixed(1)} 倍`
            )}
          </div>

          <div className="detailed-comparison">
            <h3>详细对比维度</h3>
            <div className="comparison-dimensions">
              <div className="dimension-card">
                <h4>制模工艺</h4>
                <div className="dimension-content">
                  <div className="ancient-col">
                    <h5>古代</h5>
                    <ul>
                      <li>蜂蜡+松香混合蜡料</li>
                      <li>手工雕刻蜡模</li>
                      <li>分型线明显</li>
                    </ul>
                  </div>
                  <div className="modern-col">
                    <h5>现代</h5>
                    <ul>
                      <li>专用铸造蜡料</li>
                      <li>精密模具注射成型</li>
                      <li>公差可达±0.05mm</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="dimension-card">
                <h4>型壳材料</h4>
                <div className="dimension-content">
                  <div className="ancient-col">
                    <h5>古代</h5>
                    <ul>
                      <li>黏土+砂子混合泥范</li>
                      <li>自然干燥</li>
                      <li>透气性较差</li>
                    </ul>
                  </div>
                  <div className="modern-col">
                    <h5>现代</h5>
                    <ul>
                      <li>硅溶胶+石英砂/锆英砂</li>
                      <li>恒温恒湿干燥</li>
                      <li>多层复合结构</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="dimension-card">
                <h4>熔化设备</h4>
                <div className="dimension-content">
                  <div className="ancient-col">
                    <h5>古代</h5>
                    <ul>
                      <li>木炭坩埚炉</li>
                      <li>温度控制困难</li>
                      <li>温度波动大</li>
                    </ul>
                  </div>
                  <div className="modern-col">
                    <h5>现代</h5>
                    <ul>
                      <li>中频感应炉</li>
                      <li>精密控温±5°C</li>
                      <li>真空/保护气氛</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="key-insights">
            <h3>关键洞察</h3>
            <ul className="insights-list">
              {comparison.key_insights.map((insight, idx) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      <div className="era-list-section">
        <h3>时代信息</h3>
        <div className="era-cards">
          {eras.map((era) => (
            <div
              key={era.id}
              className={`era-card ${activeEra === era.id ? "active" : ""}`}
              onClick={() => setActiveEra(activeEra === era.id ? null : era.id)}
            >
              <h4>{era.name}</h4>
              <p className="era-period">{era.period}</p>
              {activeEra === era.id && (
                <div className="era-details">
                  <p><strong>关键技术：</strong>{era.key_technologies?.join("、")}</p>
                  <p><strong>代表作品：</strong>{era.representative_works?.join("、")}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EraComparator;
