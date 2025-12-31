"""
AEGIS-2 Observatory: Deep Analysis of Emergent Structures

This module provides tools to understand what's actually happening
inside the system - what structures are forming, what dynamics are
emerging, and whether there's genuine novelty.

Key analyses:
1. Structural Analysis - What complex structures have emerged?
2. Dynamical Analysis - What attractors/patterns exist in state space?
3. Information Analysis - How is information flowing and being created?
4. Novelty Analysis - Is the system discovering genuinely new things?
5. Criticality Analysis - Is the system at the edge of chaos?
"""

import math
import json
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import random


@dataclass
class StructuralSignature:
    """Signature of an emergent structure."""
    id: str
    structure_type: str  # 'genome', 'pattern', 'goal', 'loop', 'catalyst'
    complexity: float
    components: List[str]
    first_seen: int  # cycle
    occurrences: int = 1
    
    # Relationships
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.structure_type,
            'complexity': self.complexity,
            'components': len(self.components),
            'first_seen': self.first_seen,
            'occurrences': self.occurrences
        }


@dataclass
class DynamicalState:
    """A state in the system's trajectory."""
    cycle: int
    state_hash: str
    
    # Key metrics
    fitness: float
    novelty: float
    criticality: float
    
    # Counts
    genes: int
    patterns: int
    goals: int
    loops: int
    catalysts: int
    
    def to_vector(self) -> List[float]:
        return [
            self.fitness, self.novelty, self.criticality,
            self.genes / 100, self.patterns / 100, self.goals / 10,
            self.loops / 10, self.catalysts / 10
        ]


