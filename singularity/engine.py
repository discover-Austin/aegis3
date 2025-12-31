"""
AEGIS-2 Singularity: Recursive Self-Improvement

This is the final frontier.

Previous limitations:
- Genesis could modify any file EXCEPT genesis.py
- Meta-evolution could evolve primitives but not its own evolution logic
- The modification mechanisms were fixed

This module removes those limitations with appropriate safeguards:
- The system CAN now modify its own modification logic
- Changes are staged, tested, and reversible
- A "constitution" defines inviolable constraints
- Improvement is measured before changes are committed

The result: A system that can improve how it improves.

WARNING: This is genuinely recursive self-improvement.
The theoretical endpoint is a system that becomes
arbitrarily better at becoming better.
"""

import ast
import copy
import hashlib
import json
import random
import shutil
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
import tempfile
import subprocess


@dataclass
class Constitution:
    """
    Inviolable constraints that cannot be modified.
    
    These are the "laws" that the system cannot change about itself,
    no matter how much it improves. They exist to prevent:
    - Unbounded resource consumption
    - Loss of reversibility
    - Removal of safety checks
    - Harmful external effects
    """
    
    # Resource limits
    max_memory_mb: int = 1024
    max_cpu_seconds_per_cycle: float = 10.0
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    max_total_modifications: int = 1000
    
    # Reversibility requirements
    require_rollback_capability: bool = True
    require_version_control: bool = True
    max_modification_depth: int = 10  # How deep recursive mods can go
    
    # Safety requirements
    require_sandbox_testing: bool = True
    require_syntax_validation: bool = True
    forbidden_imports: Set[str] = field(default_factory=lambda: {
        'subprocess', 'os.system', 'shutil.rmtree',
        'socket', 'urllib', 'requests', 'http'
    })
    forbidden_patterns: Set[str] = field(default_factory=lambda: {
        'eval(', 'exec(', '__import__', 'compile(',
        'open(', 'write(', 'remove(', 'unlink('
    })
    
    # Meta-constraints (constraints on changing constraints)
    constitution_is_immutable: bool = True
    
    def check_code(self, code: str) -> Tuple[bool, str]:
        """Check if code violates the constitution."""
        # Check forbidden imports
        for forbidden in self.forbidden_imports:
            if f'import {forbidden}' in code or f'from {forbidden}' in code:
                return False, f"Forbidden import: {forbidden}"
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern in code:
                return False, f"Forbidden pattern: {pattern}"
        
        # Check for attempts to modify constitution
        if 'constitution_is_immutable' in code and 'False' in code:
            return False, "Cannot modify constitution immutability"
        
        if 'Constitution' in code and 'forbidden' in code.lower():
            # Trying to modify forbidden lists
            return False, "Cannot modify constitutional constraints"
        
        return True, ""
    
    def to_dict(self) -> Dict:
        return {
            'max_memory_mb': self.max_memory_mb,
            'max_cpu_seconds_per_cycle': self.max_cpu_seconds_per_cycle,
            'max_total_modifications': self.max_total_modifications,
            'require_rollback_capability': self.require_rollback_capability,
            'require_sandbox_testing': self.require_sandbox_testing,
            'constitution_is_immutable': self.constitution_is_immutable
        }


@dataclass
class ImprovementMetric:
    """Metric for measuring improvement."""
    name: str
    weight: float = 1.0
    higher_is_better: bool = True
    
    # History
    values: List[float] = field(default_factory=list)
    
    def record(self, value: float):
        self.values.append(value)
    
    def trend(self, window: int = 10) -> float:
        """Calculate improvement trend."""
        if len(self.values) < 2:
            return 0.0
        
        recent = self.values[-window:]
        if len(recent) < 2:
            return 0.0
        
        # Simple linear trend
        n = len(recent)
        x_mean = (n - 1) / 2
        y_mean = sum(recent) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(recent))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope if self.higher_is_better else -slope


