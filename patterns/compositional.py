"""
AEGIS-2 Compositional Patterns: Pattern Algebra for Unbounded Complexity

Key insight: Real emergence requires COMPOSITIONAL EXPLOSION.
Small primitives combining into unbounded complexity.

This module implements:
- Patterns as first-class composable objects
- Pattern operators (sequence, choice, repetition, nesting)
- Pattern transformations (abstraction, specialization, analogy)
- Recursive pattern structures (patterns of patterns of patterns...)
- Pattern evolution through recombination
"""

import random
import hashlib
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from datetime import datetime
import json
from abc import ABC, abstractmethod


class PatternOperator(Enum):
    """Operators for combining patterns."""
    # Basic combinators
    SEQ = "seq"          # A then B
    ALT = "alt"          # A or B
    PAR = "par"          # A and B simultaneously
    OPT = "opt"          # A optionally
    REP = "rep"          # A repeated
    
    # Structural
    NEST = "nest"        # A contains B
    WRAP = "wrap"        # B around A
    BIND = "bind"        # A bound to variable
    
    # Transformational
    MAP = "map"          # Transform each element
    FILTER = "filter"    # Select matching elements
    FOLD = "fold"        # Reduce to single value
    
    # Meta
    META = "meta"        # Pattern about patterns
    ANTI = "anti"        # Negation of pattern
    DIFF = "diff"        # Difference between patterns
    INTERSECT = "intersect"  # Common elements


@dataclass
class Slot:
    """A variable slot in a pattern."""
    name: str
    slot_type: str = "any"  # any, number, string, pattern, list
    constraints: List[Any] = field(default_factory=list)
    default: Any = None
    bound_value: Any = None
    
    def matches(self, value: Any) -> bool:
        """Check if a value matches this slot's constraints."""
        if self.slot_type == "number":
            if not isinstance(value, (int, float)):
                return False
        elif self.slot_type == "string":
            if not isinstance(value, str):
                return False
        elif self.slot_type == "pattern":
            if not isinstance(value, ComposablePattern):
                return False
        elif self.slot_type == "list":
            if not isinstance(value, (list, tuple)):
                return False
        
        for constraint in self.constraints:
            if callable(constraint):
                if not constraint(value):
                    return False
            elif isinstance(constraint, tuple) and len(constraint) == 2:
                # Range constraint
                if not (constraint[0] <= value <= constraint[1]):
                    return False
        
        return True
    
    def bind(self, value: Any) -> bool:
        try:
                """Attempt to bind a value to this slot."""
                if self.matches(value):
                    self.bound_value = value
                    return True
                return False
        except Exception as e:
            raise  # Extended with error handling
    
    def clone(self) -> 'Slot':
        return Slot(
            name=self.name,
            slot_type=self.slot_type,
            constraints=list(self.constraints),
            default=self.default,
            bound_value=self.bound_value
        )