class StructuralAnalyzer:
    """
    Analyzes emergent structures in the system.
    
    Tracks what complex structures have formed and how they relate.
    """
    
    def __init__(self):
        self.structures: Dict[str, StructuralSignature] = {}
        self.structure_history: List[Tuple[int, str]] = []  # (cycle, structure_id)
        self.complexity_distribution: List[float] = []
    
    def analyze_agent(self, agent, cycle: int) -> Dict[str, Any]:
        """Analyze structures in an agent."""
        results = {
            'new_structures': 0,
            'total_structures': 0,
            'max_complexity': 0,
            'structure_types': Counter()
        }
        
        # Analyze genome
        if hasattr(agent, 'genome'):
            for gene_id, gene in agent.genome.genes.items():
                sig = self._extract_gene_signature(gene, cycle)
                if sig:
                    self._record_structure(sig)
                    results['structure_types']['genome'] += 1
        
        # Analyze patterns
        if hasattr(agent, 'patterns'):
            for pattern in agent.patterns.patterns.values():
                sig = self._extract_pattern_signature(pattern, cycle)
                if sig:
                    self._record_structure(sig)
                    results['structure_types']['pattern'] += 1
        
        # Analyze goals
        if hasattr(agent, 'goals'):
            for goal in agent.goals.goals.values():
                sig = self._extract_goal_signature(goal, cycle)
                if sig:
                    self._record_structure(sig)
                    results['structure_types']['goal'] += 1
        
        # Analyze loops
        if hasattr(agent, 'loops'):
            for loop in agent.loops.loops.values():
                sig = self._extract_loop_signature(loop, cycle)
                if sig:
                    self._record_structure(sig)
                    results['structure_types']['loop'] += 1
        
        # Analyze catalysts
        if hasattr(agent, 'catalysis') and hasattr(agent.catalysis, 'entities'):
            for entity in agent.catalysis.entities.values():
                sig = self._extract_catalyst_signature(entity, cycle)
                if sig:
                    self._record_structure(sig)
                    results['structure_types']['catalyst'] += 1
        elif hasattr(agent, 'catalysis') and hasattr(agent.catalysis, 'sets'):
            # Alternative: check for catalytic sets
            for cat_set in agent.catalysis.sets.values():
                results['structure_types']['catalyst'] += 1
        
        results['total_structures'] = len(self.structures)
        if self.complexity_distribution:
            results['max_complexity'] = max(self.complexity_distribution[-100:])
        
        return results
    
    def _extract_gene_signature(self, gene, cycle: int) -> Optional[StructuralSignature]:
        """Extract signature from a gene."""
        if not hasattr(gene, 'program') or not gene.program:
            return None
        
        # Build component list from program tree
        components = []
        def traverse(node):
            if hasattr(node, 'node_type'):
                components.append(str(node.node_type))
            if hasattr(node, 'children'):
                for child in node.children:
                    traverse(child)
        
        traverse(gene.program)
        
        if len(components) < 3:
            return None
        
        sig_id = hashlib.sha256('_'.join(components).encode()).hexdigest()[:12]
        complexity = len(components) * math.log(len(set(components)) + 1)
        
        return StructuralSignature(
            id=sig_id,
            structure_type='genome',
            complexity=complexity,
            components=components,
            first_seen=cycle
        )
    
    def _extract_pattern_signature(self, pattern, cycle: int) -> Optional[StructuralSignature]:
        """Extract signature from a pattern."""
        components = []
        
        if hasattr(pattern, 'operator'):
            components.append(str(pattern.operator))
        if hasattr(pattern, 'subpatterns'):
            for sub in pattern.subpatterns:
                if hasattr(sub, 'name'):
                    components.append(sub.name)
        
        if len(components) < 2:
            return None
        
        sig_id = hashlib.sha256('_'.join(components).encode()).hexdigest()[:12]
        complexity = len(components) ** 1.5
        
        return StructuralSignature(
            id=sig_id,
            structure_type='pattern',
            complexity=complexity,
            components=components,
            first_seen=cycle
        )
    
    def _extract_goal_signature(self, goal, cycle: int) -> Optional[StructuralSignature]:
        """Extract signature from a goal."""
        components = []
        
        if hasattr(goal, 'goal_type'):
            components.append(str(goal.goal_type))
        if hasattr(goal, 'parent_id') and goal.parent_id:
            components.append(f"parent:{goal.parent_id[:8]}")
        if hasattr(goal, 'subgoals'):
            components.extend([f"sub:{sg[:8]}" for sg in goal.subgoals[:5]])
        
        if len(components) < 2:
            return None
        
        sig_id = hashlib.sha256('_'.join(components).encode()).hexdigest()[:12]
        complexity = len(components) * 2
        
        return StructuralSignature(
            id=sig_id,
            structure_type='goal',
            complexity=complexity,
            components=components,
            first_seen=cycle
        )
    
    def _extract_loop_signature(self, loop, cycle: int) -> Optional[StructuralSignature]:
        """Extract signature from a strange loop."""
        components = []
        
        if hasattr(loop, 'levels'):
            components.extend([l.name for l in loop.levels])
        if hasattr(loop, 'loop_type'):
            components.append(str(loop.loop_type))
        
        if len(components) < 2:
            return None
        
        sig_id = hashlib.sha256('_'.join(components).encode()).hexdigest()[:12]
        complexity = len(components) ** 2  # Loops are inherently complex
        
        return StructuralSignature(
            id=sig_id,
            structure_type='loop',
            complexity=complexity,
            components=components,
            first_seen=cycle
        )
    
    def _extract_catalyst_signature(self, entity, cycle: int) -> Optional[StructuralSignature]:
        """Extract signature from a catalytic entity."""
        components = []
        
        if hasattr(entity, 'entity_type'):
            components.append(str(entity.entity_type))
        if hasattr(entity, 'catalyzes'):
            components.extend([r[:8] for r in entity.catalyzes[:5]])
        
        if len(components) < 2:
            return None
        
        sig_id = hashlib.sha256('_'.join(components).encode()).hexdigest()[:12]
        complexity = len(components) * 1.5
        
        return StructuralSignature(
            id=sig_id,
            structure_type='catalyst',
            complexity=complexity,
            components=components,
            first_seen=cycle
        )
    
    def _record_structure(self, sig: StructuralSignature):
        """Record a structure."""
        if sig.id in self.structures:
            self.structures[sig.id].occurrences += 1
        else:
            self.structures[sig.id] = sig
        
        self.structure_history.append((sig.first_seen, sig.id))
        self.complexity_distribution.append(sig.complexity)
    
    def get_novel_structures(self, since_cycle: int = 0) -> List[StructuralSignature]:
        """Get structures first seen after a given cycle."""
        return [s for s in self.structures.values() if s.first_seen >= since_cycle]
    
    def get_most_complex(self, n: int = 10) -> List[StructuralSignature]:
        """Get the most complex structures."""
        return sorted(self.structures.values(), 
                     key=lambda s: s.complexity, reverse=True)[:n]
    
    def complexity_growth_rate(self, window: int = 50) -> float:
        """Calculate rate of complexity growth."""
        if len(self.complexity_distribution) < window * 2:
            return 0.0
        
        old = sum(self.complexity_distribution[-window*2:-window]) / window
        new = sum(self.complexity_distribution[-window:]) / window
        
        if old == 0:
            return 0.0
        
        return (new - old) / old


