"""
AEGIS-2 Autocatalytic Sets: Self-Sustaining Complexity

Key insight from origin-of-life research: Autocatalytic sets are 
collections of entities where each entity's creation is catalyzed 
by other entities in the set. The whole sustains itself.

This is crucial for emergence: you need self-sustaining dynamics
that don't require external energy to maintain complexity.

This module implements:
- Catalytic networks (A helps create B, B helps create C, C helps create A)
- Closure detection (is the set self-sustaining?)
- RAF sets (Reflexively Autocatalytic and Food-generated)
- Hypercycle dynamics
- Bootstrapping of new autocatalytic structures
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, FrozenSet
from datetime import datetime
from collections import defaultdict
from enum import Enum


class EntityType(Enum):
    """Types of entities that can participate in autocatalysis."""
    PATTERN = "pattern"
    GENE = "gene"
    GOAL = "goal"
    BEHAVIOR = "behavior"
    CONCEPT = "concept"
    RULE = "rule"


@dataclass
class CatalyticEntity:
    """An entity that can catalyze and be catalyzed."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:12])
    name: str = ""
    entity_type: EntityType = EntityType.PATTERN
    
    # The actual content
    content: Any = None
    
    # What this entity catalyzes (helps create)
    catalyzes: Set[str] = field(default_factory=set)
    
    # What catalyzes this entity (helps create it)
    catalyzed_by: Set[str] = field(default_factory=set)
    
    # Concentration/abundance
    concentration: float = 1.0
    
    # Activity level
    activity: float = 1.0
    
    # Decay rate
    decay_rate: float = 0.01
    
    # Creation requirements (what's needed to create this)
    requirements: Set[str] = field(default_factory=set)  # Entity IDs
    
    # Food set membership (is this a "food" molecule - externally provided?)
    is_food: bool = False
    
    # Temporal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    last_catalyzed: float = 0.0
    times_catalyzed: int = 0
    
    def catalyze(self, target_id: str):
        """Record that this entity catalyzed another."""
        self.catalyzes.add(target_id)
        self.last_catalyzed = datetime.now().timestamp()
        self.times_catalyzed += 1
        self.activity = min(2.0, self.activity + 0.1)
    
    def decay(self):
        """Apply decay."""
        self.concentration *= (1 - self.decay_rate)
        self.activity *= 0.99
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'entity_type': self.entity_type.value,
            'catalyzes': list(self.catalyzes),
            'catalyzed_by': list(self.catalyzed_by),
            'concentration': self.concentration,
            'activity': self.activity,
            'is_food': self.is_food,
            'requirements': list(self.requirements),
            'times_catalyzed': self.times_catalyzed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CatalyticEntity':
        entity = cls(
            id=data['id'],
            name=data.get('name', ''),
            entity_type=EntityType(data.get('entity_type', 'pattern')),
            concentration=data.get('concentration', 1.0),
            activity=data.get('activity', 1.0),
            is_food=data.get('is_food', False),
            times_catalyzed=data.get('times_catalyzed', 0)
        )
        entity.catalyzes = set(data.get('catalyzes', []))
        entity.catalyzed_by = set(data.get('catalyzed_by', []))
        entity.requirements = set(data.get('requirements', []))
        return entity


