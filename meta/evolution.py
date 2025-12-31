"""
AEGIS-2 Meta-Evolution: Evolving Evolution Itself

This is the layer that closes the gap.

The problem with AEGIS-2 so far:
- Genome evolves, but within fixed node types
- Patterns compose, but with fixed operators
- Goals spawn, but from predefined types
- The POSSIBILITY SPACE is bounded

The solution: Evolve the possibility space itself.

This module implements:
- Evolvable node types (new genetic primitives emerge)
- Evolvable operators (new pattern combinators emerge)
- Evolvable goal types (new motivation categories emerge)
- Evolvable fitness functions (what "good" means can change)
- Evolvable evolution parameters (mutation rates evolve)

This is genuine open-endedness: the search space grows as you search.
"""

import random
import math
import hashlib
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Type
from datetime import datetime
from enum import Enum, auto
from abc import ABC, abstractmethod
import json


# =============================================================================
# EVOLVABLE PRIMITIVES
# =============================================================================

@dataclass
class Primitive:
    """
    A primitive operation that can be used in genetic programs.
    
    Unlike fixed NodeTypes, these can be CREATED and EVOLVED.
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    
    # Signature
    arity: int = 0  # Number of inputs
    input_types: List[str] = field(default_factory=list)  # Expected input types
    output_type: str = "any"
    
    # The actual computation (as a mini-program or lambda reference)
    # Stored as source code string that can be eval'd
    implementation: str = "lambda *args: args[0] if args else 0"
    
    # Composition (primitives can be composed of other primitives)
    composed_of: List[str] = field(default_factory=list)  # Primitive IDs
    
    # Evolution tracking
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutations: int = 0
    
    # Usage statistics
    usage_count: int = 0
    success_count: int = 0  # Times it contributed to fitness
    
    # Fitness of this primitive itself
    fitness: float = 0.5
    
    def execute(self, *args) -> Any:
        """Execute this primitive."""
        self.usage_count += 1
        try:
            fn = eval(self.implementation)
            result = fn(*args)
            return result
        except Exception as e:
            return 0
    
    def clone(self) -> 'Primitive':
        return Primitive(
            id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:10],
            name=f"{self.name}_clone",
            arity=self.arity,
            input_types=list(self.input_types),
            output_type=self.output_type,
            implementation=self.implementation,
            composed_of=list(self.composed_of),
            generation=self.generation + 1,
            parent_ids=[self.id]
        )
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'arity': self.arity,
            'input_types': self.input_types,
            'output_type': self.output_type,
            'implementation': self.implementation,
            'composed_of': self.composed_of,
            'generation': self.generation,
            'fitness': self.fitness,
            'usage_count': self.usage_count
        }


class PrimitiveFactory:
    """
    Factory for creating and evolving primitives.
    
    This is where new genetic building blocks come from.
    """
    
    # Base templates for generating new primitives
    TEMPLATES = {
        'arithmetic': [
            ("add", 2, "lambda a, b: a + b"),
            ("sub", 2, "lambda a, b: a - b"),
            ("mul", 2, "lambda a, b: a * b"),
            ("div", 2, "lambda a, b: a / b if b != 0 else 0"),
            ("neg", 1, "lambda a: -a"),
            ("abs", 1, "lambda a: abs(a)"),
            ("mod", 2, "lambda a, b: a % b if b != 0 else 0"),
            ("pow", 2, "lambda a, b: a ** min(10, max(-10, b))"),
        ],
        'comparison': [
            ("gt", 2, "lambda a, b: 1.0 if a > b else 0.0"),
            ("lt", 2, "lambda a, b: 1.0 if a < b else 0.0"),
            ("eq", 2, "lambda a, b: 1.0 if abs(a - b) < 0.01 else 0.0"),
            ("neq", 2, "lambda a, b: 1.0 if abs(a - b) >= 0.01 else 0.0"),
            ("gte", 2, "lambda a, b: 1.0 if a >= b else 0.0"),
            ("lte", 2, "lambda a, b: 1.0 if a <= b else 0.0"),
        ],
        'logic': [
            ("and", 2, "lambda a, b: 1.0 if (a > 0.5 and b > 0.5) else 0.0"),
            ("or", 2, "lambda a, b: 1.0 if (a > 0.5 or b > 0.5) else 0.0"),
            ("not", 1, "lambda a: 0.0 if a > 0.5 else 1.0"),
            ("xor", 2, "lambda a, b: 1.0 if ((a > 0.5) != (b > 0.5)) else 0.0"),
        ],
        'mathematical': [
            ("sin", 1, "lambda a: __import__('math').sin(a)"),
            ("cos", 1, "lambda a: __import__('math').cos(a)"),
            ("exp", 1, "lambda a: __import__('math').exp(min(10, a))"),
            ("log", 1, "lambda a: __import__('math').log(max(0.001, a))"),
            ("sqrt", 1, "lambda a: __import__('math').sqrt(max(0, a))"),
            ("tanh", 1, "lambda a: __import__('math').tanh(a)"),
        ],
        'control': [
            ("if", 3, "lambda c, t, f: t if c > 0.5 else f"),
            ("min", 2, "lambda a, b: min(a, b)"),
            ("max", 2, "lambda a, b: max(a, b)"),
            ("clamp", 3, "lambda x, lo, hi: max(lo, min(hi, x))"),
            ("lerp", 3, "lambda a, b, t: a + (b - a) * t"),
        ],
        'aggregation': [
            ("sum", 1, "lambda *args: sum(args)"),
            ("avg", 1, "lambda *args: sum(args) / len(args) if args else 0"),
            ("prod", 1, "lambda *args: __import__('functools').reduce(lambda a, b: a * b, args, 1)"),
        ],
    }
    
    def __init__(self):
        self.primitives: Dict[str, Primitive] = {}
        self.primitives_by_category: Dict[str, List[str]] = {}
        self.created_count = 0
        
        # Initialize with base primitives
        self._initialize_base()
    
    def _initialize_base(self):
        """Create base primitive set."""
        for category, templates in self.TEMPLATES.items():
            self.primitives_by_category[category] = []
            
            for name, arity, impl in templates:
                prim = Primitive(
                    id=f"base_{name}",
                    name=name,
                    arity=arity,
                    implementation=impl,
                    generation=0
                )
                self.primitives[prim.id] = prim
                self.primitives_by_category[category].append(prim.id)
                self.created_count += 1
    
    def create_composed(self, primitives: List[str], combination: str = "chain") -> Optional[Primitive]:
        try:
                """
                Create a new primitive by composing existing ones.
        
                This is how NEW primitives emerge - not from templates,
                but from combinations of what exists.
                """
                prims = [self.primitives.get(pid) for pid in primitives]
                prims = [p for p in prims if p is not None]
        
                if not prims:
                    return None
        
                if combination == "chain":
                    # f(g(x)) - chain composition
                    if len(prims) < 2:
                        return None
            
                    # Outer function takes result of inner
                    inner, outer = prims[0], prims[1]
            
                    if outer.arity < 1:
                        return None
            
                    new_arity = inner.arity
            
                    # Build composed implementation
                    impl = f"lambda *args: ({outer.implementation})({inner.implementation}(*args))"
            
                    prim = Primitive(
                        name=f"{outer.name}_of_{inner.name}",
                        arity=new_arity,
                        implementation=impl,
                        composed_of=[inner.id, outer.id],
                        generation=max(inner.generation, outer.generation) + 1,
                        parent_ids=[inner.id, outer.id]
                    )
            
                elif combination == "parallel":
                    # (f(x), g(x)) - parallel application
                    if len(prims) < 2:
                        return None
            
                    # All primitives applied to same inputs, results combined
                    max_arity = max(p.arity for p in prims)
            
                    impl_parts = [f"({p.implementation})(*args[:{ p.arity}])" for p in prims]
                    impl = f"lambda *args: ({' + '.join(impl_parts)}) / {len(prims)}"
            
                    prim = Primitive(
                        name=f"par_{'_'.join(p.name for p in prims[:3])}",
                        arity=max_arity,
                        implementation=impl,
                        composed_of=[p.id for p in prims],
                        generation=max(p.generation for p in prims) + 1,
                        parent_ids=[p.id for p in prims]
                    )
            
                elif combination == "conditional":
                    # if(c, f(x), g(x)) - conditional composition
                    if len(prims) < 3:
                        return None
            
                    cond, true_p, false_p = prims[0], prims[1], prims[2]
                    max_arity = max(cond.arity, true_p.arity, false_p.arity)
            
                    impl = f"lambda *args: ({true_p.implementation})(*args) if ({cond.implementation})(*args[:{ cond.arity}]) > 0.5 else ({false_p.implementation})(*args)"
            
                    prim = Primitive(
                        name=f"cond_{cond.name}_{true_p.name}_{false_p.name}",
                        arity=max_arity,
                        implementation=impl,
                        composed_of=[cond.id, true_p.id, false_p.id],
                        generation=max(cond.generation, true_p.generation, false_p.generation) + 1,
                        parent_ids=[cond.id, true_p.id, false_p.id]
                    )
                else:
                    return None
        
                self.primitives[prim.id] = prim
                self.created_count += 1
        
                return prim
        except Exception as e:
            raise  # Extended with error handling
    
    def mutate(self, primitive: Primitive) -> Primitive:
        """Mutate a primitive to create a variant."""
        clone = primitive.clone()
        clone.mutations = primitive.mutations + 1
        
        mutation_type = random.choice(['constant', 'operator', 'structure'])
        
        if mutation_type == 'constant':
            # Add a constant modifier
            modifier = random.choice([
                f" + {random.uniform(-1, 1):.3f}",
                f" * {random.uniform(0.5, 2):.3f}",
                f" ** {random.uniform(0.5, 2):.3f}"
            ])
            # Wrap the result
            old_impl = clone.implementation
            clone.implementation = f"lambda *args: ({old_impl})(*args){modifier}"
            clone.name = f"{clone.name}_mut"
            
        elif mutation_type == 'operator':
            # Replace an operator in the implementation
            replacements = [
                ('+', '-'), ('-', '+'), ('*', '/'), ('/', '*'),
                ('>', '<'), ('<', '>'), ('and', 'or'), ('or', 'and')
            ]
            for old, new in replacements:
                if old in clone.implementation:
                    clone.implementation = clone.implementation.replace(old, new, 1)
                    clone.name = f"{clone.name}_op"
                    break
        
        elif mutation_type == 'structure':
            # Structural mutation - add a wrapper
            wrappers = [
                "abs(({}))",
                "max(0, ({}))",
                "min(1, ({}))",
                "({}) ** 2",
                "1 / (1 + abs({}))"
            ]
            wrapper = random.choice(wrappers)
            old_impl = clone.implementation
            result_part = f"({old_impl})(*args)"
            clone.implementation = f"lambda *args: {wrapper.format(result_part)}"
            clone.name = f"{clone.name}_wrap"
        
        self.primitives[clone.id] = clone
        self.created_count += 1
        
        return clone
    
    def crossover(self, p1: Primitive, p2: Primitive) -> Primitive:
        try:
                """Create offspring from two primitives."""
                # Take structure from one, constants from another
                child = Primitive(
                    name=f"child_{p1.name[:5]}_{p2.name[:5]}",
                    arity=random.choice([p1.arity, p2.arity]),
                    implementation=p1.implementation if random.random() < 0.5 else p2.implementation,
                    generation=max(p1.generation, p2.generation) + 1,
                    parent_ids=[p1.id, p2.id]
                )
        
                # Maybe modify the implementation
                if random.random() < 0.3:
                    child = self.mutate(child)
        
                self.primitives[child.id] = child
                return child
        except Exception as e:
            raise  # Extended with error handling
    
    def evolve(self, fitness_scores: Dict[str, float], n_offspring: int = 5) -> List[Primitive]:
        """Evolve the primitive population."""
        # Update fitness
        for pid, fitness in fitness_scores.items():
            if pid in self.primitives:
                p = self.primitives[pid]
                p.fitness = 0.9 * p.fitness + 0.1 * fitness
        
        # Select parents (tournament)
        def tournament(k: int = 3) -> Primitive:
            candidates = random.sample(list(self.primitives.values()), min(k, len(self.primitives)))
            return max(candidates, key=lambda p: p.fitness)
        
        offspring = []
        
        for _ in range(n_offspring):
            if random.random() < 0.4:
                # Composition
                parent_ids = [tournament().id for _ in range(random.randint(2, 3))]
                combo = random.choice(['chain', 'parallel', 'conditional'])
                child = self.create_composed(parent_ids, combo)
                if child:
                    offspring.append(child)
            
            elif random.random() < 0.7:
                # Mutation
                parent = tournament()
                child = self.mutate(parent)
                offspring.append(child)
            
            else:
                # Crossover
                p1, p2 = tournament(), tournament()
                child = self.crossover(p1, p2)
                offspring.append(child)
        
        return offspring
    
    def get_random(self, arity: Optional[int] = None) -> Optional[Primitive]:
        """Get a random primitive, optionally filtered by arity."""
        candidates = list(self.primitives.values())
        if arity is not None:
            candidates = [p for p in candidates if p.arity == arity]
        return random.choice(candidates) if candidates else None
    
    def get_stats(self) -> Dict:
        return {
            'total_primitives': len(self.primitives),
            'created_count': self.created_count,
            'by_generation': self._count_by_generation(),
            'avg_fitness': sum(p.fitness for p in self.primitives.values()) / max(1, len(self.primitives)),
            'categories': {cat: len(pids) for cat, pids in self.primitives_by_category.items()}
        }
    
    def _count_by_generation(self) -> Dict[int, int]:
        counts = {}
        for p in self.primitives.values():
            counts[p.generation] = counts.get(p.generation, 0) + 1
        return counts


# =============================================================================
# EVOLVABLE FITNESS FUNCTIONS
# =============================================================================

@dataclass
class FitnessComponent:
    """A component of a fitness function."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:8])
    name: str = ""
    
    # What this component measures
    metric: str = ""  # 'novelty', 'goal_achievement', 'pattern_match', 'efficiency', etc.
    
    # Weight in overall fitness
    weight: float = 1.0
    
    # The computation
    implementation: str = "lambda state: state.get('fitness', 0)"
    
    # Evolution
    generation: int = 0
    mutations: int = 0
    
    def evaluate(self, state: Dict) -> float:
        """Evaluate this component on a state."""
        try:
            fn = eval(self.implementation)
            return fn(state) * self.weight
        except:
            return 0.0
    
    def clone(self) -> 'FitnessComponent':
        return FitnessComponent(
            id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:8],
            name=f"{self.name}_clone",
            metric=self.metric,
            weight=self.weight,
            implementation=self.implementation,
            generation=self.generation + 1
        )