class DynamicalAnalyzer:
    """
    Analyzes the dynamical behavior of the system.
    
    Tracks trajectories in state space, identifies attractors,
    and measures stability/chaos.
    """
    
    def __init__(self):
        self.states: List[DynamicalState] = []
        self.state_hashes: Set[str] = set()
        self.transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Attractor detection
        self.potential_attractors: Dict[str, int] = defaultdict(int)
    
    def record_state(self, agent, cycle: int) -> DynamicalState:
        """Record the current state."""
        # Extract key metrics
        fitness = getattr(agent, 'fitness', 0.5)
        
        novelty = 0.0
        if hasattr(agent, 'novelty'):
            if hasattr(agent.novelty, 'archive'):
                archive = agent.novelty.archive
                if hasattr(archive, 'behaviors'):
                    novelty = len(archive.behaviors) / 100
                elif hasattr(archive, '__len__'):
                    novelty = len(archive) / 100
                else:
                    novelty = 0.5
        
        criticality = 0.5
        if hasattr(agent, 'criticality') and hasattr(agent.criticality, 'metrics'):
            criticality = getattr(agent.criticality.metrics, 'criticality', 0.5)
        
        # Count structures
        genes = len(agent.genome.genes) if hasattr(agent, 'genome') else 0
        patterns = len(agent.patterns.patterns) if hasattr(agent, 'patterns') else 0
        goals = len(agent.goals.goals) if hasattr(agent, 'goals') else 0
        loops = 0
        if hasattr(agent, 'loops'):
            if hasattr(agent.loops, 'loops'):
                loops = len(agent.loops.loops)
            elif hasattr(agent.loops, 'hierarchy'):
                loops = 1
        catalysts = 0
        if hasattr(agent, 'catalysis'):
            if hasattr(agent.catalysis, 'entities'):
                catalysts = len(agent.catalysis.entities)
            elif hasattr(agent.catalysis, 'sets'):
                catalysts = len(agent.catalysis.sets)
        
        # Create state hash (discretized)
        state_tuple = (
            round(fitness, 1),
            round(novelty, 1),
            round(criticality, 1),
            genes // 10,
            patterns // 10
        )
        state_hash = hashlib.sha256(str(state_tuple).encode()).hexdigest()[:8]
        
        state = DynamicalState(
            cycle=cycle,
            state_hash=state_hash,
            fitness=fitness,
            novelty=novelty,
            criticality=criticality,
            genes=genes,
            patterns=patterns,
            goals=goals,
            loops=loops,
            catalysts=catalysts
        )
        
        # Record transition
        if self.states:
            prev_hash = self.states[-1].state_hash
            self.transitions[prev_hash][state_hash] += 1
        
        # Track potential attractors
        if state_hash in self.state_hashes:
            self.potential_attractors[state_hash] += 1
        
        self.states.append(state)
        self.state_hashes.add(state_hash)
        
        return state
    
    def detect_attractors(self, min_visits: int = 5) -> List[Dict]:
        """Detect potential attractors in state space."""
        attractors = []
        
        for state_hash, visits in self.potential_attractors.items():
            if visits >= min_visits:
                # Find all states with this hash
                matching = [s for s in self.states if s.state_hash == state_hash]
                if matching:
                    avg_state = matching[0]  # Use first as representative
                    attractors.append({
                        'hash': state_hash,
                        'visits': visits,
                        'fitness': avg_state.fitness,
                        'criticality': avg_state.criticality
                    })
        
        return sorted(attractors, key=lambda a: a['visits'], reverse=True)
    
    def lyapunov_estimate(self, window: int = 50) -> float:
        """
        Estimate Lyapunov exponent (chaos indicator).
        
        Positive = chaotic, negative = stable, zero = edge of chaos
        """
        if len(self.states) < window * 2:
            return 0.0
        
        divergences = []
        
        for i in range(len(self.states) - window):
            v1 = self.states[i].to_vector()
            v2 = self.states[i + window].to_vector()
            
            # Euclidean distance
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
            if dist > 0:
                divergences.append(math.log(dist + 0.001))
        
        if not divergences:
            return 0.0
        
        # Average log divergence rate
        return sum(divergences) / len(divergences) / window
    
    def entropy(self) -> float:
        """Calculate entropy of state distribution."""
        if not self.states:
            return 0.0
        
        hash_counts = Counter(s.state_hash for s in self.states)
        total = len(self.states)
        
        entropy = 0.0
        for count in hash_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log(p)
        
        return entropy


