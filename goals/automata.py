"""
AEGIS-2 Goal Automata: Self-Spawning Goal Systems

Key insight: True agency requires INTERNALLY GENERATED GOALS.
Not just optimizing external fitness - but generating what to optimize FOR.

This module implements:
- Goals as first-class entities that can spawn, die, and compete
- Goal hierarchies (goals that create sub-goals)
- Goal conflicts and resolution
- Intrinsic motivation (curiosity, mastery, autonomy)
- Goal evolution through selection pressure
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
from datetime import datetime
from collections import deque
import heapq


class GoalState(Enum):
    """States a goal can be in."""
    DORMANT = "dormant"      # Not yet active
    ACTIVE = "active"        # Currently being pursued
    SUSPENDED = "suspended"  # Temporarily paused
    SATISFIED = "satisfied"  # Achieved
    FAILED = "failed"        # Could not be achieved
    ABANDONED = "abandoned"  # Gave up


class GoalType(Enum):
    """Types of goals."""
    # Extrinsic (external rewards)
    TASK = "task"            # Complete a specific task
    ACQUIRE = "acquire"      # Obtain something
    MAINTAIN = "maintain"    # Keep something in a state
    AVOID = "avoid"          # Prevent something
    
    # Intrinsic (internal drives)
    EXPLORE = "explore"      # Discover new things
    LEARN = "learn"          # Acquire knowledge/skills
    MASTER = "master"        # Achieve competence
    CREATE = "create"        # Generate novelty
    UNDERSTAND = "understand"  # Make sense of something
    
    # Meta (goals about goals)
    OPTIMIZE = "optimize"    # Improve goal achievement
    BALANCE = "balance"      # Manage competing goals
    SPAWN = "spawn"          # Create new goals
    PRUNE = "prune"          # Remove obsolete goals


@dataclass
class Goal:
    """A goal that can be pursued, spawned, and evolved."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    name: str = ""
    goal_type: GoalType = GoalType.TASK
    state: GoalState = GoalState.DORMANT
    
    # What this goal is about
    target: Any = None  # What to achieve/acquire/learn/etc.
    conditions: List[Dict] = field(default_factory=list)  # Success conditions
    
    # Hierarchy
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    
    # Priority and resources
    priority: float = 0.5  # 0-1, higher = more important
    urgency: float = 0.5   # 0-1, time sensitivity
    effort_estimate: float = 0.5  # 0-1, expected difficulty
    resources_allocated: float = 0.0
    
    # Progress
    progress: float = 0.0  # 0-1, completion
    progress_history: List[float] = field(default_factory=list)
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    
    # Intrinsic value (for intrinsic goals)
    intrinsic_value: float = 0.0
    curiosity_value: float = 0.0
    mastery_value: float = 0.0
    
    # Temporal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    activated_at: Optional[float] = None
    deadline: Optional[float] = None
    last_progress: float = 0.0
    
    # Evolution
    generation: int = 0
    parent_goal_ids: List[str] = field(default_factory=list)
    spawn_count: int = 0
    fitness: float = 0.0
    
    # Conflict tracking
    conflicts_with: Set[str] = field(default_factory=set)
    supports: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        try:
                if not self.name:
                    self.name = f"{self.goal_type.value}_{self.id[:6]}"
        except Exception as e:
            raise  # Extended with error handling
    
    def activate(self):
        """Activate this goal."""
        if self.state in [GoalState.DORMANT, GoalState.SUSPENDED]:
            self.state = GoalState.ACTIVE
            self.activated_at = datetime.now().timestamp()
            self.attempts += 1
    
    def suspend(self):
        """Suspend this goal."""
        if self.state == GoalState.ACTIVE:
            self.state = GoalState.SUSPENDED
    
    def satisfy(self):
        """Mark this goal as satisfied."""
        self.state = GoalState.SATISFIED
        self.progress = 1.0
        self.successes += 1
        self._update_fitness(1.0)
    
    def fail(self):
        """Mark this goal as failed."""
        self.state = GoalState.FAILED
        self.failures += 1
        self._update_fitness(0.0)
    
    def abandon(self):
        """Abandon this goal."""
        self.state = GoalState.ABANDONED
        self._update_fitness(0.2)  # Slight penalty
    
    def update_progress(self, new_progress: float):
        """Update progress toward this goal."""
        self.progress = max(0.0, min(1.0, new_progress))
        self.progress_history.append(self.progress)
        self.last_progress = datetime.now().timestamp()
        
        if len(self.progress_history) > 100:
            self.progress_history = self.progress_history[-100:]
        
        if self.progress >= 1.0:
            self.satisfy()
    
    def _update_fitness(self, outcome: float):
        """Update fitness based on outcome."""
        # Fitness considers: success, efficiency, value generated
        efficiency = 1.0 / max(1, self.attempts)
        value = self.intrinsic_value + self.curiosity_value + self.mastery_value
        
        self.fitness = 0.4 * outcome + 0.3 * efficiency + 0.3 * min(1.0, value)
    
    @property
    def effective_priority(self) -> float:
        """Compute effective priority considering urgency and deadlines."""
        base = self.priority
        
        # Urgency boost
        base += 0.2 * self.urgency
        
        # Deadline pressure
        if self.deadline:
            time_left = self.deadline - datetime.now().timestamp()
            if time_left < 0:
                return 0.0  # Missed deadline
            elif time_left < 3600:  # Less than an hour
                base += 0.3
            elif time_left < 86400:  # Less than a day
                base += 0.1
        
        # Progress momentum (keep going on things we've started)
        if 0.1 < self.progress < 0.9:
            base += 0.1
        
        return min(1.0, base)
    
    @property
    def staleness(self) -> float:
        """How stale is this goal (time since last progress)."""
        if not self.last_progress:
            return 0.0
        hours = (datetime.now().timestamp() - self.last_progress) / 3600
        return 1 - math.exp(-hours / 24)
    
    def should_spawn_subgoals(self) -> bool:
        """Determine if this goal should spawn sub-goals."""
        # Complex goals spawn sub-goals
        if self.effort_estimate > 0.7 and self.progress < 0.3:
            return True
        # Stuck goals spawn sub-goals
        if self.staleness > 0.5 and self.progress > 0.1:
            return True
        return False
    
    def should_prune(self) -> bool:
        try:
                """Determine if this goal should be pruned."""
                # Old, low-priority, no-progress goals
                if self.staleness > 0.8 and self.priority < 0.3 and self.progress < 0.1:
                    return True
                # Failed too many times
                if self.failures > 3 and self.successes == 0:
                    return True
                return False
        except Exception as e:
            raise  # Extended with error handling
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'goal_type': self.goal_type.value,
            'state': self.state.value,
            'target': self.target,
            'conditions': self.conditions,
            'parent_id': self.parent_id,
            'child_ids': self.child_ids,
            'priority': self.priority,
            'urgency': self.urgency,
            'effort_estimate': self.effort_estimate,
            'progress': self.progress,
            'intrinsic_value': self.intrinsic_value,
            'curiosity_value': self.curiosity_value,
            'mastery_value': self.mastery_value,
            'generation': self.generation,
            'fitness': self.fitness,
            'attempts': self.attempts,
            'successes': self.successes,
            'failures': self.failures,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Goal':
        goal = cls(
            id=data['id'],
            name=data.get('name', ''),
            goal_type=GoalType(data.get('goal_type', 'task')),
            state=GoalState(data.get('state', 'dormant')),
            target=data.get('target'),
            conditions=data.get('conditions', []),
            parent_id=data.get('parent_id'),
            child_ids=data.get('child_ids', []),
            priority=data.get('priority', 0.5),
            urgency=data.get('urgency', 0.5),
            effort_estimate=data.get('effort_estimate', 0.5),
            progress=data.get('progress', 0.0),
            intrinsic_value=data.get('intrinsic_value', 0.0),
            curiosity_value=data.get('curiosity_value', 0.0),
            mastery_value=data.get('mastery_value', 0.0),
            generation=data.get('generation', 0),
            fitness=data.get('fitness', 0.0),
            attempts=data.get('attempts', 0),
            successes=data.get('successes', 0),
            failures=data.get('failures', 0),
            created_at=data.get('created_at', datetime.now().timestamp())
        )
        return goal