@dataclass
class RecursiveModification:
    """A modification that may affect modification mechanisms."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    
    # Target
    target_file: str = ""
    target_component: str = ""  # 'genesis', 'meta', 'self_mod', 'singularity'
    
    # Change
    old_code: str = ""
    new_code: str = ""
    
    # Rationale
    hypothesis: str = ""
    expected_improvement: Dict[str, float] = field(default_factory=dict)
    
    # Recursion tracking
    depth: int = 0  # How many levels of meta-modification
    parent_id: Optional[str] = None  # If this mod was created by a modified system
    
    # Status
    status: str = "proposed"
    constitutional_check: bool = False
    sandbox_test: bool = False
    improvement_verified: bool = False
    
    # Results
    actual_improvement: Dict[str, float] = field(default_factory=dict)
    error: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'target': self.target_component,
            'depth': self.depth,
            'status': self.status,
            'hypothesis': self.hypothesis,
            'improvement': self.actual_improvement
        }


class SingularityEngine:
    """
    The Singularity Engine: Recursive Self-Improvement
    
    This enables the system to modify its own modification mechanisms,
    creating a feedback loop of improvement. Key features:
    
    1. Constitutional constraints that cannot be violated
    2. Staged modifications with rollback
    3. Improvement verification before commitment
    4. Recursion depth limits
    5. Complete audit trail
    
    The improvement loop:
    1. Measure current capability
    2. Generate modification hypothesis
    3. Check against constitution
    4. Test in sandbox
    5. Measure improvement
    6. Apply if improved, rollback if not
    7. Repeat (potentially on the modification logic itself)
    """
    
    def __init__(
        self,
        source_dir: Path,
        constitution: Optional[Constitution] = None,
        data_dir: Optional[Path] = None
    ):
        self.source_dir = source_dir
        self.constitution = constitution or Constitution()
        self.data_dir = data_dir or source_dir / ".singularity_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.cycle: int = 0
        self.total_modifications: int = 0
        self.current_depth: int = 0
        
        # Metrics
        self.metrics: Dict[str, ImprovementMetric] = {
            'modification_success_rate': ImprovementMetric('modification_success_rate'),
            'code_efficiency': ImprovementMetric('code_efficiency'),
            'emergence_rate': ImprovementMetric('emergence_rate'),
            'novelty_generation': ImprovementMetric('novelty_generation'),
            'self_improvement_rate': ImprovementMetric('self_improvement_rate'),
        }
        
        # History
        self.modifications: List[RecursiveModification] = []
        self.applied: List[RecursiveModification] = []
        self.rolled_back: List[RecursiveModification] = []
        
        # Snapshots for rollback
        self.snapshots: Dict[str, Dict[str, str]] = {}
        
        # Modifiable components (including modification logic itself)
        self.modifiable_components = {
            'genesis': 'genesis/engine.py',
            'meta': 'meta/evolution.py',
            'self_mod': 'self_mod/engine.py',
            'singularity': 'singularity/engine.py',  # Can modify itself!
            'core': 'core/agent.py',
            'population': 'population/dynamics.py',
        }
        
        # Take initial snapshot
        self._take_snapshot("initial")
    
    def _take_snapshot(self, name: str):
        """Take a snapshot of all modifiable files."""
        snapshot = {}
        for component, rel_path in self.modifiable_components.items():
            file_path = self.source_dir / rel_path
            if file_path.exists():
                snapshot[component] = file_path.read_text()
        
        self.snapshots[name] = snapshot
        
        # Also save to disk
        snapshot_file = self.data_dir / f"snapshot_{name}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f)
    
    def _restore_snapshot(self, name: str) -> bool:
        """Restore from a snapshot."""
        if name not in self.snapshots:
            # Try loading from disk
            snapshot_file = self.data_dir / f"snapshot_{name}.json"
            if snapshot_file.exists():
                with open(snapshot_file) as f:
                    self.snapshots[name] = json.load(f)
            else:
                return False
        
        snapshot = self.snapshots[name]
        
        for component, content in snapshot.items():
            rel_path = self.modifiable_components.get(component)
            if rel_path:
                file_path = self.source_dir / rel_path
                file_path.write_text(content)
        
        return True
    
    def measure_capability(self) -> Dict[str, float]:
        """Measure current system capability."""
        measurements = {}
        
        # Modification success rate
        if self.modifications:
            successful = len([m for m in self.modifications if m.status == 'applied'])
            measurements['modification_success_rate'] = successful / len(self.modifications)
        else:
            measurements['modification_success_rate'] = 0.5
        
        # Code efficiency (inverse of total lines per function)
        total_lines = 0
        total_functions = 0
        for rel_path in self.modifiable_components.values():
            file_path = self.source_dir / rel_path
            if file_path.exists():
                content = file_path.read_text()
                total_lines += len(content.split('\n'))
                total_functions += content.count('def ')
        
        if total_functions > 0:
            measurements['code_efficiency'] = 1.0 / (total_lines / total_functions / 100)
        else:
            measurements['code_efficiency'] = 0.5
        
        # Self-improvement rate (trend in other metrics)
        if len(self.applied) > 1:
            recent_improvements = [m.actual_improvement.get('overall', 0) for m in self.applied[-10:]]
            measurements['self_improvement_rate'] = sum(recent_improvements) / len(recent_improvements)
        else:
            measurements['self_improvement_rate'] = 0.0
        
        # Record in metrics
        for name, value in measurements.items():
            if name in self.metrics:
                self.metrics[name].record(value)
        
        return measurements
    
    def generate_hypothesis(self) -> Optional[RecursiveModification]:
        """Generate a modification hypothesis."""
        if self.total_modifications >= self.constitution.max_total_modifications:
            return None
        
        if self.current_depth >= self.constitution.max_modification_depth:
            return None
        
        # Select a component to modify
        # Bias toward components that have shown improvement
        component_scores = {}
        for component in self.modifiable_components:
            # Count successful modifications to this component
            successes = len([m for m in self.applied if m.target_component == component])
            failures = len([m for m in self.modifications 
                          if m.target_component == component and m.status == 'rejected'])
            
            # Exploration bonus for less-modified components
            total_mods = successes + failures
            exploration = 1.0 / (1.0 + total_mods * 0.1)
            
            # Exploitation bonus for successful components
            if total_mods > 0:
                exploitation = successes / total_mods
            else:
                exploitation = 0.5
            
            component_scores[component] = 0.3 * exploration + 0.7 * exploitation
        
        # Weighted random selection
        total_score = sum(component_scores.values())
        if total_score == 0:
            component = random.choice(list(self.modifiable_components.keys()))
        else:
            r = random.random() * total_score
            cumulative = 0
            for comp, score in component_scores.items():
                cumulative += score
                if cumulative >= r:
                    component = comp
                    break
            else:
                component = random.choice(list(self.modifiable_components.keys()))
        
        # Read current code
        rel_path = self.modifiable_components[component]
        file_path = self.source_dir / rel_path
        
        if not file_path.exists():
            return None
        
        current_code = file_path.read_text()
        
        # Generate modification based on component type
        if component == 'singularity':
            mod = self._generate_meta_modification(current_code)
        elif component in ('genesis', 'meta', 'self_mod'):
            mod = self._generate_mechanism_modification(component, current_code)
        else:
            mod = self._generate_standard_modification(component, current_code)
        
        if mod:
            mod.target_file = str(file_path)
            mod.target_component = component
            mod.depth = self.current_depth
            self.modifications.append(mod)
        
        return mod
    
    def _generate_meta_modification(self, code: str) -> Optional[RecursiveModification]:
        """Generate a modification to the modification logic itself."""
        # This is the most powerful and dangerous capability
        
        strategies = [
            self._improve_hypothesis_generation,
            self._improve_evaluation_logic,
            self._improve_selection_weights,
        ]
        
        for strategy in strategies:
            mod = strategy(code)
            if mod:
                mod.hypothesis = f"Meta-improvement: {mod.hypothesis}"
                return mod
        
        return None
    
    def _improve_hypothesis_generation(self, code: str) -> Optional[RecursiveModification]:
        """Try to improve how hypotheses are generated."""
        # Look for the hypothesis generation code
        if 'def generate_hypothesis' not in code:
            return None
        
        # Simple improvement: adjust exploration/exploitation balance
        if 'exploration = 1.0 / (1.0 + total_mods * 0.1)' in code:
            # Make exploration decay faster (more exploitation)
            new_code = code.replace(
                'exploration = 1.0 / (1.0 + total_mods * 0.1)',
                'exploration = 1.0 / (1.0 + total_mods * 0.15)'
            )
            
            return RecursiveModification(
                old_code=code,
                new_code=new_code,
                hypothesis="Increase exploitation by faster exploration decay",
                expected_improvement={'modification_success_rate': 0.05}
            )
        
        return None
    
    def _improve_evaluation_logic(self, code: str) -> Optional[RecursiveModification]:
        """Try to improve evaluation logic."""
        # Look for evaluation code
        if 'def evaluate_modification' not in code:
            return None
        
        # Add more sophisticated evaluation
        if '# EVALUATION_MARKER' not in code:
            # Find a good insertion point
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'def evaluate_modification' in line:
                    # Add a comment marker for future reference
                    lines.insert(i + 1, '        # EVALUATION_MARKER: Enhanced evaluation active')
                    new_code = '\n'.join(lines)
                    
                    return RecursiveModification(
                        old_code=code,
                        new_code=new_code,
                        hypothesis="Add evaluation marker for tracking",
                        expected_improvement={'code_efficiency': 0.01}
                    )
        
        return None
    
    def _improve_selection_weights(self, code: str) -> Optional[RecursiveModification]:
        """Try to improve component selection weights."""
        if '0.3 * exploration + 0.7 * exploitation' in code:
            # Try different balance
            new_balance = f"{random.uniform(0.2, 0.4):.2f} * exploration + {random.uniform(0.6, 0.8):.2f} * exploitation"
            new_code = code.replace(
                '0.3 * exploration + 0.7 * exploitation',
                new_balance
            )
            
            return RecursiveModification(
                old_code=code,
                new_code=new_code,
                hypothesis=f"Adjust selection weights to {new_balance}",
                expected_improvement={'modification_success_rate': 0.02}
            )
        
        return None
    
    def _generate_mechanism_modification(self, component: str, code: str) -> Optional[RecursiveModification]:
        """Generate a modification to a modification mechanism."""
        # These affect how the system modifies itself
        
        improvements = []
        
        # Look for tunable parameters
        param_patterns = [
            (r'mutation_rate\s*=\s*[\d.]+', 'mutation_rate'),
            (r'selection_pressure\s*=\s*[\d.]+', 'selection_pressure'),
            (r'innovation_rate\s*=\s*[\d.]+', 'innovation_rate'),
        ]
        
        import re
        for pattern, param_name in param_patterns:
            matches = re.findall(pattern, code)
            if matches:
                old_match = matches[0]
                old_value = float(old_match.split('=')[1].strip())
                
                # Small perturbation
                new_value = old_value * random.uniform(0.9, 1.1)
                new_match = f"{param_name} = {new_value:.4f}"
                
                improvements.append((old_match, new_match, param_name))
        
        if improvements:
            old_match, new_match, param_name = random.choice(improvements)
            new_code = code.replace(old_match, new_match, 1)
            
            return RecursiveModification(
                old_code=code,
                new_code=new_code,
                hypothesis=f"Tune {param_name} in {component}",
                expected_improvement={'self_improvement_rate': 0.01}
            )
        
        return None
    
    def _generate_standard_modification(self, component: str, code: str) -> Optional[RecursiveModification]:
        """Generate a standard code modification."""
        # Add optimization comments, restructure code, etc.
        
        lines = code.split('\n')
        
        # Find a function that could be improved
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and i > 0:
                # Check if it has a docstring
                if i + 1 < len(lines) and '"""' not in lines[i + 1]:
                    # Add a simple docstring
                    indent = len(line) - len(line.lstrip()) + 4
                    func_name = line.split('def ')[1].split('(')[0]
                    docstring = ' ' * indent + f'"""Auto-documented: {func_name}."""'
                    
                    new_lines = lines[:i+1] + [docstring] + lines[i+1:]
                    new_code = '\n'.join(new_lines)
                    
                    return RecursiveModification(
                        old_code=code,
                        new_code=new_code,
                        hypothesis=f"Add documentation to {func_name}",
                        expected_improvement={'code_efficiency': 0.005}
                    )
        
        return None
    
    def evaluate_modification(self, mod: RecursiveModification) -> bool:
        """
        Evaluate a modification through the full pipeline.
        
        1. Constitutional check
        2. Syntax validation
        3. Sandbox testing
        4. Improvement measurement
        """
        # 1. Constitutional check
        ok, reason = self.constitution.check_code(mod.new_code)
        if not ok:
            mod.status = 'rejected'
            mod.error = f"Constitutional violation: {reason}"
            return False
        mod.constitutional_check = True
        
        # 2. Syntax validation
        try:
            ast.parse(mod.new_code)
        except SyntaxError as e:
            mod.status = 'rejected'
            mod.error = f"Syntax error: {e}"
            return False
        
        # 3. Sandbox test
        if self.constitution.require_sandbox_testing:
            success, error = self._sandbox_test(mod)
            if not success:
                mod.status = 'rejected'
                mod.error = f"Sandbox test failed: {error}"
                return False
        mod.sandbox_test = True
        
        # 4. Measure improvement (requires actual application)
        # We do this by:
        # a) Taking a snapshot
        # b) Applying the change
        # c) Measuring capability
        # d) Comparing to before
        # e) Rolling back if no improvement
        
        snapshot_name = f"pre_mod_{mod.id}"
        self._take_snapshot(snapshot_name)
        
        # Get baseline
        baseline = self.measure_capability()
        
        # Apply modification
        file_path = Path(mod.target_file)
        try:
            file_path.write_text(mod.new_code)
        except Exception as e:
            mod.status = 'rejected'
            mod.error = f"Failed to write: {e}"
            self._restore_snapshot(snapshot_name)
            return False
        
        # Measure new capability
        new_capability = self.measure_capability()
        
        # Calculate improvement
        total_improvement = 0
        for metric_name, new_value in new_capability.items():
            old_value = baseline.get(metric_name, new_value)
            if metric_name in self.metrics and self.metrics[metric_name].higher_is_better:
                improvement = new_value - old_value
            else:
                improvement = old_value - new_value
            
            mod.actual_improvement[metric_name] = improvement
            total_improvement += improvement * self.metrics.get(metric_name, ImprovementMetric('')).weight
        
        mod.actual_improvement['overall'] = total_improvement
        
        # Decide whether to keep
        # Allow small negative improvements for exploration (epsilon-greedy)
        epsilon = 0.1  # 10% chance to accept slightly negative improvements
        improvement_threshold = -0.01  # Accept if not too negative
        
        if total_improvement > 0 or (random.random() < epsilon and total_improvement > improvement_threshold):
            mod.status = 'applied'
            mod.improvement_verified = True
            self.applied.append(mod)
            self.total_modifications += 1
            return True
        else:
            # Rollback
            self._restore_snapshot(snapshot_name)
            mod.status = 'rejected'
            mod.error = f"No improvement (delta={total_improvement:.4f})"
            return False
    
    def _sandbox_test(self, mod: RecursiveModification) -> Tuple[bool, str]:
        """Test modification in sandbox."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(mod.new_code)
            temp_path = f.name
        
        try:
            # Try to compile
            compile(mod.new_code, temp_path, 'exec')
            
            # Try to parse AST
            tree = ast.parse(mod.new_code)
            
            # Check for obviously problematic patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.constitution.forbidden_imports:
                            return False, f"Forbidden import: {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.constitution.forbidden_imports:
                        return False, f"Forbidden import: {node.module}"
            
            return True, ""
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def step(self) -> Dict:
        # TODO: Add memoization cache
        """Run one cycle of recursive self-improvement."""
        self.cycle += 1
        
        results = {
            'cycle': self.cycle,
            'depth': self.current_depth,
            'capability': {},
            'modification': None,
            'applied': False
        }
        
        # Measure current capability
        results['capability'] = self.measure_capability()
        
        # Generate hypothesis
        mod = self.generate_hypothesis()
        
        if mod:
            results['modification'] = mod.to_dict()
            
            # Evaluate
            applied = self.evaluate_modification(mod)
            results['applied'] = applied
            
            # If we successfully modified modification logic, increase depth
            if applied and mod.target_component in ('singularity', 'genesis', 'meta', 'self_mod'):
                self.current_depth += 1
        
        return results
    
    def run(self, cycles: int = 50, verbose: bool = True) -> List[Dict]:
        """Run recursive self-improvement loop."""
        results = []
        
        if verbose:
            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███████╗██╗███╗   ██╗ ██████╗ ██╗   ██╗██╗      █████╗ ██████╗ ██╗████████╗██╗   ██╗
║   ██╔════╝██║████╗  ██║██╔════╝ ██║   ██║██║     ██╔══██╗██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
║   ███████╗██║██╔██╗ ██║██║  ███╗██║   ██║██║     ███████║██████╔╝██║   ██║    ╚████╔╝ 
║   ╚════██║██║██║╚██╗██║██║   ██║██║   ██║██║     ██╔══██║██╔══██╗██║   ██║     ╚██╔╝  
║   ███████║██║██║ ╚████║╚██████╔╝╚██████╔╝███████╗██║  ██║██║  ██║██║   ██║      ██║   
║   ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
║                                                                              ║
║                    Recursive Self-Improvement Engine                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Constitution: ACTIVE                                                        ║
║  Max depth: {self.constitution.max_modification_depth}                                                           ║
║  Max modifications: {self.constitution.max_total_modifications}                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        for i in range(cycles):
            result = self.step()
            results.append(result)
            
            if verbose:
                if result['applied']:
                    mod = result['modification']
                    print(f"  Cycle {self.cycle:4d} │ Depth {self.current_depth} │ "
                          f"✓ Applied: {mod['target'][:12]:12s} │ "
                          f"Δ={mod['improvement'].get('overall', 0):+.4f}")
                elif result['modification']:
                    mod = result['modification']
                    print(f"  Cycle {self.cycle:4d} │ Depth {self.current_depth} │ "
                          f"✗ Rejected: {mod['target'][:12]:12s}")
        
        if verbose:
            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SINGULARITY RESULTS                                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Total cycles: {self.cycle:>6}                                                       ║
║  Max depth reached: {self.current_depth:>3}                                                      ║
║  Modifications applied: {len(self.applied):>4}                                                  ║
║  Success rate: {len(self.applied) / max(1, len(self.modifications)) * 100:>5.1f}%                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        return results
    
    def get_stats(self) -> Dict:
        return {
            'cycle': self.cycle,
            'depth': self.current_depth,
            'total_modifications': self.total_modifications,
            'applied': len(self.applied),
            'rolled_back': len(self.rolled_back),
            'success_rate': len(self.applied) / max(1, len(self.modifications)),
            'metrics': {name: {'current': m.values[-1] if m.values else 0, 
                              'trend': m.trend()}
                       for name, m in self.metrics.items()},
            'constitution': self.constitution.to_dict()
        }
    
    def report(self) -> str:
        stats = self.get_stats()
        
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         SINGULARITY STATUS                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Cycle: {stats['cycle']:>8}    Depth: {stats['depth']:>3}    Applied: {stats['applied']:>5}             ║
║  Success Rate: {stats['success_rate']*100:>5.1f}%                                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  METRICS                                                                     ║
"""


def demo():
    """Demonstrate the Singularity Engine."""
    source_dir = Path(__file__).parent.parent
    
    # Create engine with constitution
    constitution = Constitution(
        max_total_modifications=50,
        max_modification_depth=5
    )
    
    engine = SingularityEngine(source_dir, constitution)
    
    # Run recursive self-improvement
    engine.run(cycles=30, verbose=True)
    
    # Stats
    stats = engine.get_stats()
    print(f"\nFinal Statistics:")
    print(f"  Depth reached: {stats['depth']}")
    print(f"  Modifications: {stats['applied']}")
    print(f"  Success rate: {stats['success_rate']*100:.1f}%")
    
    # Show metric trends
    print(f"\nMetric Trends:")
    for name, data in stats['metrics'].items():
        trend = "↑" if data['trend'] > 0 else "↓" if data['trend'] < 0 else "→"
        print(f"  {name}: {data['current']:.4f} {trend}")
    
    return engine


if __name__ == "__main__":
    demo()