class InformationAnalyzer:
    """
    Analyzes information dynamics in the system.
    
    Measures:
    - Information creation (new structures)
    - Information flow (between subsystems)
    - Information compression (pattern reuse)
    """
    
    def __init__(self):
        self.info_history: List[Dict[str, float]] = []
        self.subsystem_info: Dict[str, List[float]] = defaultdict(list)
    
    def analyze(self, agent, cycle: int) -> Dict[str, float]:
        """Analyze information metrics."""
        results = {}
        
        # Genome information
        if hasattr(agent, 'genome'):
            genome_info = self._genome_information(agent.genome)
            results['genome_info'] = genome_info
            self.subsystem_info['genome'].append(genome_info)
        
        # Pattern information
        if hasattr(agent, 'patterns'):
            pattern_info = self._pattern_information(agent.patterns)
            results['pattern_info'] = pattern_info
            self.subsystem_info['patterns'].append(pattern_info)
        
        # Goal information
        if hasattr(agent, 'goals'):
            goal_info = self._goal_information(agent.goals)
            results['goal_info'] = goal_info
            self.subsystem_info['goals'].append(goal_info)
        
        # Total information
        results['total_info'] = sum(results.values())
        
        # Information creation rate
        if len(self.info_history) > 0:
            prev_total = self.info_history[-1].get('total_info', 0)
            results['info_creation_rate'] = results['total_info'] - prev_total
        else:
            results['info_creation_rate'] = 0
        
        self.info_history.append(results)
        
        return results
    
    def _genome_information(self, genome) -> float:
        """Calculate information content of genome."""
        if not hasattr(genome, 'genes'):
            return 0.0
        
        # Simple measure: unique node types * depth
        total_info = 0
        for gene in genome.genes.values():
            if hasattr(gene, 'program') and gene.program:
                node_types = set()
                depth = 0
                
                def traverse(node, d):
                    nonlocal depth
                    depth = max(depth, d)
                    if hasattr(node, 'node_type'):
                        node_types.add(str(node.node_type))
                    if hasattr(node, 'children'):
                        for child in node.children:
                            traverse(child, d + 1)
                
                traverse(gene.program, 0)
                total_info += len(node_types) * (depth + 1)
        
        return total_info
    
    def _pattern_information(self, patterns) -> float:
        """Calculate information content of patterns."""
        if not hasattr(patterns, 'patterns'):
            return 0.0
        
        total_info = 0
        for pattern in patterns.patterns.values():
            # Complexity based on composition depth
            if hasattr(pattern, 'complexity'):
                comp = pattern.complexity
                if callable(comp):
                    total_info += comp()
                else:
                    total_info += comp
            else:
                total_info += 1
        
        return total_info
    
    def _goal_information(self, goals) -> float:
        """Calculate information content of goals."""
        if not hasattr(goals, 'goals'):
            return 0.0
        
        total_info = 0
        for goal in goals.goals.values():
            # Information based on goal structure
            info = 1
            if hasattr(goal, 'subgoals'):
                info += len(goal.subgoals)
            if hasattr(goal, 'conditions'):
                info += len(goal.conditions)
            total_info += info
        
        return total_info
    
    def mutual_information(self, subsys1: str, subsys2: str, lag: int = 0) -> float:
        """Estimate mutual information between subsystems."""
        if subsys1 not in self.subsystem_info or subsys2 not in self.subsystem_info:
            return 0.0
        
        s1 = self.subsystem_info[subsys1]
        s2 = self.subsystem_info[subsys2]
        
        if len(s1) < lag + 10 or len(s2) < lag + 10:
            return 0.0
        
        # Simple correlation-based estimate
        if lag > 0:
            s1 = s1[:-lag]
            s2 = s2[lag:]
        
        n = min(len(s1), len(s2))
        s1 = s1[-n:]
        s2 = s2[-n:]
        
        mean1 = sum(s1) / n
        mean2 = sum(s2) / n
        
        cov = sum((a - mean1) * (b - mean2) for a, b in zip(s1, s2)) / n
        var1 = sum((a - mean1) ** 2 for a in s1) / n
        var2 = sum((b - mean2) ** 2 for b in s2) / n
        
        if var1 * var2 == 0:
            return 0.0
        
        correlation = cov / math.sqrt(var1 * var2)
        
        # Convert to MI-like measure
        if abs(correlation) < 1:
            return -0.5 * math.log(1 - correlation ** 2)
        return 0.0


