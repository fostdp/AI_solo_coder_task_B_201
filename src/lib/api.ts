const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const WS_BASE = import.meta.env.VITE_WS_BASE || "ws://localhost:8000";

export interface SensorData {
  id?: string;
  casting_id: string;
  timestamp: string;
  wax_temperature: number;
  pouring_temperature: number;
  shell_permeability: number;
  filling_progress: number;
}

export interface DefectPrediction {
  id: string;
  casting_id: string;
  position: { x: number; y: number; z: number };
  niyama_value: number;
  volume: number;
  severity: "low" | "medium" | "high" | "critical";
  defect_type: "shrinkage_cavity" | "shrinkage_porosity";
  detected_at: string;
  mean_temperature?: number;
}

export interface AlertItem {
  id: string;
  casting_id: string;
  alert_type: string;
  severity: "warning" | "error" | "critical";
  message: string;
  data: Record<string, any>;
  acknowledged: boolean;
  acknowledged_at?: string;
  created_at: string;
}

export interface CastingTask {
  id: string;
  name: string;
  status: string;
  created_at: string;
  completed_at?: string;
  parameters: Record<string, any>;
}

export interface SimulationStatus {
  casting_id: string | null;
  status: string;
  filling_progress: number;
  current_step: number;
  total_steps: number;
}

export interface TempPoint {
  x: number;
  y: number;
  z: number;
  temperature: number;
}

export interface NiyamaPoint {
  x: number;
  y: number;
  z: number;
  niyama: number;
}

export interface SimulationStep {
  step: number;
  filling_ratio: number;
  heat: {
    points: TempPoint[];
    max_temperature: number;
    min_temperature: number;
    mean_temperature: number;
  };
  niyama: {
    points: NiyamaPoint[];
    mean_niyama: number;
  };
  defects: DefectPrediction[];
  alerts: AlertItem[];
}

async function request<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  getCastings: () => request<CastingTask[]>("/api/castings"),
  createCasting: (name: string, parameters: Record<string, any>) =>
    request<CastingTask>("/api/castings", {
      method: "POST",
      body: JSON.stringify({ name, parameters }),
    }),
  getLatestSensor: (castingId: string) =>
    request<SensorData>(`/api/sensor/latest?casting_id=${castingId}`),
  getSensorHistory: (castingId: string, limit = 100) =>
    request<SensorData[]>(`/api/sensor/history?casting_id=${castingId}&limit=${limit}`),
  getSimulationStatus: () => request<SimulationStatus>("/api/simulation/status"),
  startSimulation: (castingId: string) =>
    request("/api/simulation/start", {
      method: "POST",
      body: JSON.stringify({ casting_id: castingId }),
    }),
  stopSimulation: () => request("/api/simulation/stop", { method: "POST" }),
  getFillingData: (castingId: string) =>
    request<any[]>(`/api/simulation/filling?casting_id=${castingId}`),
  getTemperatureData: (castingId: string) =>
    request<any[]>(`/api/simulation/temperature?casting_id=${castingId}`),
  getDefects: (castingId: string, severity?: string) =>
    request<DefectPrediction[]>(
      `/api/defects/predictions?casting_id=${castingId}${severity ? `&severity=${severity}` : ""}`
    ),
  getNiyama: (castingId: string) =>
    request<any[]>(`/api/defects/niyama?casting_id=${castingId}`),
  getAlerts: (castingId?: string, unacknowledgedOnly = false) =>
    request<AlertItem[]>(
      `/api/alerts?${castingId ? `casting_id=${castingId}&` : ""}unacknowledged_only=${unacknowledgedOnly}`
    ),
  acknowledgeAlert: (alertId: string) =>
    request(`/api/alerts/${alertId}/acknowledge`, { method: "POST" }),
};

export const ws = {
  simulationUrl: `${WS_BASE}/ws/simulation`,
  alertsUrl: `${WS_BASE}/ws/alerts`,
};

export interface CraftDefectRates {
  shrinkage_cavity: number;
  shrinkage_porosity: number;
  gas_porosity: number;
  inclusion: number;
  cold_shut: number;
  misrun: number;
  [key: string]: number;
}

