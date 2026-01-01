"""
Hierarchical Temporal Abstraction

Actions at multiple timescales:
- Level 0: Primitive actions (milliseconds)
- Level 1: Skills (seconds)
- Level 2: Tactics (minutes)
- Level 3: Strategies (hours)
- Level 4: Goals (days)
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class TemporalLevel(Enum):
    """Temporal abstraction levels."""
    PRIMITIVE = 0  # Individual actions
    SKILL = 1  # Sequences of primitives
    TACTIC = 2  # Combinations of skills
    STRATEGY = 3  # Long-term plans
    GOAL = 4  # High-level objectives


@dataclass
class Option:
    """An option (skill) at a given temporal level."""
    option_id: str
    name: str
    level: TemporalLevel

    # Initiation set (where can this option start?)
    initiation_condition: Optional[Callable] = None

    # Policy (what does this option do?)
    policy: Optional[Callable] = None

    # Termination condition (when does this option end?)
    termination_condition: Optional[Callable] = None

    # Composed from lower-level options
    sub_options: List[str] = field(default_factory=list)

    # Statistics
    success_count: int = 0
    failure_count: int = 0
    avg_duration: float = 0.0

    def success_rate(self) -> float:
        """Get success rate of option."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


@dataclass
class Skill:
    """A learned skill (alias for Option at SKILL level)."""
    skill_id: str
    name: str
    primitive_actions: List[Any] = field(default_factory=list)
    duration: int = 0  # Number of primitive steps

    def execute_step(self, step: int, state: Any) -> Any:
        """Execute one step of the skill."""
        if step < len(self.primitive_actions):
            return self.primitive_actions[step]
        return None


class TemporalHierarchy:
    """
    Hierarchical action selection across multiple timescales.

    Key idea: High-level decisions operate on slower timescales,
    low-level decisions operate on faster timescales.
    """

    def __init__(self, num_levels: int = 5):
        self.num_levels = num_levels
        self.options: Dict[TemporalLevel, List[Option]] = {
            level: [] for level in TemporalLevel
        }
        self.skills: Dict[str, Skill] = {}

        # Current active option at each level
        self.active_options: Dict[TemporalLevel, Optional[Option]] = {
            level: None for level in TemporalLevel
        }

        # Timescale for each level (in primitive steps)
        self.timescales = {
            TemporalLevel.PRIMITIVE: 1,
            TemporalLevel.SKILL: 10,
            TemporalLevel.TACTIC: 100,
            TemporalLevel.STRATEGY: 1000,
            TemporalLevel.GOAL: 10000
        }

        self.step_count = 0

    def add_option(self, option: Option):
        """Add an option to the hierarchy."""
        self.options[option.level].append(option)

    def add_skill(self, skill: Skill):
        """Add a skill."""
        self.skills[skill.skill_id] = skill

    def select_action(self, state: Any) -> Any:
        """
        Select action hierarchically.

        Higher levels make decisions at their timescale,
        lower levels fill in details.
        """
        self.step_count += 1

        # Check each level from top to bottom
        for level in reversed(list(TemporalLevel)):
            timescale = self.timescales[level]

            # Should this level make a decision?
            if self.step_count % timescale == 0:
                # Select option at this level
                active = self._select_option_at_level(level, state)
                self.active_options[level] = active

        # Execute primitive action (lowest level)
        primitive_option = self.active_options[TemporalLevel.PRIMITIVE]
        if primitive_option and primitive_option.policy:
            return primitive_option.policy(state)

        return None  # Default action

    def _select_option_at_level(
        self,
        level: TemporalLevel,
        state: Any
    ) -> Optional[Option]:
        """Select an option at a specific level."""
        available_options = [
            opt for opt in self.options[level]
            if not opt.initiation_condition or opt.initiation_condition(state)
        ]

        if not available_options:
            return None

        # Select based on success rate
        if random.random() < 0.1:
            # Explore
            return random.choice(available_options)
        else:
            # Exploit
            return max(available_options, key=lambda opt: opt.success_rate())

    def update_option_success(self, level: TemporalLevel, success: bool):
        """Update success statistics for active option."""
        active = self.active_options[level]
        if active:
            if success:
                active.success_count += 1
            else:
                active.failure_count += 1

    def create_skill_from_primitives(
        self,
        primitive_actions: List[Any],
        name: str = ""
    ) -> Skill:
        """Create a new skill from sequence of primitive actions."""
        skill_id = f"skill_{len(self.skills)}"
        skill = Skill(
            skill_id=skill_id,
            name=name or skill_id,
            primitive_actions=primitive_actions,
            duration=len(primitive_actions)
        )
        self.add_skill(skill)
        return skill

    def discover_options(self, trajectory: List[Tuple[Any, Any, float]]):
        """
        Discover new options from successful trajectories.

        Args:
            trajectory: List of (state, action, reward) tuples
        """
        # Find high-reward segments
        window_size = 10
        for i in range(len(trajectory) - window_size):
            segment = trajectory[i:i + window_size]
            avg_reward = sum(r for _, _, r in segment) / window_size

            if avg_reward > 0.5:  # High-reward segment
                # Create skill from this segment
                actions = [action for _, action, _ in segment]
                skill = self.create_skill_from_primitives(
                    actions,
                    name=f"discovered_skill_{len(self.skills)}"
                )

                # Create option for skill
                option = Option(
                    option_id=f"opt_{skill.skill_id}",
                    name=skill.name,
                    level=TemporalLevel.SKILL,
                    sub_options=[f"primitive_{a}" for a in actions]
                )
                self.add_option(option)

    def get_hierarchy_depth(self) -> int:
        """Get maximum depth of learned hierarchy."""
        max_depth = 0
        for level, options in self.options.items():
            if options:
                max_depth = max(max_depth, level.value)
        return max_depth + 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get hierarchy statistics."""
        stats = {}
        for level in TemporalLevel:
            stats[level.name] = {
                'num_options': len(self.options[level]),
                'active': self.active_options[level].name if self.active_options[level] else None
            }
        return stats
