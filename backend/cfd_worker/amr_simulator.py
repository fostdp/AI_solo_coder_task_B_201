import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AMRGrid:
    levels: int
    base_cells_x: int
    base_cells_y: int
    cell_data: Dict[int, np.ndarray]
    level_offsets: Dict[int, Tuple[int, int]]
    active_cells: Dict[int, np.ndarray]


class AMRSimulator:
    def __init__(
        self,
        domain_size: Tuple[float, float] = (200.0, 200.0),
        base_cells: Tuple[int, int] = (40, 40),
        max_levels: int = 3,
        refine_ratio: int = 2,
        refinement_threshold: float = 0.05,
    ):
        self.domain_size = domain_size
        self.base_cells = base_cells
        self.max_levels = max_levels
        self.refine_ratio = refine_ratio
        self.refinement_threshold = refinement_threshold

        self.grid = self._initialize_grid()

    def _initialize_grid(self) -> AMRGrid:
        cell_data = {}
        active_cells = {}

        level_offsets = {
            0: (0, 0),
        }

        nx, ny = self.base_cells
        for level in range(self.max_levels):
            cell_data[level] = {
                "pressure": np.zeros((nx, ny), dtype=np.float64),
                "velocity_x": np.zeros((nx, ny), dtype=np.float64),
                "velocity_y": np.zeros((nx, ny), dtype=np.float64),
                "temperature": np.full((nx, ny), 1500.0, dtype=np.float64),
                "filling_fraction": np.zeros((nx, ny), dtype=np.float64),
                "refined": np.zeros((nx, ny), dtype=bool),
            }
            active_cells[level] = np.ones((nx, ny), dtype=bool)
            if level == 0:
                active_cells[level][:] = True
            else:
                active_cells[level][:] = False

            nx *= self.refine_ratio
            ny *= self.refine_ratio

        return AMRGrid(
            levels=self.max_levels,
            base_cells_x=self.base_cells[0],
            base_cells_y=self.base_cells[1],
            cell_data=cell_data,
            level_offsets=level_offsets,
            active_cells=active_cells,
        )

    def _needs_refinement(self, level: int, i: int, j: int, field_name: str = "filling_fraction") -> bool:
        if level >= self.max_levels - 1:
            return False

        data = self.grid.cell_data[level]
        field = data[field_name]
        frac = field[i, j]

        if frac < 0.05 or frac > 0.95:
            return False

        if level == 0:
            return frac > 0.01 and frac < 0.99

        return True

    def refine_cells(self, field_name: str = "filling_fraction"):
        for level in range(self.max_levels - 1):
            data = self.grid.cell_data[level]
            active = self.grid.active_cells[level]
            field = data[field_name]

            for i in range(field.shape[0]):
                for j in range(field.shape[1]):
                    if not active[i, j]:
                        continue

                    if self._needs_refinement(level, i, j, field_name):
                        data["refined"][i, j] = True
                        self._activate_children(level, i, j)

    def _activate_children(self, level: int, i: int, j: int):
        child_level = level + 1
        if child_level >= self.max_levels:
            return

        rr = self.refine_ratio
        child_i_start = i * rr
        child_j_start = j * rr

        child_active = self.grid.active_cells[child_level]
        child_data = self.grid.cell_data[child_level]
        parent_data = self.grid.cell_data[level]

        for di in range(rr):
            for dj in range(rr):
                ci = child_i_start + di
                cj = child_j_start + dj
                if ci < child_active.shape[0] and cj < child_active.shape[1]:
                    child_active[ci, cj] = True
                    for field_name in ["pressure", "velocity_x", "velocity_y", "temperature", "filling_fraction"]:
                        child_data[field_name][ci, cj] = parent_data[field_name][i, j]

    def get_cell_size(self, level: int) -> Tuple[float, float]:
        dx = self.domain_size[0] / (self.base_cells[0] * (self.refine_ratio ** level))
        dy = self.domain_size[1] / (self.base_cells[1] * (self.refine_ratio ** level))
        return dx, dy

    def get_filling_front_position(self) -> Tuple[float, float]:
        max_x = 0.0
        max_y = 0.0
        dx0, dy0 = self._get_cell_size_level_0()

        for level in range(self.max_levels):
            active = self.grid.active_cells[level]
            filling = self.grid.cell_data[level]["filling_fraction"]

            if not np.any(active):
                continue

            mask = active & (filling > 0.5)
            if not np.any(mask):
                continue

            rr = self.refine_ratio ** level
            indices = np.where(mask)
            if len(indices[0]) > 0:
                max_idx = np.max(indices[0])
                max_j = np.max(indices[1])
                x_pos = (max_idx + 0.5) * (dx0 / rr)
                y_pos = (max_j + 0.5) * (dy0 / rr)
                if x_pos > max_x:
                    max_x = x_pos
                if y_pos > max_y:
                    max_y = y_pos

        return (max_x, max_y)

    def _get_cell_size_level_0(self) -> Tuple[float, float]:
        dx = self.domain_size[0] / self.base_cells[0]
        dy = self.domain_size[1] / self.base_cells[1]
        return dx, dy

    def get_active_cell_count(self) -> Dict[int, int]:
        counts = {}
        for level in range(self.max_levels):
            counts[level] = int(np.sum(self.grid.active_cells[level]))
        return counts

    def get_total_cells(self) -> int:
        total = 0
        for count in self.get_active_cell_count().values():
            total += count
        return total

    def get_amr_efficiency(self) -> float:
        active = self.get_total_cells()
        finest_total = self.base_cells[0] * self.base_cells[1] * (self.refine_ratio ** (self.max_levels - 1)) ** 2
        if finest_total == 0:
            return 1.0
        return active / finest_total