@dataclass
class Reaction:
    """A catalyzed reaction that produces an entity."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    
    # Reactants consumed
    reactants: Set[str] = field(default_factory=set)
    
    # Catalyst (not consumed)
    catalyst: str = ""
    
    # Product created
    product: str = ""
    
    # Reaction rate
    rate: float = 1.0
    
    # Activation energy (threshold to fire)
    activation_energy: float = 0.5
    
    # Times fired
    times_fired: int = 0
    
    def can_fire(self, concentrations: Dict[str, float]) -> bool:
        """Check if reaction can fire given concentrations."""
        # Need catalyst
        if self.catalyst and concentrations.get(self.catalyst, 0) < 0.1:
            return False
        
        # Need all reactants
        for reactant in self.reactants:
            if concentrations.get(reactant, 0) < 0.1:
                return False
        
        # Check activation energy
        total_concentration = sum(concentrations.get(r, 0) for r in self.reactants)
        catalyst_boost = concentrations.get(self.catalyst, 0) if self.catalyst else 1.0
        
        return (total_concentration * catalyst_boost) > self.activation_energy
    
    def fire(self, concentrations: Dict[str, float]) -> float:
        """Fire the reaction, return amount produced."""
        if not self.can_fire(concentrations):
            return 0.0
        
        # Consume reactants
        consumption = min(concentrations.get(r, 0) * 0.5 for r in self.reactants) if self.reactants else 0.5
        
        # Catalytic boost
        catalyst_conc = concentrations.get(self.catalyst, 1.0) if self.catalyst else 1.0
        
        production = consumption * self.rate * min(2.0, catalyst_conc)
        
        self.times_fired += 1
        
        return production


class AutocatalyticSet:
    """
    An autocatalytic set - a self-sustaining network of catalytic entities.
    
    Key property: Every entity in the set has its creation catalyzed
    by at least one other entity in the set.
    """
    
    def __init__(self, set_id: Optional[str] = None):
        self.id = set_id or hashlib.sha256(str(random.random()).encode()).hexdigest()[:10]
        
        self.entities: Dict[str, CatalyticEntity] = {}
        self.reactions: Dict[str, Reaction] = {}
        
        # Food set (externally provided entities)
        self.food_set: Set[str] = set()
        
        # Closure status
        self.is_closed: bool = False
        self.closure_ratio: float = 0.0
        
        # Dynamics
        self.concentrations: Dict[str, float] = {}
        self.concentration_history: Dict[str, List[float]] = defaultdict(list)
        
        # Statistics
        self.total_reactions: int = 0
        self.entities_created: int = 0
        self.entities_died: int = 0
    
    def add_entity(self, entity: CatalyticEntity) -> str:
        """Add an entity to the set."""
        self.entities[entity.id] = entity
        self.concentrations[entity.id] = entity.concentration
        
        if entity.is_food:
            self.food_set.add(entity.id)
        
        self._update_closure()
        return entity.id
    
    def add_reaction(self, reaction: Reaction) -> str:
        """Add a reaction to the set."""
        self.reactions[reaction.id] = reaction
        
        # Update catalytic relationships
        if reaction.catalyst in self.entities:
            self.entities[reaction.catalyst].catalyzes.add(reaction.product)
        
        if reaction.product in self.entities:
            self.entities[reaction.product].catalyzed_by.add(reaction.catalyst)
        
        self._update_closure()
        return reaction.id
    
    def connect(self, catalyst_id: str, product_id: str, reactants: Optional[Set[str]] = None):
        """Create a catalytic connection between entities."""
        if catalyst_id not in self.entities or product_id not in self.entities:
            return
        
        reaction = Reaction(
            catalyst=catalyst_id,
            product=product_id,
            reactants=reactants or set()
        )
        
        self.add_reaction(reaction)
    
    def _update_closure(self):
        """Update closure status of the set."""
        if not self.entities:
            self.is_closed = False
            self.closure_ratio = 0.0
            return
        
        # An autocatalytic set is closed if every non-food entity
        # has at least one catalyst in the set
        non_food = [e for e in self.entities.values() if not e.is_food]
        
        if not non_food:
            self.is_closed = True
            self.closure_ratio = 1.0
            return
        
        catalyzed_count = 0
        for entity in non_food:
            # Check if any catalyst is in the set
            has_catalyst = any(c in self.entities for c in entity.catalyzed_by)
            if has_catalyst:
                catalyzed_count += 1
        
        self.closure_ratio = catalyzed_count / len(non_food)
        self.is_closed = (self.closure_ratio >= 1.0)
    
    def step(self) -> Dict[str, float]:
        """Run one step of the autocatalytic dynamics."""
        production = defaultdict(float)
        consumption = defaultdict(float)
        
        # Fire reactions
        for reaction in self.reactions.values():
            if reaction.can_fire(self.concentrations):
                amount = reaction.fire(self.concentrations)
                production[reaction.product] += amount
                
                for reactant in reaction.reactants:
                    consumption[reactant] += amount * 0.3
                
                self.total_reactions += 1
        
        # Update concentrations
        for entity_id, entity in self.entities.items():
            # Production
            self.concentrations[entity_id] += production.get(entity_id, 0)
            
            # Consumption
            self.concentrations[entity_id] -= consumption.get(entity_id, 0)
            
            # Decay
            entity.decay()
            self.concentrations[entity_id] *= (1 - entity.decay_rate)
            
            # Food is replenished
            if entity.is_food:
                self.concentrations[entity_id] = max(1.0, self.concentrations[entity_id])
            
            # Minimum concentration
            self.concentrations[entity_id] = max(0.0, self.concentrations[entity_id])
            
            # Track history
            self.concentration_history[entity_id].append(self.concentrations[entity_id])
            if len(self.concentration_history[entity_id]) > 100:
                self.concentration_history[entity_id] = self.concentration_history[entity_id][-100:]
            
            # Death
            if self.concentrations[entity_id] < 0.01 and not entity.is_food:
                self.entities_died += 1
        
        # Check for spontaneous entity creation (if closed and active)
        if self.is_closed and random.random() < 0.1 * self.closure_ratio:
            self._spontaneous_creation()
        
        return dict(production)
    
    def _spontaneous_creation(self):
        """Spontaneously create a new entity through autocatalysis."""
        if not self.entities:
            return
        
        # Pick a random catalyst
        active_entities = [e for e in self.entities.values() if self.concentrations.get(e.id, 0) > 0.5]
        if not active_entities:
            return
        
        catalyst = random.choice(active_entities)
        
        # Create new entity
        new_entity = CatalyticEntity(
            name=f"spawned_{self.entities_created}",
            entity_type=catalyst.entity_type,
            catalyzed_by={catalyst.id}
        )
        
        self.add_entity(new_entity)
        self.connect(catalyst.id, new_entity.id)
        self.entities_created += 1
    
    def find_raf_core(self) -> Set[str]:
        """
        Find the RAF (Reflexively Autocatalytic and Food-generated) core.
        
        The RAF is the maximal subset where:
        1. Every reaction is catalyzed by something in the set
        2. Every reactant is either food or producible from food
        """
        # Start with all entities
        raf = set(self.entities.keys())
        
        changed = True
        while changed:
            changed = False
            new_raf = set()
            
            for entity_id in raf:
                entity = self.entities[entity_id]
                
                # Food is always in RAF
                if entity.is_food:
                    new_raf.add(entity_id)
                    continue
                
                # Check if catalyzed by something in current RAF
                has_catalyst = any(c in raf for c in entity.catalyzed_by)
                
                # Check if requirements are satisfiable from RAF
                requirements_met = all(r in raf or r in self.food_set for r in entity.requirements)
                
                if has_catalyst and requirements_met:
                    new_raf.add(entity_id)
            
            if new_raf != raf:
                changed = True
                raf = new_raf
        
        return raf
    
    def hypercycle_strength(self) -> float:
        """
        Compute the strength of hypercyclic organization.
        
        A hypercycle is a cycle where each entity catalyzes the next.
        Stronger hypercycles = more robust self-maintenance.
        """
        if len(self.entities) < 2:
            return 0.0
        
        # Find cycles in the catalytic graph
        cycle_strengths = []
        
        for start_id in self.entities:
            # DFS to find cycles
            visited = set()
            path = [start_id]
            
            cycles = self._find_catalytic_cycles(start_id, start_id, visited, path)
            
            for cycle in cycles:
                # Cycle strength = product of concentrations
                strength = 1.0
                for entity_id in cycle:
                    strength *= self.concentrations.get(entity_id, 0.1)
                cycle_strengths.append(strength ** (1.0 / len(cycle)))  # Geometric mean
        
        if cycle_strengths:
            return sum(cycle_strengths) / len(cycle_strengths)
        return 0.0
    
    def _find_catalytic_cycles(self, start: str, current: str, visited: Set[str], path: List[str]) -> List[List[str]]:
        """Find cycles in catalytic graph."""
        cycles = []
        
        entity = self.entities.get(current)
        if not entity:
            return cycles
        
        for next_id in entity.catalyzes:
            if next_id == start and len(path) > 1:
                cycles.append(list(path))
            elif next_id not in visited and next_id in self.entities:
                visited.add(next_id)
                path.append(next_id)
                sub_cycles = self._find_catalytic_cycles(start, next_id, visited.copy(), list(path))
                cycles.extend(sub_cycles)
                path.pop()
        
        return cycles
    
    def get_stats(self) -> Dict:
        return {
            'num_entities': len(self.entities),
            'num_reactions': len(self.reactions),
            'food_set_size': len(self.food_set),
            'is_closed': self.is_closed,
            'closure_ratio': self.closure_ratio,
            'raf_core_size': len(self.find_raf_core()),
            'hypercycle_strength': self.hypercycle_strength(),
            'total_concentration': sum(self.concentrations.values()),
            'total_reactions_fired': self.total_reactions,
            'entities_created': self.entities_created,
            'entities_died': self.entities_died
        }
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'entities': {eid: e.to_dict() for eid, e in self.entities.items()},
            'reactions': {rid: {
                'id': r.id,
                'catalyst': r.catalyst,
                'product': r.product,
                'reactants': list(r.reactants),
                'rate': r.rate
            } for rid, r in self.reactions.items()},
            'food_set': list(self.food_set),
            'concentrations': self.concentrations,
            'is_closed': self.is_closed,
            'stats': {
                'total_reactions': self.total_reactions,
                'entities_created': self.entities_created,
                'entities_died': self.entities_died
            }
        }


class AutocatalyticNetwork:
    """
    A network of interacting autocatalytic sets.
    
    Multiple autocatalytic sets can:
    - Compete for resources
    - Merge into larger sets
    - Split into smaller sets
    - Bootstrap new sets
    """
    
    def __init__(self):
        self.sets: Dict[str, AutocatalyticSet] = {}
        
        # Shared food pool
        self.food_pool: Dict[str, float] = {}
        
        # Inter-set reactions
        self.cross_reactions: List[Tuple[str, str, str]] = []  # (set1, set2, reaction_type)
        
        # Statistics
        self.sets_created: int = 0
        self.sets_merged: int = 0
        self.sets_split: int = 0
        self.total_steps: int = 0
    
    def add_set(self, ac_set: AutocatalyticSet) -> str:
        """Add an autocatalytic set to the network."""
        self.sets[ac_set.id] = ac_set
        self.sets_created += 1
        return ac_set.id
    
    def create_set_from_entities(self, entities: List[CatalyticEntity]) -> AutocatalyticSet:
        """Create a new autocatalytic set from entities."""
        ac_set = AutocatalyticSet()
        
        for entity in entities:
            ac_set.add_entity(entity)
        
        # Auto-connect based on types
        for e1 in entities:
            for e2 in entities:
                if e1.id != e2.id and random.random() < 0.3:
                    ac_set.connect(e1.id, e2.id)
        
        self.add_set(ac_set)
        return ac_set
    
    def step(self):
        """Run one step of network dynamics."""
        self.total_steps += 1
        
        # Step each set
        for ac_set in self.sets.values():
            ac_set.step()
        
        # Check for mergers (sets that become connected)
        self._check_mergers()
        
        # Check for splits (sets that lose closure)
        self._check_splits()
        
        # Bootstrap new sets from active entities
        if random.random() < 0.05:
            self._bootstrap_new_set()
    
    def _check_mergers(self):
        """Check if any sets should merge."""
        set_ids = list(self.sets.keys())
        
        for i, id1 in enumerate(set_ids):
            for id2 in set_ids[i+1:]:
                set1 = self.sets.get(id1)
                set2 = self.sets.get(id2)
                
                if not set1 or not set2:
                    continue
                
                # Check for cross-catalysis
                cross_catalysis = 0
                for e1 in set1.entities.values():
                    for e2 in set2.entities.values():
                        if e2.id in e1.catalyzes or e1.id in e2.catalyzes:
                            cross_catalysis += 1
                
                # Merge if significant cross-catalysis
                if cross_catalysis > min(len(set1.entities), len(set2.entities)) * 0.3:
                    self._merge_sets(id1, id2)
                    return  # Only one merge per step
    
    def _merge_sets(self, id1: str, id2: str):
        """Merge two autocatalytic sets."""
        set1 = self.sets.get(id1)
        set2 = self.sets.get(id2)
        
        if not set1 or not set2:
            return
        
        # Merge into set1
        for entity in set2.entities.values():
            if entity.id not in set1.entities:
                set1.add_entity(entity)
        
        for reaction in set2.reactions.values():
            if reaction.id not in set1.reactions:
                set1.add_reaction(reaction)
        
        # Remove set2
        del self.sets[id2]
        self.sets_merged += 1
    
    def _check_splits(self):
        """Check if any sets should split."""
        for set_id, ac_set in list(self.sets.items()):
            if not ac_set.is_closed and ac_set.closure_ratio < 0.5:
                # Find the RAF core
                raf = ac_set.find_raf_core()
                
                if len(raf) > 0 and len(raf) < len(ac_set.entities) * 0.7:
                    # Split off the RAF core
                    self._split_set(set_id, raf)
                    return
    
    def _split_set(self, set_id: str, core_ids: Set[str]):
        """Split a set into core and periphery."""
        original = self.sets.get(set_id)
        if not original:
            return
        
        # Create new set from core
        core_set = AutocatalyticSet()
        for entity_id in core_ids:
            if entity_id in original.entities:
                core_set.add_entity(original.entities[entity_id])
        
        # Copy relevant reactions
        for reaction in original.reactions.values():
            if reaction.catalyst in core_ids and reaction.product in core_ids:
                core_set.add_reaction(reaction)
        
        # Remove core from original
        for entity_id in core_ids:
            if entity_id in original.entities:
                del original.entities[entity_id]
        
        self.add_set(core_set)
        self.sets_split += 1
    
    def _bootstrap_new_set(self):
        """Bootstrap a new autocatalytic set from network activity."""
        # Collect active entities across sets
        active_entities = []
        for ac_set in self.sets.values():
            for entity in ac_set.entities.values():
                if ac_set.concentrations.get(entity.id, 0) > 1.0:
                    active_entities.append(entity)
        
        if len(active_entities) < 3:
            return
        
        # Sample some active entities
        sample = random.sample(active_entities, min(5, len(active_entities)))
        
        # Create new entities inspired by the sample
        new_entities = []
        for entity in sample:
            new_entity = CatalyticEntity(
                name=f"bootstrap_{self.sets_created}_{len(new_entities)}",
                entity_type=entity.entity_type,
                catalyzed_by={entity.id}
            )
            new_entities.append(new_entity)
        
        if new_entities:
            new_set = self.create_set_from_entities(new_entities)
    
    def get_stats(self) -> Dict:
        total_entities = sum(len(s.entities) for s in self.sets.values())
        closed_sets = sum(1 for s in self.sets.values() if s.is_closed)
        
        return {
            'num_sets': len(self.sets),
            'total_entities': total_entities,
            'closed_sets': closed_sets,
            'sets_created': self.sets_created,
            'sets_merged': self.sets_merged,
            'sets_split': self.sets_split,
            'total_steps': self.total_steps,
            'avg_closure': sum(s.closure_ratio for s in self.sets.values()) / max(1, len(self.sets))
        }
    
    def to_dict(self) -> Dict:
        return {
            'sets': {sid: s.to_dict() for sid, s in self.sets.items()},
            'food_pool': self.food_pool,
            'stats': {
                'sets_created': self.sets_created,
                'sets_merged': self.sets_merged,
                'sets_split': self.sets_split,
                'total_steps': self.total_steps
            }
        }
