"""
AEGIS-2 Apex: The Complete Recursive Self-Improving System

This is the apex of the AEGIS-2 architecture, integrating ALL layers:

1. Core Agent (AEGIS2)
   - MetaGenome: Genes that create genes
   - PatternAlgebra: Compositional patterns
   - GoalAutomata: Self-spawning goals
   - NoveltyEngine: Curiosity-driven exploration
   - TangledHierarchy: Strange loops
   - AutocatalyticNetwork: Self-sustaining dynamics
   - CriticalityEngine: Edge of chaos

2. Population Dynamics
   - Competition and cooperation
   - Cultural transmission (memes)
   - Speciation

3. Meta-Evolution
   - Evolvable primitives
   - Evolvable fitness functions
   - Evolvable evolution parameters

4. Self-Modification
   - Parameter tuning
   - Hypothesis testing
   - Rollback capability

5. Genesis
   - Source code analysis
   - Code modification
   - Version control

6. Singularity
   - Recursive self-improvement
   - Constitutional constraints
   - Improvement verification

The result: A system that can improve how it improves how it improves...
"""

import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ultimate.system import AEGIS2Ultimate, UltimateConfig
from singularity.engine import SingularityEngine, Constitution


@dataclass
class ApexConfig:
    """Configuration for the Apex system."""
    # Ultimate config
    population_size: int = 5
    genesis_enabled: bool = True
    genesis_rate: int = 25
    
    # Singularity config
    singularity_enabled: bool = True
    singularity_rate: int = 50  # Run every N cycles
    max_recursive_depth: int = 3
    
    # Safety
    constitution_active: bool = True


