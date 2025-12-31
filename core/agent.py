"""
AEGIS-2 Core: Emergent Intelligence System

This is where it all comes together.

Integration of:
- MetaGenome: Self-modifying genetic programs
- Compositional Patterns: Unbounded pattern complexity
- Goal Automata: Self-spawning goals
- Novelty Engine: Curiosity-driven exploration
- Strange Loops: Self-reference and meta-cognition
- Autocatalytic Sets: Self-sustaining dynamics
- Criticality Engine: Edge of chaos regulation

The key insight: These systems don't just coexist - they FEED INTO EACH OTHER:
- Patterns trigger goals
- Goals drive exploration
- Exploration creates novelty
- Novelty updates the genome
- Genome creates new patterns
- Patterns form autocatalytic sets
- Sets maintain criticality
- Criticality enables strange loops
- Loops modify goals
- And around again...

This creates the CONDITIONS for emergence.
"""

import json
import random
import math
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from collections import deque

# Import all subsystems
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from genome.metagenome import MetaGenome, Gene, ProgramNode, NodeType, ProgramExecutor
from patterns.compositional import (
    PatternAlgebra, ComposablePattern, AtomicPattern, 
    CompoundPattern, MetaPattern, PatternOperator
)
from goals.automata import GoalAutomata, Goal, GoalType, GoalState
from novelty.engine import NoveltyEngine, BehaviorCharacterization
from loops.strange_loop import TangledHierarchy, Level, StrangeLoop, LoopType
from autocatalysis.network import AutocatalyticNetwork, AutocatalyticSet, CatalyticEntity, EntityType
from criticality.engine import CriticalityEngine, CriticalityMetrics


