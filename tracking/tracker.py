"""
Experiment Tracking System

MLflow-style experiment management for AEGIS.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Run:
    """An experiment run."""
    run_id: str
    experiment_name: str
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, List[float]] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


class ExperimentTracker:
    """Track experiments and metrics."""

    def __init__(self, tracking_dir: str = "./experiments/tracking"):
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)

        self.current_run: Optional[Run] = None
        self.runs: Dict[str, Run] = {}

    def start_run(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Start new experiment run."""
        run_id = f"run_{int(time.time())}_{experiment_name}"

        self.current_run = Run(
            run_id=run_id,
            experiment_name=experiment_name,
            config=config
        )

        self.runs[run_id] = self.current_run

        return run_id

    def log_metric(self, name: str, value: float, step: Optional[int] = None):
        """Log a metric."""
        if not self.current_run:
            return

        if name not in self.current_run.metrics:
            self.current_run.metrics[name] = []

        self.current_run.metrics[name].append(value)

    def log_config(self, config: Dict[str, Any]):
        """Log configuration."""
        if self.current_run:
            self.current_run.config.update(config)

    def save_artifact(self, name: str, data: Any):
        """Save artifact."""
        if not self.current_run:
            return

        artifact_path = self.tracking_dir / self.current_run.run_id / name

        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        with open(artifact_path, 'w') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))

        self.current_run.artifacts[name] = str(artifact_path)

    def end_run(self):
        """End current run."""
        if self.current_run:
            self.current_run.end_time = time.time()

            # Save run metadata
            self._save_run(self.current_run)

            self.current_run = None

    def _save_run(self, run: Run):
        """Save run to disk."""
        run_dir = self.tracking_dir / run.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            'run_id': run.run_id,
            'experiment_name': run.experiment_name,
            'config': run.config,
            'start_time': run.start_time,
            'end_time': run.end_time,
            'duration': (run.end_time or time.time()) - run.start_time
        }

        with open(run_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save metrics
        with open(run_dir / 'metrics.json', 'w') as f:
            json.dump(run.metrics, f, indent=2)

    def compare_runs(self, run_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple runs."""
        comparison = {}

        for run_id in run_ids:
            if run_id in self.runs:
                run = self.runs[run_id]
                comparison[run_id] = {
                    'experiment': run.experiment_name,
                    'final_metrics': {
                        name: values[-1] if values else 0
                        for name, values in run.metrics.items()
                    }
                }

        return comparison