class EvolvableFitness:
    """
    A fitness function that can evolve.
    
    Instead of a fixed fitness function, the system can discover
    what "fitness" even means.
    """
    
    def __init__(self):
        self.components: Dict[str, FitnessComponent] = {}
        self.history: List[Tuple[Dict, float]] = []  # (weights, meta_fitness)
        
        # Initialize with base components
        self._initialize_base()
    
    def _initialize_base(self):
        """Create base fitness components."""
        base_components = [
            ("novelty", "lambda s: s.get('novelty_rate', 0)"),
            ("goals", "lambda s: s.get('goals_satisfied', 0) / max(1, s.get('goals_total', 1))"),
            ("patterns", "lambda s: s.get('pattern_matches', 0) / max(1, s.get('pattern_attempts', 1))"),
            ("efficiency", "lambda s: 1.0 / (1.0 + s.get('steps', 1))"),
            ("complexity", "lambda s: min(1.0, s.get('genome_size', 0) / 100)"),
            ("stability", "lambda s: 1.0 - s.get('variance', 0)"),
            ("growth", "lambda s: max(0, s.get('fitness_delta', 0))"),
        ]
        
        for name, impl in base_components:
            comp = FitnessComponent(
                id=f"base_{name}",
                name=name,
                metric=name,
                weight=1.0 / len(base_components),
                implementation=impl
            )
            self.components[comp.id] = comp
    
    def evaluate(self, state: Dict) -> float:
        """Evaluate fitness using all components."""
        total = 0.0
        for comp in self.components.values():
            total += comp.evaluate(state)
        return total
    
    def evolve(self, meta_fitness: float):
        """
        Evolve the fitness function based on meta-fitness.
        
        Meta-fitness = how well is the current fitness function
        helping the system improve?
        """
        # Record current configuration
        weights = {cid: c.weight for cid, c in self.components.items()}
        self.history.append((weights, meta_fitness))
        
        # Adjust weights based on component contribution
        # This is a simple gradient-free optimization
        for comp in self.components.values():
            # Random perturbation
            if random.random() < 0.3:
                comp.weight *= random.uniform(0.8, 1.2)
                comp.weight = max(0.01, min(2.0, comp.weight))
        
        # Normalize weights
        total_weight = sum(c.weight for c in self.components.values())
        for comp in self.components.values():
            comp.weight /= total_weight
        
        # Occasionally create new components
        if random.random() < 0.1:
            self._create_new_component()
        
        # Occasionally remove low-weight components
        if len(self.components) > 10 and random.random() < 0.1:
            worst = min(self.components.values(), key=lambda c: c.weight)
            if worst.id not in [f"base_{c}" for c in ['novelty', 'goals']]:  # Protect core
                del self.components[worst.id]
    
    def _create_new_component(self):
        """Create a novel fitness component."""
        # Combine existing metrics in new ways
        existing = list(self.components.values())
        if len(existing) < 2:
            return
        
        c1, c2 = random.sample(existing, 2)
        
        combination = random.choice(['multiply', 'ratio', 'difference', 'threshold'])
        
        if combination == 'multiply':
            impl = f"lambda s: ({c1.implementation})(s) * ({c2.implementation})(s)"
            name = f"{c1.name}_times_{c2.name}"
        elif combination == 'ratio':
            impl = f"lambda s: ({c1.implementation})(s) / max(0.01, ({c2.implementation})(s))"
            name = f"{c1.name}_per_{c2.name}"
        elif combination == 'difference':
            impl = f"lambda s: abs(({c1.implementation})(s) - ({c2.implementation})(s))"
            name = f"{c1.name}_diff_{c2.name}"
        else:
            thresh = random.uniform(0.3, 0.7)
            impl = f"lambda s: 1.0 if ({c1.implementation})(s) > {thresh} else 0.0"
            name = f"{c1.name}_thresh"
        
        new_comp = FitnessComponent(
            name=name,
            metric=f"combined_{c1.metric}_{c2.metric}",
            weight=0.1,
            implementation=impl,
            generation=max(c1.generation, c2.generation) + 1
        )
        
        self.components[new_comp.id] = new_comp
    
    def get_stats(self) -> Dict:
        return {
            'num_components': len(self.components),
            'weights': {c.name: c.weight for c in self.components.values()},
            'history_length': len(self.history)
        }