class AMRFluidSolver:
    def __init__(
        self,
        sim: AMRSimulator,
        fluid_density: float = 7800.0,
        fluid_viscosity: float = 4.5e-3,
        gravity: float = 9.81,
    ):
        self.sim = sim
        self.density = fluid_density
        self.viscosity = fluid_viscosity
        self.gravity = gravity

    def step_filling(
        self,
        dt: float,
        pouring_velocity: Tuple[float, float] = (0.0, -1.5),
        inlet_pos: Tuple[float, float] = (100.0, 200.0),
        inlet_radius: float = 15.0,
    ) -> float:
        self._apply_inlet(inlet_pos, inlet_radius, pouring_velocity)
        self._advect_filling(dt)
        self.sim.refine_cells("filling_fraction")
        return float(np.mean(self.sim.grid.cell_data[0]["filling_fraction"]))

    def _apply_inlet(
        self,
        inlet_pos: Tuple[float, float],
        inlet_radius: float,
        velocity: Tuple[float, float],
    ):
        for level in range(self.sim.max_levels):
            data = self.sim.grid.cell_data[level]
            active = self.sim.grid.active_cells[level]
            dx, dy = self.sim.get_cell_size(level)

            rr = self.sim.refine_ratio ** level

            for i in range(data["filling_fraction"].shape[0]):
                for j in range(data["filling_fraction"].shape[1]):
                    if not active[i, j]:
                        continue

                    x = (i + 0.5) * dx
                    y = (j + 0.5) * dy
                    dist = np.sqrt((x - inlet_pos[0]) ** 2 + (y - inlet_pos[1]) ** 2)

                    if dist < inlet_radius:
                        data["filling_fraction"][i, j] = min(1.0, data["filling_fraction"][i, j] + 0.1)
                        data["velocity_x"][i, j] = velocity[0]
                        data["velocity_y"][i, j] = velocity[1]

    def _advect_filling(self, dt: float):
        for level in range(self.sim.max_levels):
            data = self.sim.grid.cell_data[level]
            active = self.sim.grid.active_cells[level]

            filling = data["filling_fraction"].copy()
            vel_x = data["velocity_x"]
            vel_y = data["velocity_y"]
            dx, dy = self.sim.get_cell_size(level)

            nx, ny = filling.shape

            for i in range(1, nx - 1):
                for j in range(1, ny - 1):
                    if not active[i, j]:
                        continue

                    vx = vel_x[i, j]
                    vy = vel_y[i, j]

                    if vx > 0:
                        grad_x = (filling[i, j] - filling[i - 1, j]) / dx
                    else:
                        grad_x = (filling[i + 1, j] - filling[i, j]) / dx

                    if vy > 0:
                        grad_y = (filling[i, j] - filling[i, j - 1]) / dy
                    else:
                        grad_y = (filling[i, j + 1] - filling[i, j]) / dy

                    flux = vx * grad_x + vy * grad_y + self.gravity * 0.01
                    new_frac = filling[i, j] - dt * flux

                    data["filling_fraction"][i, j] = np.clip(new_frac, 0.0, 1.0)


