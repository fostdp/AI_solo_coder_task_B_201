import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from cfd_worker.amr_simulator import (
    AMRSimulator,
    AMRFluidSolver,
    run_amr_simulation,
)
from cfd_worker.service import cfd_worker_service


class TestAMRSimulator:
    """CFD Worker模块测试 - AMR模拟器验证"""

    def test_simulator_initialization(self):
        sim = AMRSimulator(
            domain_size=(200.0, 200.0),
            base_cells=(40, 40),
            max_levels=3,
        )
        assert sim is not None
        assert sim.max_levels == 3
        assert sim.domain_size == (200.0, 200.0)

    def test_get_cell_size(self):
        sim = AMRSimulator(
            domain_size=(200.0, 200.0),
            base_cells=(40, 40),
            max_levels=3,
        )
        dx0, dy0 = sim.get_cell_size(0)
        assert dx0 == 200.0 / 40
        assert dy0 == 200.0 / 40

        dx1, dy1 = sim.get_cell_size(1)
        assert dx1 == dx0 / 2
        assert dy1 == dy0 / 2

    def test_get_active_cell_count(self):
        sim = AMRSimulator(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
        )
        counts = sim.get_active_cell_count()
        assert 0 in counts
        assert counts[0] > 0

    def test_get_total_cells(self):
        sim = AMRSimulator(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
        )
        total = sim.get_total_cells()
        assert total > 0

    def test_amr_efficiency(self):
        sim = AMRSimulator(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
        )
        efficiency = sim.get_amr_efficiency()
        assert 0 < efficiency <= 1.0

    def test_refine_cells(self):
        sim = AMRSimulator(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
        )
        sim.grid.cell_data[0]["filling_fraction"][5:10, 5:10] = 0.5
        before = sim.get_total_cells()
        sim.refine_cells("filling_fraction")
        after = sim.get_total_cells()
        assert after >= before

    def test_get_filling_front_position(self):
        sim = AMRSimulator(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
        )
        sim.grid.cell_data[0]["filling_fraction"][:5, :] = 1.0
        x, y = sim.get_filling_front_position()
        assert x >= 0
        assert y >= 0


class TestAMRFluidSolver:
    """CFD Worker模块测试 - 流体求解器验证"""

    def test_solver_initialization(self):
        sim = AMRSimulator(
            domain_size=(200.0, 200.0),
            base_cells=(40, 40),
            max_levels=2,
        )
        solver = AMRFluidSolver(sim, fluid_density=7800.0, fluid_viscosity=4.5e-3)
        assert solver is not None
        assert solver.density == 7800.0

    def test_step_filling(self):
        sim = AMRSimulator(
            domain_size=(200.0, 200.0),
            base_cells=(40, 40),
            max_levels=2,
        )
        solver = AMRFluidSolver(sim)
        avg_fill = solver.step_filling(
            dt=0.1,
            pouring_velocity=(0.0, -1.5),
            inlet_pos=(100.0, 200.0),
            inlet_radius=15.0,
        )
        assert 0 <= avg_fill <= 1.0


class TestAMRSimulationRun:
    """CFD Worker模块测试 - 完整仿真运行验证"""

    def test_run_amr_simulation_returns_result(self):
        result = run_amr_simulation(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
            total_time=2.0,
            dt=0.2,
        )
        assert result is not None
        assert "simulation_config" in result
        assert "time_series" in result
        assert "final_state" in result
        assert "performance" in result

    def test_simulation_time_series_has_data(self):
        result = run_amr_simulation(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
            total_time=2.0,
            dt=0.5,
        )
        ts = result["time_series"]
        assert len(ts["time_points"]) > 0
        assert len(ts["filling_progress_percent"]) == len(ts["time_points"])
        assert len(ts["active_cell_counts"]) == len(ts["time_points"])

    def test_simulation_filling_progress_increases(self):
        result = run_amr_simulation(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
            total_time=3.0,
            dt=0.5,
        )
        progress = result["time_series"]["filling_progress_percent"]
        if len(progress) >= 2:
            assert progress[-1] >= progress[0]

    def test_simulation_performance_metrics(self):
        result = run_amr_simulation(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
            total_time=1.0,
            dt=0.5,
        )
        perf = result["performance"]
        assert "total_steps" in perf
        assert "memory_savings_percent" in perf
        assert perf["total_steps"] > 0

    def test_simulation_final_state(self):
        result = run_amr_simulation(
            domain_size=(100.0, 100.0),
            base_cells=(20, 20),
            max_levels=2,
            total_time=1.0,
            dt=0.5,
        )
        final = result["final_state"]
        assert "total_active_cells" in final
        assert "amr_efficiency" in final
        assert final["total_active_cells"] > 0
        assert 0 < final["amr_efficiency"] <= 1.0


class TestCFDWorkerService:
    """CFD Worker模块测试 - 服务层验证"""

    def test_run_sync_returns_result(self):
        params = {
            "domain_size": [100.0, 100.0],
            "base_cells": [20, 20],
            "max_levels": 2,
            "total_time": 1.0,
            "dt": 0.5,
        }
        result = cfd_worker_service.run_sync(params)
        assert result is not None
        assert "status" in result
        assert result["status"] == "completed"
        assert "result" in result

    def test_get_stats(self):
        stats = cfd_worker_service.get_stats()
        assert stats is not None
        assert "num_workers" in stats
        assert "total_jobs" in stats

    def test_list_jobs(self):
        jobs = cfd_worker_service.list_jobs(limit=10)
        assert isinstance(jobs, list)

    def test_submit_simulation(self):
        params = {
            "domain_size": [100.0, 100.0],
            "base_cells": [20, 20],
            "max_levels": 2,
            "total_time": 1.0,
            "dt": 0.5,
        }
        result = cfd_worker_service.submit_simulation(params)
        assert result is not None
        assert "job_id" in result
        assert "status" in result

    def test_get_job_status_invalid(self):
        status = cfd_worker_service.get_status("nonexistent_job_id")
        assert status is None

    def test_get_job_result_invalid(self):
        result = cfd_worker_service.get_result("nonexistent_job_id")
        assert result is None
