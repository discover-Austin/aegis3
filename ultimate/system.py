"""
AEGIS-2 Ultimate: The Complete Self-Evolving System

This is the final integration layer that connects EVERYTHING:

1. Core AEGIS-2 (genome, patterns, goals, novelty, loops, catalysis, criticality)
2. Population dynamics (multi-agent evolution)
3. Meta-evolution (evolving the mechanisms of evolution)
4. Self-modification (modifying parameters and structure)
5. Genesis (modifying actual source code)

The result: A system that can genuinely modify its own implementation.

The stack:
- Level 0: Source code (modified by Genesis)
- Level 1: Evolution parameters (modified by meta-evolution)
- Level 2: Agent genomes (modified by population dynamics)
- Level 3: Agent behavior (emerges from all levels)

Each level can affect the levels above and below.
This is genuine recursive self-improvement.
"""

import random
import math
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from omega.system import AEGIS2Omega, OmegaConfig
from genesis.engine import GenesisEngine


@dataclass
class UltimateConfig:
    """Configuration for the Ultimate system."""
    # Omega config
    population_size: int = 5
    environment_complexity: float = 0.5
    environment_volatility: float = 0.2
    meta_evolution_rate: int = 5
    
    # Genesis config
    genesis_enabled: bool = True
    genesis_rate: int = 50  # Run Genesis every N cycles
    max_genesis_modifications_per_cycle: int = 3
    
    # Safety
    min_cycles_between_source_changes: int = 20
    max_total_source_modifications: int = 100
    
    # Emergence thresholds
    require_emergence_for_genesis: bool = True
    emergence_threshold: int = 10  # Need this many emergence events before Genesis
    
    def to_dict(self) -> Dict:
        return {
            'population_size': self.population_size,
            'genesis_enabled': self.genesis_enabled,
            'genesis_rate': self.genesis_rate,
            'max_genesis_modifications_per_cycle': self.max_genesis_modifications_per_cycle
        }


class AEGIS2Ultimate:
    """
    AEGIS-2 Ultimate: The Complete Self-Evolving System
    
    This is the apex of the AEGIS-2 architecture, integrating:
    - Omega (population + meta-evolution + self-modification)
    - Genesis (true source code modification)
    
    The system can now genuinely modify its own implementation.
    """
    
    def __init__(
        self,
        name: str = "ultimate",
        config: Optional[UltimateConfig] = None,
        source_dir: Optional[Path] = None,
        data_dir: Optional[Path] = None
    ):
        self.name = name
        self.config = config or UltimateConfig()
        self.source_dir = source_dir or Path(__file__).parent.parent
        self.data_dir = data_dir or Path.cwd() / f".{name}_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # === SUBSYSTEMS ===
        
        # Omega (contains population, meta-evolution, self-mod)
        omega_config = OmegaConfig(
            population_size=self.config.population_size,
            environment_complexity=self.config.environment_complexity,
            environment_volatility=self.config.environment_volatility,
            meta_evolution_rate=self.config.meta_evolution_rate
        )
        self.omega = AEGIS2Omega(
            name=f"{name}_omega",
            config=omega_config,
            data_dir=str(self.data_dir / "omega")
        )
        
        # Genesis (source code modification)
        if self.config.genesis_enabled:
            self.genesis = GenesisEngine(
                source_dir=self.source_dir,
                data_dir=self.data_dir / "genesis"
            )
        else:
            self.genesis = None
        
        # === STATE ===
        
        self.cycle: int = 0
        self.last_genesis_cycle: int = 0
        self.total_genesis_modifications: int = 0
        
        # Tracking
        self.emergence_since_genesis: int = 0
        self.genesis_events: List[Dict] = []
        
        # Performance
        self.start_time: float = time.time()
    
    def step(self) -> Dict:
        """
        Run one step of the complete system.
        
        This orchestrates:
        1. Omega (population + meta-evolution)
        2. Genesis (if conditions are met)
        """
        self.cycle += 1
        step_start = time.time()
        
        results = {
            'cycle': self.cycle,
            'omega': None,
            'genesis': None,
            'emergence': []
        }
        
        # === 1. RUN OMEGA ===
        omega_result = self.omega.step()
        results['omega'] = {
            'generation': omega_result.get('generation', 0),
            'emergence_count': len(omega_result.get('emergence', []))
        }
        
        # Track emergence
        emergence = omega_result.get('emergence', [])
        results['emergence'] = emergence
        self.emergence_since_genesis += len(emergence)
        
        # === 2. CONSIDER GENESIS ===
        if self._should_run_genesis():
            genesis_result = self._run_genesis()
            results['genesis'] = genesis_result
        
        # === 3. CROSS-LEVEL EFFECTS ===
        # If Genesis made changes, it might affect future evolution
        if results['genesis'] and results['genesis'].get('applied', 0) > 0:
            # Boost meta-evolution
            self.omega.meta.improvement_rate += 0.01
            
            # Record event
            self.genesis_events.append({
                'cycle': self.cycle,
                'modifications': results['genesis']['applied'],
                'emergence_trigger': self.emergence_since_genesis
            })
            
            self.emergence_since_genesis = 0
        
        return results
    
    def _should_run_genesis(self) -> bool:
        """Determine if Genesis should run this cycle."""
        if not self.genesis:
            return False
        
        if not self.config.genesis_enabled:
            return False
        
        # Rate limit
        if self.cycle - self.last_genesis_cycle < self.config.min_cycles_between_source_changes:
            return False
        
        # Check if it's time
        if self.cycle % self.config.genesis_rate != 0:
            return False
        
        # Total modification limit
        if self.total_genesis_modifications >= self.config.max_total_source_modifications:
            return False
        
        # Require emergence if configured
        if self.config.require_emergence_for_genesis:
            if self.emergence_since_genesis < self.config.emergence_threshold:
                return False
        
        return True
    
    def _run_genesis(self) -> Dict:
        """Run Genesis self-modification."""
        result = {
            'cycle': self.cycle,
            'proposed': 0,
            'applied': 0,
            'rejected': 0
        }
        
        self.last_genesis_cycle = self.cycle
        
        # Run Genesis for limited modifications
        for _ in range(self.config.max_genesis_modifications_per_cycle):
            mod = self.genesis.propose_modification()
            if mod:
                result['proposed'] += 1
                
                if self.genesis.evaluate_modification(mod):
                    result['applied'] += 1
                    self.total_genesis_modifications += 1
                else:
                    result['rejected'] += 1
        
        return result
    
    def run(self, cycles: int = 100, verbose: bool = True) -> List[Dict]:
        """Run the complete system for multiple cycles."""
        results = []
        
        if verbose:
            print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗ ██████╗ ██╗███████╗    ██████╗                          ║