export interface CraftInfo {
  id: string;
  name: string;
  english_name: string;
  dynasty?: string;
  period?: string;
  era?: string;
  description: string;
  representative_artifacts?: string[];
  applications?: string[];
  complexity: number;
  skill_required: number;
  production_cycle_days: number;
  material_cost: number;
  typical_defects: string[];
  defect_rates: CraftDefectRates;
  overall_defect_rate: number;
  dimensional_accuracy_mm: number;
  surface_roughness_ra: number;
  minimum_wall_thickness_mm: number;
  max_complexity_score: number;
}

export interface ComparisonMetric {
  metric: string;
  label: string;
  unit: string;
  values: Record<string, number>;
  lower_is_better?: boolean;
}

export interface ComparisonResult {
  crafts: CraftInfo[];
  comparison_metrics: ComparisonMetric[];
  defect_radar: Record<string, CraftDefectRates>;
  defect_type_comparison: { type: string; label: string; values: Record<string, number> }[];
}

export interface AncientVsModernResult {
  ancient_crafts: CraftInfo[];
  modern_crafts: CraftInfo[];
  summary: {
    avg_ancient_defect_rate: number;
    avg_modern_defect_rate: number;
    defect_reduction_percent: number;
    avg_ancient_accuracy_mm: number;
    avg_modern_accuracy_mm: number;
    accuracy_improvement_factor: number;
  };
  key_insights: string[];
}

export interface PermeabilityImpactResult {
  parameters: {
    alloy_type: string;
    pouring_temp: number;
    shell_thickness_layers: number;
    optimal_permeability: number;
  };
  permeability_values: number[];
  filling_quality_scores: number[];
  filling_speed_scores: number[];
  defect_rates_percent: number[];
  gas_porosity_rates_percent: number[];
  shrinkage_rates_percent: number[];
  analysis: {
    best_quality_permeability: number;
    best_quality_score: number;
    lowest_defect_permeability: number;
    lowest_defect_rate: number;
    worst_quality_permeability: number;
    worst_quality_score: number;
  };
  insights: string[];
  shell_materials_comparison: {
    name: string;
    permeability: number;
    strength: string;
    cost: number;
    surface_quality: number;
  }[];
}

export interface WaxMoldTemplate {
  id: string;
  name: string;
  category: string;
  difficulty: number;
  description: string;
  default_params: Record<string, any>;
  param_ranges: Record<string, { min: number; max: number; step: number; label: string }>;
  historical_note: string;
}

export interface CastingMaterial {
  id: string;
  name: string;
  pouring_temp: number;
  density: number;
  viscosity: number;
  shrinkage_rate: number;
  color_hex: string;
  historical: boolean;
}

export interface ShellMaterial {
  id: string;
  name: string;
  permeability: number;
  thermal_conductivity: number;
  strength: number;
  cost: number;
  layers: number;
  historical: boolean;
}

export interface GeometryPart {
  type: string;
  name: string;
  top_radius?: number;
  bottom_radius?: number;
  radius?: number;
  tube_radius?: number;
  height?: number;
  x_radius?: number;
  y_radius?: number;
  z_radius?: number;
  y_offset?: number;
  x?: number;
  z?: number;
  diameter?: number;
}

export interface GeometryResult {
  template_id: string;
  template_name: string;
  params: Record<string, any>;
  parts: GeometryPart[];
  properties: {
    volume_cm3: number;
    surface_area_cm2: number;
    estimated_weight_g: number;
    complexity_score: number;
    difficulty: number;
  };
}

export interface SimDefect {
  id: string;
  position: { x: number; y: number; z: number };
  volume_cm3: number;
  severity: string;
  type: string;
}

export interface SimStep {
  step: number;
  filling_progress: number;
  avg_temperature: number;
  front_temperature: number;
}

export interface SimulationResult {
  simulation_id: string;
  template_id: string;
  template_name: string;
  material: CastingMaterial;
  shell: ShellMaterial;
  geometry: GeometryResult;
  casting_parameters: {
    pouring_temp: number;
    optimal_temp: number;
    temp_deviation_percent: number;
  };
  results: {
    overall_defect_rate: number;
    filling_quality_score: number;
    defect_breakdown: {
      gas_porosity_rate: number;
      shrinkage_rate: number;
      cold_shut_rate: number;
      inclusion_rate: number;
    };
    detected_defects: SimDefect[];
    total_defect_volume: number;
  };
  simulation_steps: SimStep[];
  tips: string[];
  created_at: string;
}

