"""
Representation Evolution: Evolve the Representation Itself

Instead of evolving WITHIN a fixed representation, evolve THE representation.

This is the key to true open-endedness:
- New types can be invented
- New operators can be discovered
- New abstraction levels can emerge

Current limitation: We evolve programs composed of fixed primitives.
True open-endedness: The primitives themselves evolve.
"""

import random
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple, Set


@dataclass
class CustomType:
    """A user-defined type invented by the system."""
    type_id: str
    name: str
    base_types: List[str] = field(default_factory=list)  # Composed from what?
    properties: Dict[str, Any] = field(default_factory=dict)
    operations: List[str] = field(default_factory=list)  # What can you do with it?

    # Evolution tracking
    invented_at: int = 0  # Generation
    usage_count: int = 0
    fitness_contribution: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'type_id': self.type_id,
            'name': self.name,
            'base_types': self.base_types,
            'properties': self.properties,
            'operations': self.operations,
            'invented_at': self.invented_at,
            'usage_count': self.usage_count,
            'fitness_contribution': self.fitness_contribution
        }


@dataclass
class CustomOperator:
    """A user-defined operator invented by the system."""
    operator_id: str
    name: str
    arity: int
    implementation: Optional[Callable] = None  # Actual function
    semantic_description: str = ""

    # Composition (built from what primitives?)
    composed_from: List[str] = field(default_factory=list)

    # Evolution tracking
    invented_at: int = 0
    usage_count: int = 0
    fitness_contribution: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'operator_id': self.operator_id,
            'name': self.name,
            'arity': self.arity,
            'semantic_description': self.semantic_description,
            'composed_from': self.composed_from,
            'invented_at': self.invented_at,
            'usage_count': self.usage_count,
            'fitness_contribution': self.fitness_contribution
        }


@dataclass
class AbstractionLevel:
    """A new level of abstraction discovered by the system."""
    level_id: str
    level_number: int  # 0=primitive, 1=composed, 2=meta, ...
    types_at_level: List[str] = field(default_factory=list)
    operators_at_level: List[str] = field(default_factory=list)

    # What does this level abstract?
    abstracts_levels: List[int] = field(default_factory=list)

    # Evolution tracking
    created_at: int = 0
    usage_count: int = 0

    def to_dict(self) -> Dict:
        return {
            'level_id': self.level_id,
            'level_number': self.level_number,
            'types_at_level': self.types_at_level,
            'operators_at_level': self.operators_at_level,
            'abstracts_levels': self.abstracts_levels,
            'created_at': self.created_at,
            'usage_count': self.usage_count
        }


class TypeInventor:
    """
    Invents new types by composition and abstraction.

    Example: Invent "Color" type composed of (R, G, B) floats.
    Example: Invent "Pattern" type that represents recurring structures.
    """

    def __init__(self):
        self.types: Dict[str, CustomType] = {}
        self.type_counter = 0

        # Start with primitives
        self._initialize_primitives()

    def _initialize_primitives(self):
        """Initialize primitive types."""
        primitives = ['float', 'int', 'bool', 'string', 'list', 'dict']
        for prim in primitives:
            type_id = f"primitive_{prim}"
            self.types[type_id] = CustomType(
                type_id=type_id,
                name=prim,
                base_types=[],
                invented_at=0
            )

    def invent_composite_type(
        self,
        base_types: List[str],
        generation: int
    ) -> CustomType:
        """
        Invent a new type by composing existing types.

        Example: Compose [float, float, float] into "Vector3D"
        """
        self.type_counter += 1
        type_id = f"composite_{self.type_counter}"

        # Generate name from composition
        name = f"Composite_{'_'.join(base_types)}"

        # Infer properties
        properties = {
            'components': base_types,
            'size': len(base_types)
        }

        # Infer operations
        operations = []
        if all(t.startswith('primitive_float') or t.startswith('primitive_int') for t in base_types):
            operations = ['add', 'multiply', 'dot_product', 'norm']

        new_type = CustomType(
            type_id=type_id,
            name=name,
            base_types=base_types,
            properties=properties,
            operations=operations,
            invented_at=generation
        )

        self.types[type_id] = new_type

        return new_type

    def invent_abstraction_type(
        self,
        concrete_types: List[str],
        shared_properties: Dict[str, Any],
        generation: int
    ) -> CustomType:
        """
        Invent a new type by abstracting common properties.

        Example: Abstract "Circle", "Square", "Triangle" into "Shape"
        """
        self.type_counter += 1
        type_id = f"abstract_{self.type_counter}"

        name = f"Abstract_{self.type_counter}"

        new_type = CustomType(
            type_id=type_id,
            name=name,
            base_types=concrete_types,
            properties=shared_properties,
            invented_at=generation
        )

        self.types[type_id] = new_type

        return new_type

    def invent_pattern_type(
        self,
        pattern_signature: str,
        generation: int
    ) -> CustomType:
        """
        Invent a type representing a recurring pattern.

        Example: Detect that certain structures always appear together,
        create a type to represent that pattern.
        """
        self.type_counter += 1
        type_id = f"pattern_{hashlib.md5(pattern_signature.encode()).hexdigest()[:8]}"

        new_type = CustomType(
            type_id=type_id,
            name=f"Pattern_{self.type_counter}",
            properties={'signature': pattern_signature},
            invented_at=generation
        )

        self.types[type_id] = new_type

        return new_type

    def get_type(self, type_id: str) -> Optional[CustomType]:
        """Get type by ID."""
        return self.types.get(type_id)

    def get_active_types(self, min_usage: int = 1) -> List[CustomType]:
        """Get types that are actually being used."""
        return [
            t for t in self.types.values()
            if t.usage_count >= min_usage
        ]


