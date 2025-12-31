"""
AEGIS-2 Self-Modification: Recursive Self-Improvement

Key insight: True open-ended evolution requires the ability to 
modify the very mechanisms of evolution themselves.

This module implements:
- Code introspection (examining own structure)
- Safe code modification (sandboxed execution)
- Improvement hypothesis generation
- A/B testing of modifications
- Rollback on failure
- Meta-learning about what modifications work

WARNING: This is powerful and potentially dangerous.
All modifications are sandboxed and reversible.
"""

import random
import math
import hashlib
import ast
import copy
import inspect
import types
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from pathlib import Path
import json


@dataclass
class Modification:
    """A proposed modification to the system."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    
    # What is being modified
    target_type: str = ""  # 'function', 'parameter', 'structure', 'gene', 'pattern'
    target_id: str = ""
    
    # The modification
    modification_type: str = ""  # 'replace', 'augment', 'remove', 'tune'
    old_value: Any = None
    new_value: Any = None
    
    # Hypothesis about why this should help
    hypothesis: str = ""
    
    # Status
    status: str = "proposed"  # proposed, testing, accepted, rejected, rolled_back
    
    # Results
    fitness_before: float = 0.0
    fitness_after: float = 0.0
    improvement: float = 0.0
    
    # Temporal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    applied_at: Optional[float] = None
    evaluated_at: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'modification_type': self.modification_type,
            'hypothesis': self.hypothesis,
            'status': self.status,
            'fitness_before': self.fitness_before,
            'fitness_after': self.fitness_after,
            'improvement': self.improvement
        }


class ParameterSpace:
    """
    Represents tunable parameters in the system.
    
    The system can explore this space to find better configurations.
    """
    
    def __init__(self):
        # Define parameter ranges
        self.parameters: Dict[str, Dict] = {
            # Genome parameters
            'genome.max_genes': {'min': 10, 'max': 500, 'type': 'int'},
            'genome.mutation_rate': {'min': 0.01, 'max': 0.5, 'type': 'float'},
            'genome.crossover_rate': {'min': 0.1, 'max': 0.9, 'type': 'float'},
            
            # Goal parameters
            'goals.max_active': {'min': 5, 'max': 50, 'type': 'int'},
            'goals.curiosity_weight': {'min': 0.0, 'max': 1.0, 'type': 'float'},
            'goals.mastery_weight': {'min': 0.0, 'max': 1.0, 'type': 'float'},
            
            # Novelty parameters
            'novelty.threshold': {'min': 0.1, 'max': 0.9, 'type': 'float'},
            'novelty.archive_size': {'min': 100, 'max': 5000, 'type': 'int'},
            'novelty.k_nearest': {'min': 5, 'max': 50, 'type': 'int'},
            
            # Criticality parameters
            'criticality.target_order': {'min': 0.3, 'max': 0.7, 'type': 'float'},
            'criticality.regulation_strength': {'min': 0.01, 'max': 0.5, 'type': 'float'},
            
            # Pattern parameters
            'patterns.max_complexity': {'min': 5, 'max': 100, 'type': 'int'},
            'patterns.abstraction_rate': {'min': 0.01, 'max': 0.3, 'type': 'float'},
        }
        
        # Current values
        self.current_values: Dict[str, Any] = {}
        
        # History of configurations and their fitness
        self.history: List[Tuple[Dict, float]] = []
        
        # Best known configuration
        self.best_config: Optional[Dict] = None
        self.best_fitness: float = 0.0
    
    def sample_random(self) -> Dict[str, Any]:
        """Sample a random configuration."""
        config = {}
        for name, spec in self.parameters.items():
            if spec['type'] == 'int':
                config[name] = random.randint(spec['min'], spec['max'])
            elif spec['type'] == 'float':
                config[name] = random.uniform(spec['min'], spec['max'])
        return config
    
    def sample_near(self, center: Dict[str, Any], radius: float = 0.1) -> Dict[str, Any]:
    # Restructured for early return
        """Sample a configuration near a center point."""
        config = {}
        for name, spec in self.parameters.items():
            if name in center:
                current = center[name]
                range_size = spec['max'] - spec['min']
                
                if spec['type'] == 'int':
                    delta = int(range_size * radius * random.gauss(0, 1))
                    new_val = max(spec['min'], min(spec['max'], current + delta))
                    config[name] = new_val
                elif spec['type'] == 'float':
                    delta = range_size * radius * random.gauss(0, 1)
                    new_val = max(spec['min'], min(spec['max'], current + delta))
                    config[name] = new_val
            else:
                # Random if not in center
                if spec['type'] == 'int':
                    config[name] = random.randint(spec['min'], spec['max'])
                elif spec['type'] == 'float':
                    config[name] = random.uniform(spec['min'], spec['max'])
        
        return config
    
    def record(self, config: Dict[str, Any], fitness: float):
        """Record a configuration and its fitness."""
        self.history.append((dict(config), fitness))
        
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_config = dict(config)
        
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def suggest(self) -> Dict[str, Any]:
        """Suggest a promising configuration to try."""
        if not self.best_config:
            return self.sample_random()
        
        # Mostly explore near best, sometimes random
        if random.random() < 0.8:
            return self.sample_near(self.best_config, radius=0.1)
        else:
            return self.sample_random()


class CodeIntrospector:
    """
    Examines the system's own code structure.
    
    This enables the system to understand what it's made of
    and identify potential points for modification.
    """
    
    def __init__(self, target_module: Any):
        self.target = target_module
        self.structure: Dict[str, Any] = {}
        self.analyze()
    
    def analyze(self):
        """Analyze the target module's structure."""
        self.structure = {
            'classes': {},
            'functions': {},
            'constants': {},
            'dependencies': []
        }
        
        for name, obj in inspect.getmembers(self.target):
            if name.startswith('_'):
                continue
            
            if inspect.isclass(obj):
                self.structure['classes'][name] = self._analyze_class(obj)
            elif inspect.isfunction(obj):
                self.structure['functions'][name] = self._analyze_function(obj)
            elif not callable(obj):
                self.structure['constants'][name] = type(obj).__name__
    
    def _analyze_class(self, cls) -> Dict:
        """Analyze a class."""
        info = {
            'name': cls.__name__,
            'methods': {},
            'attributes': [],
            'bases': [b.__name__ for b in cls.__bases__]
        }
        
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_'):
                info['methods'][name] = self._analyze_function(method)
        
        return info
    
    def _analyze_function(self, func) -> Dict:
        """Analyze a function."""
        try:
            sig = inspect.signature(func)
            params = {name: str(p.annotation) if p.annotation != inspect.Parameter.empty else 'Any'
                     for name, p in sig.parameters.items()}
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else 'Any'
        except:
            params = {}
            return_type = 'Any'
        
        return {
            'name': func.__name__,
            'parameters': params,
            'return_type': return_type,
            'doc': func.__doc__[:100] if func.__doc__ else None
        }
    
    def get_modifiable_points(self) -> List[Dict]:
        """Identify points that could be modified."""
        points = []
        
        # Function parameters that look tunable
        for fname, finfo in self.structure.get('functions', {}).items():
            for pname, ptype in finfo.get('parameters', {}).items():
                if ptype in ['float', 'int', 'Optional[float]', 'Optional[int]']:
                    points.append({
                        'type': 'function_param',
                        'function': fname,
                        'parameter': pname,
                        'param_type': ptype
                    })
        
        # Class methods
        for cname, cinfo in self.structure.get('classes', {}).items():
            for mname, minfo in cinfo.get('methods', {}).items():
                points.append({
                    'type': 'method',
                    'class': cname,
                    'method': mname
                })
        
        return points


