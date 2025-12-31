#!/usr/bin/env python3
"""
AEGIS-2 Command Line Interface

Run emergence experiments, visualize dynamics, and explore the system.
"""

import cmd
import json
import sys
import time
import math
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import threading

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.agent import AEGIS2
from population.dynamics import Population, Environment


class ProgressBar:
    """Simple progress bar for terminal."""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, current: int, suffix: str = ""):
        self.current = current
        filled = int(self.width * current / self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        percent = 100 * current / self.total
        print(f'\r  [{bar}] {percent:.1f}% {suffix}', end='', flush=True)
    
    def finish(self):
        print()


class AEGIS2CLI(cmd.Cmd):
    """Interactive CLI for AEGIS-2."""
    
    intro = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗ ██████╗ ██╗███████╗    ██████╗                          ║
║    ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝    ╚════██╗                         ║
║    ███████║█████╗  ██║  ███╗██║███████╗     █████╔╝                         ║
║    ██╔══██║██╔══╝  ██║   ██║██║╚════██║    ██╔═══╝                          ║
║    ██║  ██║███████╗╚██████╔╝██║███████║    ███████╗                         ║
║    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝    ╚══════╝                         ║
║                                                                              ║
║         Adaptive Emergent Generative Intelligence System v2                 ║
║                                                                              ║
║    An open-ended evolving system designed for genuine emergence.            ║
║                                                                              ║
║    Type 'help' for commands, 'tutorial' for getting started.               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    prompt = '\033[1;36maegis2>\033[0m '
    
    def __init__(self):
        super().__init__()
        self.agent: Optional[AEGIS2] = None
        self.population: Optional[Population] = None
        self.running = False
        self.data_dir = Path.cwd() / ".aegis2_data"
        
        # Experiment tracking
        self.experiment_name: Optional[str] = None
        self.experiment_log: List[Dict] = []
    
    # === BASIC COMMANDS ===
    
    def do_create(self, arg):
        """Create a new AEGIS-2 agent: create [name]"""
        name = arg.strip() or f"agent_{datetime.now().strftime('%H%M%S')}"
        self.agent = AEGIS2(name=name, data_dir=str(self.data_dir / name))
        print(f"  ✓ Created agent: {name}")
        self._show_agent_summary()
    
    def do_status(self, arg):
        """Show current agent/population status"""
        if self.population:
            self._show_population_status()
        elif self.agent:
            self._show_agent_status()
        else:
            print("  No agent or population active. Use 'create' or 'population'.")
    
    def do_step(self, arg):
        """Run one step: step [count]"""
        if not self.agent:
            print("  No agent active. Use 'create' first.")
            return
        
        count = int(arg) if arg.strip().isdigit() else 1
        
        for i in range(count):
            inputs = {
                'signal': math.sin(self.agent.cycle / 10) * 0.5 + 0.5,
                'noise': random.random()
            }
            result = self.agent.step(inputs)
            
            if result.get('emergence'):
                print(f"  Cycle {self.agent.cycle}: EMERGENCE!")
                for e in result['emergence']:
                    print(f"    ★ {e['type']}: {e.get('description', '')[:50]}")
        
        print(f"  Completed {count} step(s). Cycle: {self.agent.cycle}, Fitness: {self.agent.fitness:.4f}")
    
    def do_run(self, arg):
        """Run for multiple cycles: run <cycles> [--verbose]"""
        if not self.agent:
            print("  No agent active. Use 'create' first.")
            return
        
        parts = arg.split()
        cycles = int(parts[0]) if parts and parts[0].isdigit() else 100
        verbose = '--verbose' in parts or '-v' in parts
        
        print(f"  Running {cycles} cycles...")
        
        progress = ProgressBar(cycles)
        emergence_count = 0
        
        start_fitness = self.agent.fitness
        start_time = time.time()
        
        for i in range(cycles):
            inputs = {
                'signal': math.sin(self.agent.cycle / 10) * 0.5 + 0.5,
                'noise': random.random(),
                'cycle': i
            }
            result = self.agent.step(inputs)
            
            if result.get('emergence'):
                emergence_count += len(result['emergence'])
                if verbose:
                    for e in result['emergence']:
                        print(f"\n    ★ {e['type']}")
            
            progress.update(i + 1, f"F={self.agent.fitness:.3f}")
        
        progress.finish()
        elapsed = time.time() - start_time
        
        print(f"""
  ╔══════════════════════════════════════════╗
  ║  Run Complete                            ║
  ╠══════════════════════════════════════════╣
  ║  Cycles:     {cycles:>8}                   ║
  ║  Time:       {elapsed:>7.2f}s                   ║
  ║  Cycles/sec: {cycles/elapsed:>8.1f}                   ║
  ║                                          ║
  ║  Fitness:    {start_fitness:.4f} → {self.agent.fitness:.4f}         ║
  ║  Emergence:  {emergence_count:>8} events            ║
  ╚══════════════════════════════════════════╝
""")
    
    def do_save(self, arg):
        """Save current state: save [path]"""
        if self.agent:
            path = arg.strip() if arg.strip() else None
            self.agent.save(path)
            print(f"  ✓ Saved agent to {self.agent.data_dir}")
        elif self.population:
            self.population.save()
            print(f"  ✓ Saved population to {self.population.data_dir}")
        else:
            print("  Nothing to save.")
    
    def do_load(self, arg):
        """Load saved state: load <name>"""
        name = arg.strip()
        if not name:
            print("  Usage: load <agent_name>")
            return
        
        path = self.data_dir / name / "aegis2_state.json"
        if path.exists():
            self.agent = AEGIS2(name=name, data_dir=str(self.data_dir / name))
            self.agent.load()
            print(f"  ✓ Loaded agent: {name}")
            self._show_agent_summary()
        else:
            print(f"  No saved state found for: {name}")
    
    # === POPULATION COMMANDS ===
    
    def do_population(self, arg):
        """Create/manage population: population [create|status|run] [args]"""
        parts = arg.split()
        subcmd = parts[0] if parts else 'status'
        
        if subcmd == 'create':
            size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            self.population = Population(
                size=size,
                environment=Environment(complexity=0.5, volatility=0.2),
                data_dir=str(self.data_dir / "population")
            )
            print(f"  ✓ Created population with {size} agents")
            
        elif subcmd == 'run':
            if not self.population:
                print("  No population. Use 'population create' first.")
                return
            
            generations = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 50
            
            print(f"  Running {generations} generations...")
            progress = ProgressBar(generations)
            
            for g in range(generations):
                self.population.generation = g
                result = self.population.step()
                progress.update(g + 1, f"pop={len(self.population.agents)}")
                
                if result.get('emergence'):
                    for e in result['emergence']:
                        print(f"\n    ★ {e.get('type', 'unknown')}")
            
            progress.finish()
            self._show_population_status()
            
        else:
            self._show_population_status()
    
    # === EXPLORATION COMMANDS ===
    
    def do_genome(self, arg):
        """Explore genome: genome [list|detail <id>|mutate]"""
        if not self.agent:
            print("  No agent active.")
            return
        
        parts = arg.split()
        subcmd = parts[0] if parts else 'list'
        
        if subcmd == 'list':
            print(f"\n  Genome: {len(self.agent.genome.genes)} genes")
            print("  " + "-" * 50)
            for gene_id, gene in list(self.agent.genome.genes.items())[:10]:
                print(f"    {gene_id[:10]:12s} | {gene.name:20s} | expr={gene.expression:.2f}")
            if len(self.agent.genome.genes) > 10:
                print(f"    ... and {len(self.agent.genome.genes) - 10} more")
                
        elif subcmd == 'detail' and len(parts) > 1:
            gene_id = parts[1]
            for gid, gene in self.agent.genome.genes.items():
                if gene_id in gid:
                    print(f"\n  Gene: {gene.id}")
                    print(f"  Name: {gene.name}")
                    print(f"  Type: {gene.gene_type}")
                    print(f"  Expression: {gene.expression:.4f}")
                    print(f"  Fitness: {gene.fitness_contribution:.4f}")
                    print(f"  Generation: {gene.generation}")
                    print(f"  Mutations: {gene.mutations}")
                    break
        
        elif subcmd == 'mutate':
            if self.agent.genome.genes:
                gene = random.choice(list(self.agent.genome.genes.values()))
                self.agent.genome._mutate_gene(gene)
                print(f"  ✓ Mutated gene: {gene.id}")
    
    def do_patterns(self, arg):
        """Explore patterns: patterns [list|compose|abstract]"""
        if not self.agent:
            print("  No agent active.")
            return
        
        parts = arg.split()
        subcmd = parts[0] if parts else 'list'
        
        if subcmd == 'list':
            stats = self.agent.patterns.get_stats()
            print(f"\n  Patterns: {stats['total_patterns']}")
            print(f"  Compositions: {stats['compositions']}")
            print(f"  Abstractions: {stats['abstractions']}")
            print("  " + "-" * 50)
            
            for pid, pattern in list(self.agent.patterns.patterns.items())[:10]:
                print(f"    {pid[:10]:12s} | {pattern.name[:25]:25s} | c={pattern.complexity()}")
                
        elif subcmd == 'compose':
            patterns = list(self.agent.patterns.patterns.values())
            if len(patterns) >= 2:
                p1, p2 = random.sample(patterns, 2)
                composed = self.agent.patterns.compose([p1, p2])
                print(f"  ✓ Composed: {composed.id}")
    
    def do_goals(self, arg):
        """Explore goals: goals [list|active|spawn]"""
        if not self.agent:
            print("  No agent active.")
            return
        
        parts = arg.split()
        subcmd = parts[0] if parts else 'list'
        
        stats = self.agent.goals.get_stats()
        
        if subcmd == 'list':
            print(f"\n  Total Goals: {stats['total_goals']}")
            print(f"  Spawned: {stats['goals_spawned']}")
            print(f"  Satisfied: {stats['goals_satisfied']}")
            print("  " + "-" * 50)
            print("  By State:")
            for state, count in stats['by_state'].items():
                print(f"    {state:15s}: {count}")
                
        elif subcmd == 'active':
            active = self.agent.goals.get_active_goals()
            print(f"\n  Active Goals: {len(active)}")
            for goal in active[:10]:
                print(f"    {goal.id[:10]:12s} | {goal.goal_type.value:10s} | p={goal.priority:.2f}")
                
        elif subcmd == 'spawn':
            from goals.automata import GoalType
            goal = self.agent.goals.spawn_goal(
                random.choice(list(GoalType)),
                target="user_spawned"
            )
            print(f"  ✓ Spawned goal: {goal.id}")
    
    def do_novelty(self, arg):
        """Explore novelty engine: novelty [stats|frontiers|archive]"""
        if not self.agent:
            print("  No agent active.")
            return
        
        stats = self.agent.novelty.get_stats()
        
        print(f"\n  Novelty Engine Stats:")
        print("  " + "-" * 50)
        print(f"    Behaviors explored: {stats['behaviors_explored']}")
        print(f"    Novel found: {stats['novel_behaviors_found']}")
        print(f"    Novelty rate: {stats['novelty_rate']:.2%}")
        print(f"    Surprises detected: {stats['surprises_detected']}")
        print(f"    Archive size: {stats['archive']['archive_size']}")
        print(f"    Frontiers: {stats['frontiers']}")
    
    def do_criticality(self, arg):
        """Show criticality metrics"""
        if not self.agent:
            print("  No agent active.")
            return
        
        stats = self.agent.criticality.get_stats()
        metrics = stats['metrics']
        
        print(f"\n  Criticality Analysis:")
        print("  " + "-" * 50)
        print(f"    Order parameter: {metrics['order_parameter']:.4f}")
        print(f"    Branching ratio: {metrics['branching_ratio']:.4f}")
        print(f"    Correlation length: {metrics['correlation_length']:.4f}")
        print(f"    Power law exponent: {metrics['power_law_exponent']:.4f}")
        print(f"    Entropy: {metrics['entropy']:.4f}")
        print(f"    Critical distance: {metrics['criticality_distance']:.4f}")
        print(f"    Is critical: {'YES' if metrics['is_critical'] else 'NO'}")
    
    def do_hierarchy(self, arg):
        """Show strange loop hierarchy"""
        if not self.agent:
            print("  No agent active.")
            return
        
        stats = self.agent.hierarchy.get_stats()
        
        print(f"\n  Tangled Hierarchy:")
        print("  " + "-" * 50)
        print(f"    Levels: {stats['num_levels']}")
        print(f"    Strange loops: {stats['num_loops']}")
        print(f"    Level crossings: {stats['level_crossings']}")
        print(f"    Loop traversals: {stats['loop_traversals']}")
        print(f"    Emergent properties: {stats['emergent_properties_detected']}")
        print(f"    Self-model updates: {stats['self_model_updates']}")
        print(f"    Self-prediction accuracy: {stats['self_prediction_accuracy']:.2%}")
    
    def do_catalysis(self, arg):
        """Show autocatalytic networks"""
        if not self.agent:
            print("  No agent active.")
            return
        
        stats = self.agent.catalysis.get_stats()
        
        print(f"\n  Autocatalytic Network:")
        print("  " + "-" * 50)
        print(f"    Sets: {stats['num_sets']}")
        print(f"    Total entities: {stats['total_entities']}")
        print(f"    Closed sets: {stats['closed_sets']}")
        print(f"    Avg closure: {stats['avg_closure']:.2%}")
        print(f"    Sets created: {stats['sets_created']}")
        print(f"    Sets merged: {stats['sets_merged']}")
    
    def do_emergence(self, arg):
        """Show emergence history"""
        if not self.agent:
            print("  No agent active.")
            return
        
        phenomena = self.agent.emergent_phenomena
        
        print(f"\n  Emergence Events: {len(phenomena)}")
        print("  " + "-" * 50)
        
        # Group by type
        by_type = {}
        for p in phenomena:
            t = p.get('type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1
        
        for t, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"    {t:25s}: {count}")
        
        if phenomena:
            print("\n  Recent events:")
            for p in phenomena[-5:]:
                print(f"    Cycle {p.get('cycle', '?')}: {p.get('type', '?')} - {p.get('description', '')[:40]}")
    
    # === EXPERIMENT COMMANDS ===
    
    def do_experiment(self, arg):
        """Run structured experiment: experiment <name> <cycles>"""
        parts = arg.split()
        if len(parts) < 2:
            print("  Usage: experiment <name> <cycles>")
            return
        
        name = parts[0]
        cycles = int(parts[1])
        
        self.experiment_name = name
        self.experiment_log = []
        
        print(f"\n  ╔════════════════════════════════════════╗")
        print(f"  ║  Experiment: {name:26s} ║")
        print(f"  ╠════════════════════════════════════════╣")
        
        # Create fresh agent
        self.agent = AEGIS2(name=f"exp_{name}", data_dir=str(self.data_dir / f"exp_{name}"))
        
        print(f"  ║  Agent: {self.agent.name:28s} ║")
        print(f"  ║  Cycles: {cycles:27d} ║")
        print(f"  ╚════════════════════════════════════════╝")
        print()
        
        # Run experiment
        progress = ProgressBar(cycles)
        checkpoints = [cycles // 4, cycles // 2, 3 * cycles // 4, cycles]
        
        for i in range(cycles):
            inputs = {
                'signal': math.sin(i / 10) * 0.5 + 0.5,
                'noise': random.random() * 0.3,
                'cycle': i
            }
            result = self.agent.step(inputs)
            
            # Log
            self.experiment_log.append({
                'cycle': i,
                'fitness': self.agent.fitness,
                'emergence': len(result.get('emergence', []))
            })
            
            progress.update(i + 1, f"F={self.agent.fitness:.3f}")
            
            # Checkpoint reporting
            if i + 1 in checkpoints:
                print()
                self._experiment_checkpoint(i + 1, cycles)
        
        progress.finish()
        
        # Final report
        self._experiment_report()
        
        # Save
        self.agent.save()
        
        # Save experiment log
        log_path = self.data_dir / f"exp_{name}" / "experiment_log.json"
        with open(log_path, 'w') as f:
            json.dump(self.experiment_log, f)
        
        print(f"\n  Experiment saved to: {self.data_dir / f'exp_{name}'}")
    
    def _experiment_checkpoint(self, cycle: int, total: int):
        """Print experiment checkpoint."""
        pct = cycle / total * 100
        print(f"\n  ── Checkpoint {pct:.0f}% ──")
        print(f"     Fitness: {self.agent.fitness:.4f}")
        print(f"     Genes: {len(self.agent.genome.genes)}")
        print(f"     Patterns: {len(self.agent.patterns.patterns)}")
        print(f"     Emergence: {len(self.agent.emergent_phenomena)}")
    
    def _experiment_report(self):
        """Print final experiment report."""
        print(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║                    EXPERIMENT COMPLETE                       ║
  ╠══════════════════════════════════════════════════════════════╣
""")
        
        status = self.agent.status()
        
        print(f"  ║  Final Fitness:     {status['fitness']:>8.4f}                       ║")
        print(f"  ║  Cycles Completed:  {status['cycle']:>8d}                       ║")
        print(f"  ║                                                              ║")
        print(f"  ║  Genome:                                                     ║")
        print(f"  ║    Genes:           {status['genome']['total_genes']:>8d}                       ║")
        print(f"  ║    Mutations:       {status['genome']['total_mutations']:>8d}                       ║")
        print(f"  ║                                                              ║")
        print(f"  ║  Patterns:          {status['patterns']['total_patterns']:>8d}                       ║")
        print(f"  ║  Goals Satisfied:   {status['goals']['goals_satisfied']:>8d}                       ║")
        print(f"  ║  Novel Behaviors:   {status['novelty']['novel_behaviors_found']:>8d}                       ║")
        print(f"  ║  Emergence Events:  {status['emergent_phenomena']:>8d}                       ║")
        print(f"  ╚══════════════════════════════════════════════════════════════╝")
    
    # === VISUALIZATION ===
    
    def do_visualize(self, arg):
        """Visualize system state: visualize [fitness|genome|emergence]"""
        if not self.agent:
            print("  No agent active.")
            return
        
        parts = arg.split()
        what = parts[0] if parts else 'fitness'
        
        if what == 'fitness':
            self._visualize_fitness()
        elif what == 'genome':
            self._visualize_genome()
        elif what == 'emergence':
            self._visualize_emergence()
        else:
            print("  Options: fitness, genome, emergence")
    
    def _visualize_fitness(self):
        """ASCII visualization of fitness history."""
        history = self.agent.fitness_history[-60:]
        if not history:
            print("  No fitness history yet.")
            return
        
        max_f = max(history)
        min_f = min(history)
        range_f = max_f - min_f if max_f > min_f else 1
        
        height = 10
        width = len(history)
        
        print(f"\n  Fitness History (last {len(history)} cycles)")
        print(f"  {max_f:.3f} ┤", end="")
        
        for row in range(height):
            threshold = max_f - (row / height) * range_f
            line = ""
            for val in history:
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            if row > 0:
                print(f"        │{line}")
            else:
                print(line)
        
        print(f"  {min_f:.3f} └" + "─" * width)
    
    def _visualize_genome(self):
        """ASCII visualization of genome structure."""
        genes = list(self.agent.genome.genes.values())
        if not genes:
            print("  No genes.")
            return
        
        print(f"\n  Genome Structure ({len(genes)} genes)")
        print("  " + "─" * 50)
        
        # Group by type
        by_type = {}
        for gene in genes:
            t = gene.gene_type
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(gene)
        
        for gtype, type_genes in by_type.items():
            print(f"  {gtype}:")
            bar_width = 40
            for gene in type_genes[:5]:
                expr = min(1.0, gene.expression)
                filled = int(bar_width * expr)
                bar = "▓" * filled + "░" * (bar_width - filled)
                print(f"    {gene.id[:8]:10s} [{bar}] {expr:.2f}")
            if len(type_genes) > 5:
                print(f"    ... and {len(type_genes) - 5} more")
    
    def _visualize_emergence(self):
        """ASCII visualization of emergence timeline."""
        phenomena = self.agent.emergent_phenomena
        if not phenomena:
            print("  No emergence events yet.")
            return
        
        print(f"\n  Emergence Timeline ({len(phenomena)} events)")
        print("  " + "─" * 60)
        
        # Timeline
        max_cycle = self.agent.cycle
        width = 60
        
        timeline = [' '] * width
        for p in phenomena:
            cycle = p.get('cycle', 0)
            pos = int((cycle / max(1, max_cycle)) * (width - 1))
            timeline[pos] = '★'
        
        print("  " + "".join(timeline))
        print(f"  0{'─' * (width-2)}{max_cycle}")
    
    # === UTILITY ===
    
    def do_tutorial(self, arg):
        """Show getting started tutorial"""
        print("""
  ╔═══════════════════════════════════════════════════════════════╗
  ║                    AEGIS-2 TUTORIAL                           ║
  ╚═══════════════════════════════════════════════════════════════╝
  
  AEGIS-2 is an open-ended evolving system designed for emergence.
  
  QUICK START:
  
    1. Create an agent:
       > create my_agent
    
    2. Run some cycles:
       > run 100
    
    3. Check status:
       > status
    
    4. Explore subsystems:
       > genome list
       > patterns list
       > goals active
       > emergence
    
    5. Run a longer experiment:
       > experiment test1 1000
    
    6. Save your work:
       > save
  
  KEY CONCEPTS:
  
    • MetaGenome: Self-modifying genetic programs
    • Patterns: Compositional structure recognition  
    • Goals: Self-spawning objectives with intrinsic motivation
    • Novelty: Curiosity-driven exploration
    • Strange Loops: Self-reference enabling meta-cognition
    • Autocatalysis: Self-sustaining reaction networks
    • Criticality: Edge of chaos dynamics
  
  COMMANDS:
    Type 'help' for full command list.
    Type 'help <command>' for specific command help.
""")
    
    def do_quit(self, arg):
        """Exit the CLI"""
        print("\n  Goodbye!\n")
        return True
    
    def do_exit(self, arg):
        """Exit the CLI"""
        return self.do_quit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        print()
        return self.do_quit(arg)
    
    # === HELPERS ===
    
    def _show_agent_summary(self):
        """Show brief agent summary."""
        if not self.agent:
            return
        print(f"    Cycle: {self.agent.cycle}")
        print(f"    Fitness: {self.agent.fitness:.4f}")
        print(f"    Genes: {len(self.agent.genome.genes)}")
        print(f"    Patterns: {len(self.agent.patterns.patterns)}")
    
    def _show_agent_status(self):
        """Show detailed agent status."""
        if not self.agent:
            return
        
        status = self.agent.status()
        
        print(f"""
  ╔══════════════════════════════════════════╗
  ║  Agent: {self.agent.name:30s}  ║
  ╠══════════════════════════════════════════╣
  ║  Cycle:    {status['cycle']:>8d}                   ║
  ║  Fitness:  {status['fitness']:>8.4f}                   ║
  ╠══════════════════════════════════════════╣
  ║  Genome:                                 ║
  ║    Genes:      {status['genome']['total_genes']:>6d}                   ║
  ║    Mutations:  {status['genome']['total_mutations']:>6d}                   ║
  ║                                          ║
  ║  Patterns:     {status['patterns']['total_patterns']:>6d}                   ║
  ║  Goals:        {status['goals']['total_goals']:>6d}                   ║
  ║  Novelty Rate: {status['novelty']['novelty_rate']:>6.2%}                   ║
  ║                                          ║
  ║  Emergence:    {status['emergent_phenomena']:>6d}                   ║
  ╚══════════════════════════════════════════╝
""")
    
    def _show_population_status(self):
        """Show population status."""
        if not self.population:
            print("  No population active.")
            return
        
        stats = self.population.get_stats()
        
        print(f"""
  ╔══════════════════════════════════════════╗
  ║  Population Status                       ║
  ╠══════════════════════════════════════════╣
  ║  Size:         {stats['population_size']:>6d}                   ║
  ║  Generation:   {stats['generation']:>6d}                   ║
  ║  Mean Fitness: {stats['mean_fitness']:>6.4f}                   ║
  ║  Max Fitness:  {stats['max_fitness']:>6.4f}                   ║
  ║  Diversity:    {stats['diversity']:>6.4f}                   ║
  ║                                          ║
  ║  Total Created: {stats['total_created']:>5d}                   ║
  ║  Total Deaths:  {stats['total_deaths']:>5d}                   ║
  ║  Reproductions: {stats['total_reproductions']:>5d}                   ║
  ║                                          ║
  ║  Meme Pool:    {stats['meme_pool_size']:>6d}                   ║
  ║  Emergence:    {stats['emergence_events']:>6d}                   ║
  ╚══════════════════════════════════════════╝
""")
    
    def default(self, line):
        """Handle unknown commands."""
        print(f"  Unknown command: {line}")
        print("  Type 'help' for available commands.")
    
    def emptyline(self):
        """Handle empty line."""
        pass


def main():
    """Main entry point."""
    cli = AEGIS2CLI()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n  Interrupted. Goodbye!\n")


if __name__ == "__main__":
    main()