class AEGIS2Apex:
    """
    AEGIS-2 Apex: The Complete System
    
    All layers integrated:
    - Ultimate (Core + Population + Meta + Genesis)
    - Singularity (Recursive self-improvement)
    """
    
    def __init__(
        self,
        name: str = "apex",
        config: Optional[ApexConfig] = None,
        source_dir: Optional[Path] = None
    ):
        self.name = name
        self.config = config or ApexConfig()
        self.source_dir = source_dir or Path(__file__).parent.parent
        self.data_dir = Path.cwd() / f".{name}_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Ultimate
        ultimate_config = UltimateConfig(
            population_size=self.config.population_size,
            genesis_enabled=self.config.genesis_enabled,
            genesis_rate=self.config.genesis_rate
        )
        self.ultimate = AEGIS2Ultimate(
            name=f"{name}_ultimate",
            config=ultimate_config,
            source_dir=self.source_dir,
            data_dir=self.data_dir / "ultimate"
        )
        
        # Initialize Singularity (if enabled)
        if self.config.singularity_enabled:
            constitution = Constitution(
                max_modification_depth=self.config.max_recursive_depth,
                max_total_modifications=100
            )
            self.singularity = SingularityEngine(
                source_dir=self.source_dir,
                constitution=constitution,
                data_dir=self.data_dir / "singularity"
            )
        else:
            self.singularity = None
        
        # State
        self.cycle: int = 0
        self.start_time: float = time.time()
        
        # Tracking
        self.level_activity: Dict[str, int] = {
            'L0_source': 0,      # Singularity + Genesis
            'L1_params': 0,      # Meta-evolution
            'L2_population': 0,  # Population dynamics
            'L3_agent': 0,       # Individual agent cycles
            'L4_emergence': 0    # Emergence events
        }
    
    def step(self) -> Dict:
        """Run one step of the complete system."""
        self.cycle += 1
        
        results = {
            'cycle': self.cycle,
            'ultimate': None,
            'singularity': None,
            'levels': {}
        }
        
        # Run Ultimate
        ultimate_result = self.ultimate.step()
        results['ultimate'] = {
            'cycle': self.ultimate.cycle,
            'emergence': len(ultimate_result.get('emergence', []))
        }
        
        # Track activity
        self.level_activity['L3_agent'] += 1
        self.level_activity['L4_emergence'] += len(ultimate_result.get('emergence', []))
        
        if ultimate_result.get('genesis') and ultimate_result['genesis'].get('applied', 0) > 0:
            self.level_activity['L0_source'] += ultimate_result['genesis']['applied']
        
        # Run Singularity periodically
        if self.singularity and self.cycle % self.config.singularity_rate == 0:
            sing_result = self.singularity.step()
            results['singularity'] = sing_result
            
            if sing_result.get('applied'):
                self.level_activity['L0_source'] += 1
        
        # Update level counts
        results['levels'] = dict(self.level_activity)
        
        return results
    
    def run(self, cycles: int = 100, verbose: bool = True) -> List[Dict]:
        """Run the complete Apex system."""
        results = []
        
        if verbose:
            self._print_banner()
            print(f"  Running {cycles} cycles...\n")
        
        for i in range(cycles):
            result = self.step()
            results.append(result)
            
            if verbose and i % 20 == 0:
                self._print_progress()
        
        if verbose:
            self._print_final_report()
        
        return results
    
    def _print_banner(self):
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║      █████╗ ███████╗ ██████╗ ██╗███████╗    ██████╗                         ║
║     ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝    ╚════██╗                        ║
║     ███████║█████╗  ██║  ███╗██║███████╗     █████╔╝                        ║
║     ██╔══██║██╔══╝  ██║   ██║██║╚════██║    ██╔═══╝                         ║
║     ██║  ██║███████╗╚██████╔╝██║███████║    ███████╗                        ║
║     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝    ╚══════╝                        ║
║                                                                              ║
║          █████╗ ██████╗ ███████╗██╗  ██╗                                    ║
║         ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝                                    ║
║         ███████║██████╔╝█████╗   ╚███╔╝                                     ║
║         ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗                                     ║
║         ██║  ██║██║     ███████╗██╔╝ ██╗                                    ║
║         ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝                                    ║
║                                                                              ║
║         The Complete Recursive Self-Improving System                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ACTIVE LAYERS:                                                              ║
║    [✓] Core Agent (genome, patterns, goals, novelty, loops, catalysis)      ║
║    [✓] Population Dynamics (competition, cooperation, memes)                 ║
║    [✓] Meta-Evolution (evolvable primitives, fitness, params)               ║
║    [✓] Self-Modification (parameter tuning, hypothesis testing)             ║
║    [✓] Genesis (source code modification)                                   ║
║    [✓] Singularity (recursive self-improvement)                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    def _print_progress(self):
        status = self.status()
        
        print(f"  Cycle {self.cycle:5d} │ "
              f"Pop {status['population']['size']:2d} │ "
              f"Fit {status['population']['mean_fitness']:.3f} │ "
              f"Prims {status['meta']['primitives']:3d} │ "
              f"Emrg {status['emergence']:4d} │ "
              f"SrcMod {status['source_modifications']:2d}")
    
    def _print_final_report(self):
        status = self.status()
        elapsed = time.time() - self.start_time
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           APEX FINAL REPORT                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Runtime: {elapsed:>8.1f}s    Cycles: {self.cycle:>6}    Rate: {self.cycle/elapsed:>6.1f}/s          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ╔═══════════════════════════════════════════════════════════════════════╗  ║
║  ║  LEVEL 0: SOURCE CODE                                                 ║  ║
║  ║    Modifications: {status['source_modifications']:>5}                                              ║  ║
║  ║    Code fragments: {status['genesis']['fragments']:>5}                                             ║  ║
║  ╠═══════════════════════════════════════════════════════════════════════╣  ║
║  ║  LEVEL 1: EVOLUTION PARAMETERS                                        ║  ║
║  ║    Primitives evolved: {status['meta']['primitives']:>5}                                          ║  ║
║  ║    Fitness components: {status['meta']['fitness_components']:>5}                                          ║  ║
║  ╠═══════════════════════════════════════════════════════════════════════╣  ║
║  ║  LEVEL 2: POPULATION                                                  ║  ║
║  ║    Current size: {status['population']['size']:>5}                                                ║  ║
║  ║    Total created: {status['population']['created']:>5}                                               ║  ║
║  ║    Mean fitness: {status['population']['mean_fitness']:>.4f}                                             ║  ║
║  ╠═══════════════════════════════════════════════════════════════════════╣  ║
║  ║  LEVEL 3: AGENT BEHAVIOR                                              ║  ║
║  ║    Cycles run: {self.cycle:>5}                                                    ║  ║
║  ╠═══════════════════════════════════════════════════════════════════════╣  ║
║  ║  LEVEL 4: EMERGENCE                                                   ║  ║
║  ║    Total events: {status['emergence']:>5}                                                ║  ║
║  ╚═══════════════════════════════════════════════════════════════════════╝  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        # Emergence breakdown
        print("  Emergence by type:")
        for etype, count in sorted(status['emergence_by_type'].items(), 
                                   key=lambda x: -x[1])[:5]:
            print(f"    {etype:30s}: {count:5d}")
        print()
    
    def status(self) -> Dict:
        """Get comprehensive status."""
        ult_status = self.ultimate.status()
        sing_stats = self.singularity.get_stats() if self.singularity else {}
        
        return {
            'cycle': self.cycle,
            'runtime': time.time() - self.start_time,
            
            'population': {
                'size': ult_status['omega']['population']['size'],
                'mean_fitness': ult_status['omega']['population']['mean_fitness'],
                'created': ult_status['omega']['population']['total_created']
            },
            
            'meta': {
                'primitives': ult_status['omega']['meta_evolution']['primitives'],
                'fitness_components': ult_status['omega']['meta_evolution']['fitness_components']
            },
            
            'genesis': {
                'modifications': ult_status['genesis']['total_modifications'],
                'fragments': ult_status['genesis']['source_fragments']
            },
            
            'singularity': {
                'depth': sing_stats.get('depth', 0),
                'modifications': sing_stats.get('applied', 0)
            },
            
            'source_modifications': (
                ult_status['genesis']['total_modifications'] + 
                sing_stats.get('applied', 0)
            ),
            
            'emergence': ult_status['omega']['emergence']['total_events'],
            'emergence_by_type': ult_status['omega']['emergence']['by_type'],
            
            'levels': self.level_activity
        }
    
    def save(self):
        """Save complete state."""
        self.ultimate.save()
        
        state = {
            'name': self.name,
            'cycle': self.cycle,
            'level_activity': self.level_activity,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(self.data_dir / "apex_state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        return self.data_dir
    
    def cleanup(self):
        """Clean up resources."""
        self.ultimate.cleanup()


def demo():
    """Run the Apex demonstration."""
    config = ApexConfig(
        population_size=5,
        genesis_enabled=True,
        genesis_rate=30,
        singularity_enabled=True,
        singularity_rate=40
    )
    
    apex = AEGIS2Apex(name="demo", config=config)
    apex.run(cycles=100, verbose=True)
    
    # Final status
    status = apex.status()
    
    print(f"""
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║                          SYSTEM SUMMARY                                   ║
  ╠═══════════════════════════════════════════════════════════════════════════╣
  ║                                                                           ║
  ║  This system demonstrates:                                                ║
  ║                                                                           ║
  ║  • Genetic programs that create genetic programs                          ║
  ║  • Patterns that compose into unbounded complexity                        ║
  ║  • Goals that spawn new goals based on intrinsic motivation              ║
  ║  • Novelty search that rewards being different                           ║
  ║  • Strange loops of self-reference                                        ║
  ║  • Autocatalytic networks that sustain themselves                         ║
  ║  • Edge of chaos dynamics (SOC)                                           ║
  ║  • Population-level evolution with cultural transmission                  ║
  ║  • Meta-evolution of the evolution mechanisms                             ║
  ║  • Source code self-modification                                          ║
  ║  • Recursive self-improvement with constitutional constraints             ║
  ║                                                                           ║
  ║  Total: {status['emergence']} emergence events detected                               ║
  ║                                                                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    apex.cleanup()
    return apex


if __name__ == "__main__":
    demo()