export const craftsApi = {
  getAncientCrafts: () => request<CraftInfo[]>("/api/crafts/ancient"),
  getModernCrafts: () => request<CraftInfo[]>("/api/crafts/modern"),
  getAllCrafts: () => request<CraftInfo[]>("/api/crafts/all"),
  getCraftDetail: (id: string) => request<CraftInfo>(`/api/crafts/${id}`),
  compareCrafts: (ids: string[]) =>
    request<ComparisonResult>(`/api/crafts/compare?craft_ids=${ids.join(",")}`),
  getAncientVsModern: () => request<AncientVsModernResult>("/api/crafts/ancient-vs-modern"),
  calculateDefectRate: (craftId: string, pouringTemp: number, permeability: number, alloyType = "bronze") =>
    request("/api/crafts/calculate-defect-rate", {
      method: "POST",
      body: JSON.stringify({
        craft_id: craftId,
        pouring_temp: pouringTemp,
        shell_permeability: permeability,
        alloy_type: alloyType,
      }),
    }),
};

export const permeabilityApi = {
  analyzeImpact: (alloyType = "bronze", pouringTemp = 1180, shellThickness = 9) =>
    request<PermeabilityImpactResult>(
      `/api/permeability/impact?alloy_type=${alloyType}&pouring_temp=${pouringTemp}&shell_thickness=${shellThickness}`
    ),
  analyzeHistorical: (castingId: string) =>
    request(`/api/permeability/historical/${castingId}`),
  compareScenarios: (scenarios: any[]) =>
    request("/api/permeability/compare", {
      method: "POST",
      body: JSON.stringify({ scenarios }),
    }),
};

export const virtualApi = {
  getTemplates: () => request<WaxMoldTemplate[]>("/api/virtual/templates"),
  getTemplate: (id: string) => request<WaxMoldTemplate>(`/api/virtual/templates/${id}`),
  getMaterials: () => request<CastingMaterial[]>("/api/virtual/materials"),
  getShells: () => request<ShellMaterial[]>("/api/virtual/shells"),
  generateGeometry: (templateId: string, params: Record<string, any>) =>
    request<GeometryResult>("/api/virtual/geometry", {
      method: "POST",
      body: JSON.stringify({ template_id: templateId, params }),
    }),
  simulateCasting: (templateId: string, params: Record<string, any>, materialId: string, shellId: string, pouringTemp?: number) =>
    request<SimulationResult>("/api/virtual/simulate", {
      method: "POST",
      body: JSON.stringify({
        template_id: templateId,
        params,
        material_id: materialId,
        shell_id: shellId,
        pouring_temp: pouringTemp,
      }),
    }),
  getExperiments: (limit = 20) =>
    request(`/api/virtual/experiments?limit=${limit}`),
  getExperiment: (id: string) => request(`/api/virtual/experiments/${id}`),
  saveExperiment: (experiment: Record<string, any>) =>
    request("/api/virtual/experiments", {
      method: "POST",
      body: JSON.stringify(experiment),
    }),
};

export const processComparatorApi = {
  getAncientCrafts: () => request<CraftInfo[]>("/api/process-comparator/ancient"),
  getModernCrafts: () => request<CraftInfo[]>("/api/process-comparator/modern"),
  getAllCrafts: () => request<CraftInfo[]>("/api/process-comparator/all"),
  getCraftDetail: (id: string) => request<CraftInfo>(`/api/process-comparator/${id}`),
  compareCrafts: (ids: string[]) =>
    request<ComparisonResult>(`/api/process-comparator/compare?craft_ids=${ids.join(",")}`),
  calculateDefectRate: (craftId: string, pouringTemp: number, permeability: number, alloyType = "bronze") =>
    request("/api/process-comparator/calculate-defect-rate", {
      method: "POST",
      body: JSON.stringify({
        craft_id: craftId,
        pouring_temp: pouringTemp,
        shell_permeability: permeability,
        alloy_type: alloyType,
      }),
    }),
};