def run_amr_simulation(
    domain_size: Tuple[float, float] = (200.0, 200.0),
    base_cells: Tuple[int, int] = (40, 40),
    max_levels: int = 3,
    total_time: float = 10.0,
    dt: float = 0.1,
    fluid_density: float = 7800.0,
    fluid_viscosity: float = 4.5e-3,
    pouring_velocity: Tuple[float, float] = (0.0, -1.5),
    inlet_pos: Tuple[float, float] = (100.0, 200.0),
    inlet_radius: float = 15.0,
    progress_callback=None,
) -> Dict[str, Any]:
    sim = AMRSimulator(
        domain_size=domain_size,
        base_cells=base_cells,
        max_levels=max_levels,
    )
    solver = AMRFluidSolver(
        sim,
        fluid_density=fluid_density,
        fluid_viscosity=fluid_viscosity,
    )

    num_steps = int(total_time / dt)
    time_points = []
    filling_progress = []
    cell_counts = []
    amr_efficiencies = []
    front_positions = []

    for step in range(num_steps):
        current_time = step * dt
        avg_filling = solver.step_filling(
            dt,
            pouring_velocity=pouring_velocity,
            inlet_pos=inlet_pos,
            inlet_radius=inlet_radius,
        )

        time_points.append(round(current_time, 2))
        filling_progress.append(round(avg_filling * 100, 2))
        cell_counts.append(sim.get_total_cells())
        amr_efficiencies.append(round(sim.get_amr_efficiency() * 100, 2))

        front_x, front_y = sim.get_filling_front_position()
        front_positions.append((round(front_x, 2), round(front_y, 2)))

        if progress_callback and step % 5 == 0:
            progress_callback(step / num_steps, {
                "time": current_time,
                "filling_progress": avg_filling * 100,
                "active_cells": sim.get_total_cells(),
            })

    final_fillings = {}
    for level in range(max_levels):
        final_fillings[level] = sim.grid.cell_data[level]["filling_fraction"].tolist()

    return {
        "simulation_config": {
            "domain_size": domain_size,
            "base_cells": base_cells,
            "max_levels": max_levels,
            "refine_ratio": sim.refine_ratio,
            "total_time": total_time,
            "dt": dt,
            "fluid_density": fluid_density,
            "fluid_viscosity": fluid_viscosity,
        },
        "time_series": {
            "time_points": time_points,
            "filling_progress_percent": filling_progress,
            "active_cell_counts": cell_counts,
            "amr_efficiency_percent": amr_efficiencies,
            "front_positions": front_positions,
        },
        "final_state": {
            "filling_fraction_levels": final_fillings,
            "active_cell_counts": sim.get_active_cell_count(),
            "total_active_cells": sim.get_total_cells(),
            "amr_efficiency": round(sim.get_amr_efficiency(), 4),
        },
        "performance": {
            "total_steps": num_steps,
            "memory_savings_percent": round((1 - sim.get_amr_efficiency()) * 100, 1),
            "speedup_estimate": round(1.0 / max(sim.get_amr_efficiency(), 0.01), 1),
        },
    }