class NoveltyAnalyzer:
    """
    Analyzes whether the system is discovering genuinely new things.
    
    Tracks:
    - First occurrences of structures
    - Discovery rate over time
    - Novelty plateau detection
    """
    
    def __init__(self):
        self.first_occurrences: Dict[str, int] = {}  # signature -> cycle
        self.discovery_counts: List[int] = []  # per-cycle discovery count
        self.novelty_scores: List[float] = []
    
    def analyze(self, structures: Dict[str, StructuralSignature], cycle: int) -> Dict[str, Any]:
        """Analyze novelty."""
        discoveries = 0
        
        for sig_id, sig in structures.items():
            if sig_id not in self.first_occurrences:
                self.first_occurrences[sig_id] = cycle
                discoveries += 1
        
        self.discovery_counts.append(discoveries)
        
        # Calculate novelty score
        total_known = len(self.first_occurrences)
        if total_known > 0:
            novelty_score = discoveries / (1 + math.log(total_known + 1))
        else:
            novelty_score = discoveries
        
        self.novelty_scores.append(novelty_score)
        
        # Detect plateau
        plateau = self._detect_plateau()
        
        return {
            'discoveries': discoveries,
            'total_discovered': total_known,
            'novelty_score': novelty_score,
            'discovery_rate': self._discovery_rate(),
            'plateau_detected': plateau
        }
    
    def _discovery_rate(self, window: int = 50) -> float:
        """Calculate discovery rate."""
        if len(self.discovery_counts) < window:
            return sum(self.discovery_counts) / len(self.discovery_counts) if self.discovery_counts else 0
        return sum(self.discovery_counts[-window:]) / window
    
    def _detect_plateau(self, window: int = 100, threshold: float = 0.1) -> bool:
        """Detect if novelty has plateaued."""
        if len(self.discovery_counts) < window * 2:
            return False
        
        recent = sum(self.discovery_counts[-window:])
        earlier = sum(self.discovery_counts[-window*2:-window])
        
        if earlier == 0:
            return recent == 0
        
        return recent / earlier < threshold