║    ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝    ╚════██╗                         ║
║    ███████║█████╗  ██║  ███╗██║███████╗     █████╔╝                         ║
║    ██╔══██║██╔══╝  ██║   ██║██║╚════██║    ██╔═══╝                          ║
║    ██║  ██║███████╗╚██████╔╝██║███████║    ███████╗                         ║
║    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝    ╚══════╝                         ║
║                                                                              ║
║                     ██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗
║                     ██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
║                     ██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗  
║                     ██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
║                     ╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
║                      ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
║                                                                              ║
║              The Complete Self-Evolving System                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  Configuration:
    Population: {self.config.population_size} agents
    Genesis: {'ENABLED' if self.config.genesis_enabled else 'DISABLED'}
    Genesis rate: every {self.config.genesis_rate} cycles
    Source fragments: {len(self.genesis.analyzer.fragments) if self.genesis else 'N/A'}

  Running {cycles} cycles...
""")
        
        for i in range(cycles):
            result = self.step()
            results.append(result)
            
            if verbose:
                # Progress every 10 cycles
                if i % 10 == 0:
                    omega_stats = self.omega.status()
                    print(f"  Cycle {self.cycle:5d} | "
                          f"Pop {omega_stats['population']['size']:3d} | "
                          f"Fit {omega_stats['population']['mean_fitness']:.3f} | "
                          f"Emrg {omega_stats['emergence']['total_events']:5d} | "
                          f"GenMod {self.total_genesis_modifications:3d}")
                
                # Report Genesis events
                if result['genesis'] and result['genesis']['applied'] > 0:
                    print(f"    ⚡ GENESIS: {result['genesis']['applied']} source modifications applied!")
                
                # Report significant emergence
                for e in result['emergence'][:2]:
                    if e.get('type') not in ['catalytic_emergence']:  # Filter noise
                        print(f"    ★ {e.get('type', 'unknown')}: {e.get('description', '')[:40]}")
        
        elapsed = time.time() - self.start_time
        
        if verbose:
            print(f"""
{'='*80}
  Completed in {elapsed:.1f}s ({cycles/elapsed:.1f} cycles/sec)
{'='*80}
""")
        
        return results
    
    def status(self) -> Dict:
        """Get comprehensive system status."""
        omega_status = self.omega.status()
        genesis_stats = self.genesis.get_stats() if self.genesis else {}
        
        return {
            'cycle': self.cycle,
            'runtime': time.time() - self.start_time,
            
            'omega': omega_status,
            
            'genesis': {
                'enabled': self.config.genesis_enabled,
                'total_modifications': self.total_genesis_modifications,
                'source_fragments': genesis_stats.get('fragments', 0),
                'version_history': genesis_stats.get('version_history', 0),
                'last_genesis_cycle': self.last_genesis_cycle,
                'emergence_since_genesis': self.emergence_since_genesis
            },
            
            'levels': {
                'L0_source_mods': self.total_genesis_modifications,
                'L1_param_mods': omega_status['self_modification']['applied'],
                'L2_genome_mods': omega_status['population']['total_created'],
                'L3_emergence': omega_status['emergence']['total_events']
            }
        }
    
    def report(self) -> str:
        """Generate a comprehensive status report."""
        status = self.status()
        omega = status['omega']
        genesis = status['genesis']
        
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        AEGIS-2 ULTIMATE STATUS                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Cycle: {status['cycle']:>8}                    Runtime: {status['runtime']:>8.1f}s              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  MULTI-LEVEL SELF-MODIFICATION STACK                                        ║
║  ═══════════════════════════════════                                         ║
║                                                                              ║
║  Level 0 - SOURCE CODE (Genesis)                                            ║
║    Modifications: {genesis['total_modifications']:>6}    Fragments: {genesis['source_fragments']:>6}                  ║
║    Version History: {genesis['version_history']:>4} commits                                       ║
║                                                                              ║
║  Level 1 - EVOLUTION PARAMS (Meta-Evolution)                                ║
║    Primitives: {omega['meta_evolution']['primitives']:>6}    Created: {omega['meta_evolution']['primitives_created']:>6}                  ║
║    Fitness Components: {omega['meta_evolution']['fitness_components']:>3}                                           ║
║                                                                              ║
║  Level 2 - AGENT GENOMES (Population)                                       ║
║    Population: {omega['population']['size']:>6}    Created: {omega['population']['total_created']:>6}    Deaths: {omega['population']['total_deaths']:>6}  ║
║    Mean Fitness: {omega['population']['mean_fitness']:>.4f}                                           ║
║                                                                              ║
║  Level 3 - EMERGENT BEHAVIOR                                                ║
║    Total Events: {omega['emergence']['total_events']:>6}                                               ║
"""
    
    def save(self):
        """Save complete system state."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Omega
        self.omega.save()
        
        # Save Ultimate state
        state = {
            'name': self.name,
            'config': self.config.to_dict(),
            'cycle': self.cycle,
            'last_genesis_cycle': self.last_genesis_cycle,
            'total_genesis_modifications': self.total_genesis_modifications,
            'emergence_since_genesis': self.emergence_since_genesis,
            'genesis_events': self.genesis_events[-50:],
            'saved_at': datetime.now().isoformat()
        }
        
        with open(self.data_dir / "ultimate_state.json", 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return self.data_dir
    
    def cleanup(self):
        """Clean up resources."""
        if self.genesis:
            self.genesis.cleanup()


def demo():
    """Demonstrate the Ultimate system."""
    # Create Ultimate system
    config = UltimateConfig(
        population_size=3,
        genesis_enabled=True,
        genesis_rate=25,
        max_genesis_modifications_per_cycle=2,
        require_emergence_for_genesis=True,
        emergence_threshold=5
    )
    
    ultimate = AEGIS2Ultimate(name="demo", config=config)
    
    # Run
    ultimate.run(cycles=100, verbose=True)
    
    # Report
    print(ultimate.report())
    
    # Status summary
    status = ultimate.status()
    print(f"""
  Level Summary:
    L0 (Source):    {status['levels']['L0_source_mods']:>5} modifications
    L1 (Params):    {status['levels']['L1_param_mods']:>5} modifications
    L2 (Genomes):   {status['levels']['L2_genome_mods']:>5} created
    L3 (Emergence): {status['levels']['L3_emergence']:>5} events
""")
    
    # Save
    save_path = ultimate.save()
    print(f"  State saved to: {save_path}")
    
    # Cleanup
    ultimate.cleanup()
    
    return ultimate


if __name__ == "__main__":
    demo()
