"""
AEGIS-2 Omega: The Complete System

This is the final integration layer that connects:
- Core AEGIS-2 (genome, patterns, goals, novelty, loops, catalysis, criticality)
- Population dynamics (multi-agent evolution)
- Self-modification (recursive self-improvement)
- Meta-evolution (evolving the mechanisms of evolution)

The result: A system where EVERYTHING can evolve, including:
- The genetic building blocks (primitives)
- What fitness means (evolvable fitness functions)
- How evolution works (evolvable evolution parameters)
- The system's own code (self-modification)

This is as close to genuine open-endedness as we can get without
the system rewriting this very file.
"""

import random
import math
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

# Import everything
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import AEGIS2, EmergentEvent
from population.dynamics import Population, Environment
from self_mod.engine import SelfModificationEngine, Modification
from meta.evolution import MetaEvolutionEngine, Primitive, EvolutionParams


@dataclass
class OmegaConfig:
    """Configuration for the Omega system."""
    # Population
    population_size: int = 10
    environment_complexity: float = 0.5
    environment_volatility: float = 0.2
    
    # Meta-evolution
    meta_evolution_rate: int = 10  # Run meta-evolution every N cycles
    primitive_injection_rate: float = 0.1  # Rate of injecting evolved primitives
    
    # Self-modification
    self_mod_rate: int = 50  # Consider self-modification every N cycles
    modification_threshold: float = 0.05  # Min improvement to apply
    
    # Emergence
    emergence_detection_window: int = 100
    
    # Persistence
    save_interval: int = 100
    
    def to_dict(self) -> Dict:
        return {
            'population_size': self.population_size,
            'environment_complexity': self.environment_complexity,
            'environment_volatility': self.environment_volatility,
            'meta_evolution_rate': self.meta_evolution_rate,
            'self_mod_rate': self.self_mod_rate
        }