class OperatorDiscovery:
    """
    Discovers new operators by composition and abstraction.

    Example: Discover "normalize" operator from composition of (divide, sqrt, sum, square).
    Example: Discover "convolve" operator from recurring pattern.
    """

    def __init__(self):
        self.operators: Dict[str, CustomOperator] = {}
        self.operator_counter = 0

        # Primitives
        self._initialize_primitives()

    def _initialize_primitives(self):
        """Initialize primitive operators."""
        primitives = [
            ('add', 2, lambda a, b: a + b),
            ('multiply', 2, lambda a, b: a * b),
            ('compare', 2, lambda a, b: 1.0 if a > b else 0.0)
        ]

        for name, arity, impl in primitives:
            op_id = f"primitive_{name}"
            self.operators[op_id] = CustomOperator(
                operator_id=op_id,
                name=name,
                arity=arity,
                implementation=impl,
                invented_at=0
            )

    def discover_composed_operator(
        self,
        component_operators: List[str],
        arity: int,
        generation: int
    ) -> CustomOperator:
        """
        Discover new operator by composing existing ones.

        Example: Compose [square, sum, sqrt] into "norm"
        """
        self.operator_counter += 1
        op_id = f"composed_{self.operator_counter}"

        name = f"Composed_{'_'.join(component_operators)}"

        new_operator = CustomOperator(
            operator_id=op_id,
            name=name,
            arity=arity,
            composed_from=component_operators,
            semantic_description=f"Composition of {component_operators}",
            invented_at=generation
        )

        self.operators[op_id] = new_operator

        return new_operator

    def discover_abstracted_operator(
        self,
        similar_operators: List[str],
        abstraction: str,
        generation: int
    ) -> CustomOperator:
        """
        Discover operator by abstracting similar patterns.

        Example: Abstract various filtering operations into general "filter" operator.
        """
        self.operator_counter += 1
        op_id = f"abstract_{self.operator_counter}"

        new_operator = CustomOperator(
            operator_id=op_id,
            name=f"Abstract_{abstraction}",
            arity=2,  # Most abstractions are binary
            composed_from=similar_operators,
            semantic_description=f"Abstraction of {similar_operators}",
            invented_at=generation
        )

        self.operators[op_id] = new_operator

        return new_operator

    def discover_from_pattern(
        self,
        pattern_code: str,
        generation: int
    ) -> CustomOperator:
        """
        Discover operator from recurring code pattern.

        Example: Detect that certain sequence of operations keeps appearing,
        create an operator for it.
        """
        self.operator_counter += 1
        op_id = f"pattern_{hashlib.md5(pattern_code.encode()).hexdigest()[:8]}"

        new_operator = CustomOperator(
            operator_id=op_id,
            name=f"PatternOp_{self.operator_counter}",
            arity=len(pattern_code.split()) // 2,  # Rough estimate
            semantic_description=f"Pattern: {pattern_code[:50]}...",
            invented_at=generation
        )

        self.operators[op_id] = new_operator

        return new_operator

    def get_operator(self, op_id: str) -> Optional[CustomOperator]:
        """Get operator by ID."""
        return self.operators.get(op_id)

    def get_active_operators(self, min_usage: int = 1) -> List[CustomOperator]:
        """Get operators that are actually being used."""
        return [
            op for op in self.operators.values()
            if op.usage_count >= min_usage
        ]