class ComposablePattern(ABC):
    """Base class for all composable patterns."""
    
    @abstractmethod
    def match(self, input_data: Any, bindings: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        Attempt to match input data against this pattern.
        Returns (success, bindings) where bindings maps slot names to values.
        """
        pass
    
    @abstractmethod
    def instantiate(self, bindings: Dict) -> Any:
        """Create an instance of this pattern with given bindings."""
        pass
    
    @abstractmethod
    def clone(self) -> 'ComposablePattern':
        """Create a deep copy of this pattern."""
        pass
    
    @abstractmethod
    def complexity(self) -> int:
        """Return the complexity (size) of this pattern."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        pass
    
    def compose(self, other: 'ComposablePattern', operator: PatternOperator) -> 'CompoundPattern':
        """Compose with another pattern using an operator."""
        return CompoundPattern(operator=operator, children=[self, other])
    
    def seq(self, other: 'ComposablePattern') -> 'CompoundPattern':
        return self.compose(other, PatternOperator.SEQ)
    
    def alt(self, other: 'ComposablePattern') -> 'CompoundPattern':
        return self.compose(other, PatternOperator.ALT)
    
    def nest(self, other: 'ComposablePattern') -> 'CompoundPattern':
        return self.compose(other, PatternOperator.NEST)
    
    def repeat(self, min_count: int = 0, max_count: int = -1) -> 'CompoundPattern':
        return CompoundPattern(
            operator=PatternOperator.REP,
            children=[self],
            params={'min': min_count, 'max': max_count}
        )


@dataclass
class AtomicPattern(ComposablePattern):
    """An atomic (non-composite) pattern."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    template: Any = None  # The pattern template
    slots: Dict[str, Slot] = field(default_factory=dict)
    
    # Matching configuration
    exact: bool = False  # Require exact match vs. contains
    normalize: bool = True  # Normalize before matching
    
    # Statistics
    match_count: int = 0
    success_count: int = 0
    
    def __post_init__(self):
        if not self.name:
            self.name = f"atom_{self.id[:6]}"
    
    def match(self, input_data: Any, bindings: Optional[Dict] = None) -> Tuple[bool, Dict]:
        bindings = bindings.copy() if bindings else {}
        self.match_count += 1
        
        if self.template is None:
            # Wildcard pattern
            self.success_count += 1
            return True, bindings
        
        # Normalize if needed
        if self.normalize:
            if isinstance(input_data, str):
                input_data = input_data.lower().strip()
            if isinstance(self.template, str):
                template = self.template.lower().strip()
            else:
                template = self.template
        else:
            template = self.template
        
        # Extract slots from template and attempt matching
        if isinstance(template, str) and isinstance(input_data, str):
            success, slot_bindings = self._match_string_template(template, input_data)
        elif isinstance(template, dict) and isinstance(input_data, dict):
            success, slot_bindings = self._match_dict_template(template, input_data)
        elif isinstance(template, (list, tuple)) and isinstance(input_data, (list, tuple)):
            success, slot_bindings = self._match_list_template(template, input_data)
        else:
            # Direct comparison
            success = (template == input_data) if self.exact else (template in str(input_data) if template else True)
            slot_bindings = {}
        
        if success:
            bindings.update(slot_bindings)
            self.success_count += 1
        
        return success, bindings
    
    def _match_string_template(self, template: str, input_str: str) -> Tuple[bool, Dict]:
        """Match a string template with {slot} placeholders."""
        import re
        
        # Find slots in template
        slot_pattern = r'\{(\w+)\}'
        slot_names = re.findall(slot_pattern, template)
        
        if not slot_names:
            # No slots, direct match
            if self.exact:
                return template == input_str, {}
            return template in input_str, {}
        
        # Convert template to regex
        regex_pattern = template
        for slot_name in slot_names:
            regex_pattern = regex_pattern.replace(f'{{{slot_name}}}', f'(?P<{slot_name}>.+?)')
        
        if self.exact:
            regex_pattern = f'^{regex_pattern}$'
        
        try:
            match = re.search(regex_pattern, input_str)
            if match:
                bindings = match.groupdict()
                # Validate against slot constraints
                for slot_name, value in bindings.items():
                    if slot_name in self.slots:
                        if not self.slots[slot_name].matches(value):
                            return False, {}
                return True, bindings
        except re.error:
            pass
        
        return False, {}
    
    def _match_dict_template(self, template: Dict, input_dict: Dict) -> Tuple[bool, Dict]:
        """Match a dictionary template."""
        bindings = {}
        
        for key, value in template.items():
            if key not in input_dict:
                if not self.exact:
                    continue
                return False, {}
            
            if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                # Slot
                slot_name = value[1:-1]
                bindings[slot_name] = input_dict[key]
            elif value != input_dict[key]:
                return False, {}
        
        return True, bindings
    
    def _match_list_template(self, template: list, input_list: list) -> Tuple[bool, Dict]:
        """Match a list template."""
        bindings = {}
        
        if self.exact and len(template) != len(input_list):
            return False, {}
        
        for i, item in enumerate(template):
            if i >= len(input_list):
                return False, {}
            
            if isinstance(item, str) and item.startswith('{') and item.endswith('}'):
                slot_name = item[1:-1]
                bindings[slot_name] = input_list[i]
            elif item != input_list[i]:
                return False, {}
        
        return True, bindings
    
    def instantiate(self, bindings: Dict) -> Any:
        if self.template is None:
            return bindings.get('_', None)
        
        if isinstance(self.template, str):
            result = self.template
            for name, value in bindings.items():
                result = result.replace(f'{{{name}}}', str(value))
            return result
        elif isinstance(self.template, dict):
            result = {}
            for key, value in self.template.items():
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    slot_name = value[1:-1]
                    result[key] = bindings.get(slot_name, value)
                else:
                    result[key] = value
            return result
        elif isinstance(self.template, (list, tuple)):
            result = []
            for item in self.template:
                if isinstance(item, str) and item.startswith('{') and item.endswith('}'):
                    slot_name = item[1:-1]
                    result.append(bindings.get(slot_name, item))
                else:
                    result.append(item)
            return type(self.template)(result)
        
        return self.template
    
    def clone(self) -> 'AtomicPattern':
        return AtomicPattern(
            id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:10],
            name=f"{self.name}_clone",
            template=json.loads(json.dumps(self.template)) if self.template else None,
            slots={k: v.clone() for k, v in self.slots.items()},
            exact=self.exact,
            normalize=self.normalize
        )
    
    def complexity(self) -> int:
        if self.template is None:
            return 1
        if isinstance(self.template, str):
            return len(self.template.split()) + len(self.slots)
        if isinstance(self.template, dict):
            return len(self.template) + len(self.slots)
        if isinstance(self.template, (list, tuple)):
            return len(self.template) + len(self.slots)
        return 1
    
    def to_dict(self) -> Dict:
        return {
            'type': 'atomic',
            'id': self.id,
            'name': self.name,
            'template': self.template,
            'slots': {k: {'name': v.name, 'type': v.slot_type} for k, v in self.slots.items()},
            'exact': self.exact,
            'normalize': self.normalize,
            'match_count': self.match_count,
            'success_count': self.success_count
        }


@dataclass
class CompoundPattern(ComposablePattern):
    """A pattern composed of other patterns using operators."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    operator: PatternOperator = PatternOperator.SEQ
    children: List[ComposablePattern] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Transformation function (for MAP, FILTER, FOLD)
    transform: Optional[Any] = None
    
    # Statistics
    match_count: int = 0
    success_count: int = 0
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.operator.value}_{self.id[:6]}"
    
    def match(self, input_data: Any, bindings: Optional[Dict] = None) -> Tuple[bool, Dict]:
        bindings = bindings.copy() if bindings else {}
        self.match_count += 1
        
        op = self.operator
        
        if op == PatternOperator.SEQ:
            # All children must match in sequence
            if not isinstance(input_data, (list, tuple, str)):
                return False, bindings
            
            if isinstance(input_data, str):
                parts = input_data.split()
            else:
                parts = list(input_data)
            
            if len(parts) < len(self.children):
                return False, bindings
            
            all_bindings = dict(bindings)
            for i, child in enumerate(self.children):
                if i >= len(parts):
                    return False, bindings
                success, child_bindings = child.match(parts[i], all_bindings)
                if not success:
                    return False, bindings
                all_bindings.update(child_bindings)
            
            self.success_count += 1
            return True, all_bindings
        
        elif op == PatternOperator.ALT:
            # Any child can match
            for child in self.children:
                success, child_bindings = child.match(input_data, bindings)
                if success:
                    self.success_count += 1
                    return True, {**bindings, **child_bindings}
            return False, bindings
        
        elif op == PatternOperator.PAR:
            # All children must match the same input
            all_bindings = dict(bindings)
            for child in self.children:
                success, child_bindings = child.match(input_data, all_bindings)
                if not success:
                    return False, bindings
                all_bindings.update(child_bindings)
            self.success_count += 1
            return True, all_bindings
        
        elif op == PatternOperator.OPT:
            # Child matches optionally
            if self.children:
                success, child_bindings = self.children[0].match(input_data, bindings)
                if success:
                    self.success_count += 1
                    return True, {**bindings, **child_bindings}
            self.success_count += 1
            return True, bindings
        
        elif op == PatternOperator.REP:
            # Child matches repeatedly
            if not self.children:
                return True, bindings
            
            if not isinstance(input_data, (list, tuple)):
                # Try to match the single child
                success, child_bindings = self.children[0].match(input_data, bindings)
                if success:
                    self.success_count += 1
                    return True, {**bindings, **child_bindings}
                return self.params.get('min', 0) == 0, bindings
            
            min_count = self.params.get('min', 0)
            max_count = self.params.get('max', -1)
            
            all_bindings = dict(bindings)
            matches = 0
            
            for item in input_data:
                if max_count >= 0 and matches >= max_count:
                    break
                success, child_bindings = self.children[0].match(item, all_bindings)
                if success:
                    matches += 1
                    all_bindings.update(child_bindings)
            
            if matches >= min_count:
                self.success_count += 1
                return True, all_bindings
            return False, bindings
        
        elif op == PatternOperator.NEST:
            # First child contains second child
            if len(self.children) < 2:
                return False, bindings
            
            success1, bindings1 = self.children[0].match(input_data, bindings)
            if not success1:
                return False, bindings
            
            # Look for nested pattern in matched content
            matched = self.children[0].instantiate(bindings1)
            success2, bindings2 = self.children[1].match(matched, bindings1)
            
            if success2:
                self.success_count += 1
                return True, {**bindings1, **bindings2}
            return False, bindings
        
        elif op == PatternOperator.META:
            # Pattern matching patterns
            if isinstance(input_data, ComposablePattern):
                if self.children:
                    # Match against pattern structure
                    success, child_bindings = self.children[0].match(
                        input_data.to_dict(),
                        bindings
                    )
                    if success:
                        self.success_count += 1
                        return True, {**bindings, **child_bindings}
            return False, bindings
        
        elif op == PatternOperator.ANTI:
            # Negation - match if child doesn't match
            if self.children:
                success, _ = self.children[0].match(input_data, bindings)
                if not success:
                    self.success_count += 1
                    return True, bindings
            return False, bindings
        
        # Default
        return False, bindings
    
    def instantiate(self, bindings: Dict) -> Any:
        op = self.operator
        
        if op == PatternOperator.SEQ:
            return [child.instantiate(bindings) for child in self.children]
        
        elif op == PatternOperator.ALT:
            # Instantiate first child (or random)
            if self.children:
                return random.choice(self.children).instantiate(bindings)
            return None
        
        elif op == PatternOperator.PAR:
            return [child.instantiate(bindings) for child in self.children]
        
        elif op == PatternOperator.OPT:
            if self.children and random.random() > 0.5:
                return self.children[0].instantiate(bindings)
            return None
        
        elif op == PatternOperator.REP:
            if not self.children:
                return []
            min_count = self.params.get('min', 1)
            max_count = self.params.get('max', 3) if self.params.get('max', -1) >= 0 else 3
            count = random.randint(min_count, max_count)
            return [self.children[0].instantiate(bindings) for _ in range(count)]
        
        elif op == PatternOperator.NEST:
            if len(self.children) >= 2:
                outer = self.children[0].instantiate(bindings)
                inner = self.children[1].instantiate(bindings)
                if isinstance(outer, dict):
                    outer['_nested'] = inner
                    return outer
                return {'outer': outer, 'inner': inner}
            return None
        
        # Default
        if self.children:
            return self.children[0].instantiate(bindings)
        return None
    
    def clone(self) -> 'CompoundPattern':
        return CompoundPattern(
            id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:10],
            name=f"{self.name}_clone",
            operator=self.operator,
            children=[c.clone() for c in self.children],
            params=dict(self.params),
            transform=self.transform
        )
    
    def complexity(self) -> int:
        base = 1 + len(self.children)
        return base + sum(c.complexity() for c in self.children)
    
    def to_dict(self) -> Dict:
        return {
            'type': 'compound',
            'id': self.id,
            'name': self.name,
            'operator': self.operator.value,
            'children': [c.to_dict() for c in self.children],
            'params': self.params,
            'match_count': self.match_count,
            'success_count': self.success_count
        }


