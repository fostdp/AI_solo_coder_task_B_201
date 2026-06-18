import React, { useState, useEffect, useRef } from "react";
import {
  vrLostWaxApi,
  WaxMoldTemplate,
  CastingMaterial,
  ShellMaterial,
  SimulationResult,
  GeometryResult,
} from "../../lib/api";

interface VrLostWaxProps {
  initialTemplateId?: string;
  mode?: "simple" | "expert";
  onSimulationComplete?: (result: SimulationResult) => void;
}

const VrLostWax: React.FC<VrLostWaxProps> = ({
  initialTemplateId,
  mode = "simple",
  onSimulationComplete,
}) => {
  const [templates, setTemplates] = useState<WaxMoldTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<WaxMoldTemplate | null>(null);
  const [materials, setMaterials] = useState<CastingMaterial[]>([]);
  const [shells, setShells] = useState<ShellMaterial[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<string>("bronze_cu_sn");
  const [selectedShell, setSelectedShell] = useState<string>("silica_sol");
  const [geometry, setGeometry] = useState<GeometryResult | null>(null);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState<"simple" | "expert">(mode);

  const [simpleParams, setSimpleParams] = useState({
    sizeLevel: 3,
    ornamentLevel: 3,
    thicknessLevel: 3,
  });

  const [expertParams, setExpertParams] = useState<Record<string, any>>({});
  const [simulationRunning, setSimulationRunning] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    loadTemplates();
    loadMaterials();
    loadShells();
  }, []);

  useEffect(() => {
    if (selectedTemplate) {
      updateGeometry();
    }
  }, [selectedTemplate, selectedMaterial, selectedShell]);

  const loadTemplates = async () => {
    try {
      const data = await vrLostWaxApi.getTemplates();
      setTemplates(data);
      if (data.length > 0) {
        const initial = initialTemplateId
          ? data.find((t) => t.id === initialTemplateId) || data[0]
          : data[0];
        setSelectedTemplate(initial);
        setExpertParams({ ...initial.default_params });
      }
    } catch (err) {
      console.error("Failed to load templates:", err);
    }
  };

  const loadMaterials = async () => {
    try {
      const data = await vrLostWaxApi.getMaterials();
      setMaterials(data);
    } catch (err) {
      console.error("Failed to load materials:", err);
    }
  };

  const loadShells = async () => {
    try {
      const data = await vrLostWaxApi.getShells();
      setShells(data);
    } catch (err) {
      console.error("Failed to load shells:", err);
    }
  };

  const updateGeometry = async () => {
    if (!selectedTemplate) return;
    try {
      setLoading(true);
      const params =
        currentMode === "simple"
          ? await vrLostWaxApi.applySimpleMode(
              selectedTemplate.id,
              simpleParams.sizeLevel,
              simpleParams.ornamentLevel,
              simpleParams.thicknessLevel
            )
          : expertParams;

      const geo = await vrLostWaxApi.generateGeometry(selectedTemplate.id, params);
      setGeometry(geo);
    } catch (err) {
      console.error("Geometry generation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    if (!selectedTemplate || !geometry) return;
    try {
      setSimulationRunning(true);
      const material = materials.find((m) => m.id === selectedMaterial);
      const result = await vrLostWaxApi.simulateCasting(
        selectedTemplate.id,
        geometry.params,
        selectedMaterial,
        selectedShell,
        material?.pouring_temp
      );
      setSimulationResult(result);
      onSimulationComplete?.(result);
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimulationRunning(false);
    }
  };

  const handleTemplateChange = (templateId: string) => {
    const template = templates.find((t) => t.id === templateId);
    if (template) {
      setSelectedTemplate(template);
      setExpertParams({ ...template.default_params });
      setSimulationResult(null);
    }
  };

  const handleSimpleParamChange = (key: string, value: number) => {
    setSimpleParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleExpertParamChange = (key: string, value: number | boolean) => {
    setExpertParams((prev) => ({ ...prev, [key]: value }));
  };

  const applyPreset = async (presetId: string) => {
    if (!selectedTemplate) return;
    try {
      const params = await vrLostWaxApi.applyPreset(selectedTemplate.id, presetId);
      setExpertParams(params);
      if (currentMode === "expert") {
        const geo = await vrLostWaxApi.generateGeometry(selectedTemplate.id, params);
        setGeometry(geo);
      }
    } catch (err) {
      console.error("Failed to apply preset:", err);
    }
  };

  const renderSimpleControls = () => (
    <div className="simple-controls">
      <h4>简易模式</h4>
      <p className="mode-desc">使用滑块快速调整蜡模外观参数</p>

      <div className="param-slider">
        <label>整体尺寸 (等级 {simpleParams.sizeLevel})</label>
        <input
          type="range"
          min="1"
          max="5"
          step="1"
          value={simpleParams.sizeLevel}
          onChange={(e) => handleSimpleParamChange("sizeLevel", Number(e.target.value))}
        />
        <div className="slider-labels">
          <span>小巧</span>
          <span>宏大</span>
        </div>
      </div>

      <div className="param-slider">
        <label>纹饰程度 (等级 {simpleParams.ornamentLevel})</label>
        <input
          type="range"
          min="1"
          max="5"
          step="1"
          value={simpleParams.ornamentLevel}
          onChange={(e) => handleSimpleParamChange("ornamentLevel", Number(e.target.value))}
        />
        <div className="slider-labels">
          <span>素面</span>
          <span>繁缛</span>
        </div>
      </div>

      <div className="param-slider">
        <label>壁厚程度 (等级 {simpleParams.thicknessLevel})</label>
        <input
          type="range"
          min="1"
          max="5"
          step="1"
          value={simpleParams.thicknessLevel}
          onChange={(e) => handleSimpleParamChange("thicknessLevel", Number(e.target.value))}
        />
        <div className="slider-labels">
          <span>轻薄</span>
          <span>厚重</span>
        </div>
      </div>

      <button className="btn-secondary" onClick={updateGeometry}>
        更新模型
      </button>
    </div>
  );

  const renderExpertControls = () => (
    <div className="expert-controls">
      <h4>专家模式</h4>
      <p className="mode-desc">精确调整每一项参数</p>

      {selectedTemplate &&
        Object.entries(selectedTemplate.param_ranges).map(([key, range]: [string, any]) => {
          const value = expertParams[key];
          const isBool = typeof value === "boolean";

          return (
            <div key={key} className="expert-param">
              <label>{range.label}</label>
              {isBool ? (
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => handleExpertParamChange(key, e.target.checked)}
                />
              ) : (
                <div className="number-input">
                  <input
                    type="number"
                    min={range.min}
                    max={range.max}
                    step={range.step}
                    value={value}
                    onChange={(e) => handleExpertParamChange(key, Number(e.target.value))}
                  />
                  <span className="unit">{range.unit || ""}</span>
                </div>
              )}
            </div>
          );
        })}

      <button className="btn-secondary" onClick={updateGeometry}>
        更新模型
      </button>
    </div>
  );

  return (
    <div className="vr-lost-wax">
      <div className="vr-header">
        <h2>虚拟失蜡铸造体验</h2>
        <p className="subtitle">设计您的专属蜡模，模拟浇铸过程</p>
      </div>

      <div className="vr-layout">
        <div className="vr-sidebar">
          <div className="template-selector">
            <h4>选择器型</h4>
            <div className="template-list">
              {templates.map((t) => (
                <div
                  key={t.id}
                  className={`template-item ${selectedTemplate?.id === t.id ? "active" : ""}`}
                  onClick={() => handleTemplateChange(t.id)}
                >
                  <span className="template-name">{t.name}</span>
                  <span className="template-difficulty">
                    {"★".repeat(t.difficulty)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mode-switch">
            <button
              className={currentMode === "simple" ? "active" : ""}
              onClick={() => setCurrentMode("simple")}
            >
              简易模式
            </button>
            <button
              className={currentMode === "expert" ? "active" : ""}
              onClick={() => setCurrentMode("expert")}
            >
              专家模式
            </button>
          </div>

          {currentMode === "simple" ? renderSimpleControls() : renderExpertControls()}

          <div className="material-selector">
            <h4>铸造材料</h4>
            <select
              value={selectedMaterial}
              onChange={(e) => setSelectedMaterial(e.target.value)}
            >
              {materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>

          <div className="shell-selector">
            <h4>型壳材料</h4>
            <select
              value={selectedShell}
              onChange={(e) => setSelectedShell(e.target.value)}
            >
              {shells.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="btn-primary simulate-btn"
            onClick={runSimulation}
            disabled={simulationRunning || !geometry}
          >
            {simulationRunning ? "模拟中..." : "开始浇铸模拟"}
          </button>
        </div>

        <div className="vr-main">
          <div className="canvas-section">
            <canvas ref={canvasRef} className="wax-canvas" />
            {loading && <div className="canvas-loading">生成中...</div>}
          </div>

          {geometry && (
            <div className="geometry-info">
              <h4>模型信息</h4>
              <div className="info-grid">
                <div>
                  <span className="info-label">体积</span>
                  <span className="info-value">
                    {geometry.properties.volume_cm3} cm³
                  </span>
                </div>
                <div>
                  <span className="info-label">表面积</span>
                  <span className="info-value">
                    {geometry.properties.surface_area_cm2} cm²
                  </span>
                </div>
                <div>
                  <span className="info-label">预估重量</span>
                  <span className="info-value">
                    {geometry.properties.estimated_weight_g} g
                  </span>
                </div>
                <div>
                  <span className="info-label">复杂度</span>
                  <span className="info-value">
                    {geometry.properties.complexity_score}/100
                  </span>
                </div>
              </div>
            </div>
          )}

          {simulationResult && (
            <div className="simulation-result">
              <h4>模拟结果</h4>
              <div className="result-cards">
                <div className="result-card quality">
                  <span className="result-label">充型质量</span>
                  <span className="result-value">
                    {simulationResult.results.filling_quality_score}
                  </span>
                </div>
                <div className="result-card defect">
                  <span className="result-label">缺陷率</span>
                  <span className="result-value">
                    {simulationResult.results.overall_defect_rate}%
                  </span>
                </div>
                <div className="result-card defects">
                  <span className="result-label">缺陷数量</span>
                  <span className="result-value">
                    {simulationResult.results.detected_defects.length}
                  </span>
                </div>
              </div>

              <div className="tips-section">
                <h5>工艺建议</h5>
                <ul>
                  {simulationResult.tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VrLostWax;