class AEGIS2Omega:
    """
    AEGIS-2 Omega: The Complete Open-Ended System
    
    Integrates:
    - Multiple AEGIS-2 agents in a population
    - Meta-evolution of primitives and fitness
    - Self-modification capabilities
    - Multi-level emergence detection
    """
    
    def __init__(
        self,
        name: str = "omega",
        config: Optional[OmegaConfig] = None,
        data_dir: Optional[str] = None
    ):
        self.name = name
        self.config = config or OmegaConfig()
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / f".{name}_data"
        
        # === SUBSYSTEMS ===
        
        # Environment
        self.environment = Environment(
            complexity=self.config.environment_complexity,
            volatility=self.config.environment_volatility
        )
        
        # Population of agents
        self.population = Population(
            size=self.config.population_size,
            environment=self.environment,
            data_dir=str(self.data_dir / "population")
        )
        
        # Meta-evolution engine
        self.meta = MetaEvolutionEngine()
        
        # Self-modification engine
        self.self_mod = SelfModificationEngine()
        
        # === STATE ===
        
        self.cycle: int = 0
        self.generation: int = 0
        
        # Fitness tracking
        self.population_fitness: List[float] = []
        self.meta_fitness: List[float] = []
        
        # Emergence tracking
        self.emergence_events: List[Dict] = []
        self.emergence_by_type: Dict[str, int] = {}
        
        # Performance
        self.cycles_per_second: float = 0.0
        self.start_time: float = time.time()
        
        # Callbacks
        self.on_emergence: List[Callable[[Dict], None]] = []
        self.on_generation: List[Callable[[int, Dict], None]] = []
    
    def step(self) -> Dict:
        """
        Run one step of the complete system.
        
        This orchestrates:
        1. Population dynamics
        2. Meta-evolution
        3. Self-modification consideration
        4. Cross-level emergence detection
        """
        self.cycle += 1
        step_start = time.time()
        
        results = {
            'cycle': self.cycle,
            'generation': self.generation,
            'events': [],
            'emergence': [],
            'modifications': []
        }
        
        # === 1. POPULATION STEP ===
        pop_result = self.population.step()
        
        # Track population emergence
        for e in pop_result.get('emergence', []):
            self._record_emergence(e)
            results['emergence'].append(e)
        
        # Update generation
        self.generation = self.population.generation
        
        # Record population fitness
        stats = self.population.get_stats()
        self.population_fitness.append(stats['mean_fitness'])
        
        # === 2. META-EVOLUTION ===
        if self.cycle % self.config.meta_evolution_rate == 0:
            meta_result = self._run_meta_evolution()
            results['events'].append({
                'type': 'meta_evolution',
                'data': meta_result
            })
            
            # Inject evolved primitives into agents
            self._inject_primitives()
        
        # === 3. SELF-MODIFICATION ===
        if self.cycle % self.config.self_mod_rate == 0:
            mod_result = self._consider_self_modification()
            if mod_result:
                results['modifications'].append(mod_result)
        
        # === 4. CROSS-LEVEL EMERGENCE ===
        cross_emergence = self._detect_cross_level_emergence()
        for e in cross_emergence:
            self._record_emergence(e)
            results['emergence'].append(e)
        
        # === 5. UPDATE METRICS ===
        elapsed = time.time() - step_start
        self.cycles_per_second = 1.0 / max(0.001, elapsed)
        
        # Notify callbacks
        for callback in self.on_generation:
            callback(self.generation, results)
        
        for e in results['emergence']:
            for callback in self.on_emergence:
                callback(e)
        
        return results
    
    def _run_meta_evolution(self) -> Dict:
        """Run meta-evolution step."""
        # Aggregate state from population
        system_state = self._aggregate_population_state()
        
        # Run meta-evolution
        result = self.meta.step(system_state)
        
        # Use evolved fitness to evaluate population
        for agent_id, agent in self.population.agents.items():
            agent_state = agent.status()
            evolved_fitness = self.meta.evaluate_fitness({
                'novelty_rate': agent_state['novelty'].get('novelty_rate', 0),
                'goals_satisfied': agent_state['goals'].get('goals_satisfied', 0),
                'goals_total': agent_state['goals'].get('total_goals', 1),
                'pattern_matches': agent_state['patterns'].get('total_patterns', 0),
                'steps': agent.cycle,
                'genome_size': agent_state['genome'].get('total_genes', 0)
            })
            
            # Blend with agent's own fitness
            agent.fitness = 0.7 * agent.fitness + 0.3 * evolved_fitness
        
        # Track meta-fitness
        self.meta_fitness.append(result['changes'].get('meta_fitness', 0))
        
        return result
    
    def _inject_primitives(self):
        """Inject evolved primitives into agent genomes."""
        if random.random() > self.config.primitive_injection_rate:
            return
        
        # Get a novel primitive
        primitive = self.meta.get_primitive()
        if not primitive:
            return
        
        # Inject into random agents - boost their fitness based on primitive
        for agent_id, agent in random.sample(
            list(self.population.agents.items()),
            min(3, len(self.population.agents))
        ):
            # Boost agent fitness with primitive value
            agent.fitness += 0.01 * primitive.fitness
            
            # Also trigger a mutation in the agent's genome
            if agent.genome.genes:
                gene = random.choice(list(agent.genome.genes.values()))
                agent.genome._mutate_gene(gene)
    
    def _aggregate_population_state(self) -> Dict:
        """Aggregate state from all agents in population."""
        if not self.population.agents:
            return {}
        
        total_novelty = 0
        total_goals_satisfied = 0
        total_goals = 0
        total_patterns = 0
        total_genes = 0
        
        for agent in self.population.agents.values():
            status = agent.status()
            total_novelty += status['novelty'].get('novelty_rate', 0)
            total_goals_satisfied += status['goals'].get('goals_satisfied', 0)
            total_goals += status['goals'].get('total_goals', 1)
            total_patterns += status['patterns'].get('total_patterns', 0)
            total_genes += status['genome'].get('total_genes', 0)
        
        n = len(self.population.agents)
        
        return {
            'novelty_rate': total_novelty / n,
            'goals_satisfied': total_goals_satisfied,
            'goals_total': total_goals,
            'pattern_matches': total_patterns,
            'pattern_attempts': total_patterns * 2,
            'steps': self.cycle,
            'genome_size': total_genes / n,
            'variance': self._compute_fitness_variance(),
            'fitness_delta': self._compute_fitness_delta()
        }
    
    def _compute_fitness_variance(self) -> float:
        """Compute variance in population fitness."""
        if len(self.population_fitness) < 2:
            return 0.5
        
        recent = self.population_fitness[-10:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        return variance
    
    def _compute_fitness_delta(self) -> float:
        """Compute recent fitness improvement."""
        if len(self.population_fitness) < 2:
            return 0.0
        
        return self.population_fitness[-1] - self.population_fitness[-2]
    
    def _consider_self_modification(self) -> Optional[Dict]:
        """Consider self-modification based on current state."""
        # Get current fitness
        current_fitness = self.population_fitness[-1] if self.population_fitness else 0.5
        
        # Generate modification hypothesis
        observations = self._aggregate_population_state()
        modification = self.self_mod.generate_hypothesis(current_fitness, observations)
        
        if not modification:
            return None
        
        # Test the modification (simulated)
        def test_fn():
            # Simulate modified behavior
            return current_fitness + random.gauss(0, 0.05)
        
        success = self.self_mod.test(modification, test_fn)
        
        if success and modification.improvement > self.config.modification_threshold:
            # Apply the modification
            def apply_fn(mod):
                # Apply to evolution params
                params = self.meta.get_params()
                if mod.target_type == 'parameter':
                    if 'mutation' in mod.target_id:
                        params.mutation_rate = mod.new_value
                    elif 'selection' in mod.target_id:
                        params.selection_pressure = mod.new_value
            
            self.self_mod.apply(modification, apply_fn)
            
            return {
                'modification': modification.to_dict(),
                'improvement': modification.improvement
            }
        
        return None
    
    def _detect_cross_level_emergence(self) -> List[Dict]:
        """
        Detect emergence that spans multiple levels:
        - Agent level
        - Population level
        - Meta level
        """
        phenomena = []
        
        # === META-POPULATION SYNCHRONIZATION ===
        # When meta-evolution and population evolution synchronize
        if len(self.meta_fitness) > 5 and len(self.population_fitness) > 5:
            meta_trend = self.meta_fitness[-1] - self.meta_fitness[-5]
            pop_trend = self.population_fitness[-1] - self.population_fitness[-5]
            
            if meta_trend > 0.1 and pop_trend > 0.1:
                phenomena.append({
                    'type': 'meta_pop_sync',
                    'description': 'Meta-evolution and population evolution synchronized',
                    'meta_trend': meta_trend,
                    'pop_trend': pop_trend,
                    'cycle': self.cycle
                })
        
        # === PRIMITIVE EXPLOSION ===
        # Rapid growth in evolved primitives
        meta_stats = self.meta.get_stats()
        if meta_stats['primitives']['created_count'] > self.cycle * 3:
            phenomena.append({
                'type': 'primitive_explosion',
                'description': 'Rapid primitive evolution',
                'primitives': meta_stats['primitives']['total_primitives'],
                'rate': meta_stats['primitives']['created_count'] / max(1, self.cycle),
                'cycle': self.cycle
            })
        
        # === FITNESS FUNCTION EVOLUTION ===
        # Significant change in fitness weights
        if meta_stats['fitness']['num_components'] > 10:
            phenomena.append({
                'type': 'fitness_complexity',
                'description': 'Complex evolved fitness function',
                'components': meta_stats['fitness']['num_components'],
                'cycle': self.cycle
            })
        
        # === SELF-MODIFICATION SUCCESS ===
        self_mod_stats = self.self_mod.get_stats()
        if self_mod_stats['applied'] > 5:
            phenomena.append({
                'type': 'self_mod_cascade',
                'description': 'Multiple successful self-modifications',
                'applied': self_mod_stats['applied'],
                'cycle': self.cycle
            })
        
        # === POPULATION DIVERSITY EXPLOSION ===
        pop_stats = self.population.get_stats()
        if pop_stats['diversity'] > 0.8:
            phenomena.append({
                'type': 'diversity_explosion',
                'description': 'High population diversity',
                'diversity': pop_stats['diversity'],
                'cycle': self.cycle
            })
        
        return phenomena
    
    def _record_emergence(self, event: Dict):
        """Record an emergence event."""
        self.emergence_events.append(event)
        
        event_type = event.get('type', 'unknown')
        self.emergence_by_type[event_type] = self.emergence_by_type.get(event_type, 0) + 1
        
        # Limit history
        if len(self.emergence_events) > 10000:
            self.emergence_events = self.emergence_events[-10000:]
    
    def run(self, cycles: int = 100, verbose: bool = True) -> List[Dict]:
        """Run the complete system for multiple cycles."""
        results = []
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"  AEGIS-2 Omega: Running {cycles} cycles")
            print(f"  Population: {self.config.population_size} agents")
            print(f"{'='*70}\n")
        
        start_time = time.time()
        
        for i in range(cycles):
            result = self.step()
            results.append(result)
            
            if verbose:
                # Progress indicator
                if i % 10 == 0:
                    pop_stats = self.population.get_stats()
                    meta_stats = self.meta.get_stats()
                    
                    print(f"  Cycle {self.cycle:5d} | "
                          f"Gen {self.generation:4d} | "
                          f"Pop {pop_stats['population_size']:3d} | "
                          f"Fit {pop_stats['mean_fitness']:.3f} | "
                          f"Prims {meta_stats['primitives']['total_primitives']:4d} | "
                          f"Emrg {len(self.emergence_events):5d}")
                
                # Report emergence
                if result['emergence']:
                    for e in result['emergence']:
                        print(f"    ★ {e.get('type', 'unknown')}: {e.get('description', '')[:50]}")
        
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"  Completed in {elapsed:.1f}s ({cycles/elapsed:.1f} cycles/sec)")
            print(f"{'='*70}\n")
        
        return results
    
    def status(self) -> Dict:
        """Get comprehensive system status."""
        pop_stats = self.population.get_stats()
        meta_stats = self.meta.get_stats()
        self_mod_stats = self.self_mod.get_stats()
        
        return {
            'cycle': self.cycle,
            'generation': self.generation,
            'runtime': time.time() - self.start_time,
            'cycles_per_second': self.cycles_per_second,
            
            'population': {
                'size': pop_stats['population_size'],
                'mean_fitness': pop_stats['mean_fitness'],
                'max_fitness': pop_stats['max_fitness'],
                'diversity': pop_stats['diversity'],
                'total_created': pop_stats['total_created'],
                'total_deaths': pop_stats['total_deaths']
            },
            
            'meta_evolution': {
                'primitives': meta_stats['primitives']['total_primitives'],
                'primitives_created': meta_stats['primitives']['created_count'],
                'fitness_components': meta_stats['fitness']['num_components'],
                'improvement_rate': meta_stats['meta_metrics']['improvement_rate'],
                'innovation_rate': meta_stats['meta_metrics']['innovation_rate']
            },
            
            'self_modification': {
                'proposed': self_mod_stats['proposed'],
                'applied': self_mod_stats['applied'],
                'rejected': self_mod_stats['rejected']
            },
            
            'emergence': {
                'total_events': len(self.emergence_events),
                'by_type': dict(self.emergence_by_type),
                'recent': self.emergence_events[-5:] if self.emergence_events else []
            },
            
            'environment': self.environment.get_stats()
        }
    
    def save(self):
        """Save complete system state."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save population
        self.population.save()
        
        # Save Omega state
        state = {
            'name': self.name,
            'config': self.config.to_dict(),
            'cycle': self.cycle,
            'generation': self.generation,
            'population_fitness': self.population_fitness[-1000:],
            'meta_fitness': self.meta_fitness[-1000:],
            'emergence_by_type': self.emergence_by_type,
            'emergence_events': self.emergence_events[-100:],
            'meta': self.meta.to_dict(),
            'self_mod': self.self_mod.get_stats(),
            'saved_at': datetime.now().isoformat()
        }
        
        with open(self.data_dir / "omega_state.json", 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return self.data_dir
    
    def report(self) -> str:
        """Generate a detailed status report."""
        status = self.status()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           AEGIS-2 OMEGA STATUS                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Cycle: {status['cycle']:>8}    Generation: {status['generation']:>8}    Runtime: {status['runtime']:>8.1f}s         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  POPULATION                                                                  ║
║    Size: {status['population']['size']:>6}    Mean Fitness: {status['population']['mean_fitness']:>6.4f}    Max: {status['population']['max_fitness']:>6.4f}       ║
║    Diversity: {status['population']['diversity']:>6.4f}    Created: {status['population']['total_created']:>5}    Deaths: {status['population']['total_deaths']:>5}       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  META-EVOLUTION                                                              ║
║    Primitives: {status['meta_evolution']['primitives']:>6}    Created: {status['meta_evolution']['primitives_created']:>6}                          ║
║    Fitness Components: {status['meta_evolution']['fitness_components']:>3}    Innovation Rate: {status['meta_evolution']['innovation_rate']:>6.2f}             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SELF-MODIFICATION                                                           ║
║    Proposed: {status['self_modification']['proposed']:>5}    Applied: {status['self_modification']['applied']:>5}    Rejected: {status['self_modification']['rejected']:>5}             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  EMERGENCE                                                                   ║
║    Total Events: {status['emergence']['total_events']:>6}                                                     ║
"""
        
        # Add emergence by type
        for etype, count in sorted(status['emergence']['by_type'].items(), key=lambda x: -x[1])[:5]:
            report += f"║      {etype[:30]:30s}: {count:>6}                                ║\n"
        
        report += "╚══════════════════════════════════════════════════════════════════════════════╝"
        
        return report


