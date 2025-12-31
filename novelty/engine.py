"""
AEGIS-2 Novelty Engine: Exploring the Unknown

Key insight: Optimizing a fixed objective leads to local optima.
Novelty search - rewarding DIFFERENCE - leads to open-ended discovery.

This module implements:
- Behavioral characterization (what makes behaviors unique)
- Novelty archive (history of explored behaviors)  
- Novelty-based fitness (reward for being different)
- Curiosity-driven exploration
- Surprise detection (expectation vs reality)
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from datetime import datetime
from collections import deque
import heapq


@dataclass
class BehaviorCharacterization:
    """
    A characterization of a behavior in behavior space.
    
    The key insight: we don't just look at outcomes, we look at
    HOW the system behaves - its trajectory through state space.
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    
    # The behavior vector (high-dimensional representation)
    vector: List[float] = field(default_factory=list)
    
    # What produced this behavior
    source_type: str = ""  # 'genome', 'pattern', 'goal', 'action'
    source_id: str = ""
    
    # Context in which behavior occurred
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Outcomes (optional - novelty doesn't require this)
    outcomes: List[Any] = field(default_factory=list)
    
    # Novelty metrics
    novelty_score: float = 0.0
    nearest_neighbors: List[str] = field(default_factory=list)
    
    # Temporal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    # Surprise (if we had predictions)
    prediction_error: float = 0.0
    
    def distance(self, other: 'BehaviorCharacterization') -> float:
        """Compute distance to another behavior."""
        if not self.vector or not other.vector:
            return float('inf')
        
        # Euclidean distance
        dim = min(len(self.vector), len(other.vector))
        if dim == 0:
            return float('inf')
        
        sq_sum = sum((self.vector[i] - other.vector[i]) ** 2 for i in range(dim))
        return math.sqrt(sq_sum)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'vector': self.vector,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'context': self.context,
            'novelty_score': self.novelty_score,
            'prediction_error': self.prediction_error,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BehaviorCharacterization':
        return cls(
            id=data['id'],
            vector=data.get('vector', []),
            source_type=data.get('source_type', ''),
            source_id=data.get('source_id', ''),
            context=data.get('context', {}),
            novelty_score=data.get('novelty_score', 0.0),
            prediction_error=data.get('prediction_error', 0.0),
            created_at=data.get('created_at', datetime.now().timestamp())
        )


class NoveltyArchive:
    """
    Archive of explored behaviors.
    
    The archive maintains a diverse collection of behaviors,
    enabling novelty computation relative to what's been seen.
    """
    
    def __init__(self, max_size: int = 1000, k_nearest: int = 15):
        self.max_size = max_size
        self.k_nearest = k_nearest
        
        self.archive: Dict[str, BehaviorCharacterization] = {}
        
        # Spatial index for fast neighbor queries (simplified)
        self._grid: Dict[Tuple[int, ...], List[str]] = {}
        self._grid_resolution = 10
        
        # Statistics
        self.behaviors_added = 0
        self.behaviors_rejected = 0
        self.total_novelty = 0.0
    
    def _get_grid_cell(self, vector: List[float]) -> Tuple[int, ...]:
        """Get grid cell for a vector."""
        return tuple(int(v * self._grid_resolution) for v in vector[:5])  # First 5 dims
    
    def add(self, behavior: BehaviorCharacterization, min_novelty: float = 0.0) -> bool:
        """Add a behavior to the archive if sufficiently novel."""
        if behavior.id in self.archive:
            return False
        
        # Compute novelty
        novelty = self.compute_novelty(behavior)
        behavior.novelty_score = novelty
        
        # Check if novel enough
        if novelty < min_novelty:
            self.behaviors_rejected += 1
            return False
        
        # Add to archive
        self.archive[behavior.id] = behavior
        self.behaviors_added += 1
        self.total_novelty += novelty
        
        # Update grid index
        cell = self._get_grid_cell(behavior.vector)
        if cell not in self._grid:
            self._grid[cell] = []
        self._grid[cell].append(behavior.id)
        
        # Prune if too large
        if len(self.archive) > self.max_size:
            self._prune()
        
        return True
    
    def compute_novelty(self, behavior: BehaviorCharacterization) -> float:
        """Compute novelty of a behavior relative to archive."""
        if not self.archive:
            return 1.0  # First behavior is maximally novel
        
        # Find k nearest neighbors
        distances = []
        for archived in self.archive.values():
            dist = behavior.distance(archived)
            distances.append(dist)
        
        distances.sort()
        
        # Average distance to k nearest neighbors
        k = min(self.k_nearest, len(distances))
        if k == 0:
            return 1.0
        
        avg_distance = sum(distances[:k]) / k
        
        # Normalize (simple heuristic)
        novelty = min(1.0, avg_distance / 2.0)
        
        return novelty
    
    def get_nearest(self, behavior: BehaviorCharacterization, k: int = 5) -> List[Tuple[BehaviorCharacterization, float]]:
        """Get k nearest behaviors in archive."""
        distances = []
        for archived in self.archive.values():
            dist = behavior.distance(archived)
            distances.append((archived, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def _prune(self):
        """Prune archive to maintain diversity."""
        # Remove behaviors with lowest novelty
        sorted_behaviors = sorted(
            self.archive.values(),
            key=lambda b: b.novelty_score,
            reverse=True
        )
        
        # Keep top max_size
        keep_ids = {b.id for b in sorted_behaviors[:self.max_size]}
        
        for bid in list(self.archive.keys()):
            if bid not in keep_ids:
                behavior = self.archive.pop(bid)
                cell = self._get_grid_cell(behavior.vector)
                if cell in self._grid and bid in self._grid[cell]:
                    self._grid[cell].remove(bid)
    
    def get_diverse_sample(self, n: int = 10) -> List[BehaviorCharacterization]:
        """Get a diverse sample of behaviors."""
        if len(self.archive) <= n:
            return list(self.archive.values())
        
        # Farthest point sampling
        selected = [random.choice(list(self.archive.values()))]
        selected_ids = {selected[0].id}
        
        while len(selected) < n:
            best_dist = -1
            best_behavior = None
            
            for behavior in self.archive.values():
                if behavior.id in selected_ids:
                    continue
                
                min_dist = min(behavior.distance(s) for s in selected)
                if min_dist > best_dist:
                    best_dist = min_dist
                    best_behavior = behavior
            
            if best_behavior:
                selected.append(best_behavior)
                selected_ids.add(best_behavior.id)
            else:
                break
        
        return selected
    
    def get_stats(self) -> Dict:
        return {
            'archive_size': len(self.archive),
            'behaviors_added': self.behaviors_added,
            'behaviors_rejected': self.behaviors_rejected,
            'avg_novelty': self.total_novelty / max(1, self.behaviors_added),
            'grid_cells': len(self._grid)
        }


class SurpriseDetector:
    """
    Detects surprising events by comparing predictions to reality.
    
    Surprise drives learning - we learn most from unexpected outcomes.
    """
    
    def __init__(self, memory_size: int = 100):
        self.memory_size = memory_size
        
        # Prediction models (simple associative memory)
        self.predictions: Dict[str, List[Tuple[List[float], float]]] = {}  # context_key -> [(outcome, weight)]
        
        # Recent surprises
        self.recent_surprises: deque = deque(maxlen=memory_size)
        
        # Surprise statistics
        self.total_predictions = 0
        self.total_surprise = 0.0
        self.max_surprise = 0.0
    
    def predict(self, context: Dict) -> Optional[float]:
        """Predict outcome for a context."""
        key = self._context_key(context)
        
        if key not in self.predictions:
            return None
        
        # Weighted average of past outcomes
        records = self.predictions[key]
        if not records:
            return None
        
        total_weight = sum(w for _, w in records)
        if total_weight == 0:
            return None
        
        weighted_sum = sum(o * w for o, w in records)
        return weighted_sum / total_weight
    
    def observe(self, context: Dict, outcome: float) -> float:
        """
        Observe an outcome and compute surprise.
        Returns surprise value (higher = more surprising).
        """
        self.total_predictions += 1
        
        prediction = self.predict(context)
        
        if prediction is None:
            # Unknown context is moderately surprising
            surprise = 0.5
        else:
            # Surprise proportional to prediction error
            surprise = abs(outcome - prediction)
        
        # Update prediction model
        key = self._context_key(context)
        if key not in self.predictions:
            self.predictions[key] = []
        
        # Add observation with decaying weight
        self.predictions[key].append((outcome, 1.0))
        
        # Decay old observations
        self.predictions[key] = [
            (o, w * 0.9) for o, w in self.predictions[key]
            if w * 0.9 > 0.01
        ][-20:]  # Keep last 20
        
        # Track surprise
        self.recent_surprises.append({
            'context': context,
            'prediction': prediction,
            'outcome': outcome,
            'surprise': surprise,
            'timestamp': datetime.now().timestamp()
        })
        
        self.total_surprise += surprise
        self.max_surprise = max(self.max_surprise, surprise)
        
        return surprise
    
    def _context_key(self, context: Dict) -> str:
        """Generate a hashable key from context."""
        # Simple: use sorted string representation
        items = sorted((str(k), str(v)[:20]) for k, v in context.items())
        return str(items)
    
    def get_surprising_contexts(self, threshold: float = 0.5) -> List[Dict]:
        """Get contexts that produced high surprise."""
        return [
            s['context'] for s in self.recent_surprises
            if s['surprise'] > threshold
        ]
    
    def get_stats(self) -> Dict:
        return {
            'total_predictions': self.total_predictions,
            'avg_surprise': self.total_surprise / max(1, self.total_predictions),
            'max_surprise': self.max_surprise,
            'recent_surprises': len(self.recent_surprises),
            'context_models': len(self.predictions)
        }


class NoveltyEngine:
    """
    The main novelty engine - drives exploration through novelty and curiosity.
    
    Key mechanisms:
    1. Novelty search: reward behaviors for being different
    2. Curiosity: seek states with high learning potential
    3. Surprise: focus on unexpected outcomes
    4. Coverage: ensure broad exploration of behavior space
    """
    
    def __init__(
        self,
        archive_size: int = 1000,
        k_nearest: int = 15,
        novelty_threshold: float = 0.2
    ):
        self.archive = NoveltyArchive(max_size=archive_size, k_nearest=k_nearest)
        self.surprise_detector = SurpriseDetector()
        
        self.novelty_threshold = novelty_threshold
        
        # Behavior characterization functions
        self.characterizers: Dict[str, Callable] = {}
        
        # Exploration frontiers (unexplored regions)
        self.frontiers: List[List[float]] = []
        
        # Current exploration targets
        self.targets: List[BehaviorCharacterization] = []
        
        # Statistics
        self.behaviors_explored = 0
        self.novel_behaviors_found = 0
        self.surprises_detected = 0
    
    def register_characterizer(self, name: str, func: Callable[[Any], List[float]]):
        """Register a behavior characterization function."""
        self.characterizers[name] = func
    
    def characterize(self, entity: Any, source_type: str, source_id: str, context: Dict) -> BehaviorCharacterization:
        """Create a behavior characterization for an entity."""
        vector = []
        
        # Apply all characterizers
        for name, func in self.characterizers.items():
            try:
                char = func(entity)
                if isinstance(char, (list, tuple)):
                    vector.extend(char)
                elif isinstance(char, (int, float)):
                    vector.append(float(char))
            except:
                pass
        
        # Default characterization if no characterizers
        if not vector:
            # Hash-based characterization
            h = hashlib.sha256(str(entity).encode()).hexdigest()
            vector = [int(h[i:i+2], 16) / 255.0 for i in range(0, 16, 2)]
        
        return BehaviorCharacterization(
            vector=vector,
            source_type=source_type,
            source_id=source_id,
            context=context
        )
    
    def evaluate_novelty(self, entity: Any, source_type: str, source_id: str, context: Dict) -> Tuple[float, BehaviorCharacterization]:
        """Evaluate the novelty of an entity."""
        behavior = self.characterize(entity, source_type, source_id, context)
        self.behaviors_explored += 1
        
        novelty = self.archive.compute_novelty(behavior)
        behavior.novelty_score = novelty
        
        # Add to archive if novel enough
        if novelty > self.novelty_threshold:
            self.archive.add(behavior)
            self.novel_behaviors_found += 1
        
        return novelty, behavior
    
    def evaluate_surprise(self, context: Dict, outcome: float) -> float:
        """Evaluate surprise of an outcome."""
        surprise = self.surprise_detector.observe(context, outcome)
        if surprise > 0.5:
            self.surprises_detected += 1
        return surprise
    
    def compute_curiosity(self, entity: Any, source_type: str, source_id: str, context: Dict) -> float:
        """
        Compute curiosity value - how interesting is exploring this?
        
        Curiosity combines:
        - Novelty (is it different from what we've seen?)
        - Learning potential (will we learn from it?)
        - Uncertainty (how little do we know about it?)
        """
        novelty, behavior = self.evaluate_novelty(entity, source_type, source_id, context)
        
        # Predict outcome
        prediction = self.surprise_detector.predict(context)
        
        # Uncertainty (higher if no prediction available)
        uncertainty = 1.0 if prediction is None else 0.3
        
        # Learning potential (based on prediction accuracy in similar contexts)
        learning_potential = self._estimate_learning_potential(behavior)
        
        # Combine
        curiosity = (
            0.4 * novelty +
            0.3 * uncertainty +
            0.3 * learning_potential
        )
        
        return curiosity
    
    def _estimate_learning_potential(self, behavior: BehaviorCharacterization) -> float:
        """Estimate how much we could learn from exploring this behavior."""
        # Look at similar behaviors in archive
        similar = self.archive.get_nearest(behavior, k=5)
        
        if not similar:
            return 0.8  # Unknown = high learning potential
        
        # High variance in similar behaviors = high learning potential
        if len(similar) < 2:
            return 0.5
        
        novelties = [b.novelty_score for b, _ in similar]
        variance = sum((n - sum(novelties)/len(novelties))**2 for n in novelties) / len(novelties)
        
        return min(1.0, 0.3 + variance * 2)
    
    def identify_frontiers(self, n: int = 10) -> List[List[float]]:
        """Identify unexplored regions of behavior space."""
        if len(self.archive.archive) < 10:
            # Not enough data - random frontiers
            self.frontiers = [[random.random() for _ in range(8)] for _ in range(n)]
            return self.frontiers
        
        # Get diverse sample from archive
        diverse = self.archive.get_diverse_sample(n * 2)
        
        # Generate frontier points between/beyond diverse samples
        frontiers = []
        for _ in range(n):
            # Pick two random points
            if len(diverse) >= 2:
                p1, p2 = random.sample(diverse, 2)
                
                # Extrapolate beyond
                alpha = random.uniform(-0.5, 1.5)
                dim = min(len(p1.vector), len(p2.vector))
                frontier = [
                    p1.vector[i] + alpha * (p2.vector[i] - p1.vector[i])
                    for i in range(dim)
                ]
                frontiers.append(frontier)
        
        self.frontiers = frontiers
        return frontiers
    
    def get_exploration_targets(self, n: int = 5) -> List[Dict]:
        """Get targets for exploration - where to look for novelty."""
        targets = []
        
        # From frontiers
        if self.frontiers:
            for frontier in self.frontiers[:n//2]:
                targets.append({
                    'type': 'frontier',
                    'vector': frontier,
                    'priority': 0.7
                })
        
        # High-novelty recent behaviors (explore similar)
        novel_behaviors = sorted(
            self.archive.archive.values(),
            key=lambda b: b.novelty_score,
            reverse=True
        )[:n//2]
        
        for behavior in novel_behaviors:
            targets.append({
                'type': 'near_novel',
                'vector': behavior.vector,
                'source_id': behavior.source_id,
                'priority': behavior.novelty_score
            })
        
        # Surprising contexts (try to understand them)
        surprising = self.surprise_detector.get_surprising_contexts(0.5)
        for ctx in surprising[:n//4]:
            targets.append({
                'type': 'surprising',
                'context': ctx,
                'priority': 0.8
            })
        
        targets.sort(key=lambda t: t.get('priority', 0), reverse=True)
        return targets[:n]
    
    def novelty_fitness(self, entity: Any, source_type: str, source_id: str, context: Dict, objective_fitness: float = 0.0) -> float:
        """
        Compute fitness based on novelty + objective.
        
        This is the key to open-ended search:
        - Pure objective search gets stuck in local optima
        - Pure novelty search explores randomly
        - Combining them enables both progress and exploration
        """
        novelty, _ = self.evaluate_novelty(entity, source_type, source_id, context)
        
        # Adaptive weighting
        # More novelty weight when stuck, more objective when making progress
        archive_growth = self.novel_behaviors_found / max(1, self.behaviors_explored)
        
        if archive_growth > 0.2:
            # Finding lots of novelty - can focus more on objective
            novelty_weight = 0.3
        else:
            # Not finding novelty - explore more
            novelty_weight = 0.7
        
        combined = novelty_weight * novelty + (1 - novelty_weight) * objective_fitness
        
        return combined
    
    def get_stats(self) -> Dict:
        return {
            'behaviors_explored': self.behaviors_explored,
            'novel_behaviors_found': self.novel_behaviors_found,
            'novelty_rate': self.novel_behaviors_found / max(1, self.behaviors_explored),
            'surprises_detected': self.surprises_detected,
            'archive': self.archive.get_stats(),
            'surprise': self.surprise_detector.get_stats(),
            'frontiers': len(self.frontiers)
        }
    
    def to_dict(self) -> Dict:
        return {
            'archive': {bid: b.to_dict() for bid, b in self.archive.archive.items()},
            'novelty_threshold': self.novelty_threshold,
            'behaviors_explored': self.behaviors_explored,
            'novel_behaviors_found': self.novel_behaviors_found,
            'surprises_detected': self.surprises_detected,
            'frontiers': self.frontiers
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NoveltyEngine':
        engine = cls(novelty_threshold=data.get('novelty_threshold', 0.2))
        
        for bid, bdata in data.get('archive', {}).items():
            behavior = BehaviorCharacterization.from_dict(bdata)
            engine.archive.archive[bid] = behavior
        
        engine.behaviors_explored = data.get('behaviors_explored', 0)
        engine.novel_behaviors_found = data.get('novel_behaviors_found', 0)
        engine.surprises_detected = data.get('surprises_detected', 0)
        engine.frontiers = data.get('frontiers', [])
        
        return engine
