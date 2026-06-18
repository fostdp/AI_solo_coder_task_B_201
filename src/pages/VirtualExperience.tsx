import { useEffect, useRef, useState, useCallback } from "react";
import { virtualApi, type WaxMoldTemplate, type CastingMaterial, type ShellMaterial, type GeometryResult, type SimulationResult, type SimStep } from "@/lib/api";
import { VirtualWaxViewer } from "@/lib/virtual_wax_viewer";
import { Palette, FlaskConical, Layers, Play, RotateCcw, Eye, EyeOff, Sparkles, AlertTriangle, Info, CheckCircle } from "lucide-react";

type Stage = "design" | "casting" | "result";

export default function VirtualExperiencePage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<VirtualWaxViewer | null>(null);
  const animationRef = useRef<number | null>(null);

  const [templates, setTemplates] = useState<WaxMoldTemplate[]>([]);
  const [materials, setMaterials] = useState<CastingMaterial[]>([]);
  const [shells, setShells] = useState<ShellMaterial[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("zunpan");
  const [selectedMaterial, setSelectedMaterial] = useState<string>("bronze_cu_sn");
  const [selectedShell, setSelectedShell] = useState<string>("silica_sol");
  const [params, setParams] = useState<Record<string, number>>({});
  const [geometry, setGeometry] = useState<GeometryResult | null>(null);
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [stage, setStage] = useState<Stage>("design");
  const [currentStep, setCurrentStep] = useState<SimStep | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showShell, setShowShell] = useState(false);
  const [showDefects, setShowDefects] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [tmpls, mats, shls] = await Promise.all([
          virtualApi.getTemplates(),
          virtualApi.getMaterials(),
          virtualApi.getShells(),
        ]);
        setTemplates(tmpls);
        setMaterials(mats);
        setShells(shls);
        if (tmpls.length > 0) {
          const first = tmpls[0];
          setSelectedTemplate(first.id);
          setParams(first.default_params);
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    if (containerRef.current && !viewerRef.current) {
      const viewer = new VirtualWaxViewer(containerRef.current);
      viewer.createParticles(2000);
      viewerRef.current = viewer;
    }
    return () => {
      if (viewerRef.current) {
        viewerRef.current.dispose();
        viewerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!viewerRef.current || !geometry) return;
    const scale = 0.012;
    viewerRef.current.buildWaxModel(geometry.parts, scale);
    const mat = materials.find((m) => m.id === selectedMaterial);
    if (mat) {
      viewerRef.current.setMetalColor(mat.color_hex);
    }
  }, [geometry, selectedMaterial, materials]);

  const generateGeometry = useCallback(async () => {
    if (!selectedTemplate) return;
    try {
      const geo = await virtualApi.generateGeometry(selectedTemplate, params);
      setGeometry(geo);
    } catch (err) {
      console.error("Failed to generate geometry:", err);
    }
  }, [selectedTemplate, params]);

  useEffect(() => {
    if (selectedTemplate && templates.length > 0) {
      generateGeometry();
    }
  }, [selectedTemplate, generateGeometry, templates.length]);

  const handleTemplateSelect = (templateId: string) => {
    const tmpl = templates.find((t) => t.id === templateId);
    if (tmpl) {
      setSelectedTemplate(templateId);
      setParams({ ...tmpl.default_params });
      setSimResult(null);
      setStage("design");
      if (viewerRef.current) {
        viewerRef.current.resetToWax();
        viewerRef.current.showParticles(false);
        viewerRef.current.toggleDefects(false);
      }
    }
  };

  const handleParamChange = (key: string, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleApplyParams = () => {
    generateGeometry();
    setSimResult(null);
    setStage("design");
    if (viewerRef.current) {
      viewerRef.current.resetToWax();
      viewerRef.current.showParticles(false);
    }
  };

  const startCasting = async () => {
    if (!selectedTemplate || !selectedMaterial || !selectedShell) return;

    try {
      const result = await virtualApi.simulateCasting(
        selectedTemplate,
        params,
        selectedMaterial,
        selectedShell
      );
      setSimResult(result);
      setStage("casting");
      setStepIndex(0);
      setIsPlaying(true);

      if (viewerRef.current) {
        viewerRef.current.resetToWax();
        viewerRef.current.showParticles(true);
        viewerRef.current.setDefects(result.results.detected_defects, 1.5);
      }
    } catch (err) {
      console.error("Casting simulation failed:", err);
    }
  };

  useEffect(() => {
    if (!isPlaying || !simResult || stage !== "casting") return;

    const steps = simResult.simulation_steps;
    if (stepIndex >= steps.length) {
      setIsPlaying(false);
      setStage("result");
      if (viewerRef.current) {
        viewerRef.current.setAsMetal();
        viewerRef.current.showParticles(false);
      }
      return;
    }

    const step = steps[stepIndex];
    setCurrentStep(step);

    if (viewerRef.current) {
      viewerRef.current.updateFilling(step.filling_progress, step.front_temperature);
    }

    animationRef.current = window.setTimeout(() => {
      setStepIndex((s) => s + 1);
    }, 500);

    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [isPlaying, stepIndex, simResult, stage]);

  const resetDesign = () => {
    setStage("design");
    setSimResult(null);
    setCurrentStep(null);
    setStepIndex(0);
    setIsPlaying(false);
    setShowDefects(false);
    if (viewerRef.current) {
      viewerRef.current.resetToWax();
      viewerRef.current.showParticles(false);
      viewerRef.current.toggleDefects(false);
    }
  };

  const toggleShell = () => {
    setShowShell((s) => !s);
    if (viewerRef.current) {
      viewerRef.current.showShell(!showShell);
    }
  };

  const toggleDefectsView = () => {
    setShowDefects((s) => !s);
    if (viewerRef.current) {
      viewerRef.current.toggleDefects(!showDefects);
    }
  };

  const toggleAutoRotate = () => {
    setAutoRotate((r) => !r);
    if (viewerRef.current) {
      viewerRef.current.setAutoRotate(!autoRotate);
    }
  };

  const currentTemplate = templates.find((t) => t.id === selectedTemplate);
  const currentMaterial = materials.find((m) => m.id === selectedMaterial);
  const currentShell = shells.find((s) => s.id === selectedShell);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-amber-400">加载中...</div>
      </div>
    );
  }

  const qualityColor = simResult
    ? simResult.results.filling_quality_score >= 80
      ? "text-emerald-400"
      : simResult.results.filling_quality_score >= 60
        ? "text-amber-400"
        : "text-red-400"
    : "";

  return (
    <div className="flex h-full w-full overflow-hidden">
      <aside className="flex w-72 shrink-0 flex-col border-r border-amber-900/30 bg-gradient-to-b from-[#0a0807] via-[#100b08] to-[#0a0807]">
        <div className="border-b border-amber-900/30 p-4">
          <h2 className="flex items-center gap-2 font-serif text-lg font-bold text-amber-300">
            <Palette className="h-5 w-5" />
            蜡模设计
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-5">
            <h3 className="mb-2 text-xs font-medium text-amber-400/80">选择器型</h3>
            <div className="grid grid-cols-2 gap-2">
              {templates.map((tmpl) => (
                <button
                  key={tmpl.id}
                  onClick={() => handleTemplateSelect(tmpl.id)}
                  className={`rounded-lg border p-2 text-xs transition-all ${
                    selectedTemplate === tmpl.id
                      ? "border-amber-500/60 bg-amber-900/20 text-amber-200"
                      : "border-amber-900/30 text-amber-400/70 hover:border-amber-700/50"
                  }`}
                >
                  <div className="font-medium">{tmpl.name}</div>
                  <div className="mt-1 text-[10px] opacity-70">难度 {"★".repeat(tmpl.difficulty)}</div>
                </button>
              ))}
            </div>
          </div>

          {currentTemplate && (
            <>
              <div className="mb-4 rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <p className="text-xs text-amber-300/80 leading-relaxed">
                  {currentTemplate.description}
                </p>
                <div className="mt-2 pt-2 border-t border-amber-900/20">
                  <p className="text-[10px] text-amber-500/60 italic">
                    📜 {currentTemplate.historical_note}
                  </p>
                </div>
              </div>

              <div className="mb-5">
                <h3 className="mb-2 flex items-center gap-1.5 text-xs font-medium text-amber-400/80">
                  <Sparkles className="h-3.5 w-3.5" />
                  设计参数
                </h3>
                <div className="space-y-3">
                  {Object.entries(currentTemplate.param_ranges || {}).map(([key, range]) => (
                    <div key={key}>
                      <div className="mb-1 flex justify-between text-[11px]">
                        <span className="text-amber-400/70">{range.label}</span>
                        <span className="font-mono text-amber-300">
                          {params[key]?.toFixed?.(1) ?? params[key]}
                        </span>
                      </div>
                      <input
                        type="range"
                        min={range.min}
                        max={range.max}
                        step={range.step}
                        value={params[key] ?? range.min}
                        onChange={(e) => handleParamChange(key, Number(e.target.value))}
                        className="w-full accent-amber-500"
                        disabled={stage !== "design"}
                      />
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleApplyParams}
                  disabled={stage !== "design"}
                  className="mt-3 w-full rounded-lg border border-amber-600/40 bg-amber-800/20 py-2 text-xs font-medium text-amber-200 transition-all hover:bg-amber-700/30 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  应用参数
                </button>
              </div>

              <div className="mb-5">
                <h3 className="mb-2 flex items-center gap-1.5 text-xs font-medium text-amber-400/80">
                  <FlaskConical className="h-3.5 w-3.5" />
                  铸造合金
                </h3>
                <div className="space-y-1.5">
                  {materials.map((mat) => (
                    <button
                      key={mat.id}
                      onClick={() => setSelectedMaterial(mat.id)}
                      disabled={stage !== "design"}
                      className={`flex w-full items-center gap-2 rounded-lg border px-2.5 py-2 text-xs transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
                        selectedMaterial === mat.id
                          ? "border-amber-500/50 bg-amber-900/20"
                          : "border-amber-900/25 hover:border-amber-700/40"
                      }`}
                    >
                      <span
                        className="h-3.5 w-3.5 shrink-0 rounded-full border border-amber-700/40"
                        style={{ backgroundColor: mat.color_hex }}
                      />
                      <span className="flex-1 text-left text-amber-200/90">{mat.name}</span>
                      <span className="font-mono text-[10px] text-amber-500/70">
                        {mat.pouring_temp}°C
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-5">
                <h3 className="mb-2 flex items-center gap-1.5 text-xs font-medium text-amber-400/80">
                  <Layers className="h-3.5 w-3.5" />
                  型壳材料
                </h3>
                <div className="space-y-1.5">
                  {shells.map((shl) => (
                    <button
                      key={shl.id}
                      onClick={() => setSelectedShell(shl.id)}
                      disabled={stage !== "design"}
                      className={`flex w-full items-center justify-between rounded-lg border px-2.5 py-2 text-xs transition-all disabled:cursor-not-allowed disabled:opacity-50 ${
                        selectedShell === shl.id
                          ? "border-amber-500/50 bg-amber-900/20"
                          : "border-amber-900/25 hover:border-amber-700/40"
                      }`}
                    >
                      <span className="text-amber-200/90">{shl.name}</span>
                      <span className="font-mono text-[10px] text-amber-500/70">
                        透气 {shl.permeability}%
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {stage === "design" && (
            <button
              onClick={startCasting}
              className="w-full rounded-lg bg-gradient-to-r from-amber-600 to-amber-800 py-3 text-sm font-bold text-amber-50 shadow-lg shadow-amber-900/40 transition-all hover:from-amber-500 hover:to-amber-700"
            >
              <Play className="mr-2 inline h-4 w-4" />
              开始浇铸
            </button>
          )}

          {stage !== "design" && (
            <button
              onClick={resetDesign}
              className="w-full rounded-lg border border-amber-700/40 bg-amber-900/20 py-2.5 text-sm font-medium text-amber-200 transition-all hover:bg-amber-800/30"
            >
              <RotateCcw className="mr-2 inline h-4 w-4" />
              重新设计
            </button>
          )}
        </div>
      </aside>

      <main className="relative flex-1 overflow-hidden">
        <div ref={containerRef} className="absolute inset-0" />

        <div className="absolute left-4 top-4 flex gap-2">
          <button
            onClick={toggleAutoRotate}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition-all ${
              autoRotate
                ? "border-amber-500/50 bg-amber-900/30 text-amber-200"
                : "border-amber-800/40 bg-black/50 text-amber-400/70 hover:border-amber-600/50"
            }`}
          >
            <RotateCcw className="h-3.5 w-3.5" />
            自动旋转
          </button>
          <button
            onClick={toggleShell}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition-all ${
              showShell
                ? "border-amber-500/50 bg-amber-900/30 text-amber-200"
                : "border-amber-800/40 bg-black/50 text-amber-400/70 hover:border-amber-600/50"
            }`}
          >
            {showShell ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
            型壳
          </button>
          {stage === "result" && (
            <button
              onClick={toggleDefectsView}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition-all ${
                showDefects
                  ? "border-red-500/50 bg-red-900/30 text-red-200"
                  : "border-amber-800/40 bg-black/50 text-amber-400/70 hover:border-amber-600/50"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              缺陷
            </button>
          )}
        </div>

        {stage === "casting" && currentStep && (
          <div className="absolute bottom-6 left-1/2 w-[60%] -translate-x-1/2">
            <div className="mb-2 flex justify-between text-xs text-amber-300">
              <span>浇铸进度</span>
              <span className="font-mono">{currentStep.filling_progress.toFixed(1)}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-amber-950/60">
              <div
                className="h-full rounded-full bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 transition-all duration-300"
                style={{ width: `${currentStep.filling_progress}%` }}
              />
            </div>
            <div className="mt-2 flex justify-between text-[11px] text-amber-500/70">
              <span>
                前沿温度: <span className="font-mono text-orange-400">{currentStep.front_temperature}°C</span>
              </span>
              <span>
                平均温度: <span className="font-mono text-amber-400">{currentStep.avg_temperature}°C</span>
              </span>
            </div>
          </div>
        )}

        <div className="absolute right-4 top-4 rounded-xl border border-amber-800/30 bg-black/70 p-3 text-xs backdrop-blur-sm">
          <div className="mb-2 font-serif text-sm font-semibold text-amber-300">
            {currentTemplate?.name}
          </div>
          {geometry && (
            <div className="space-y-1 text-amber-400/80">
              <div className="flex justify-between gap-4">
                <span>体积</span>
                <span className="font-mono text-amber-300">{geometry.properties.volume_cm3} cm³</span>
              </div>
              <div className="flex justify-between gap-4">
                <span>重量</span>
                <span className="font-mono text-amber-300">{geometry.properties.estimated_weight_g} g</span>
              </div>
              <div className="flex justify-between gap-4">
                <span>复杂度</span>
                <span className="font-mono text-amber-300">{geometry.properties.complexity_score}分</span>
              </div>
            </div>
          )}
          {currentMaterial && (
            <div className="mt-2 pt-2 border-t border-amber-900/30">
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: currentMaterial.color_hex }}
                />
                <span className="text-amber-300">{currentMaterial.name}</span>
              </div>
            </div>
          )}
          {currentShell && (
            <div className="text-amber-400/70">
              {currentShell.name} · 透气 {currentShell.permeability}%
            </div>
          )}
        </div>
      </main>

      <aside className="flex w-72 shrink-0 flex-col border-l border-amber-900/30 bg-gradient-to-b from-[#0a0807] via-[#100b08] to-[#0a0807]">
        <div className="border-b border-amber-900/30 p-4">
          <h2 className="flex items-center gap-2 font-serif text-lg font-bold text-amber-300">
            <Info className="h-5 w-5" />
            {stage === "design" ? "工艺信息" : stage === "casting" ? "浇铸中..." : "铸造结果"}
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {stage === "design" && (
            <div className="space-y-4">
              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <h3 className="mb-2 text-sm font-medium text-amber-300">铸造工艺简介</h3>
                <p className="text-xs text-amber-400/70 leading-relaxed">
                  失蜡法也称"熔模铸造"，是中国古代三大铸造技术之一。
                  工艺过程：用蜡料制成模型→外敷耐火材料→加热脱蜡→高温焙烧型壳→浇注金属液→破壳取件。
                </p>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <h3 className="mb-2 text-sm font-medium text-amber-300">工艺流程</h3>
                <div className="space-y-2">
                  {[
                    { step: 1, title: "制蜡模", desc: "雕刻或压制成型" },
                    { step: 2, title: "制型壳", desc: "多层耐火材料涂挂" },
                    { step: 3, title: "脱蜡焙烧", desc: "高温使蜡流出并硬化" },
                    { step: 4, title: "浇注金属", desc: "铜液注入型壳空腔" },
                    { step: 5, title: "破壳清理", desc: "敲碎型壳取出铸件" },
                  ].map((item) => (
                    <div key={item.step} className="flex gap-3">
                      <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-700/40 text-[10px] font-bold text-amber-200">
                        {item.step}
                      </div>
                      <div>
                        <div className="text-xs font-medium text-amber-200">{item.title}</div>
                        <div className="text-[11px] text-amber-500/60">{item.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {stage === "casting" && (
            <div className="space-y-4">
              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <div className="mb-2 text-xs text-amber-400/70">当前步骤</div>
                <div className="font-mono text-2xl font-bold text-amber-300">
                  {currentStep?.step || 0} / {simResult?.simulation_steps.length || 10}
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <div className="mb-2 text-xs text-amber-400/70">充型进度</div>
                <div className="font-mono text-2xl font-bold text-orange-400">
                  {currentStep?.filling_progress.toFixed(1) || 0}%
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <div className="mb-2 text-xs text-amber-400/70">金属液前沿温度</div>
                <div className="font-mono text-2xl font-bold text-red-400">
                  {currentStep?.front_temperature || 0}°C
                </div>
              </div>

              <div className="animate-pulse rounded-lg border border-amber-500/30 bg-amber-900/20 p-3">
                <div className="flex items-center gap-2 text-sm text-amber-300">
                  <Sparkles className="h-4 w-4" />
                  正在浇铸中...
                </div>
                <div className="mt-1 text-xs text-amber-500/70">
                  高温金属液正在充填型腔
                </div>
              </div>
            </div>
          )}

          {stage === "result" && simResult && (
            <div className="space-y-4">
              <div className="rounded-lg border border-emerald-700/40 bg-emerald-900/15 p-3">
                <div className="mb-1 text-xs text-emerald-400/70">充型质量评分</div>
                <div className={`font-mono text-3xl font-bold ${qualityColor}`}>
                  {simResult.results.filling_quality_score}
                  <span className="text-lg">/100</span>
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <div className="mb-2 text-xs text-amber-400/70">综合缺陷率</div>
                <div className="font-mono text-2xl font-bold text-red-400">
                  {simResult.results.overall_defect_rate}%
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <h3 className="mb-2 text-xs font-medium text-amber-400/80">缺陷明细</h3>
                <div className="space-y-1.5">
                  {[
                    { label: "气孔率", value: simResult.results.defect_breakdown.gas_porosity_rate },
                    { label: "缩孔缩松率", value: simResult.results.defect_breakdown.shrinkage_rate },
                    { label: "冷隔率", value: simResult.results.defect_breakdown.cold_shut_rate },
                    { label: "夹杂率", value: simResult.results.defect_breakdown.inclusion_rate },
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between text-xs">
                      <span className="text-amber-400/70">{item.label}</span>
                      <span className="font-mono text-amber-300">{item.value.toFixed(2)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-black/30 p-3">
                <div className="mb-2 flex justify-between text-xs">
                  <span className="text-amber-400/70">检出缺陷数</span>
                  <span className="font-mono text-amber-300">
                    {simResult.results.detected_defects.length} 处
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-amber-400/70">总缺陷体积</span>
                  <span className="font-mono text-amber-300">
                    {simResult.results.total_defect_volume.toFixed(3)} cm³
                  </span>
                </div>
              </div>

              <div className="rounded-lg border border-amber-800/30 bg-gradient-to-br from-amber-900/10 to-black/30 p-3">
                <h3 className="mb-2 flex items-center gap-1.5 text-xs font-medium text-amber-300">
                  <CheckCircle className="h-3.5 w-3.5" />
                  工艺建议
                </h3>
                <div className="space-y-2">
                  {simResult.tips.slice(0, 3).map((tip, idx) => (
                    <p key={idx} className="text-[11px] text-amber-400/80 leading-relaxed">
                      • {tip}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