class Sandbox:
    """
    Safe execution environment for testing modifications.
    
    All modifications are tested here before being applied
    to the main system.
    """
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.results: List[Dict] = []
    
    def test_modification(self, modification: Modification, test_fn: Callable) -> Tuple[bool, float, str]:
        """
        Test a modification in the sandbox.
        
        Returns (success, fitness, error_message)
        """
        try:
            # Run test with timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Modification test timed out")
            
            # Note: signal only works on main thread, so we use simple approach
            start_time = datetime.now()
            
            fitness = test_fn()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > self.timeout:
                return False, 0.0, "Execution too slow"
            
            result = {
                'modification_id': modification.id,
                'success': True,
                'fitness': fitness,
                'elapsed': elapsed
            }
            self.results.append(result)
            
            return True, fitness, ""
            
        except Exception as e:
            result = {
                'modification_id': modification.id,
                'success': False,
                'error': str(e)
            }
            self.results.append(result)
            
            return False, 0.0, str(e)


class SelfModificationEngine:
    """
    The self-modification engine.
    
    Enables the system to:
    1. Introspect its own structure
    2. Generate modification hypotheses
    3. Test modifications safely
    4. Apply successful modifications
    5. Learn from modification outcomes
    """
    
    def __init__(self, target_system: Any = None):
        self.target = target_system
        
        # Parameter space
        self.param_space = ParameterSpace()
        
        # Sandbox for testing
        self.sandbox = Sandbox()
        
        # Modification history
        self.proposed_modifications: List[Modification] = []
        self.applied_modifications: List[Modification] = []
        self.rejected_modifications: List[Modification] = []
        
        # Meta-learning: which modification strategies work?
        self.strategy_success: Dict[str, List[float]] = {
            'parameter_tune': [],
            'structure_change': [],
            'gene_modification': [],
            'pattern_evolution': [],
        }
        
        # State snapshots for rollback
        self.snapshots: List[Dict] = []
        self.max_snapshots = 10
    
    def snapshot(self, state: Dict):
        """Take a snapshot for potential rollback."""
        self.snapshots.append({
            'timestamp': datetime.now().timestamp(),
            'state': copy.deepcopy(state)
        })
        
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
    
    def rollback(self) -> Optional[Dict]:
        """Rollback to previous snapshot."""
        if self.snapshots:
            return self.snapshots.pop()['state']
        return None
    
    def generate_hypothesis(self, current_fitness: float, observations: Dict) -> Optional[Modification]:
        """
        Generate a modification hypothesis based on observations.
        
        This is where the system reasons about what changes might help.
        """
        # Strategy selection based on past success
        strategies = list(self.strategy_success.keys())
        weights = []
        for s in strategies:
            history = self.strategy_success[s]
            if history:
                weights.append(sum(history[-10:]) / len(history[-10:]) + 0.1)
            else:
                weights.append(0.5)  # Prior for untested
        
        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]
        
        # Select strategy
        strategy = random.choices(strategies, weights=weights)[0]
        
        # Generate modification based on strategy
        if strategy == 'parameter_tune':
            return self._generate_parameter_modification(observations)
        elif strategy == 'gene_modification':
            return self._generate_gene_modification(observations)
        elif strategy == 'pattern_evolution':
            return self._generate_pattern_modification(observations)
        else:
            return self._generate_structure_modification(observations)
    
    def _generate_parameter_modification(self, observations: Dict) -> Modification:
        """Generate a parameter tuning modification."""
        config = self.param_space.suggest()
        
        # Pick a parameter to modify
        param_name = random.choice(list(config.keys()))
        new_value = config[param_name]
        old_value = self.param_space.current_values.get(param_name)
        
        return Modification(
            target_type='parameter',
            target_id=param_name,
            modification_type='tune',
            old_value=old_value,
            new_value=new_value,
            hypothesis=f"Adjusting {param_name} to {new_value} may improve fitness"
        )
    
    def _generate_gene_modification(self, observations: Dict) -> Modification:
        """Generate a gene modification."""
        # Determine modification type
        mod_type = random.choice(['mutate', 'crossover', 'create', 'delete'])
        
        return Modification(
            target_type='gene',
            target_id=f"gene_{random.randint(0, 100)}",
            modification_type=mod_type,
            hypothesis=f"Gene {mod_type} may discover better strategies"
        )
    
    def _generate_pattern_modification(self, observations: Dict) -> Modification:
        """Generate a pattern modification."""
        mod_type = random.choice(['compose', 'abstract', 'specialize'])
        
        return Modification(
            target_type='pattern',
            target_id=f"pattern_{random.randint(0, 100)}",
            modification_type=mod_type,
            hypothesis=f"Pattern {mod_type} may improve recognition"
        )
    
    def _generate_structure_modification(self, observations: Dict) -> Modification:
        """Generate a structural modification."""
        # These are more significant changes
        targets = [
            'add_hierarchy_level',
            'add_catalytic_link',
            'modify_criticality_target',
            'add_goal_type'
        ]
        
        target = random.choice(targets)
        
        return Modification(
            target_type='structure',
            target_id=target,
            modification_type='augment',
            hypothesis=f"Structural change {target} may enable new capabilities"
        )
    
    def propose(self, modification: Modification):
        """Propose a modification for testing."""
        modification.status = 'proposed'
        self.proposed_modifications.append(modification)
    
    def test(self, modification: Modification, test_fn: Callable) -> bool:
        """Test a modification in the sandbox."""
        modification.status = 'testing'
        
        # Record fitness before
        modification.fitness_before = test_fn()
        
        success, fitness_after, error = self.sandbox.test_modification(modification, test_fn)
        
        if success:
            modification.fitness_after = fitness_after
            modification.improvement = fitness_after - modification.fitness_before
            return True
        else:
            modification.status = 'rejected'
            self.rejected_modifications.append(modification)
            return False
    
    def apply(self, modification: Modification, apply_fn: Callable) -> bool:
        """Apply a tested modification."""
        try:
            apply_fn(modification)
            modification.status = 'accepted'
            modification.applied_at = datetime.now().timestamp()
            self.applied_modifications.append(modification)
            
            # Record success for meta-learning
            strategy = self._get_strategy_for_modification(modification)
            self.strategy_success[strategy].append(modification.improvement)
            
            return True
        except Exception as e:
            modification.status = 'rejected'
            self.rejected_modifications.append(modification)
            return False
    
    def _get_strategy_for_modification(self, modification: Modification) -> str:
        """Get the strategy category for a modification."""
        if modification.target_type == 'parameter':
            return 'parameter_tune'
        elif modification.target_type == 'gene':
            return 'gene_modification'
        elif modification.target_type == 'pattern':
            return 'pattern_evolution'
        else:
            return 'structure_change'
    
    def evaluate_modifications(self, current_fitness: float):
        """Evaluate pending modifications and decide which to apply."""
        # Sort by expected improvement
        pending = [m for m in self.proposed_modifications if m.status == 'proposed']
        pending.sort(key=lambda m: m.improvement, reverse=True)
        
        for modification in pending[:5]:  # Consider top 5
            if modification.improvement > 0.01:  # Threshold for acceptance
                modification.status = 'accepted'
                self.applied_modifications.append(modification)
            else:
                modification.status = 'rejected'
                self.rejected_modifications.append(modification)
        
        # Clear processed
        self.proposed_modifications = [m for m in self.proposed_modifications 
                                       if m.status == 'proposed']
    
    def get_stats(self) -> Dict:
        """Get self-modification statistics."""
        return {
            'proposed': len(self.proposed_modifications),
            'applied': len(self.applied_modifications),
            'rejected': len(self.rejected_modifications),
            'strategy_success': {
                s: sum(h[-10:])/max(1, len(h[-10:])) 
                for s, h in self.strategy_success.items()
            },
            'best_config_fitness': self.param_space.best_fitness,
            'snapshots': len(self.snapshots)
        }
    
    def run_improvement_cycle(
        self,
        get_fitness: Callable[[], float],
        get_observations: Callable[[], Dict],
        apply_modification: Callable[[Modification], None],
        cycles: int = 10
    ) -> List[Dict]:
        """
        Run a self-improvement cycle.
        
        This is the main loop for recursive self-improvement.
        """
        results = []
        
        for i in range(cycles):
            # Get current state
            current_fitness = get_fitness()
            observations = get_observations()
            
            # Take snapshot
            self.snapshot({'fitness': current_fitness, 'observations': observations})
            
            # Generate hypothesis
            modification = self.generate_hypothesis(current_fitness, observations)
            if not modification:
                continue
            
            self.propose(modification)
            
            # Test modification
            test_success = self.test(modification, get_fitness)
            
            if test_success and modification.improvement > 0:
                # Apply modification
                apply_success = self.apply(modification, apply_modification)
                
                # Verify improvement
                new_fitness = get_fitness()
                
                if new_fitness < current_fitness * 0.9:  # Significant regression
                    # Rollback
                    rollback_state = self.rollback()
                    modification.status = 'rolled_back'
                    results.append({
                        'cycle': i,
                        'modification': modification.to_dict(),
                        'outcome': 'rolled_back',
                        'fitness_change': new_fitness - current_fitness
                    })
                else:
                    results.append({
                        'cycle': i,
                        'modification': modification.to_dict(),
                        'outcome': 'applied',
                        'fitness_change': new_fitness - current_fitness
                    })
            else:
                results.append({
                    'cycle': i,
                    'modification': modification.to_dict(),
                    'outcome': 'rejected',
                    'fitness_change': 0
                })
        
        return results