# =============================================================================
# EVOLVABLE EVOLUTION PARAMETERS
# =============================================================================

@dataclass
class EvolutionParams:
    """
    Parameters that control evolution - which themselves evolve.
    
    This is meta-evolution: the parameters of evolution are 
    themselves subject to selection.
    """
    # Mutation rates
    mutation_rate: float = 0.1
    mutation_strength: float = 0.5
    
    # Selection parameters
    selection_pressure: float = 0.5  # 0 = random, 1 = greedy
    tournament_size: int = 3
    elitism_rate: float = 0.1
    
    # Population dynamics
    reproduction_rate: float = 0.3
    death_rate: float = 0.2
    
    # Crossover parameters
    crossover_rate: float = 0.5
    crossover_points: int = 1
    
    # Diversity maintenance
    diversity_weight: float = 0.3
    niche_radius: float = 0.1
    
    # Innovation parameters
    new_gene_rate: float = 0.05
    gene_deletion_rate: float = 0.02
    
    # Self-reference
    param_mutation_rate: float = 0.1  # Rate at which THESE parameters mutate
    
    def mutate(self) -> 'EvolutionParams':
        """Mutate the evolution parameters themselves."""
        clone = EvolutionParams(
            mutation_rate=self.mutation_rate,
            mutation_strength=self.mutation_strength,
            selection_pressure=self.selection_pressure,
            tournament_size=self.tournament_size,
            elitism_rate=self.elitism_rate,
            reproduction_rate=self.reproduction_rate,
            death_rate=self.death_rate,
            crossover_rate=self.crossover_rate,
            crossover_points=self.crossover_points,
            diversity_weight=self.diversity_weight,
            niche_radius=self.niche_radius,
            new_gene_rate=self.new_gene_rate,
            gene_deletion_rate=self.gene_deletion_rate,
            param_mutation_rate=self.param_mutation_rate
        )
        
        # Each parameter has a chance to mutate
        if random.random() < self.param_mutation_rate:
            clone.mutation_rate = max(0.01, min(0.9, self.mutation_rate + random.gauss(0, 0.1)))
        if random.random() < self.param_mutation_rate:
            clone.mutation_strength = max(0.1, min(2.0, self.mutation_strength + random.gauss(0, 0.2)))
        if random.random() < self.param_mutation_rate:
            clone.selection_pressure = max(0.0, min(1.0, self.selection_pressure + random.gauss(0, 0.1)))
        if random.random() < self.param_mutation_rate:
            clone.tournament_size = max(2, min(10, self.tournament_size + random.randint(-1, 1)))
        if random.random() < self.param_mutation_rate:
            clone.elitism_rate = max(0.0, min(0.5, self.elitism_rate + random.gauss(0, 0.05)))
        if random.random() < self.param_mutation_rate:
            clone.reproduction_rate = max(0.1, min(0.9, self.reproduction_rate + random.gauss(0, 0.1)))
        if random.random() < self.param_mutation_rate:
            clone.crossover_rate = max(0.0, min(1.0, self.crossover_rate + random.gauss(0, 0.1)))
        if random.random() < self.param_mutation_rate:
            clone.diversity_weight = max(0.0, min(1.0, self.diversity_weight + random.gauss(0, 0.1)))
        if random.random() < self.param_mutation_rate:
            clone.new_gene_rate = max(0.0, min(0.3, self.new_gene_rate + random.gauss(0, 0.02)))
        if random.random() < self.param_mutation_rate * 0.5:  # Rarer
            clone.param_mutation_rate = max(0.01, min(0.5, self.param_mutation_rate + random.gauss(0, 0.05)))
        
        return clone
    
    def to_dict(self) -> Dict:
        return {
            'mutation_rate': self.mutation_rate,
            'mutation_strength': self.mutation_strength,
            'selection_pressure': self.selection_pressure,
            'tournament_size': self.tournament_size,
            'elitism_rate': self.elitism_rate,
            'reproduction_rate': self.reproduction_rate,
            'death_rate': self.death_rate,
            'crossover_rate': self.crossover_rate,
            'diversity_weight': self.diversity_weight,
            'new_gene_rate': self.new_gene_rate,
            'param_mutation_rate': self.param_mutation_rate
        }