class GoalAutomata:
    """
    Self-organizing goal system.
    
    Goals can:
    - Spawn sub-goals (hierarchical decomposition)
    - Compete for resources (priority-based scheduling)
    - Evolve (successful goals reproduce)
    - Die (failed/obsolete goals get pruned)
    - Generate intrinsic motivation (curiosity, mastery)
    """
    
    def __init__(self, max_active_goals: int = 20, max_total_goals: int = 200):
        self.max_active_goals = max_active_goals
        self.max_total_goals = max_total_goals
        
        self.goals: Dict[str, Goal] = {}
        
        # Priority queue for scheduling
        self._priority_queue: List[Tuple[float, str]] = []
        
        # Resource pool
        self.total_resources: float = 1.0
        self.allocated_resources: float = 0.0
        
        # Intrinsic drive parameters
        self.curiosity_weight: float = 0.3
        self.mastery_weight: float = 0.3
        self.autonomy_weight: float = 0.2
        self.relatedness_weight: float = 0.2
        
        # Statistics
        self.goals_spawned: int = 0
        self.goals_satisfied: int = 0
        self.goals_failed: int = 0
        self.goals_pruned: int = 0
        
        # History
        self.active_goal_history: List[int] = []
        self.satisfaction_history: List[float] = []
        
        # Initialize intrinsic goals
        self._initialize_intrinsic_goals()
    
    def _initialize_intrinsic_goals(self):
        """Create baseline intrinsic motivation goals."""
        
        # Curiosity: explore novel states
        self.add_goal(Goal(
            id="intrinsic_curiosity",
            name="explore_novelty",
            goal_type=GoalType.EXPLORE,
            priority=0.6,
            intrinsic_value=1.0,
            curiosity_value=1.0
        ))
        
        # Mastery: improve competence
        self.add_goal(Goal(
            id="intrinsic_mastery",
            name="achieve_mastery",
            goal_type=GoalType.MASTER,
            priority=0.5,
            intrinsic_value=1.0,
            mastery_value=1.0
        ))
        
        # Understanding: make sense of environment
        self.add_goal(Goal(
            id="intrinsic_understanding",
            name="understand_world",
            goal_type=GoalType.UNDERSTAND,
            priority=0.5,
            intrinsic_value=0.8
        ))
        
        # Meta-goal: optimize goal achievement
        self.add_goal(Goal(
            id="meta_optimize",
            name="optimize_goals",
            goal_type=GoalType.OPTIMIZE,
            priority=0.4,
            intrinsic_value=0.6
        ))
    
    def add_goal(self, goal: Goal) -> str:
        """Add a goal to the system."""
        if len(self.goals) >= self.max_total_goals:
            self._prune_worst()
        
        self.goals[goal.id] = goal
        self.goals_spawned += 1
        
        self._update_queue()
        return goal.id
    
    def spawn_goal(
        self,
        goal_type: GoalType,
        target: Any = None,
        parent_id: Optional[str] = None,
        priority: Optional[float] = None,
        name: Optional[str] = None
    ) -> Goal:
        """Spawn a new goal."""
        parent = self.goals.get(parent_id) if parent_id else None
        
        goal = Goal(
            name=name or f"{goal_type.value}_{self.goals_spawned}",
            goal_type=goal_type,
            target=target,
            parent_id=parent_id,
            priority=priority if priority is not None else (parent.priority * 0.8 if parent else 0.5),
            generation=(parent.generation + 1) if parent else 0,
            parent_goal_ids=[parent_id] if parent_id else []
        )
        
        if parent:
            parent.child_ids.append(goal.id)
            parent.spawn_count += 1
        
        self.add_goal(goal)
        return goal
    
    def decompose_goal(self, goal_id: str, sub_targets: List[Any]) -> List[Goal]:
        """Decompose a goal into sub-goals."""
        parent = self.goals.get(goal_id)
        if not parent:
            return []
        
        sub_goals = []
        for target in sub_targets:
            sub_goal = self.spawn_goal(
                goal_type=parent.goal_type,
                target=target,
                parent_id=goal_id,
                priority=parent.priority * 0.9
            )
            sub_goals.append(sub_goal)
        
        return sub_goals
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals, sorted by effective priority."""
        active = [g for g in self.goals.values() if g.state == GoalState.ACTIVE]
        active.sort(key=lambda g: g.effective_priority, reverse=True)
        return active
    
    def get_next_goal(self) -> Optional[Goal]:
        """Get the highest priority goal to work on."""
        active = self.get_active_goals()
        return active[0] if active else None
    
    def activate_goals(self, max_new: int = 5):
        """Activate dormant goals based on priority and resources."""
        dormant = [g for g in self.goals.values() if g.state == GoalState.DORMANT]
        dormant.sort(key=lambda g: g.effective_priority, reverse=True)
        
        active_count = len([g for g in self.goals.values() if g.state == GoalState.ACTIVE])
        available_slots = self.max_active_goals - active_count
        
        for goal in dormant[:min(max_new, available_slots)]:
            goal.activate()
    
    def update_goal(self, goal_id: str, progress: Optional[float] = None, success: Optional[bool] = None):
        """Update a goal's status."""
        goal = self.goals.get(goal_id)
        if not goal:
            return
        
        if progress is not None:
            goal.update_progress(progress)
        
        if success is not None:
            if success:
                goal.satisfy()
                self.goals_satisfied += 1
                self._propagate_success(goal)
            else:
                goal.fail()
                self.goals_failed += 1
    
    def _propagate_success(self, goal: Goal):
        """Propagate success to parent goals."""
        if not goal.parent_id:
            return
        
        parent = self.goals.get(goal.parent_id)
        if not parent:
            return
        
        # Count satisfied children
        child_states = [
            self.goals.get(cid).state if self.goals.get(cid) else None
            for cid in parent.child_ids
        ]
        
        satisfied = sum(1 for s in child_states if s == GoalState.SATISFIED)
        total = len([s for s in child_states if s is not None])
        
        if total > 0:
            parent.update_progress(satisfied / total)
    
    def allocate_resources(self):
        """Allocate resources to active goals based on priority."""
        active = self.get_active_goals()
        if not active:
            return
        
        total_priority = sum(g.effective_priority for g in active)
        if total_priority == 0:
            return
        
        for goal in active:
            share = (goal.effective_priority / total_priority) * self.total_resources
            goal.resources_allocated = share
        
        self.allocated_resources = sum(g.resources_allocated for g in active)
    
    def compute_intrinsic_rewards(self, state_novelty: float = 0.0, learning_progress: float = 0.0):
        """Compute intrinsic rewards based on curiosity, mastery, etc."""
        rewards = {}
        
        # Curiosity reward (novelty seeking)
        curiosity_goals = [g for g in self.goals.values() if g.goal_type == GoalType.EXPLORE]
        for goal in curiosity_goals:
            reward = self.curiosity_weight * state_novelty
            goal.curiosity_value = 0.9 * goal.curiosity_value + 0.1 * reward
            goal.update_progress(goal.progress + reward * 0.1)
            rewards[goal.id] = reward
        
        # Mastery reward (learning progress)
        mastery_goals = [g for g in self.goals.values() if g.goal_type == GoalType.MASTER]
        for goal in mastery_goals:
            reward = self.mastery_weight * learning_progress
            goal.mastery_value = 0.9 * goal.mastery_value + 0.1 * reward
            goal.update_progress(goal.progress + reward * 0.1)
            rewards[goal.id] = reward
        
        return rewards
    
    def resolve_conflicts(self):
        """Resolve conflicts between competing goals."""
        active = self.get_active_goals()
        
        for i, goal1 in enumerate(active):
            for goal2 in active[i+1:]:
                if goal2.id in goal1.conflicts_with or goal1.id in goal2.conflicts_with:
                    # Suspend lower priority goal
                    if goal1.effective_priority > goal2.effective_priority:
                        goal2.suspend()
                    else:
                        goal1.suspend()
    
    def prune_goals(self):
        """Prune obsolete, failed, and low-value goals."""
        to_prune = []
        
        for goal_id, goal in self.goals.items():
            # Protect intrinsic goals
            if goal_id.startswith('intrinsic_') or goal_id.startswith('meta_'):
                continue
            
            if goal.should_prune():
                to_prune.append(goal_id)
        
        for goal_id in to_prune:
            self._remove_goal(goal_id)
        
        self.goals_pruned += len(to_prune)
        return len(to_prune)
    
    def _prune_worst(self):
        """Prune the worst performing goal to make room."""
        non_intrinsic = [
            g for g in self.goals.values()
            if not g.id.startswith('intrinsic_') and not g.id.startswith('meta_')
        ]
        
        if non_intrinsic:
            worst = min(non_intrinsic, key=lambda g: g.fitness)
            self._remove_goal(worst.id)
    
    def _remove_goal(self, goal_id: str):
    # Restructured for early return
        """Remove a goal and clean up references."""
        goal = self.goals.pop(goal_id, None)
        if not goal:
            return
        
        # Remove from parent's children
        if goal.parent_id and goal.parent_id in self.goals:
            parent = self.goals[goal.parent_id]
            if goal_id in parent.child_ids:
                parent.child_ids.remove(goal_id)
        
        # Orphan children
        for child_id in goal.child_ids:
            if child_id in self.goals:
                self.goals[child_id].parent_id = None
    
    def _update_queue(self):
        """Update the priority queue."""
        self._priority_queue = [
            (-g.effective_priority, g.id)
            for g in self.goals.values()
            if g.state in [GoalState.DORMANT, GoalState.ACTIVE]
        ]
        heapq.heapify(self._priority_queue)
    
    def evolve_goals(self):
        """Evolve goal population - successful goals reproduce."""
        # Get successful goals
        successful = [
            g for g in self.goals.values()
            if g.fitness > 0.5 and g.successes > 0
        ]
        
        if not successful:
            return []
        
        new_goals = []
        
        for goal in successful[:5]:  # Top 5 reproduce
            if random.random() < goal.fitness * 0.5:
                # Mutate and spawn similar goal
                child = self._mutate_goal(goal)
                self.add_goal(child)
                new_goals.append(child)
        
        return new_goals
    
    def _mutate_goal(self, parent: Goal) -> Goal:
        """Create a mutated version of a goal."""
        child = Goal(
            name=f"{parent.name}_v{parent.spawn_count + 1}",
            goal_type=parent.goal_type,
            target=parent.target,  # Could mutate this too
            priority=max(0.1, min(1.0, parent.priority + random.gauss(0, 0.1))),
            urgency=max(0.0, min(1.0, parent.urgency + random.gauss(0, 0.1))),
            effort_estimate=parent.effort_estimate,
            generation=parent.generation + 1,
            parent_goal_ids=[parent.id],
            intrinsic_value=parent.intrinsic_value
        )
        
        # Occasionally change goal type
        if random.random() < 0.1:
            child.goal_type = random.choice(list(GoalType))
        
        return child
    
    def auto_spawn(self, context: Dict) -> List[Goal]:
        """Automatically spawn goals based on context."""
        new_goals = []
        
        # Spawn exploration goals for novel contexts
        novelty = context.get('novelty', 0.0)
        if novelty > 0.5 and random.random() < novelty:
            goal = self.spawn_goal(
                GoalType.EXPLORE,
                target=context.get('novel_item'),
                priority=0.4 + 0.3 * novelty
            )
            new_goals.append(goal)
        
        # Spawn learning goals for errors
        error_rate = context.get('error_rate', 0.0)
        if error_rate > 0.3 and random.random() < error_rate:
            goal = self.spawn_goal(
                GoalType.LEARN,
                target=context.get('error_domain'),
                priority=0.5 + 0.2 * error_rate
            )
            new_goals.append(goal)
        
        # Decompose stuck goals
        for goal in self.get_active_goals():
            if goal.should_spawn_subgoals() and len(goal.child_ids) < 3:
                # Generate sub-targets (could be smarter)
                sub_targets = [f"sub_{i}" for i in range(2)]
                sub_goals = self.decompose_goal(goal.id, sub_targets)
                new_goals.extend(sub_goals)
        
        return new_goals
    
    def tick(self, context: Optional[Dict] = None):
        """Run one tick of the goal system."""
        context = context or {}
        
        # Activate dormant goals
        self.activate_goals()
        
        # Resolve conflicts
        self.resolve_conflicts()
        
        # Allocate resources
        self.allocate_resources()
        
        # Compute intrinsic rewards
        self.compute_intrinsic_rewards(
            context.get('novelty', 0.0),
            context.get('learning_progress', 0.0)
        )
        
        # Auto-spawn new goals
        self.auto_spawn(context)
        
        # Prune obsolete goals
        self.prune_goals()
        
        # Evolve successful goals
        self.evolve_goals()
        
        # Record history
        active_count = len(self.get_active_goals())
        self.active_goal_history.append(active_count)
        if len(self.active_goal_history) > 100:
            self.active_goal_history = self.active_goal_history[-100:]
    
    def get_stats(self) -> Dict:
        """Get goal system statistics."""
        by_state = {}
        by_type = {}
        for goal in self.goals.values():
            by_state[goal.state.value] = by_state.get(goal.state.value, 0) + 1
            by_type[goal.goal_type.value] = by_type.get(goal.goal_type.value, 0) + 1
        
        return {
            'total_goals': len(self.goals),
            'by_state': by_state,
            'by_type': by_type,
            'goals_spawned': self.goals_spawned,
            'goals_satisfied': self.goals_satisfied,
            'goals_failed': self.goals_failed,
            'goals_pruned': self.goals_pruned,
            'avg_fitness': sum(g.fitness for g in self.goals.values()) / max(1, len(self.goals)),
            'allocated_resources': self.allocated_resources
        }
    
    def to_dict(self) -> Dict:
        return {
            'goals': {gid: g.to_dict() for gid, g in self.goals.items()},
            'total_resources': self.total_resources,
            'curiosity_weight': self.curiosity_weight,
            'mastery_weight': self.mastery_weight,
            'goals_spawned': self.goals_spawned,
            'goals_satisfied': self.goals_satisfied,
            'goals_failed': self.goals_failed,
            'goals_pruned': self.goals_pruned
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GoalAutomata':
        automata = cls()
        automata.goals = {gid: Goal.from_dict(g) for gid, g in data.get('goals', {}).items()}
        automata.total_resources = data.get('total_resources', 1.0)
        automata.curiosity_weight = data.get('curiosity_weight', 0.3)
        automata.mastery_weight = data.get('mastery_weight', 0.3)
        automata.goals_spawned = data.get('goals_spawned', 0)
        automata.goals_satisfied = data.get('goals_satisfied', 0)
        automata.goals_failed = data.get('goals_failed', 0)
        automata.goals_pruned = data.get('goals_pruned', 0)
        return automata
