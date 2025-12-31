"""
AEGIS-2 Strange Loops: Self-Reference for Emergence

Key insight from Hofstadter: Strange loops - tangled hierarchies where 
moving through levels brings you back to where you started - are the 
source of meaning, self, and emergence.

This module implements:
- Self-referential structures that can examine themselves
- Tangled hierarchies of abstraction
- Level-crossing feedback (higher levels affecting lower, and vice versa)
- Self-models that update based on behavior
- Meta-cognition (thinking about thinking)
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from collections import deque


class LoopType(Enum):
    """Types of strange loops."""
    SELF_REFERENCE = "self_ref"      # Direct self-reference
    MUTUAL_REFERENCE = "mutual"       # A refers to B refers to A
    HIERARCHICAL = "hierarchical"     # Crosses abstraction levels
    TEMPORAL = "temporal"             # Future affects past (planning)
    CAUSAL = "causal"                 # Effect becomes cause


@dataclass
class Level:
    """A level in a tangled hierarchy."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    height: int = 0  # 0 = base level
    
    # Contents at this level
    entities: Dict[str, Any] = field(default_factory=dict)
    
    # Upward and downward links
    abstracts_from: List[str] = field(default_factory=list)  # Lower levels this abstracts
    grounds_to: List[str] = field(default_factory=list)      # Lower levels this grounds to
    
    # Strange loop connections (same level or crossing)
    loops_to: List[str] = field(default_factory=list)
    
    # Activation
    activation: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'entities': list(self.entities.keys()),
            'abstracts_from': self.abstracts_from,
            'grounds_to': self.grounds_to,
            'loops_to': self.loops_to,
            'activation': self.activation
        }