def demo():
    """Demonstrate the complete Omega system."""
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║     █████╗ ███████╗ ██████╗ ██╗███████╗    ██████╗                   ║
    ║    ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝    ╚════██╗                  ║
    ║    ███████║█████╗  ██║  ███╗██║███████╗     █████╔╝                  ║
    ║    ██╔══██║██╔══╝  ██║   ██║██║╚════██║    ██╔═══╝                   ║
    ║    ██║  ██║███████╗╚██████╔╝██║███████║    ███████╗                  ║
    ║    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝    ╚══════╝                  ║
    ║                                                                       ║
    ║                      ╔═══════════════════╗                           ║
    ║                      ║   O M E G A       ║                           ║
    ║                      ╚═══════════════════╝                           ║
    ║                                                                       ║
    ║         The Complete Open-Ended Evolving System                      ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create Omega system
    config = OmegaConfig(
        population_size=5,
        environment_complexity=0.5,
        meta_evolution_rate=5,
        self_mod_rate=20
    )
    
    omega = AEGIS2Omega(name="demo", config=config)
    
    # Run for 100 cycles
    omega.run(cycles=100, verbose=True)
    
    # Print final report
    print(omega.report())
    
    # Save
    save_path = omega.save()
    print(f"\n  State saved to: {save_path}")
    
    return omega


if __name__ == "__main__":
    demo()