# =============================================================================
# META-EVOLUTION ENGINE
# =============================================================================

class MetaEvolutionEngine:
    """
    The meta-evolution engine.
    
    This manages the evolution of evolution itself:
    - Primitives evolve (new building blocks emerge)
    - Fitness functions evolve (what "good" means changes)
    - Evolution parameters evolve (how evolution works changes)
    
    Together, this creates genuine open-endedness.
    """
    
    def __init__(self):
        # Evolvable components
        self.primitives = PrimitiveFactory()
        self.fitness = EvolvableFitness()
        self.params = EvolutionParams()
        
        # Parameter population (multiple parameter sets competing)
        self.param_population: List[Tuple[EvolutionParams, float]] = [(self.params, 0.5)]
        
        # History
        self.generation: int = 0
        self.primitive_history: List[Dict] = []
        self.fitness_history: List[Dict] = []
        self.param_history: List[Dict] = []
        
        # Meta-metrics
        self.improvement_rate: float = 0.0
        self.innovation_rate: float = 0.0
        self.diversity_index: float = 0.0
    
    def step(self, system_state: Dict) -> Dict:
        """
        One step of meta-evolution.
        
        system_state contains metrics from the main AEGIS-2 system.
        """
        self.generation += 1
        
        results = {
            'generation': self.generation,
            'events': [],
            'changes': {}
        }
        
        # === 1. Evaluate current fitness function ===
        current_fitness = self.fitness.evaluate(system_state)
        
        # === 2. Compute meta-fitness (is our fitness function good?) ===
        meta_fitness = self._compute_meta_fitness(system_state, current_fitness)
        
        # === 3. Evolve primitives ===
        primitive_fitness = self._compute_primitive_fitness(system_state)
        new_primitives = self.primitives.evolve(primitive_fitness)
        
        if new_primitives:
            results['events'].append({
                'type': 'primitives_evolved',
                'count': len(new_primitives),
                'new_names': [p.name for p in new_primitives[:3]]
            })
        
        # === 4. Evolve fitness function ===
        self.fitness.evolve(meta_fitness)
        
        # === 5. Evolve evolution parameters ===
        self._evolve_params(meta_fitness)
        
        # === 6. Update meta-metrics ===
        self._update_meta_metrics(system_state)
        
        # === 7. Record history ===
        self._record_history()
        
        results['changes'] = {
            'primitives': len(self.primitives.primitives),
            'fitness_components': len(self.fitness.components),
            'param_population': len(self.param_population),
            'meta_fitness': meta_fitness
        }
        
        return results
    
    def _compute_meta_fitness(self, state: Dict, fitness: float) -> float:
        """
        Compute meta-fitness: how good is our fitness function?
        
        A good fitness function:
        - Correlates with improvement over time
        - Maintains diversity
        - Enables innovation
        """
        components = []
        
        # Correlation with improvement
        if len(self.fitness_history) > 1:
            recent_fitnesses = [h.get('fitness', 0) for h in self.fitness_history[-10:]]
            if len(recent_fitnesses) > 1:
                improvement = recent_fitnesses[-1] - recent_fitnesses[0]
                components.append(max(0, improvement) * 2)
        
        # Diversity maintenance
        components.append(self.diversity_index)
        
        # Innovation rate
        components.append(self.innovation_rate)
        
        # Stability (not changing too wildly)
        if len(self.fitness_history) > 2:
            recent = [h.get('fitness', 0) for h in self.fitness_history[-5:]]
            variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)
            stability = 1.0 / (1.0 + variance * 10)
            components.append(stability)
        
        if components:
            return sum(components) / len(components)
        return 0.5
    
    def _compute_primitive_fitness(self, state: Dict) -> Dict[str, float]:
        """Compute fitness for each primitive based on usage and success."""
        fitness = {}
        
        for pid, prim in self.primitives.primitives.items():
            # Base fitness on usage
            usage_fitness = min(1.0, prim.usage_count / 100)
            
            # Success rate
            if prim.usage_count > 0:
                success_rate = prim.success_count / prim.usage_count
            else:
                success_rate = 0.5  # Prior for unused
            
            # Recency bonus (newer primitives get a chance)
            recency = 1.0 / (1.0 + prim.generation * 0.1)
            
            fitness[pid] = 0.4 * usage_fitness + 0.4 * success_rate + 0.2 * recency
        
        return fitness
    
    def _evolve_params(self, meta_fitness: float):
        """Evolve the evolution parameters."""
        # Add meta-fitness to current params
        self.param_population = [(p, 0.9 * f + 0.1 * meta_fitness) 
                                  for p, f in self.param_population]
        
        # Select best
        self.param_population.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top half
        self.param_population = self.param_population[:max(1, len(self.param_population) // 2)]
        
        # Create offspring
        while len(self.param_population) < 5:
            parent, parent_fitness = random.choice(self.param_population)
            child = parent.mutate()
            self.param_population.append((child, parent_fitness * 0.9))
        
        # Use best params
        self.params = self.param_population[0][0]
    
    def _update_meta_metrics(self, state: Dict):
        """Update meta-level metrics."""
        # Improvement rate
        if len(self.fitness_history) > 5:
            recent = [h.get('fitness', 0) for h in self.fitness_history[-5:]]
            older = [h.get('fitness', 0) for h in self.fitness_history[-10:-5]]
            if older:
                self.improvement_rate = (sum(recent)/len(recent)) / max(0.01, sum(older)/len(older)) - 1
        
        # Innovation rate (new primitives per generation)
        if self.generation > 0:
            self.innovation_rate = self.primitives.created_count / self.generation
        
        # Diversity index
        if self.primitives.primitives:
            generations = [p.generation for p in self.primitives.primitives.values()]
            unique_gens = len(set(generations))
            self.diversity_index = unique_gens / max(1, self.generation)
    
    def _record_history(self):
        """Record current state for history."""
        self.primitive_history.append(self.primitives.get_stats())
        self.fitness_history.append({
            'fitness': self.fitness.evaluate({'dummy': 0}),
            'components': len(self.fitness.components)
        })
        self.param_history.append(self.params.to_dict())
        
        # Limit history size
        max_history = 1000
        if len(self.primitive_history) > max_history:
            self.primitive_history = self.primitive_history[-max_history:]
        if len(self.fitness_history) > max_history:
            self.fitness_history = self.fitness_history[-max_history:]
        if len(self.param_history) > max_history:
            self.param_history = self.param_history[-max_history:]
    
    def get_primitive(self, arity: Optional[int] = None) -> Optional[Primitive]:
        """Get a primitive for use in the main system."""
        return self.primitives.get_random(arity)
    
    def evaluate_fitness(self, state: Dict) -> float:
        """Evaluate fitness using the evolved fitness function."""
        return self.fitness.evaluate(state)
    
    def get_params(self) -> EvolutionParams:
        """Get current evolution parameters."""
        return self.params
    
    def get_stats(self) -> Dict:
        return {
            'generation': self.generation,
            'primitives': self.primitives.get_stats(),
            'fitness': self.fitness.get_stats(),
            'params': self.params.to_dict(),
            'meta_metrics': {
                'improvement_rate': self.improvement_rate,
                'innovation_rate': self.innovation_rate,
                'diversity_index': self.diversity_index
            },
            'param_population_size': len(self.param_population)
        }
    
    def to_dict(self) -> Dict:
        return {
            'generation': self.generation,
            'primitives': {pid: p.to_dict() for pid, p in self.primitives.primitives.items()},
            'fitness_components': {cid: c.to_dict() if hasattr(c, 'to_dict') else {'weight': c.weight} 
                                   for cid, c in self.fitness.components.items()},
            'params': self.params.to_dict(),
            'meta_metrics': {
                'improvement_rate': self.improvement_rate,
                'innovation_rate': self.innovation_rate,
                'diversity_index': self.diversity_index
            }
        }


def demo():
    """Demonstrate meta-evolution."""
    print("=" * 70)
    print("   AEGIS-2 Meta-Evolution: Evolving Evolution Itself")
    print("=" * 70)
    print()
    
    engine = MetaEvolutionEngine()
    
    print(f"Initial state:")
    print(f"  Primitives: {len(engine.primitives.primitives)}")
    print(f"  Fitness components: {len(engine.fitness.components)}")
    print()
    
    # Simulate system state evolution
    print("Running 50 meta-evolution cycles...")
    
    for i in range(50):
        # Simulated system state
        state = {
            'novelty_rate': 0.3 + 0.01 * i + random.gauss(0, 0.05),
            'goals_satisfied': random.randint(0, 10),
            'goals_total': 20,
            'pattern_matches': random.randint(5, 20),
            'pattern_attempts': 30,
            'steps': i + 1,
            'genome_size': 10 + i // 5,
            'variance': max(0, 0.3 - 0.005 * i),
            'fitness_delta': random.gauss(0.01, 0.02)
        }
        
        result = engine.step(state)
        
        if result['events']:
            for e in result['events']:
                print(f"  Gen {i}: {e['type']} - {e.get('count', '')} {e.get('new_names', '')}")
    
    print()
    print("=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    
    stats = engine.get_stats()
    
    print(f"""
  Meta-Evolution Generation: {stats['generation']}
  
  Primitives:
    Total: {stats['primitives']['total_primitives']}
    Created: {stats['primitives']['created_count']}
    By generation: {stats['primitives']['by_generation']}
    
  Fitness Function:
    Components: {stats['fitness']['num_components']}
    Weights: {dict(list(stats['fitness']['weights'].items())[:5])}...
    
  Evolution Parameters:
    Mutation rate: {stats['params']['mutation_rate']:.4f}
    Selection pressure: {stats['params']['selection_pressure']:.4f}
    Diversity weight: {stats['params']['diversity_weight']:.4f}
    Param mutation rate: {stats['params']['param_mutation_rate']:.4f}
    
  Meta-Metrics:
    Improvement rate: {stats['meta_metrics']['improvement_rate']:.4f}
    Innovation rate: {stats['meta_metrics']['innovation_rate']:.4f}
    Diversity index: {stats['meta_metrics']['diversity_index']:.4f}
""")
    
    return engine


if __name__ == "__main__":
    demo()