@dataclass
class SelfModel:
    """
    A model the system maintains of itself.
    
    This is the key to self-awareness: having a representation
    of oneself that can be examined and updated.
    """
    id: str = "self"
    
    # What the system believes about itself
    beliefs: Dict[str, Any] = field(default_factory=dict)
    
    # Observed behaviors
    behavior_history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # Predicted vs actual
    predictions: List[Dict] = field(default_factory=list)
    prediction_accuracy: float = 0.5
    
    # Capabilities (what can I do?)
    capabilities: Dict[str, float] = field(default_factory=dict)  # capability -> confidence
    
    # Goals (what do I want?)
    goal_representations: Dict[str, Any] = field(default_factory=dict)
    
    # State (how am I doing?)
    state_estimate: Dict[str, float] = field(default_factory=dict)
    
    # Meta-level (what do I know about knowing?)
    meta_beliefs: Dict[str, Any] = field(default_factory=dict)
    
    # Update history
    updates: int = 0
    last_update: float = 0.0
    
    def observe_behavior(self, action: Any, context: Dict, outcome: Any):
        """Observe own behavior and update model."""
        observation = {
            'action': action,
            'context': context,
            'outcome': outcome,
            'timestamp': datetime.now().timestamp()
        }
        self.behavior_history.append(observation)
        
        # Update capability beliefs
        action_type = str(type(action).__name__) if action else 'unknown'
        success = self._evaluate_success(outcome)
        
        if action_type not in self.capabilities:
            self.capabilities[action_type] = 0.5
        
        # Exponential moving average
        self.capabilities[action_type] = 0.9 * self.capabilities[action_type] + 0.1 * success
        
        self.updates += 1
        self.last_update = datetime.now().timestamp()
    
    def predict_behavior(self, context: Dict) -> Dict:
        try:
                """Predict own behavior in a context."""
                # Simple prediction based on history
                prediction = {
                    'expected_action': None,
                    'expected_outcome': None,
                    'confidence': 0.5
                }
        
                # Find similar contexts in history
                similar = []
                for obs in self.behavior_history:
                    similarity = self._context_similarity(context, obs['context'])
                    if similarity > 0.5:
                        similar.append((obs, similarity))
        
                if similar:
                    similar.sort(key=lambda x: x[1], reverse=True)
                    best = similar[0][0]
                    prediction['expected_action'] = best['action']
                    prediction['expected_outcome'] = best['outcome']
                    prediction['confidence'] = similar[0][1]
        
                self.predictions.append({
                    'context': context,
                    'prediction': prediction,
                    'timestamp': datetime.now().timestamp()
                })
        
                return prediction
        except Exception as e:
            raise  # Extended with error handling
    
    def evaluate_prediction(self, context: Dict, actual_action: Any, actual_outcome: Any):
        """Evaluate how accurate our prediction was."""
        # Find the prediction for this context
        for pred in reversed(self.predictions[-10:]):
            if self._context_similarity(context, pred['context']) > 0.8:
                predicted = pred['prediction']
                
                # Compare
                action_match = (str(predicted.get('expected_action')) == str(actual_action))
                outcome_match = (str(predicted.get('expected_outcome')) == str(actual_outcome))
                
                accuracy = (0.5 if action_match else 0.0) + (0.5 if outcome_match else 0.0)
                
                # Update prediction accuracy
                self.prediction_accuracy = 0.9 * self.prediction_accuracy + 0.1 * accuracy
                
                return accuracy
        
        return 0.5  # No prediction found
    
    def _evaluate_success(self, outcome: Any) -> float:
        """Evaluate if an outcome was successful."""
        if outcome is None:
            return 0.5
        if isinstance(outcome, bool):
            return 1.0 if outcome else 0.0
        if isinstance(outcome, (int, float)):
            return max(0.0, min(1.0, outcome))
        if isinstance(outcome, dict):
            return outcome.get('success', 0.5)
        return 0.5
    
    def _context_similarity(self, ctx1: Dict, ctx2: Dict) -> float:
        """Compute similarity between contexts."""
        if not ctx1 or not ctx2:
            return 0.0
        
        keys1 = set(ctx1.keys())
        keys2 = set(ctx2.keys())
        
        if not keys1 and not keys2:
            return 1.0
        if not keys1 or not keys2:
            return 0.0
        
        overlap = len(keys1 & keys2)
        total = len(keys1 | keys2)
        
        key_sim = overlap / total
        
        # Value similarity for overlapping keys
        value_sim = 0.0
        for key in keys1 & keys2:
            if str(ctx1[key]) == str(ctx2[key]):
                value_sim += 1.0
        value_sim /= max(1, overlap)
        
        return 0.5 * key_sim + 0.5 * value_sim
    
    def reflect(self) -> Dict:
        """Reflect on self - meta-cognition."""
        reflection = {
            'behavioral_consistency': self._compute_consistency(),
            'prediction_accuracy': self.prediction_accuracy,
            'capability_confidence': sum(self.capabilities.values()) / max(1, len(self.capabilities)),
            'self_knowledge_depth': len(self.beliefs) + len(self.meta_beliefs),
            'observations': len(self.behavior_history)
        }
        
        # Update meta-beliefs based on reflection
        self.meta_beliefs['consistency'] = reflection['behavioral_consistency']
        self.meta_beliefs['self_prediction_skill'] = self.prediction_accuracy
        self.meta_beliefs['reflection_count'] = self.meta_beliefs.get('reflection_count', 0) + 1
        
        return reflection
    
    def _compute_consistency(self) -> float:
        """Compute behavioral consistency."""
        if len(self.behavior_history) < 5:
            return 0.5
        
        # Check if similar contexts led to similar actions
        recent = list(self.behavior_history)[-20:]
        
        consistency_scores = []
        for i, obs1 in enumerate(recent):
            for obs2 in recent[i+1:]:
                ctx_sim = self._context_similarity(obs1['context'], obs2['context'])
                if ctx_sim > 0.7:
                    action_same = (str(obs1['action']) == str(obs2['action']))
                    consistency_scores.append(1.0 if action_same else 0.0)
        
        if consistency_scores:
            return sum(consistency_scores) / len(consistency_scores)
        return 0.5
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'beliefs': self.beliefs,
            'capabilities': self.capabilities,
            'prediction_accuracy': self.prediction_accuracy,
            'meta_beliefs': self.meta_beliefs,
            'state_estimate': self.state_estimate,
            'updates': self.updates
        }