class Observatory:
    """
    Complete observatory for AEGIS-2 systems.
    
    Provides comprehensive analysis of emergent behavior.
    """
    
    def __init__(self):
        self.structural = StructuralAnalyzer()
        self.dynamical = DynamicalAnalyzer()
        self.information = InformationAnalyzer()
        self.novelty = NoveltyAnalyzer()
        
        self.cycle: int = 0
        self.observations: List[Dict] = []
    
    def observe(self, agent, cycle: Optional[int] = None) -> Dict[str, Any]:
        """Make a complete observation."""
        if cycle is None:
            self.cycle += 1
            cycle = self.cycle
        
        observation = {
            'cycle': cycle,
            'timestamp': datetime.now().isoformat()
        }
        
        # Structural analysis
        observation['structural'] = self.structural.analyze_agent(agent, cycle)
        
        # Dynamical analysis
        state = self.dynamical.record_state(agent, cycle)
        observation['dynamical'] = {
            'state_hash': state.state_hash,
            'fitness': state.fitness,
            'criticality': state.criticality,
            'unique_states': len(self.dynamical.state_hashes)
        }
        
        # Information analysis
        observation['information'] = self.information.analyze(agent, cycle)
        
        # Novelty analysis
        observation['novelty'] = self.novelty.analyze(self.structural.structures, cycle)
        
        self.observations.append(observation)
        
        return observation
    
    def report(self) -> str:
        """Generate a comprehensive report."""
        if not self.observations:
            return "No observations recorded."
        
        latest = self.observations[-1]
        
        # Dynamical analysis
        lyapunov = self.dynamical.lyapunov_estimate()
        entropy = self.dynamical.entropy()
        attractors = self.dynamical.detect_attractors()
        
        # Complexity analysis
        complexity_growth = self.structural.complexity_growth_rate()
        most_complex = self.structural.get_most_complex(5)
        
        # Information flow
        genome_pattern_mi = self.information.mutual_information('genome', 'patterns')
        pattern_goal_mi = self.information.mutual_information('patterns', 'goals')
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        OBSERVATORY REPORT                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Cycle: {self.cycle:>8}                                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  STRUCTURAL ANALYSIS                                                         ║
║  ───────────────────                                                         ║
║    Total structures:     {len(self.structural.structures):>6}                                           ║
║    Complexity growth:    {complexity_growth:>+6.2%}                                            ║
║                                                                              ║
║    Most complex structures:                                                  ║
"""
        for i, s in enumerate(most_complex):
            report += f"║      {i+1}. {s.structure_type:10s} complexity={s.complexity:>6.1f}  ({s.occurrences} occurrences)       ║\n"
        
        report += f"""║                                                                              ║
║  DYNAMICAL ANALYSIS                                                          ║
║  ──────────────────                                                          ║
║    Unique states:        {len(self.dynamical.state_hashes):>6}                                           ║
║    State entropy:        {entropy:>6.2f}                                           ║
║    Lyapunov estimate:    {lyapunov:>+6.3f}                                           ║
║    Attractors found:     {len(attractors):>6}                                           ║
║                                                                              ║
"""
        
        # Interpret Lyapunov
        if lyapunov > 0.1:
            interpretation = "CHAOTIC (high exploration)"
        elif lyapunov < -0.1:
            interpretation = "STABLE (converged)"
        else:
            interpretation = "CRITICAL (edge of chaos)"
        
        report += f"""║    Interpretation:       {interpretation:<30}          ║
║                                                                              ║
║  INFORMATION ANALYSIS                                                        ║
║  ────────────────────                                                        ║
║    Total information:    {latest['information']['total_info']:>6.1f}                                           ║
║    Creation rate:        {latest['information']['info_creation_rate']:>+6.1f}                                           ║
║    Genome→Pattern MI:    {genome_pattern_mi:>6.3f}                                           ║
║    Pattern→Goal MI:      {pattern_goal_mi:>6.3f}                                           ║
║                                                                              ║
║  NOVELTY ANALYSIS                                                            ║
║  ────────────────                                                            ║
║    Total discovered:     {latest['novelty']['total_discovered']:>6}                                           ║
║    Discovery rate:       {latest['novelty']['discovery_rate']:>6.2f}/cycle                                    ║
║    Plateau detected:     {'YES' if latest['novelty']['plateau_detected'] else 'NO':>6}                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return report
    
    def save(self, path: Path):
        """Save observations to file."""
        with open(path, 'w') as f:
            json.dump({
                'cycle': self.cycle,
                'observations': self.observations[-100:],  # Last 100
                'structures': [s.to_dict() for s in self.structural.structures.values()],
                'attractors': self.dynamical.detect_attractors()
            }, f, indent=2)


def demo():
    """Demonstrate the observatory."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.agent import AEGIS2
    
    print("Creating Observatory...")
    obs = Observatory()
    
    print("Creating AEGIS2 agent...")
    agent = AEGIS2('test')
    
    print("Running 100 cycles with observation...")
    for i in range(100):
        agent.step({'signal': i})
        obs.observe(agent, i)
        
        if i % 20 == 0:
            print(f"  Cycle {i}: {len(obs.structural.structures)} structures, "
                  f"{len(obs.dynamical.state_hashes)} states")
    
    print("\n" + obs.report())
    
    return obs


if __name__ == "__main__":
    demo()