export const eraComparatorApi = {
  listEras: () => request<any[]>("/api/era-comparator/eras"),
  getEra: (id: string) => request<any>(`/api/era-comparator/eras/${id}`),
  getAncientVsModern: () => request<AncientVsModernResult>("/api/era-comparator/ancient-vs-modern"),
};

export const permeabilityAnalyzerApi = {
  analyzeImpact: (alloyType = "bronze", pouringTemp = 1180, shellThickness = 9) =>
    request<PermeabilityImpactResult>(
      `/api/permeability-analyzer/impact?alloy_type=${alloyType}&pouring_temp=${pouringTemp}&shell_thickness=${shellThickness}`
    ),
  analyzeHistorical: (castingId: string) =>
    request(`/api/permeability-analyzer/historical/${castingId}`),
  compareScenarios: (scenarios: any[]) =>
    request("/api/permeability-analyzer/compare", {
      method: "POST",
      body: JSON.stringify({ scenarios }),
    }),
};

export const vrLostWaxApi = {
  getTemplates: (audience?: string, category?: string) => {
    let url = "/api/vr-lost-wax/templates";
    const params = new URLSearchParams();
    if (audience) params.set("audience", audience);
    if (category) params.set("category", category);
    const qs = params.toString();
    if (qs) url += `?${qs}`;
    return request<WaxMoldTemplate[]>(url);
  },
  getTemplate: (id: string) => request<WaxMoldTemplate>(`/api/vr-lost-wax/templates/${id}`),
  getMaterials: () => request<CastingMaterial[]>("/api/vr-lost-wax/materials"),
  getShells: () => request<ShellMaterial[]>("/api/vr-lost-wax/shell-materials"),
  getSimpleModePresets: () => request<any[]>("/api/vr-lost-wax/simple-mode/presets"),
  getSimpleModeParams: () => request<any>("/api/vr-lost-wax/simple-mode/params"),
  applySimpleMode: (templateId: string, sizeLevel: number, ornamentLevel: number, thicknessLevel: number) =>
    request("/api/vr-lost-wax/simple-mode/apply", {
      method: "POST",
      body: JSON.stringify({
        template_id: templateId,
        size_level: sizeLevel,
        ornament_level: ornamentLevel,
        thickness_level: thicknessLevel,
      }),
    }),
  applyPreset: (templateId: string, presetId: string) =>
    request("/api/vr-lost-wax/simple-mode/preset", {
      method: "POST",
      body: JSON.stringify({ template_id: templateId, preset_id: presetId }),
    }),
  generateGeometry: (templateId: string, params: Record<string, any>) =>
    request<GeometryResult>("/api/vr-lost-wax/geometry", {
      method: "POST",
      body: JSON.stringify({ template_id: templateId, params }),
    }),
  simulateCasting: (templateId: string, params: Record<string, any>, materialId: string, shellId: string, pouringTemp?: number) =>
    request<SimulationResult>("/api/vr-lost-wax/simulate", {
      method: "POST",
      body: JSON.stringify({
        template_id: templateId,
        params,
        material_id: materialId,
        shell_id: shellId,
        pouring_temp: pouringTemp,
      }),
    }),
  getExperiments: (limit = 20) =>
    request(`/api/vr-lost-wax/experiments?limit=${limit}`),
  getExperiment: (id: string) => request(`/api/vr-lost-wax/experiments/${id}`),
};

export const cfdWorkerApi = {
  submitSimulation: (params: Record<string, any>) =>
    request("/api/cfd-worker/submit", {
      method: "POST",
      body: JSON.stringify(params),
    }),
  getJobStatus: (jobId: string) => request(`/api/cfd-worker/jobs/${jobId}/status`),
  getJobResult: (jobId: string) => request(`/api/cfd-worker/jobs/${jobId}/result`),
  cancelJob: (jobId: string) =>
    request(`/api/cfd-worker/jobs/${jobId}`, { method: "DELETE" }),
  listJobs: (limit = 50) => request(`/api/cfd-worker/jobs?limit=${limit}`),
  getStats: () => request("/api/cfd-worker/stats"),
  runSync: (params: Record<string, any>) =>
    request("/api/cfd-worker/run-sync", {
      method: "POST",
      body: JSON.stringify(params),
    }),
};