@dataclass  
class StrangeLoop:
    """
    A strange loop - a self-referential cycle in a tangled hierarchy.
    
    The loop enables:
    - Self-modification
    - Level-crossing feedback
    - Emergent properties not present at any single level
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    loop_type: LoopType = LoopType.SELF_REFERENCE
    
    # Levels involved in the loop
    level_ids: List[str] = field(default_factory=list)
    
    # The referential cycle
    cycle: List[Tuple[str, str, str]] = field(default_factory=list)  # (from, relation, to)
    
    # Activation tracking
    times_traversed: int = 0
    current_position: int = 0
    
    # Effects of loop traversal
    effects: List[Dict] = field(default_factory=list)
    
    # Energy/activation
    energy: float = 1.0
    
    def traverse(self) -> Tuple[str, str, str]:
        """Traverse one step around the loop."""
        if not self.cycle:
            return ('', '', '')
        
        step = self.cycle[self.current_position]
        self.current_position = (self.current_position + 1) % len(self.cycle)
        
        if self.current_position == 0:
            self.times_traversed += 1
        
        return step
    
    def complete_cycle(self) -> List[Tuple[str, str, str]]:
        """Complete one full cycle around the loop."""
        steps = []
        start_pos = self.current_position
        
        while True:
            step = self.traverse()
            steps.append(step)
            if self.current_position == start_pos:
                break
            if len(steps) > len(self.cycle) + 1:  # Safety
                break
        
        return steps
    
    def add_effect(self, effect: Dict):
        """Record an effect of loop traversal."""
        effect['timestamp'] = datetime.now().timestamp()
        effect['traversal'] = self.times_traversed
        self.effects.append(effect)
        
        if len(self.effects) > 100:
            self.effects = self.effects[-100:]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'loop_type': self.loop_type.value,
            'level_ids': self.level_ids,
            'cycle': self.cycle,
            'times_traversed': self.times_traversed,
            'energy': self.energy
        }


class TangledHierarchy:
    """
    A tangled hierarchy of abstraction levels with strange loops.
    
    This is where emergence happens: when levels interact in
    non-linear ways, creating properties that exist at no single level.
    """
    
    def __init__(self, max_levels: int = 10):
        self.max_levels = max_levels
        
        self.levels: Dict[str, Level] = {}
        self.loops: Dict[str, StrangeLoop] = {}
        
        # Self-model
        self.self_model = SelfModel()
        
        # Level registry
        self._level_by_height: Dict[int, List[str]] = {}
        
        # Loop detection
        self._reference_graph: Dict[str, Set[str]] = {}
        
        # Statistics
        self.level_crossings: int = 0
        self.loop_traversals: int = 0
        self.emergent_properties: List[Dict] = []
        
        # Initialize base levels
        self._initialize_base_levels()
    
    def _initialize_base_levels(self):
        """Create fundamental levels."""
        # Level 0: Raw data/signals
        self.add_level(Level(
            id="level_0_raw",
            name="raw_signals",
            height=0
        ))
        
        # Level 1: Patterns
        self.add_level(Level(
            id="level_1_patterns",
            name="patterns",
            height=1,
            abstracts_from=["level_0_raw"]
        ))
        
        # Level 2: Concepts
        self.add_level(Level(
            id="level_2_concepts",
            name="concepts",
            height=2,
            abstracts_from=["level_1_patterns"]
        ))
        
        # Level 3: Goals
        self.add_level(Level(
            id="level_3_goals",
            name="goals",
            height=3,
            abstracts_from=["level_2_concepts"]
        ))
        
        # Level 4: Self-model (meta-level)
        self.add_level(Level(
            id="level_4_self",
            name="self_model",
            height=4,
            abstracts_from=["level_3_goals", "level_2_concepts", "level_1_patterns"],
            grounds_to=["level_0_raw"]  # Self-model affects raw behavior!
        ))
        
        # Create initial strange loop: self-reference
        self.add_loop(StrangeLoop(
            id="loop_self_ref",
            name="self_reference",
            loop_type=LoopType.SELF_REFERENCE,
            level_ids=["level_4_self"],
            cycle=[
                ("level_4_self", "observes", "level_0_raw"),
                ("level_0_raw", "produces", "level_1_patterns"),
                ("level_1_patterns", "abstracted_to", "level_4_self")
            ]
        ))
    
    def add_level(self, level: Level) -> str:
        """Add a level to the hierarchy."""
        if len(self.levels) >= self.max_levels:
            return ""
        
        self.levels[level.id] = level
        
        if level.height not in self._level_by_height:
            self._level_by_height[level.height] = []
        self._level_by_height[level.height].append(level.id)
        
        # Update reference graph
        self._reference_graph[level.id] = set()
        for lower in level.abstracts_from:
            self._reference_graph[level.id].add(lower)
        for lower in level.grounds_to:
            self._reference_graph[level.id].add(lower)
        
        return level.id
    
    def add_loop(self, loop: StrangeLoop) -> str:
        """Add a strange loop."""
        self.loops[loop.id] = loop
        
        # Update level loop connections
        for level_id in loop.level_ids:
            if level_id in self.levels:
                self.levels[level_id].loops_to.append(loop.id)
        
        return loop.id
    
    def detect_loops(self) -> List[StrangeLoop]:
        """Detect new strange loops in the hierarchy."""
        new_loops = []
        
        # Find cycles in reference graph using DFS
        for start in self._reference_graph:
            visited = set()
            path = []
            
            cycles = self._find_cycles(start, start, visited, path)
            
            for cycle in cycles:
                if len(cycle) >= 2:
                    # Create loop
                    loop_cycle = []
                    for i in range(len(cycle) - 1):
                        loop_cycle.append((cycle[i], "references", cycle[i+1]))
                    loop_cycle.append((cycle[-1], "references", cycle[0]))
                    
                    loop = StrangeLoop(
                        name=f"detected_loop_{len(self.loops)}",
                        loop_type=LoopType.HIERARCHICAL if self._crosses_levels(cycle) else LoopType.MUTUAL_REFERENCE,
                        level_ids=cycle,
                        cycle=loop_cycle
                    )
                    
                    if loop.id not in self.loops:
                        self.add_loop(loop)
                        new_loops.append(loop)
        
        return new_loops
    
    def _find_cycles(self, start: str, current: str, visited: Set[str], path: List[str]) -> List[List[str]]:
        """Find cycles starting from a node."""
        cycles = []
        
        if current in visited:
            if current == start and len(path) > 1:
                cycles.append(list(path))
            return cycles
        
        visited.add(current)
        path.append(current)
        
        for neighbor in self._reference_graph.get(current, set()):
            sub_cycles = self._find_cycles(start, neighbor, visited.copy(), list(path))
            cycles.extend(sub_cycles)
        
        return cycles
    
    def _crosses_levels(self, level_ids: List[str]) -> bool:
        """Check if a cycle crosses abstraction levels."""
        heights = set()
        for lid in level_ids:
            if lid in self.levels:
                heights.add(self.levels[lid].height)
        return len(heights) > 1
    
    def propagate_activation(self, source_level: str, activation: float):
        """Propagate activation through the hierarchy and loops."""
        if source_level not in self.levels:
            return
        
        level = self.levels[source_level]
        level.activation = activation
        
        # Propagate upward (abstraction)
        for upper_id in self._level_by_height.get(level.height + 1, []):
            upper = self.levels.get(upper_id)
            if upper and source_level in upper.abstracts_from:
                upper.activation = max(upper.activation, activation * 0.8)
                self.level_crossings += 1
        
        # Propagate through loops
        for loop_id in level.loops_to:
            loop = self.loops.get(loop_id)
            if loop:
                # Traverse loop
                for from_id, relation, to_id in loop.cycle:
                    if from_id == source_level and to_id in self.levels:
                        self.levels[to_id].activation = max(
                            self.levels[to_id].activation,
                            activation * loop.energy * 0.7
                        )
                        self.loop_traversals += 1
                        loop.times_traversed += 1
    
    def cross_level_effect(self, source_level: str, target_level: str, effect: Dict):
        """
        Create a cross-level effect (higher affects lower or vice versa).
        This is key to strange loop dynamics.
        """
        source = self.levels.get(source_level)
        target = self.levels.get(target_level)
        
        if not source or not target:
            return
        
        # Record the crossing
        self.level_crossings += 1
        
        # If higher level affects lower, that's the strange loop in action
        if source.height > target.height:
            # Top-down causation
            effect['type'] = 'top_down'
            effect['from_height'] = source.height
            effect['to_height'] = target.height
            
            # This is where emergence happens!
            self._check_emergence(source, target, effect)
        else:
            # Bottom-up causation (normal)
            effect['type'] = 'bottom_up'
        
        # Update reference graph
        if source_level not in self._reference_graph:
            self._reference_graph[source_level] = set()
        self._reference_graph[source_level].add(target_level)
        
        # Check for new loops
        self.detect_loops()
    
    def _check_emergence(self, higher: Level, lower: Level, effect: Dict):
        """Check for emergent properties from cross-level effects."""
        # Emergence = properties of the whole not present in parts
        
        # Simple heuristic: if higher level modifies lower level behavior,
        # and this creates novel patterns, that's emergence
        
        emergence_candidate = {
            'timestamp': datetime.now().timestamp(),
            'higher_level': higher.id,
            'lower_level': lower.id,
            'effect': effect,
            'novel': True  # Would need pattern detection to verify
        }
        
        self.emergent_properties.append(emergence_candidate)
        
        # Notify self-model
        self.self_model.observe_behavior(
            action={'type': 'emergence', 'levels': [higher.id, lower.id]},
            context={'effect': effect},
            outcome={'emergent': True}
        )
    
    def self_observe(self, action: Any, context: Dict, outcome: Any):
        """Observe own behavior and update self-model."""
        self.self_model.observe_behavior(action, context, outcome)
        
        # Propagate through hierarchy
        # Action enters at raw level
        self.propagate_activation("level_0_raw", 0.8)
        
        # Self-observation activates self-model level
        self.propagate_activation("level_4_self", 0.9)
    
    def self_predict(self, context: Dict) -> Dict:
        """Predict own behavior using self-model."""
        prediction = self.self_model.predict_behavior(context)
        
        # This is the strange loop: self-model predicts self
        # The prediction can INFLUENCE the actual behavior!
        
        return prediction
    
    def reflect(self) -> Dict:
        """Perform meta-cognition - reflect on the hierarchy itself."""
        self_reflection = self.self_model.reflect()
        
        hierarchy_reflection = {
            'levels': len(self.levels),
            'loops': len(self.loops),
            'level_crossings': self.level_crossings,
            'loop_traversals': self.loop_traversals,
            'emergent_properties': len(self.emergent_properties),
            'self_model': self_reflection
        }
        
        # The act of reflection is itself a strange loop!
        self.cross_level_effect(
            "level_4_self",
            "level_0_raw",
            {'action': 'reflection', 'depth': self_reflection.get('self_knowledge_depth', 0)}
        )
        
        return hierarchy_reflection
    
    def bootstrap_new_level(self) -> Optional[Level]:
        """
        Bootstrap a new level of abstraction from existing levels.
        
        This is the key to unbounded growth: the system can create
        new levels of abstraction from existing ones.
        """
        if len(self.levels) >= self.max_levels:
            return None
        
        # Find the highest current level
        max_height = max(l.height for l in self.levels.values())
        
        # Create new level abstracting from current top levels
        top_levels = [l.id for l in self.levels.values() if l.height == max_height]
        
        new_level = Level(
            name=f"emergent_level_{max_height + 1}",
            height=max_height + 1,
            abstracts_from=top_levels
        )
        
        self.add_level(new_level)
        
        # Create strange loop from new level back down
        loop = StrangeLoop(
            name=f"bootstrap_loop_{max_height + 1}",
            loop_type=LoopType.HIERARCHICAL,
            level_ids=[new_level.id] + top_levels,
            cycle=[
                (new_level.id, "abstracts", top_levels[0]),
                (top_levels[0], "grounds", "level_0_raw"),
                ("level_0_raw", "produces", new_level.id)
            ]
        )
        self.add_loop(loop)
        
        return new_level
    
    def get_stats(self) -> Dict:
        return {
            'num_levels': len(self.levels),
            'num_loops': len(self.loops),
            'level_crossings': self.level_crossings,
            'loop_traversals': self.loop_traversals,
            'emergent_properties_detected': len(self.emergent_properties),
            'self_model_updates': self.self_model.updates,
            'self_prediction_accuracy': self.self_model.prediction_accuracy,
            'levels_by_height': {h: len(ids) for h, ids in self._level_by_height.items()}
        }
    
    def to_dict(self) -> Dict:
        return {
            'levels': {lid: l.to_dict() for lid, l in self.levels.items()},
            'loops': {lid: l.to_dict() for lid, l in self.loops.items()},
            'self_model': self.self_model.to_dict(),
            'level_crossings': self.level_crossings,
            'loop_traversals': self.loop_traversals,
            'emergent_properties': self.emergent_properties[-10:]
        }