@dataclass
class MetaPattern(ComposablePattern):
    """
    A pattern ABOUT patterns - enables recursive structure.
    
    This is where emergence can happen: patterns that recognize
    and transform other patterns, creating new levels of abstraction.
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    name: str = ""
    
    # What this pattern recognizes in other patterns
    structure_template: Dict[str, Any] = field(default_factory=dict)
    
    # How to transform recognized patterns
    transformation: Optional[str] = None  # 'abstract', 'specialize', 'compose', 'decompose'
    
    # Child patterns (for recursive structure)
    sub_patterns: List[ComposablePattern] = field(default_factory=list)
    
    # Level of abstraction (0 = base, higher = more abstract)
    abstraction_level: int = 0
    
    # Statistics
    patterns_recognized: int = 0
    patterns_generated: int = 0
    
    def match(self, input_data: Any, bindings: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """Match against a pattern structure."""
        bindings = bindings.copy() if bindings else {}
        
        if not isinstance(input_data, ComposablePattern):
            return False, bindings
        
        pattern_dict = input_data.to_dict()
        
        # Check structure template
        for key, expected in self.structure_template.items():
            if key not in pattern_dict:
                return False, bindings
            
            actual = pattern_dict[key]
            
            if isinstance(expected, str) and expected.startswith('{') and expected.endswith('}'):
                # Slot
                slot_name = expected[1:-1]
                bindings[slot_name] = actual
            elif expected != actual:
                return False, bindings
        
        self.patterns_recognized += 1
        return True, bindings
    
    def instantiate(self, bindings: Dict) -> ComposablePattern:
        """Create a new pattern based on bindings and transformation."""
        self.patterns_generated += 1
        
        if self.transformation == 'abstract':
            # Create more abstract version
            return self._abstract(bindings)
        elif self.transformation == 'specialize':
            # Create more specific version
            return self._specialize(bindings)
        elif self.transformation == 'compose':
            # Compose sub-patterns
            return self._compose(bindings)
        elif self.transformation == 'decompose':
            # Break into sub-patterns
            return self._decompose(bindings)
        else:
            # Default: clone with bindings
            return self._default_instantiate(bindings)
    
    def _abstract(self, bindings: Dict) -> ComposablePattern:
        """Create a more abstract pattern by introducing slots."""
        base = bindings.get('pattern', self.sub_patterns[0] if self.sub_patterns else None)
        if not base:
            return AtomicPattern(template=None)
        
        clone = base.clone()
        if isinstance(clone, AtomicPattern) and isinstance(clone.template, str):
            # Replace specific words with slots
            words = clone.template.split()
            if len(words) > 1:
                idx = random.randrange(len(words))
                slot_name = f"slot_{random.randint(0, 99)}"
                words[idx] = f"{{{slot_name}}}"
                clone.template = ' '.join(words)
                clone.slots[slot_name] = Slot(name=slot_name)
        
        clone.name = f"{clone.name}_abstract"
        return clone
    
    def _specialize(self, bindings: Dict) -> ComposablePattern:
        """Create a more specific pattern by filling slots."""
        base = bindings.get('pattern', self.sub_patterns[0] if self.sub_patterns else None)
        if not base:
            return AtomicPattern(template=bindings.get('value', 'specialized'))
        
        clone = base.clone()
        if isinstance(clone, AtomicPattern) and clone.slots:
            # Fill in some slots with concrete values
            for slot_name, slot in list(clone.slots.items()):
                if slot_name in bindings:
                    clone.template = clone.template.replace(f"{{{slot_name}}}", str(bindings[slot_name]))
                    del clone.slots[slot_name]
        
        clone.name = f"{clone.name}_specialized"
        return clone
    
    def _compose(self, bindings: Dict) -> ComposablePattern:
        # TODO: Add memoization cache
        """Compose multiple patterns into one."""
        patterns = bindings.get('patterns', self.sub_patterns)
        if not patterns:
            return AtomicPattern()
        
        if len(patterns) == 1:
            return patterns[0].clone()
        
        operator = bindings.get('operator', PatternOperator.SEQ)
        return CompoundPattern(
            operator=operator,
            children=[p.clone() for p in patterns],
            name=f"composed_{len(patterns)}"
        )
    
    def _decompose(self, bindings: Dict) -> List[ComposablePattern]:
        """Break a pattern into components."""
        pattern = bindings.get('pattern', self.sub_patterns[0] if self.sub_patterns else None)
        if not pattern:
            return []
        
        if isinstance(pattern, CompoundPattern):
            return [c.clone() for c in pattern.children]
        
        return [pattern.clone()]
    
    def _default_instantiate(self, bindings: Dict) -> ComposablePattern:
        """Default instantiation."""
        if self.sub_patterns:
            return self.sub_patterns[0].clone()
        return AtomicPattern(
            template=bindings.get('template', None),
            name=f"generated_{self.id[:6]}"
        )
    
    def clone(self) -> 'MetaPattern':
        try:
                return MetaPattern(
                    id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:10],
                    name=f"{self.name}_clone",
                    structure_template=dict(self.structure_template),
                    transformation=self.transformation,
                    sub_patterns=[p.clone() for p in self.sub_patterns],
                    abstraction_level=self.abstraction_level
                )
        except Exception as e:
            raise  # Extended with error handling
    
    def complexity(self) -> int:
        base = 2 + len(self.structure_template) + self.abstraction_level
        return base + sum(p.complexity() for p in self.sub_patterns)
    
    def to_dict(self) -> Dict:
        return {
            'type': 'meta',
            'id': self.id,
            'name': self.name,
            'structure_template': self.structure_template,
            'transformation': self.transformation,
            'sub_patterns': [p.to_dict() for p in self.sub_patterns],
            'abstraction_level': self.abstraction_level,
            'patterns_recognized': self.patterns_recognized,
            'patterns_generated': self.patterns_generated
        }


class PatternAlgebra:
    """
    The pattern algebra - operations on patterns that enable composition.
    
    This is the engine of compositional explosion.
    """
    
    def __init__(self):
        self.patterns: Dict[str, ComposablePattern] = {}
        self.abstraction_hierarchy: Dict[int, List[str]] = {}  # level -> pattern_ids
        
        # Statistics
        self.compositions: int = 0
        self.abstractions: int = 0
        self.specializations: int = 0
    
    def register(self, pattern: ComposablePattern) -> str:
        """Register a pattern in the algebra."""
        self.patterns[pattern.id] = pattern
        
        if isinstance(pattern, MetaPattern):
            level = pattern.abstraction_level
            if level not in self.abstraction_hierarchy:
                self.abstraction_hierarchy[level] = []
            self.abstraction_hierarchy[level].append(pattern.id)
        
        return pattern.id
    
    def compose(
        self,
        patterns: List[ComposablePattern],
        operator: PatternOperator = PatternOperator.SEQ
    ) -> CompoundPattern:
        """Compose multiple patterns with an operator."""
        self.compositions += 1
        
        result = CompoundPattern(
            operator=operator,
            children=patterns,
            name=f"composed_{operator.value}_{self.compositions}"
        )
        
        self.register(result)
        return result
    
    def abstract(self, pattern: ComposablePattern) -> MetaPattern:
        """Create a meta-pattern that abstracts the given pattern."""
        self.abstractions += 1
        
        meta = MetaPattern(
            name=f"abstract_{pattern.name}",
            structure_template={'type': pattern.to_dict().get('type')},
            transformation='abstract',
            sub_patterns=[pattern],
            abstraction_level=(pattern.abstraction_level + 1 if isinstance(pattern, MetaPattern) else 1)
        )
        
        self.register(meta)
        return meta
    
    def specialize(self, pattern: ComposablePattern, bindings: Dict) -> ComposablePattern:
        """Create a specialized version of a pattern."""
        self.specializations += 1
        
        if isinstance(pattern, MetaPattern):
            meta = pattern.clone()
            meta.transformation = 'specialize'
            return meta.instantiate(bindings)
        else:
            clone = pattern.clone()
            if isinstance(clone, AtomicPattern):
                for slot_name, value in bindings.items():
                    if slot_name in clone.slots:
                        clone.template = clone.template.replace(f"{{{slot_name}}}", str(value))
                        del clone.slots[slot_name]
            return clone
    
    def find_analogies(
        self,
        source: ComposablePattern,
        candidates: List[ComposablePattern]
    ) -> List[Tuple[ComposablePattern, float]]:
        """Find patterns analogous to source."""
        analogies = []
        
        source_dict = source.to_dict()
        source_type = source_dict.get('type')
        source_complexity = source.complexity()
        
        for candidate in candidates:
            if candidate.id == source.id:
                continue
            
            cand_dict = candidate.to_dict()
            
            # Similarity based on structure
            similarity = 0.0
            
            # Same type
            if cand_dict.get('type') == source_type:
                similarity += 0.3
            
            # Similar complexity
            complexity_ratio = min(source_complexity, candidate.complexity()) / max(source_complexity, candidate.complexity())
            similarity += 0.3 * complexity_ratio
            
            # For compounds, similar operator
            if source_type == 'compound' and cand_dict.get('type') == 'compound':
                if source_dict.get('operator') == cand_dict.get('operator'):
                    similarity += 0.4
            
            if similarity > 0.3:
                analogies.append((candidate, similarity))
        
        analogies.sort(key=lambda x: x[1], reverse=True)
        return analogies
    
    def evolve_patterns(self, fitness_scores: Dict[str, float]) -> List[ComposablePattern]:
        """Evolve patterns based on fitness, creating new ones."""
        new_patterns = []
        
        # Sort by fitness
        sorted_patterns = sorted(
            [(pid, fitness_scores.get(pid, 0.0)) for pid in self.patterns],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Top patterns reproduce
        top_n = max(2, len(sorted_patterns) // 4)
        for pid, fitness in sorted_patterns[:top_n]:
            pattern = self.patterns[pid]
            
            # Mutation
            if random.random() < 0.3:
                mutated = self._mutate(pattern)
                new_patterns.append(mutated)
                self.register(mutated)
            
            # Crossover with another top pattern
            if random.random() < 0.2 and len(sorted_patterns) >= 2:
                other_pid = random.choice([p for p, _ in sorted_patterns[:top_n] if p != pid])
                other = self.patterns.get(other_pid)
                if other:
                    child = self._crossover(pattern, other)
                    new_patterns.append(child)
                    self.register(child)
            
            # Abstraction
            if random.random() < 0.1:
                abstract = self.abstract(pattern)
                new_patterns.append(abstract)
        
        return new_patterns
    
    def _mutate(self, pattern: ComposablePattern) -> ComposablePattern:
        """Mutate a pattern."""
        clone = pattern.clone()
        
        if isinstance(clone, AtomicPattern):
            if random.random() < 0.5 and clone.template:
                # Add or modify a slot
                if isinstance(clone.template, str):
                    words = clone.template.split()
                    if words:
                        idx = random.randrange(len(words))
                        if '{' in words[idx]:
                            # Replace slot with concrete
                            words[idx] = f"word_{random.randint(0, 99)}"
                        else:
                            # Create new slot
                            slot_name = f"mut_{random.randint(0, 99)}"
                            words[idx] = f"{{{slot_name}}}"
                            clone.slots[slot_name] = Slot(name=slot_name)
                        clone.template = ' '.join(words)
        
        elif isinstance(clone, CompoundPattern):
            if random.random() < 0.5 and clone.children:
                # Mutate a child
                idx = random.randrange(len(clone.children))
                clone.children[idx] = self._mutate(clone.children[idx])
            else:
                # Change operator
                operators = list(PatternOperator)
                clone.operator = random.choice(operators)
        
        clone.name = f"{clone.name}_mut"
        return clone
    
    def _crossover(self, p1: ComposablePattern, p2: ComposablePattern) -> ComposablePattern:
        """Crossover two patterns."""
        if isinstance(p1, CompoundPattern) and isinstance(p2, CompoundPattern):
            # Swap children
            children = []
            all_children = p1.children + p2.children
            for child in all_children:
                if random.random() < 0.5:
                    children.append(child.clone())
            
            if not children:
                children = [p1.children[0].clone()] if p1.children else [p2.children[0].clone()]
            
            return CompoundPattern(
                operator=random.choice([p1.operator, p2.operator]),
                children=children,
                name=f"cross_{p1.id[:4]}_{p2.id[:4]}"
            )
        else:
            # Compose them
            return CompoundPattern(
                operator=random.choice([PatternOperator.SEQ, PatternOperator.ALT]),
                children=[p1.clone(), p2.clone()],
                name=f"cross_{p1.id[:4]}_{p2.id[:4]}"
            )
    
    def get_stats(self) -> Dict:
        return {
            'total_patterns': len(self.patterns),
            'abstraction_levels': len(self.abstraction_hierarchy),
            'compositions': self.compositions,
            'abstractions': self.abstractions,
            'specializations': self.specializations,
            'patterns_by_level': {k: len(v) for k, v in self.abstraction_hierarchy.items()}
        }


def pattern_from_dict(data: Dict) -> ComposablePattern:
    """Deserialize a pattern from dictionary."""
    pattern_type = data.get('type')
    
    if pattern_type == 'atomic':
        return AtomicPattern(
            id=data.get('id', ''),
            name=data.get('name', ''),
            template=data.get('template'),
            exact=data.get('exact', False),
            normalize=data.get('normalize', True)
        )
    elif pattern_type == 'compound':
        return CompoundPattern(
            id=data.get('id', ''),
            name=data.get('name', ''),
            operator=PatternOperator(data.get('operator', 'seq')),
            children=[pattern_from_dict(c) for c in data.get('children', [])],
            params=data.get('params', {})
        )
    elif pattern_type == 'meta':
        return MetaPattern(
            id=data.get('id', ''),
            name=data.get('name', ''),
            structure_template=data.get('structure_template', {}),
            transformation=data.get('transformation'),
            sub_patterns=[pattern_from_dict(p) for p in data.get('sub_patterns', [])],
            abstraction_level=data.get('abstraction_level', 0)
        )
    
    raise ValueError(f"Unknown pattern type: {pattern_type}")