@dataclass
class EmergentEvent:
    """An event in the emergent system."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    event_type: str = ""  # 'pattern', 'goal', 'gene', 'novelty', 'loop', 'catalysis', 'avalanche'
    source_system: str = ""
    
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Propagation
    triggered_events: List[str] = field(default_factory=list)
    triggered_by: Optional[str] = None
    
    # Impact
    novelty_score: float = 0.0
    fitness_contribution: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'source_system': self.source_system,
            'data': self.data,
            'triggered_events': self.triggered_events,
            'novelty_score': self.novelty_score,
            'fitness_contribution': self.fitness_contribution
        }


class AEGIS2:
    """
    Adaptive Emergent Generative Intelligence System v2
    
    An open-ended evolving system designed for genuine emergence.
    """
    
    def __init__(
        self,
        name: str = "aegis2",
        data_dir: Optional[str] = None,
        genome_size: int = 100,
        population_size: int = 20
    ):
        self.name = name
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / f".{name}_data"
        
        # === SUBSYSTEMS ===
        
        # 1. Meta-Genome: Self-modifying genetic programs
        self.genome = MetaGenome(max_genes=genome_size)
        
        # 2. Pattern Algebra: Compositional patterns
        self.patterns = PatternAlgebra()
        
        # 3. Goal Automata: Self-spawning goals
        self.goals = GoalAutomata(max_active_goals=20, max_total_goals=200)
        
        # 4. Novelty Engine: Curiosity-driven exploration
        self.novelty = NoveltyEngine(archive_size=500)
        
        # 5. Strange Loops: Self-reference and meta-cognition
        self.hierarchy = TangledHierarchy(max_levels=10)
        
        # 6. Autocatalytic Network: Self-sustaining dynamics
        self.catalysis = AutocatalyticNetwork()
        
        # 7. Criticality Engine: Edge of chaos
        self.criticality = CriticalityEngine(window_size=100)
        
        # === INTEGRATION ===
        
        # Event bus for cross-system communication
        self.event_queue: deque = deque(maxlen=1000)
        self.event_history: List[EmergentEvent] = []
        
        # Fitness tracking
        self.fitness: float = 0.0
        self.fitness_history: List[float] = []
        
        # Emergence detection
        self.emergent_phenomena: List[Dict] = []
        
        # Cycle tracking
        self.cycle: int = 0
        self.cycles_per_second: float = 0.0
        
        # Callbacks
        self.on_event: List[Callable[[EmergentEvent], None]] = []
        self.on_emergence: List[Callable[[Dict], None]] = []
        
        # Initialize integration
        self._initialize_integration()
    
    def _initialize_integration(self):
        """Set up cross-system integration."""
        
        # Register novelty characterizers
        self.novelty.register_characterizer('genome', self._characterize_genome)
        self.novelty.register_characterizer('goals', self._characterize_goals)
        self.novelty.register_characterizer('patterns', self._characterize_patterns)
        
        # Create initial autocatalytic set from subsystems
        self._bootstrap_catalysis()
        
        # Create initial patterns from genome
        self._bootstrap_patterns()
    
    def _characterize_genome(self, entity: Any) -> List[float]:
        """Characterize genome state for novelty."""
        stats = self.genome.get_stats()
        return [
            stats['total_genes'] / 100,
            stats['total_fitness'],
            stats['avg_generation'] / 10,
            stats['regulatory_connections'] / 50
        ]
    
    def _characterize_goals(self, entity: Any) -> List[float]:
        """Characterize goal state for novelty."""
        stats = self.goals.get_stats()
        return [
            stats['total_goals'] / 100,
            stats['by_state'].get('active', 0) / 20,
            stats['goals_satisfied'] / max(1, stats['goals_spawned']),
            stats['avg_fitness']
        ]
    
    def _characterize_patterns(self, entity: Any) -> List[float]:
        """Characterize pattern state for novelty."""
        stats = self.patterns.get_stats()
        return [
            stats['total_patterns'] / 100,
            stats['abstraction_levels'] / 5,
            stats['compositions'] / 50,
            stats['abstractions'] / 20
        ]
    
    def _bootstrap_catalysis(self):
        """Create initial autocatalytic structure."""
        # Create food set (basic inputs)
        food_entities = [
            CatalyticEntity(id="food_input", name="input", entity_type=EntityType.PATTERN, is_food=True),
            CatalyticEntity(id="food_energy", name="energy", entity_type=EntityType.CONCEPT, is_food=True),
            CatalyticEntity(id="food_random", name="randomness", entity_type=EntityType.CONCEPT, is_food=True),
        ]
        
        # Create catalytic entities from subsystems
        system_entities = [
            CatalyticEntity(id="cat_genome", name="genome", entity_type=EntityType.GENE),
            CatalyticEntity(id="cat_patterns", name="patterns", entity_type=EntityType.PATTERN),
            CatalyticEntity(id="cat_goals", name="goals", entity_type=EntityType.GOAL),
            CatalyticEntity(id="cat_novelty", name="novelty", entity_type=EntityType.BEHAVIOR),
        ]
        
        # Create autocatalytic set
        ac_set = AutocatalyticSet()
        for entity in food_entities + system_entities:
            ac_set.add_entity(entity)
        
        # Create catalytic connections (the integration!)
        ac_set.connect("cat_genome", "cat_patterns")    # Genome creates patterns
        ac_set.connect("cat_patterns", "cat_goals")      # Patterns trigger goals
        ac_set.connect("cat_goals", "cat_novelty")       # Goals drive exploration
        ac_set.connect("cat_novelty", "cat_genome")      # Novelty updates genome
        
        # Food connections
        ac_set.connect("food_input", "cat_patterns")
        ac_set.connect("food_energy", "cat_goals")
        ac_set.connect("food_random", "cat_novelty")
        
        self.catalysis.add_set(ac_set)
    
    def _bootstrap_patterns(self):
        """Create initial patterns from genome genes."""
        for gene in list(self.genome.genes.values())[:5]:
            pattern = AtomicPattern(
                name=f"gene_pattern_{gene.id}",
                template=gene.name
            )
            self.patterns.register(pattern)
    
    # === MAIN LOOP ===
    
    def step(self, inputs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run one step of the emergent system.
        
        This is where everything happens:
        1. Process inputs
        2. Express genome
        3. Match patterns
        4. Update goals
        5. Explore novelty
        6. Traverse loops
        7. Run catalysis
        8. Maintain criticality
        9. Detect emergence
        """
        self.cycle += 1
        inputs = inputs or {}
        
        results = {
            'cycle': self.cycle,
            'events': [],
            'emergence': [],
            'fitness': 0.0
        }
        
        # === 1. PROCESS INPUTS ===
        input_event = self._process_inputs(inputs)
        if input_event:
            self._emit_event(input_event)
            results['events'].append(input_event.id)
        
        # === 2. EXPRESS GENOME ===
        genome_results = self._express_genome(inputs)
        for event in genome_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 3. MATCH PATTERNS ===
        pattern_results = self._match_patterns(inputs)
        for event in pattern_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 4. UPDATE GOALS ===
        goal_results = self._update_goals(inputs)
        for event in goal_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 5. EXPLORE NOVELTY ===
        novelty_results = self._explore_novelty(inputs)
        for event in novelty_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 6. TRAVERSE LOOPS ===
        loop_results = self._traverse_loops(inputs)
        for event in loop_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 7. RUN CATALYSIS ===
        catalysis_results = self._run_catalysis()
        for event in catalysis_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 8. MAINTAIN CRITICALITY ===
        criticality_results = self._maintain_criticality()
        for event in criticality_results:
            self._emit_event(event)
            results['events'].append(event.id)
        
        # === 9. PROCESS EVENT CASCADES ===
        cascade_events = self._process_cascades()
        for event in cascade_events:
            results['events'].append(event.id)
        
        # === 10. DETECT EMERGENCE ===
        emergence = self._detect_emergence()
        if emergence:
            results['emergence'] = emergence
            self.emergent_phenomena.extend(emergence)
        
        # === 11. UPDATE FITNESS ===
        self.fitness = self._compute_fitness()
        self.fitness_history.append(self.fitness)
        results['fitness'] = self.fitness
        
        # === 12. GENOME FEEDBACK ===
        self._genome_feedback()
        
        return results
    
    def _process_inputs(self, inputs: Dict) -> Optional[EmergentEvent]:
        """Process external inputs."""
        if not inputs:
            return None
        
        event = EmergentEvent(
            event_type='input',
            source_system='external',
            data={'inputs': inputs}
        )
        
        # Feed to hierarchy
        self.hierarchy.self_observe(
            action={'type': 'receive_input', 'data': inputs},
            context=inputs,
            outcome={'processed': True}
        )
        
        # Record activity for criticality
        activity = sum(float(v) if isinstance(v, (int, float)) else 0.5 for v in inputs.values())
        self.criticality.record_activity(activity / max(1, len(inputs)), event.to_dict())
        
        return event
    
    def _express_genome(self, inputs: Dict) -> List[EmergentEvent]:
        """Express genes and collect effects."""
        events = []
        
        # Prepare inputs for gene expression
        gene_inputs = {
            'fitness': self.fitness,
            'novelty': self.novelty.novel_behaviors_found / max(1, self.novelty.behaviors_explored),
            'goals_active': len(self.goals.get_active_goals()),
            'criticality': self.criticality.metrics.order_parameter,
            'cycle': self.cycle,
            **inputs
        }
        
        # Express all genes
        outputs, effects = self.genome.express_all(gene_inputs)
        
        # Process gene effects
        if effects:
            processed = self.genome.process_effects()
            
            for effect_desc in processed:
                event = EmergentEvent(
                    event_type='gene_effect',
                    source_system='genome',
                    data={'effect': effect_desc, 'outputs': outputs}
                )
                events.append(event)
        
        # Create patterns from active genes
        for gene_id, output in outputs.items():
            if isinstance(output, (int, float)) and output > 0.5:
                gene = self.genome.genes.get(gene_id)
                if gene and random.random() < 0.1:
                    # Create new pattern from gene
                    pattern = AtomicPattern(
                        name=f"expressed_{gene.name}",
                        template=str(gene.program.to_dict())[:50]
                    )
                    self.patterns.register(pattern)
                    
                    event = EmergentEvent(
                        event_type='pattern_created',
                        source_system='genome',
                        data={'gene_id': gene_id, 'pattern_id': pattern.id}
                    )
                    events.append(event)
        
        return events
    
    def _match_patterns(self, inputs: Dict) -> List[EmergentEvent]:
        """Match patterns against inputs."""
        events = []
        
        input_str = str(inputs)
        
        for pattern_id, pattern in self.patterns.patterns.items():
            success, bindings = pattern.match(input_str)
            
            if success:
                event = EmergentEvent(
                    event_type='pattern_match',
                    source_system='patterns',
                    data={
                        'pattern_id': pattern_id,
                        'bindings': bindings,
                        'complexity': pattern.complexity()
                    }
                )
                events.append(event)
                
                # Pattern matches can trigger goals
                if pattern.complexity() > 3 and random.random() < 0.2:
                    goal = self.goals.spawn_goal(
                        GoalType.EXPLORE,
                        target=pattern_id,
                        name=f"explore_pattern_{pattern_id[:6]}"
                    )
                    
                    goal_event = EmergentEvent(
                        event_type='goal_spawned',
                        source_system='patterns',
                        data={'goal_id': goal.id, 'trigger': pattern_id},
                        triggered_by=event.id
                    )
                    event.triggered_events.append(goal_event.id)
                    events.append(goal_event)
        
        # Evolve patterns based on matches
        if self.cycle % 10 == 0:
            fitness_scores = {
                pid: p.success_count / max(1, p.match_count)
                for pid, p in self.patterns.patterns.items()
                if hasattr(p, 'match_count')
            }
            new_patterns = self.patterns.evolve_patterns(fitness_scores)
            
            for pattern in new_patterns:
                event = EmergentEvent(
                    event_type='pattern_evolved',
                    source_system='patterns',
                    data={'pattern_id': pattern.id, 'complexity': pattern.complexity()}
                )
                events.append(event)
        
        return events
    
    def _update_goals(self, inputs: Dict) -> List[EmergentEvent]:
        """Update goal automata."""
        events = []
        
        # Prepare context
        context = {
            'novelty': self.novelty.novel_behaviors_found / max(1, self.novelty.behaviors_explored),
            'learning_progress': self.fitness - (self.fitness_history[-2] if len(self.fitness_history) > 1 else 0),
            'error_rate': 1.0 - self.fitness,
            **inputs
        }
        
        # Tick goals
        self.goals.tick(context)
        
        # Check for satisfied goals
        satisfied = [g for g in self.goals.goals.values() if g.state == GoalState.SATISFIED]
        for goal in satisfied[-5:]:  # Recent satisfactions
            event = EmergentEvent(
                event_type='goal_satisfied',
                source_system='goals',
                data={'goal_id': goal.id, 'goal_type': goal.goal_type.value}
            )
            events.append(event)
            
            # Satisfied goals boost related patterns
            if goal.target and isinstance(goal.target, str):
                if goal.target in self.patterns.patterns:
                    # Boost pattern fitness
                    pass
        
        # Active goals
        active = self.goals.get_active_goals()
        for goal in active[:3]:
            event = EmergentEvent(
                event_type='goal_active',
                source_system='goals',
                data={
                    'goal_id': goal.id,
                    'priority': goal.effective_priority,
                    'progress': goal.progress
                }
            )
            events.append(event)
        
        return events
    
    def _explore_novelty(self, inputs: Dict) -> List[EmergentEvent]:
        """Explore for novelty."""
        events = []
        
        # Characterize current state
        state = {
            'genome': self.genome.get_stats(),
            'patterns': self.patterns.get_stats(),
            'goals': self.goals.get_stats()
        }
        
        novelty_score, behavior = self.novelty.evaluate_novelty(
            entity=state,
            source_type='system_state',
            source_id=f"cycle_{self.cycle}",
            context=inputs
        )
        
        if novelty_score > 0.5:
            event = EmergentEvent(
                event_type='novelty_found',
                source_system='novelty',
                data={
                    'novelty_score': novelty_score,
                    'behavior_id': behavior.id
                },
                novelty_score=novelty_score
            )
            events.append(event)
            
            # High novelty triggers genome mutation
            if novelty_score > 0.7:
                # Pick a random gene and mutate
                if self.genome.genes:
                    gene = random.choice(list(self.genome.genes.values()))
                    self.genome._mutate_gene(gene)
                    
                    mutation_event = EmergentEvent(
                        event_type='gene_mutated',
                        source_system='novelty',
                        data={'gene_id': gene.id, 'trigger': 'high_novelty'},
                        triggered_by=event.id
                    )
                    event.triggered_events.append(mutation_event.id)
                    events.append(mutation_event)
        
        # Curiosity-driven goal spawning
        curiosity = self.novelty.compute_curiosity(
            entity=inputs,
            source_type='input',
            source_id=f"input_{self.cycle}",
            context=inputs
        )
        
        if curiosity > 0.6:
            goal = self.goals.spawn_goal(
                GoalType.EXPLORE,
                target=inputs,
                priority=curiosity
            )
            
            event = EmergentEvent(
                event_type='curiosity_goal',
                source_system='novelty',
                data={'goal_id': goal.id, 'curiosity': curiosity}
            )
            events.append(event)
        
        return events
    
    def _traverse_loops(self, inputs: Dict) -> List[EmergentEvent]:
        """Traverse strange loops."""
        events = []
        
        # Propagate activation through hierarchy
        self.hierarchy.propagate_activation("level_0_raw", 0.8)
        
        # Self-observation creates strange loop
        self.hierarchy.self_observe(
            action={'type': 'step', 'cycle': self.cycle},
            context=inputs,
            outcome={'fitness': self.fitness}
        )
        
        # Self-prediction
        prediction = self.hierarchy.self_predict(inputs)
        
        if prediction.get('confidence', 0) > 0.5:
            event = EmergentEvent(
                event_type='self_prediction',
                source_system='loops',
                data={
                    'prediction': prediction,
                    'confidence': prediction.get('confidence')
                }
            )
            events.append(event)
        
        # Reflect (meta-cognition)
        if self.cycle % 10 == 0:
            reflection = self.hierarchy.reflect()
            
            event = EmergentEvent(
                event_type='reflection',
                source_system='loops',
                data=reflection
            )
            events.append(event)
            
            # Reflection can bootstrap new levels
            if reflection.get('emergent_properties_detected', 0) > 3:
                new_level = self.hierarchy.bootstrap_new_level()
                if new_level:
                    level_event = EmergentEvent(
                        event_type='level_bootstrapped',
                        source_system='loops',
                        data={'level_id': new_level.id, 'height': new_level.height},
                        triggered_by=event.id
                    )
                    event.triggered_events.append(level_event.id)
                    events.append(level_event)
        
        return events
    
    def _run_catalysis(self) -> List[EmergentEvent]:
        """Run autocatalytic dynamics."""
        events = []
        
        # Step the catalytic network
        self.catalysis.step()
        
        # Check for closure
        for set_id, ac_set in self.catalysis.sets.items():
            if ac_set.is_closed:
                event = EmergentEvent(
                    event_type='catalytic_closure',
                    source_system='catalysis',
                    data={
                        'set_id': set_id,
                        'entities': len(ac_set.entities),
                        'hypercycle_strength': ac_set.hypercycle_strength()
                    }
                )
                events.append(event)
        
        # RAF detection
        for set_id, ac_set in self.catalysis.sets.items():
            raf = ac_set.find_raf_core()
            if len(raf) > 3:
                event = EmergentEvent(
                    event_type='raf_detected',
                    source_system='catalysis',
                    data={
                        'set_id': set_id,
                        'raf_size': len(raf)
                    }
                )
                events.append(event)
        
        return events
    
    def _maintain_criticality(self) -> List[EmergentEvent]:
        """Maintain edge of chaos."""
        events = []
        
        # Record current activity
        activity = len(self.event_queue) / 100.0
        self.criticality.record_activity(activity)
        
        # Check if critical
        if self.criticality.metrics.is_critical():
            event = EmergentEvent(
                event_type='critical_state',
                source_system='criticality',
                data=self.criticality.metrics.to_dict()
            )
            events.append(event)
        
        # Regulate toward criticality
        adjustments = self.criticality.regulate()
        
        if adjustments:
            event = EmergentEvent(
                event_type='criticality_regulation',
                source_system='criticality',
                data={'adjustments': adjustments}
            )
            events.append(event)
            
            # Apply adjustments to other systems
            if 'temperature' in adjustments:
                # Higher temperature = more mutation
                if adjustments['temperature'] > 0:
                    for gene in random.sample(list(self.genome.genes.values()), 
                                            min(3, len(self.genome.genes))):
                        self.genome._mutate_gene(gene)
        
        return events
    
    def _process_cascades(self) -> List[EmergentEvent]:
        """Process event cascades (avalanches)."""
        events = []
        
        # Process queued events
        processed = 0
        while self.event_queue and processed < 50:
            event = self.event_queue.popleft()
            processed += 1
            
            # Check if this event should propagate
            if self.criticality.should_propagate(event.novelty_score):
                # Create cascade event
                cascade = EmergentEvent(
                    event_type='cascade',
                    source_system='integration',
                    data={'trigger': event.id, 'depth': 1},
                    triggered_by=event.id
                )
                events.append(cascade)
                
                # Record cascade for criticality
                self.criticality.record_cascade(
                    trigger=event.to_dict(),
                    propagation=[cascade.to_dict()]
                )
        
        return events
    
    def _detect_emergence(self) -> List[Dict]:
        try:
                """Detect emergent phenomena."""
                phenomena = []
        
                # Emergence indicators:
        
                # 1. Sudden fitness jump
                if len(self.fitness_history) > 10:
                    recent = self.fitness_history[-10:]
                    older = self.fitness_history[-20:-10] if len(self.fitness_history) > 20 else [0.5]
            
                    if recent and older:
                        recent_avg = sum(recent) / len(recent)
                        older_avg = sum(older) / len(older)
                
                        if recent_avg > older_avg * 1.5:
                            phenomena.append({
                                'type': 'fitness_emergence',
                                'description': 'Sudden fitness improvement',
                                'magnitude': recent_avg / max(0.01, older_avg),
                                'cycle': self.cycle
                            })
        
                # 2. New abstraction level
                if self.hierarchy.emergent_properties:
                    recent = [p for p in self.hierarchy.emergent_properties 
                             if p.get('timestamp', 0) > datetime.now().timestamp() - 60]
                    if len(recent) > 3:
                        phenomena.append({
                            'type': 'abstraction_emergence',
                            'description': 'New level of abstraction forming',
                            'count': len(recent),
                            'cycle': self.cycle
                        })
        
                # 3. Autocatalytic closure
                closed_sets = [s for s in self.catalysis.sets.values() if s.is_closed]
                if closed_sets:
                    for ac_set in closed_sets:
                        if ac_set.hypercycle_strength() > 0.5:
                            phenomena.append({
                                'type': 'catalytic_emergence',
                                'description': 'Self-sustaining catalytic cycle',
                                'set_id': ac_set.id,
                                'strength': ac_set.hypercycle_strength(),
                                'cycle': self.cycle
                            })
        
                # 4. Critical state
                if self.criticality.metrics.is_critical():
                    phenomena.append({
                        'type': 'critical_emergence',
                        'description': 'System at edge of chaos',
                        'metrics': self.criticality.metrics.to_dict(),
                        'cycle': self.cycle
                    })
        
                # 5. Novel pattern composition
                if self.patterns.compositions > self.cycle * 0.3:
                    phenomena.append({
                        'type': 'compositional_emergence',
                        'description': 'Rapid pattern composition',
                        'compositions': self.patterns.compositions,
                        'cycle': self.cycle
                    })
        
                # Notify callbacks
                for phenomenon in phenomena:
                    for callback in self.on_emergence:
                        callback(phenomenon)
        
                return phenomena
        except Exception as e:
            raise  # Extended with error handling
    
    def _compute_fitness(self) -> float:
        """Compute overall system fitness."""
        components = []
        
        # Genome fitness
        genome_fitness = self.genome.total_fitness / max(1, len(self.genome.genes))
        components.append(genome_fitness * 0.2)
        
        # Goal satisfaction
        goal_stats = self.goals.get_stats()
        goal_fitness = goal_stats['goals_satisfied'] / max(1, goal_stats['goals_spawned'])
        components.append(goal_fitness * 0.2)
        
        # Novelty finding
        novelty_stats = self.novelty.get_stats()
        novelty_fitness = novelty_stats['novelty_rate']
        components.append(novelty_fitness * 0.2)
        
        # Autocatalytic closure
        catalysis_stats = self.catalysis.get_stats()
        catalysis_fitness = catalysis_stats['avg_closure']
        components.append(catalysis_fitness * 0.2)
        
        # Criticality (being near edge of chaos is good)
        critical_fitness = 1.0 - self.criticality.metrics.criticality_distance
        components.append(critical_fitness * 0.2)
        
        return sum(components)
    
    def _genome_feedback(self):
        try:
                """Update genome based on fitness."""
                gene_fitnesses = {}
        
                for gene_id in self.genome.genes:
                    # Gene fitness based on expression and outcomes
                    gene = self.genome.genes[gene_id]
                    gene_fitnesses[gene_id] = (
                        0.5 +
                        0.3 * (gene.expression_count / max(1, self.cycle)) +
                        0.2 * random.random()  # Exploration noise
                    )
        
                self.genome.update_fitness(gene_fitnesses)
        except Exception as e:
            raise  # Extended with error handling
    
    def _emit_event(self, event: EmergentEvent):
        """Emit an event to the system."""
        self.event_queue.append(event)
        self.event_history.append(event)
        
        if len(self.event_history) > 10000:
            self.event_history = self.event_history[-10000:]
        
        for callback in self.on_event:
            callback(event)
    
    # === PUBLIC INTERFACE ===
    
    def run(self, steps: int = 100, inputs_fn: Optional[Callable[[int], Dict]] = None):
        """Run for multiple steps."""
        results = []
        
        for i in range(steps):
            inputs = inputs_fn(i) if inputs_fn else {}
            result = self.step(inputs)
            results.append(result)
            
            if result['emergence']:
                print(f"Cycle {self.cycle}: EMERGENCE DETECTED")
                for e in result['emergence']:
                    print(f"  - {e['type']}: {e['description']}")
        
        return results
    
    def status(self) -> Dict:
        """Get comprehensive status."""
        return {
            'cycle': self.cycle,
            'fitness': self.fitness,
            'genome': self.genome.get_stats(),
            'patterns': self.patterns.get_stats(),
            'goals': self.goals.get_stats(),
            'novelty': self.novelty.get_stats(),
            'hierarchy': self.hierarchy.get_stats(),
            'catalysis': self.catalysis.get_stats(),
            'criticality': self.criticality.get_stats(),
            'emergent_phenomena': len(self.emergent_phenomena),
            'events_processed': len(self.event_history)
        }
    
    def save(self, path: Optional[str] = None):
        """Save system state."""
        save_path = Path(path) if path else self.data_dir / "aegis2_state.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            'name': self.name,
            'cycle': self.cycle,
            'fitness': self.fitness,
            'fitness_history': self.fitness_history[-100:],
            'genome': self.genome.to_dict(),
            'patterns': {pid: p.to_dict() for pid, p in self.patterns.patterns.items()},
            'goals': self.goals.to_dict(),
            'novelty': self.novelty.to_dict(),
            'hierarchy': self.hierarchy.to_dict(),
            'catalysis': self.catalysis.to_dict(),
            'criticality': self.criticality.to_dict(),
            'emergent_phenomena': self.emergent_phenomena[-50:],
            'saved_at': datetime.now().isoformat()
        }
        
        with open(save_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load(self, path: Optional[str] = None) -> bool:
        """Load system state."""
        load_path = Path(path) if path else self.data_dir / "aegis2_state.json"
        
        if not load_path.exists():
            return False
        
        with open(load_path, 'r') as f:
            state = json.load(f)
        
        self.name = state.get('name', self.name)
        self.cycle = state.get('cycle', 0)
        self.fitness = state.get('fitness', 0.0)
        self.fitness_history = state.get('fitness_history', [])
        self.emergent_phenomena = state.get('emergent_phenomena', [])
        
        # Reconstruct subsystems from state
        if 'genome' in state:
            self.genome = MetaGenome.from_dict(state['genome'])
        
        if 'goals' in state:
            self.goals = GoalAutomata.from_dict(state['goals'])
        
        if 'novelty' in state:
            self.novelty = NoveltyEngine.from_dict(state['novelty'])
        
        return True


def demo():
    """Demonstrate AEGIS-2."""
    print("=" * 70)
    print("   AEGIS-2: Emergent Intelligence System")
    print("=" * 70)
    print()
    
    system = AEGIS2(name="emergence_demo")
    
    # Register callbacks
    def on_emergence(phenomenon):
        print(f"  ★ EMERGENCE: {phenomenon['type']}")
    
    system.on_emergence.append(on_emergence)
    
    print("Running 100 cycles...")
    print()
    
    def generate_inputs(cycle):
        return {
            'signal': math.sin(cycle / 10) * 0.5 + 0.5,
            'noise': random.random(),
            'cycle': cycle
        }
    
    results = system.run(steps=100, inputs_fn=generate_inputs)
    
    print()
    print("=" * 70)
    print("FINAL STATUS")
    print("=" * 70)
    
    status = system.status()
    
    print(f"""
  Cycles: {status['cycle']}
  Fitness: {status['fitness']:.4f}
  
  Genome:
    Genes: {status['genome']['total_genes']}
    Mutations: {status['genome']['total_mutations']}
    
  Patterns:
    Total: {status['patterns']['total_patterns']}
    Compositions: {status['patterns']['compositions']}
    
  Goals:
    Total: {status['goals']['total_goals']}
    Satisfied: {status['goals']['goals_satisfied']}
    
  Novelty:
    Explored: {status['novelty']['behaviors_explored']}
    Novel found: {status['novelty']['novel_behaviors_found']}
    
  Catalysis:
    Sets: {status['catalysis']['num_sets']}
    Closure: {status['catalysis']['avg_closure']:.2%}
    
  Criticality:
    Critical: {status['criticality']['is_critical']}
    Order: {status['criticality']['metrics']['order_parameter']:.3f}
    
  EMERGENT PHENOMENA: {status['emergent_phenomena']}
""")
    
    system.save()
    print(f"  State saved to: {system.data_dir}")
    
    return system


if __name__ == "__main__":
    demo()