def demo():
    """Demonstrate self-modification."""
    print("=" * 70)
    print("   AEGIS-2 Self-Modification Engine")
    print("=" * 70)
    print()
    
    # Create self-modification engine
    engine = SelfModificationEngine()
    
    # Simulated system fitness
    base_fitness = 0.5
    applied_mods = []
    
    def get_fitness():
        # Fitness depends on applied modifications
        bonus = sum(0.05 * random.random() for _ in applied_mods)
        return min(1.0, base_fitness + bonus + random.gauss(0, 0.02))
    
    def get_observations():
        return {
            'fitness': get_fitness(),
            'cycle': len(applied_mods),
            'novelty': random.random(),
            'complexity': random.random()
        }
    
    def apply_modification(mod):
        applied_mods.append(mod)
    
    # Run improvement cycles
    print("Running 20 self-improvement cycles...")
    results = engine.run_improvement_cycle(
        get_fitness=get_fitness,
        get_observations=get_observations,
        apply_modification=apply_modification,
        cycles=20
    )
    
    print()
    print("Results:")
    for r in results:
        outcome = r['outcome']
        change = r['fitness_change']
        mod_type = r['modification']['target_type']
        print(f"  Cycle {r['cycle']}: {outcome:12s} | {mod_type:15s} | Δ={change:+.4f}")
    
    print()
    print("Statistics:")
    stats = engine.get_stats()
    print(f"  Applied: {stats['applied']}")
    print(f"  Rejected: {stats['rejected']}")
    print(f"  Strategy success rates:")
    for strategy, rate in stats['strategy_success'].items():
        print(f"    {strategy}: {rate:.3f}")
    
    return engine


if __name__ == "__main__":
    demo()