class AbstractionLevelCreator:
    """
    Creates new levels of abstraction.

    Level 0: Primitives (add, multiply, etc.)
    Level 1: Composed operations (normalize, convolve, etc.)
    Level 2: Meta-operations (map, fold, etc.)
    Level 3: Meta-meta-operations (???)

    The key insight: Each level operates on entities from the level below.
    """

    def __init__(self):
        self.levels: Dict[int, AbstractionLevel] = {}
        self.max_level = 0

        # Initialize level 0 (primitives)
        self._initialize_primitive_level()

    def _initialize_primitive_level(self):
        """Create level 0 with primitives."""
        level_0 = AbstractionLevel(
            level_id="level_0",
            level_number=0,
            types_at_level=['primitive_float', 'primitive_int'],
            operators_at_level=['primitive_add', 'primitive_multiply'],
            created_at=0
        )
        self.levels[0] = level_0

    def create_next_level(
        self,
        previous_level: int,
        generation: int
    ) -> AbstractionLevel:
        """
        Create a new abstraction level above the previous one.

        The new level operates on constructs from the previous level.
        """
        new_level_number = previous_level + 1

        if new_level_number > self.max_level:
            self.max_level = new_level_number

        level = AbstractionLevel(
            level_id=f"level_{new_level_number}",
            level_number=new_level_number,
            abstracts_levels=[previous_level],
            created_at=generation
        )

        self.levels[new_level_number] = level

        return level

    def add_type_to_level(self, level_number: int, type_id: str):
        """Add a type to a level."""
        if level_number in self.levels:
            if type_id not in self.levels[level_number].types_at_level:
                self.levels[level_number].types_at_level.append(type_id)

    def add_operator_to_level(self, level_number: int, operator_id: str):
        """Add an operator to a level."""
        if level_number in self.levels:
            if operator_id not in self.levels[level_number].operators_at_level:
                self.levels[level_number].operators_at_level.append(operator_id)

    def get_level(self, level_number: int) -> Optional[AbstractionLevel]:
        """Get abstraction level."""
        return self.levels.get(level_number)

    def get_highest_level(self) -> int:
        """Get the highest abstraction level achieved."""
        return self.max_level


class RepresentationEvolution:
    """
    Main class for representation evolution.

    Coordinates type invention, operator discovery, and abstraction level creation.
    """

    def __init__(self):
        self.type_inventor = TypeInventor()
        self.operator_discovery = OperatorDiscovery()
        self.abstraction_creator = AbstractionLevelCreator()

        self.generation = 0
        self.evolution_history: List[Dict[str, Any]] = []

    def evolve(self, fitness_landscape: Dict[str, float]) -> Dict[str, Any]:
        """
        Evolve the representation based on fitness landscape.

        Args:
            fitness_landscape: Mapping of type/operator IDs to fitness contributions

        Returns:
            Summary of representation changes
        """
        self.generation += 1

        changes = {
            'new_types': [],
            'new_operators': [],
            'new_levels': [],
            'generation': self.generation
        }

        # Update usage statistics
        for type_id, fitness in fitness_landscape.items():
            type_obj = self.type_inventor.get_type(type_id)
            if type_obj:
                type_obj.usage_count += 1
                type_obj.fitness_contribution += fitness

            op_obj = self.operator_discovery.get_operator(type_id)
            if op_obj:
                op_obj.usage_count += 1
                op_obj.fitness_contribution += fitness

        # Invent new types (probabilistic)
        if random.random() < 0.1:  # 10% chance
            # Compose existing types
            active_types = [t.type_id for t in self.type_inventor.get_active_types()]
            if len(active_types) >= 2:
                base_types = random.sample(active_types, random.randint(2, min(4, len(active_types))))
                new_type = self.type_inventor.invent_composite_type(base_types, self.generation)
                changes['new_types'].append(new_type.to_dict())

        # Discover new operators (probabilistic)
        if random.random() < 0.15:  # 15% chance
            # Compose existing operators
            active_ops = [op.operator_id for op in self.operator_discovery.get_active_operators()]
            if len(active_ops) >= 2:
                components = random.sample(active_ops, random.randint(2, min(3, len(active_ops))))
                arity = random.randint(1, 3)
                new_op = self.operator_discovery.discover_composed_operator(
                    components, arity, self.generation
                )
                changes['new_operators'].append(new_op.to_dict())

        # Create new abstraction levels (rare)
        if random.random() < 0.05:  # 5% chance
            # Create level above current max
            max_level = self.abstraction_creator.get_highest_level()
            new_level = self.abstraction_creator.create_next_level(max_level, self.generation)
            changes['new_levels'].append(new_level.to_dict())

        self.evolution_history.append(changes)

        return changes

    def get_representation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the evolved representation."""
        return {
            'generation': self.generation,
            'total_types': len(self.type_inventor.types),
            'active_types': len(self.type_inventor.get_active_types()),
            'total_operators': len(self.operator_discovery.operators),
            'active_operators': len(self.operator_discovery.get_active_operators()),
            'abstraction_levels': self.abstraction_creator.get_highest_level() + 1,
            'evolution_events': len(self.evolution_history)
        }

    def get_type(self, type_id: str) -> Optional[CustomType]:
        """Get type by ID."""
        return self.type_inventor.get_type(type_id)

    def get_operator(self, operator_id: str) -> Optional[CustomOperator]:
        """Get operator by ID."""
        return self.operator_discovery.get_operator(operator_id)

    def get_all_types(self) -> List[CustomType]:
        """Get all types."""
        return list(self.type_inventor.types.values())

    def get_all_operators(self) -> List[CustomOperator]:
        """Get all operators."""
        return list(self.operator_discovery.operators.values())
