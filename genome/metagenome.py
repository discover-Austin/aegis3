"""
AEGIS-2 MetaGenome: Genetic Programming for Open-Ended Evolution

This is NOT parameter optimization. This is STRUCTURE GENERATION.

Key insight: Instead of fixed genes with tunable values, we have:
- Genes that ARE programs (executable code trees)
- Genes that CREATE other genes
- Genes that MODIFY the genome structure itself
- Meta-genes that control how evolution happens

This enables genuine open-endedness: the search space grows as you search.
"""

import random
import math
import hashlib
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Union
from enum import Enum
from datetime import datetime
import json


class NodeType(Enum):
    """Types of nodes in genetic program trees."""
    # Terminals (leaves)
    CONSTANT = "const"
    VARIABLE = "var"
    INPUT = "input"
    MEMORY = "memory"
    RANDOM = "random"
    
    # Arithmetic
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    POW = "pow"
    
    # Comparison
    GT = "gt"
    LT = "lt"
    EQ = "eq"
    
    # Logic
    AND = "and"
    OR = "or"
    NOT = "not"
    IF = "if"
    
    # Control flow
    SEQ = "seq"
    LOOP = "loop"
    
    # Memory operations
    STORE = "store"
    LOAD = "load"
    
    # Meta operations (genes about genes)
    CREATE_GENE = "create_gene"
    MODIFY_GENE = "modify_gene"
    DELETE_GENE = "delete_gene"
    COPY_GENE = "copy_gene"
    CROSSOVER = "crossover"
    
    # Structure operations
    GROW = "grow"
    PRUNE = "prune"
    CONNECT = "connect"
    SPLIT = "split"
    MERGE = "merge"
    
    # Goal operations
    SPAWN_GOAL = "spawn_goal"
    PRIORITIZE = "prioritize"
    SATISFY = "satisfy"
    
    # Pattern operations
    MATCH = "match"
    ABSTRACT = "abstract"
    COMPOSE = "compose"
    DECOMPOSE = "decompose"


# Arity of each node type (number of children)
NODE_ARITY = {
    NodeType.CONSTANT: 0,
    NodeType.VARIABLE: 0,
    NodeType.INPUT: 0,
    NodeType.MEMORY: 0,
    NodeType.RANDOM: 0,
    NodeType.ADD: 2,
    NodeType.SUB: 2,
    NodeType.MUL: 2,
    NodeType.DIV: 2,
    NodeType.MOD: 2,
    NodeType.POW: 2,
    NodeType.GT: 2,
    NodeType.LT: 2,
    NodeType.EQ: 2,
    NodeType.AND: 2,
    NodeType.OR: 2,
    NodeType.NOT: 1,
    NodeType.IF: 3,
    NodeType.SEQ: 2,
    NodeType.LOOP: 2,
    NodeType.STORE: 2,
    NodeType.LOAD: 1,
    NodeType.CREATE_GENE: 1,
    NodeType.MODIFY_GENE: 2,
    NodeType.DELETE_GENE: 1,
    NodeType.COPY_GENE: 1,
    NodeType.CROSSOVER: 2,
    NodeType.GROW: 1,
    NodeType.PRUNE: 1,
    NodeType.CONNECT: 2,
    NodeType.SPLIT: 1,
    NodeType.MERGE: 2,
    NodeType.SPAWN_GOAL: 1,
    NodeType.PRIORITIZE: 2,
    NodeType.SATISFY: 1,
    NodeType.MATCH: 2,
    NodeType.ABSTRACT: 1,
    NodeType.COMPOSE: 2,
    NodeType.DECOMPOSE: 1,
}


@dataclass
class ProgramNode:
    """A node in a genetic program tree."""
    node_type: NodeType
    children: List['ProgramNode'] = field(default_factory=list)
    value: Any = None  # For constants, variable names, etc.
    
    # Execution tracking
    execution_count: int = 0
    total_output: float = 0.0
    last_output: Any = None
    
    # Mutation tracking
    mutations: int = 0
    
    def __post_init__(self):
        expected_arity = NODE_ARITY.get(self.node_type, 0)
        while len(self.children) < expected_arity:
            self.children.append(ProgramNode(NodeType.CONSTANT, value=0.0))
    
    @property
    def depth(self) -> int:
        try:
                if not self.children:
                    return 1
                return 1 + max(c.depth for c in self.children)
        except Exception as e:
            raise  # Extended with error handling
    
    @property
    def size(self) -> int:
        return 1 + sum(c.size for c in self.children)
    
    def clone(self) -> 'ProgramNode':
        return ProgramNode(
            node_type=self.node_type,
            children=[c.clone() for c in self.children],
            value=copy.deepcopy(self.value)
        )
    
    def to_dict(self) -> Dict:
        return {
            'type': self.node_type.value,
            'value': self.value,
            'children': [c.to_dict() for c in self.children],
            'exec_count': self.execution_count,
            'mutations': self.mutations
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProgramNode':
        return cls(
            node_type=NodeType(data['type']),
            children=[cls.from_dict(c) for c in data.get('children', [])],
            value=data.get('value'),
            execution_count=data.get('exec_count', 0),
            mutations=data.get('mutations', 0)
        )


class ProgramExecutor:
    """Executes genetic program trees with safety limits."""
    
    def __init__(
        self,
        max_steps: int = 10000,
        max_depth: int = 100,
        memory_size: int = 256
    ):
        self.max_steps = max_steps
        self.max_depth = max_depth
        self.memory_size = memory_size
        
        # Execution state
        self.memory: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.inputs: Dict[str, Any] = {}
        self.step_count = 0
        
        # Side effects (meta-operations)
        self.side_effects: List[Dict] = []
    
    def reset(self):
        self.memory = {}
        self.variables = {}
        self.inputs = {}
        self.step_count = 0
        self.side_effects = []
    
    def execute(
        self,
        program: ProgramNode,
        inputs: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, List[Dict]]:
        """Execute a program and return (result, side_effects)."""
        self.reset()
        self.inputs = inputs or {}
        self.variables = variables or {}
        
        try:
            result = self._execute_node(program, depth=0)
        except Exception as e:
            result = None
        
        return result, self.side_effects
    
    def _execute_node(self, node: ProgramNode, depth: int) -> Any:
        """Execute a single node."""
        self.step_count += 1
        node.execution_count += 1
        
        if self.step_count > self.max_steps:
            raise RuntimeError("Max steps exceeded")
        if depth > self.max_depth:
            raise RuntimeError("Max depth exceeded")
        
        nt = node.node_type
        
        # Terminals
        if nt == NodeType.CONSTANT:
            return node.value if node.value is not None else 0.0
        
        if nt == NodeType.VARIABLE:
            return self.variables.get(node.value, 0.0)
        
        if nt == NodeType.INPUT:
            return self.inputs.get(node.value, 0.0)
        
        if nt == NodeType.MEMORY:
            return self.memory.get(node.value, 0.0)
        
        if nt == NodeType.RANDOM:
            return random.random()
        
        # Get child values lazily
        def child(i: int) -> Any:
            if i < len(node.children):
                return self._execute_node(node.children[i], depth + 1)
            return 0.0
        
        # Arithmetic
        if nt == NodeType.ADD:
            return self._safe_num(child(0)) + self._safe_num(child(1))
        if nt == NodeType.SUB:
            return self._safe_num(child(0)) - self._safe_num(child(1))
        if nt == NodeType.MUL:
            return self._safe_num(child(0)) * self._safe_num(child(1))
        if nt == NodeType.DIV:
            b = self._safe_num(child(1))
            return self._safe_num(child(0)) / b if b != 0 else 0.0
        if nt == NodeType.MOD:
            b = self._safe_num(child(1))
            return self._safe_num(child(0)) % b if b != 0 else 0.0
        if nt == NodeType.POW:
            base = self._safe_num(child(0))
            exp = min(10, max(-10, self._safe_num(child(1))))
            try:
                return math.pow(base, exp)
            except:
                return 0.0
        
        # Comparison
        if nt == NodeType.GT:
            return 1.0 if self._safe_num(child(0)) > self._safe_num(child(1)) else 0.0
        if nt == NodeType.LT:
            return 1.0 if self._safe_num(child(0)) < self._safe_num(child(1)) else 0.0
        if nt == NodeType.EQ:
            return 1.0 if abs(self._safe_num(child(0)) - self._safe_num(child(1))) < 0.001 else 0.0
        
        # Logic
        if nt == NodeType.AND:
            return 1.0 if (self._truthy(child(0)) and self._truthy(child(1))) else 0.0
        if nt == NodeType.OR:
            return 1.0 if (self._truthy(child(0)) or self._truthy(child(1))) else 0.0
        if nt == NodeType.NOT:
            return 0.0 if self._truthy(child(0)) else 1.0
        if nt == NodeType.IF:
            return child(1) if self._truthy(child(0)) else child(2)
        
        # Control flow
        if nt == NodeType.SEQ:
            child(0)
            return child(1)
        if nt == NodeType.LOOP:
            count = min(100, max(0, int(self._safe_num(child(0)))))
            result = 0.0
            for _ in range(count):
                result = child(1)
            return result
        
        # Memory
        if nt == NodeType.STORE:
            key = str(node.value or child(0))[:32]
            val = child(1) if len(node.children) > 1 else child(0)
            if len(self.memory) < self.memory_size:
                self.memory[key] = val
            return val
        if nt == NodeType.LOAD:
            key = str(node.value or child(0))
            return self.memory.get(key, 0.0)
        
        # Meta operations - these produce side effects
        if nt == NodeType.CREATE_GENE:
            self.side_effects.append({
                'op': 'create_gene',
                'template': child(0)
            })
            return 1.0
        
        if nt == NodeType.MODIFY_GENE:
            self.side_effects.append({
                'op': 'modify_gene',
                'target': child(0),
                'modification': child(1)
            })
            return 1.0
        
        if nt == NodeType.DELETE_GENE:
            self.side_effects.append({
                'op': 'delete_gene',
                'target': child(0)
            })
            return 1.0
        
        if nt == NodeType.COPY_GENE:
            self.side_effects.append({
                'op': 'copy_gene',
                'source': child(0)
            })
            return 1.0
        
        if nt == NodeType.CROSSOVER:
            self.side_effects.append({
                'op': 'crossover',
                'parent1': child(0),
                'parent2': child(1)
            })
            return 1.0
        
        # Structure operations
        if nt == NodeType.GROW:
            self.side_effects.append({'op': 'grow', 'target': child(0)})
            return 1.0
        if nt == NodeType.PRUNE:
            self.side_effects.append({'op': 'prune', 'target': child(0)})
            return 1.0
        if nt == NodeType.CONNECT:
            self.side_effects.append({'op': 'connect', 'a': child(0), 'b': child(1)})
            return 1.0
        if nt == NodeType.SPLIT:
            self.side_effects.append({'op': 'split', 'target': child(0)})
            return 1.0
        if nt == NodeType.MERGE:
            self.side_effects.append({'op': 'merge', 'a': child(0), 'b': child(1)})
            return 1.0
        
        # Goal operations
        if nt == NodeType.SPAWN_GOAL:
            self.side_effects.append({'op': 'spawn_goal', 'spec': child(0)})
            return 1.0
        if nt == NodeType.PRIORITIZE:
            self.side_effects.append({'op': 'prioritize', 'goal': child(0), 'priority': child(1)})
            return 1.0
        if nt == NodeType.SATISFY:
            self.side_effects.append({'op': 'satisfy', 'goal': child(0)})
            return 1.0
        
        # Pattern operations
        if nt == NodeType.MATCH:
            self.side_effects.append({'op': 'match', 'pattern': child(0), 'input': child(1)})
            return 1.0
        if nt == NodeType.ABSTRACT:
            self.side_effects.append({'op': 'abstract', 'concrete': child(0)})
            return 1.0
        if nt == NodeType.COMPOSE:
            self.side_effects.append({'op': 'compose', 'a': child(0), 'b': child(1)})
            return 1.0
        if nt == NodeType.DECOMPOSE:
            self.side_effects.append({'op': 'decompose', 'pattern': child(0)})
            return 1.0
        
        return 0.0
    
    def _safe_num(self, val: Any) -> float:
        try:
            f = float(val)
            if math.isnan(f) or math.isinf(f):
                return 0.0
            return max(-1e10, min(1e10, f))
        except:
            return 0.0
    
    def _truthy(self, val: Any) -> bool:
        if isinstance(val, (int, float)):
            return val > 0.5
        return bool(val)


@dataclass
class Gene:
    """
    A gene in the meta-genome.
    
    Unlike simple parameter genes, these ARE executable programs.
    They can compute values, make decisions, and modify other genes.
    """
    id: str
    name: str
    program: ProgramNode
    
    # Gene type
    gene_type: str = "compute"  # compute, control, meta, goal, pattern
    
    # Activation (when does this gene run?)
    activation_conditions: List[ProgramNode] = field(default_factory=list)
    activation_threshold: float = 0.5
    
    # Expression level (how strongly is this gene expressed?)
    expression: float = 1.0
    base_expression: float = 1.0
    
    # Regulatory connections (genes that affect this gene's expression)
    regulators: Dict[str, float] = field(default_factory=dict)  # gene_id -> influence
    
    # Fitness tracking
    fitness_contribution: float = 0.0
    fitness_history: List[float] = field(default_factory=list)
    
    # Lineage
    parent_ids: List[str] = field(default_factory=list)
    generation: int = 0
    mutations: int = 0
    
    # Temporal
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    last_expressed: float = 0.0
    expression_count: int = 0
    
    def clone(self) -> 'Gene':
        return Gene(
            id=hashlib.sha256(f"{self.id}:{random.random()}".encode()).hexdigest()[:12],
            name=f"{self.name}_copy",
            program=self.program.clone(),
            gene_type=self.gene_type,
            activation_conditions=[c.clone() for c in self.activation_conditions],
            activation_threshold=self.activation_threshold,
            expression=self.expression,
            base_expression=self.base_expression,
            regulators=dict(self.regulators),
            parent_ids=[self.id],
            generation=self.generation + 1
        )
    
    def should_activate(self, executor: ProgramExecutor, context: Dict) -> bool:
        """Determine if this gene should activate given context."""
        if not self.activation_conditions:
            return True
        
        for condition in self.activation_conditions:
            result, _ = executor.execute(condition, inputs=context)
            if result is not None and result > self.activation_threshold:
                return True
        return False
    
    def express(
        self,
        executor: ProgramExecutor,
        inputs: Dict,
        variables: Dict
    ) -> Tuple[Any, List[Dict]]:
        """Express this gene (execute its program)."""
        self.last_expressed = datetime.now().timestamp()
        self.expression_count += 1
        
        result, effects = executor.execute(
            self.program,
            inputs=inputs,
            variables=variables
        )
        
        # Scale result by expression level
        if isinstance(result, (int, float)):
            result = result * self.expression
        
        return result, effects
    
    def update_expression(self, gene_outputs: Dict[str, float]):
        """Update expression level based on regulatory genes."""
        if not self.regulators:
            self.expression = self.base_expression
            return
        
        regulation = 0.0
        for reg_id, influence in self.regulators.items():
            if reg_id in gene_outputs:
                regulation += influence * gene_outputs[reg_id]
        
        # Sigmoid activation
        self.expression = self.base_expression * (1 / (1 + math.exp(-regulation)))
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'program': self.program.to_dict(),
            'gene_type': self.gene_type,
            'activation_conditions': [c.to_dict() for c in self.activation_conditions],
            'activation_threshold': self.activation_threshold,
            'expression': self.expression,
            'base_expression': self.base_expression,
            'regulators': self.regulators,
            'fitness_contribution': self.fitness_contribution,
            'parent_ids': self.parent_ids,
            'generation': self.generation,
            'mutations': self.mutations,
            'created_at': self.created_at,
            'expression_count': self.expression_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Gene':
        gene = cls(
            id=data['id'],
            name=data['name'],
            program=ProgramNode.from_dict(data['program']),
            gene_type=data.get('gene_type', 'compute'),
            activation_threshold=data.get('activation_threshold', 0.5),
            expression=data.get('expression', 1.0),
            base_expression=data.get('base_expression', 1.0),
            regulators=data.get('regulators', {}),
            fitness_contribution=data.get('fitness_contribution', 0.0),
            parent_ids=data.get('parent_ids', []),
            generation=data.get('generation', 0),
            mutations=data.get('mutations', 0),
            created_at=data.get('created_at', datetime.now().timestamp()),
            expression_count=data.get('expression_count', 0)
        )
        gene.activation_conditions = [
            ProgramNode.from_dict(c) for c in data.get('activation_conditions', [])
        ]
        return gene


class MetaGenome:
    """
    A self-modifying genome of genetic programs.
    
    This is the core of open-ended evolution:
    - Genes are programs, not just parameters
    - Genes can create, modify, and delete other genes
    - The genome structure itself evolves
    - Regulatory networks emerge
    """
    
    def __init__(self, max_genes: int = 1000):
        self.max_genes = max_genes
        self.genes: Dict[str, Gene] = {}
        self.executor = ProgramExecutor()
        
        # Gene expression order (topologically sorted by regulation)
        self.expression_order: List[str] = []
        
        # Accumulated side effects waiting to be processed
        self.pending_effects: List[Dict] = []
        
        # Fitness tracking
        self.total_fitness: float = 0.0
        self.fitness_history: List[float] = []
        
        # Structural stats
        self.genes_created: int = 0
        self.genes_deleted: int = 0
        self.total_mutations: int = 0
        
        # Initialize with bootstrap genes
        self._initialize_bootstrap()
    
    def _initialize_bootstrap(self):
        """Create initial genes that bootstrap the system."""
        
        # Meta-gene: creates new genes based on fitness landscape
        self._add_gene(Gene(
            id="meta_create",
            name="gene_creator",
            gene_type="meta",
            program=ProgramNode(
                NodeType.IF,
                children=[
                    ProgramNode(NodeType.GT, children=[
                        ProgramNode(NodeType.INPUT, value="fitness_gradient"),
                        ProgramNode(NodeType.CONSTANT, value=0.1)
                    ]),
                    ProgramNode(NodeType.CREATE_GENE, children=[
                        ProgramNode(NodeType.RANDOM)
                    ]),
                    ProgramNode(NodeType.CONSTANT, value=0.0)
                ]
            )
        ))
        
        # Meta-gene: prunes low-fitness genes
        self._add_gene(Gene(
            id="meta_prune",
            name="gene_pruner",
            gene_type="meta",
            program=ProgramNode(
                NodeType.IF,
                children=[
                    ProgramNode(NodeType.LT, children=[
                        ProgramNode(NodeType.INPUT, value="gene_fitness"),
                        ProgramNode(NodeType.CONSTANT, value=0.1)
                    ]),
                    ProgramNode(NodeType.DELETE_GENE, children=[
                        ProgramNode(NodeType.INPUT, value="gene_id")
                    ]),
                    ProgramNode(NodeType.CONSTANT, value=0.0)
                ]
            )
        ))
        
        # Regulatory gene: modulates other genes based on context
        self._add_gene(Gene(
            id="regulator_context",
            name="context_regulator",
            gene_type="control",
            program=ProgramNode(
                NodeType.MUL,
                children=[
                    ProgramNode(NodeType.INPUT, value="context_signal"),
                    ProgramNode(NodeType.ADD, children=[
                        ProgramNode(NodeType.CONSTANT, value=0.5),
                        ProgramNode(NodeType.MUL, children=[
                            ProgramNode(NodeType.RANDOM),
                            ProgramNode(NodeType.CONSTANT, value=0.5)
                        ])
                    ])
                ]
            )
        ))
        
        # Compute gene: basic decision making
        self._add_gene(Gene(
            id="compute_decide",
            name="decision_maker",
            gene_type="compute",
            program=ProgramNode(
                NodeType.IF,
                children=[
                    ProgramNode(NodeType.GT, children=[
                        ProgramNode(NodeType.INPUT, value="confidence"),
                        ProgramNode(NodeType.VARIABLE, value="threshold")
                    ]),
                    ProgramNode(NodeType.INPUT, value="action_a"),
                    ProgramNode(NodeType.INPUT, value="action_b")
                ]
            )
        ))
        
        # Goal gene: spawns sub-goals
        self._add_gene(Gene(
            id="goal_spawner",
            name="goal_spawner",
            gene_type="goal",
            program=ProgramNode(
                NodeType.IF,
                children=[
                    ProgramNode(NodeType.GT, children=[
                        ProgramNode(NodeType.INPUT, value="complexity"),
                        ProgramNode(NodeType.CONSTANT, value=0.5)
                    ]),
                    ProgramNode(NodeType.SPAWN_GOAL, children=[
                        ProgramNode(NodeType.DECOMPOSE, children=[
                            ProgramNode(NodeType.INPUT, value="current_goal")
                        ])
                    ]),
                    ProgramNode(NodeType.CONSTANT, value=0.0)
                ]
            )
        ))
        
        # Pattern gene: abstracts patterns from experience
        self._add_gene(Gene(
            id="pattern_abstract",
            name="pattern_abstractor",
            gene_type="pattern",
            program=ProgramNode(
                NodeType.SEQ,
                children=[
                    ProgramNode(NodeType.MATCH, children=[
                        ProgramNode(NodeType.INPUT, value="template"),
                        ProgramNode(NodeType.INPUT, value="instance")
                    ]),
                    ProgramNode(NodeType.IF, children=[
                        ProgramNode(NodeType.GT, children=[
                            ProgramNode(NodeType.INPUT, value="match_count"),
                            ProgramNode(NodeType.CONSTANT, value=2)
                        ]),
                        ProgramNode(NodeType.ABSTRACT, children=[
                            ProgramNode(NodeType.INPUT, value="matched_set")
                        ]),
                        ProgramNode(NodeType.CONSTANT, value=0.0)
                    ])
                ]
            )
        ))
        
        self._update_expression_order()
    
    def _add_gene(self, gene: Gene):
        """Add a gene to the genome."""
        if len(self.genes) >= self.max_genes:
            # Remove lowest fitness gene
            if self.genes:
                worst = min(self.genes.values(), key=lambda g: g.fitness_contribution)
                del self.genes[worst.id]
                self.genes_deleted += 1
        
        self.genes[gene.id] = gene
        self.genes_created += 1
    
    def _update_expression_order(self):
        """Update the order in which genes are expressed (topological sort)."""
        # Simple dependency-based ordering
        # Genes with more regulators go later
        self.expression_order = sorted(
            self.genes.keys(),
            key=lambda gid: len(self.genes[gid].regulators)
        )
    
    def express_all(
        self,
        inputs: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        Express all genes and collect results.
        
        Returns (gene_outputs, side_effects)
        """
        variables = variables or {}
        outputs: Dict[str, Any] = {}
        all_effects: List[Dict] = []
        
        # First pass: compute gene outputs
        for gene_id in self.expression_order:
            gene = self.genes.get(gene_id)
            if not gene:
                continue
            
            # Check activation conditions
            if not gene.should_activate(self.executor, inputs):
                continue
            
            # Update expression level based on regulators
            gene.update_expression(outputs)
            
            # Express the gene
            result, effects = gene.express(
                self.executor,
                inputs={**inputs, **outputs},  # Include previous gene outputs
                variables=variables
            )
            
            outputs[gene_id] = result
            all_effects.extend(effects)
        
        self.pending_effects.extend(all_effects)
        return outputs, all_effects
    
    def process_effects(self) -> List[str]:
        """Process pending side effects (gene creation, modification, etc.)."""
        processed = []
        
        for effect in self.pending_effects:
            op = effect.get('op')
            
            if op == 'create_gene':
                new_gene = self._create_random_gene()
                self._add_gene(new_gene)
                processed.append(f"Created gene: {new_gene.id}")
            
            elif op == 'delete_gene':
                target = effect.get('target')
                if isinstance(target, str) and target in self.genes:
                    if target not in ['meta_create', 'meta_prune']:  # Protect bootstrap
                        del self.genes[target]
                        self.genes_deleted += 1
                        processed.append(f"Deleted gene: {target}")
            
            elif op == 'modify_gene':
                target = effect.get('target')
                if isinstance(target, str) and target in self.genes:
                    self._mutate_gene(self.genes[target])
                    processed.append(f"Modified gene: {target}")
            
            elif op == 'copy_gene':
                source = effect.get('source')
                if isinstance(source, str) and source in self.genes:
                    clone = self.genes[source].clone()
                    self._add_gene(clone)
                    processed.append(f"Copied gene: {source} -> {clone.id}")
            
            elif op == 'crossover':
                p1 = effect.get('parent1')
                p2 = effect.get('parent2')
                if isinstance(p1, str) and isinstance(p2, str):
                    if p1 in self.genes and p2 in self.genes:
                        child = self._crossover(self.genes[p1], self.genes[p2])
                        self._add_gene(child)
                        processed.append(f"Crossover: {p1} x {p2} -> {child.id}")
        
        self.pending_effects = []
        self._update_expression_order()
        
        return processed
    
    def _create_random_gene(self, gene_type: Optional[str] = None) -> Gene:
        """Create a new random gene."""
        gene_type = gene_type or random.choice(['compute', 'control', 'pattern'])
        
        program = self._generate_random_program(max_depth=4)
        
        gene = Gene(
            id=hashlib.sha256(f"gen:{random.random()}:{datetime.now()}".encode()).hexdigest()[:12],
            name=f"evolved_{gene_type}_{self.genes_created}",
            program=program,
            gene_type=gene_type,
            base_expression=random.uniform(0.5, 1.5)
        )
        
        # Random regulatory connections
        if self.genes and random.random() < 0.3:
            regulator = random.choice(list(self.genes.keys()))
            gene.regulators[regulator] = random.uniform(-1, 1)
        
        return gene
    
    def _generate_random_program(self, max_depth: int = 4, depth: int = 0) -> ProgramNode:
        """Generate a random program tree."""
        if depth >= max_depth or (depth > 0 and random.random() < 0.3):
            # Terminal node
            terminal_types = [
                NodeType.CONSTANT,
                NodeType.VARIABLE,
                NodeType.INPUT,
                NodeType.RANDOM
            ]
            node_type = random.choice(terminal_types)
            
            if node_type == NodeType.CONSTANT:
                return ProgramNode(node_type, value=random.uniform(-1, 1))
            elif node_type == NodeType.VARIABLE:
                return ProgramNode(node_type, value=f"var_{random.randint(0, 5)}")
            elif node_type == NodeType.INPUT:
                inputs = ['fitness', 'context_signal', 'confidence', 'complexity', 'novelty']
                return ProgramNode(node_type, value=random.choice(inputs))
            else:
                return ProgramNode(node_type)
        
        # Non-terminal node
        non_terminals = [
            NodeType.ADD, NodeType.SUB, NodeType.MUL, NodeType.DIV,
            NodeType.GT, NodeType.LT, NodeType.IF,
            NodeType.AND, NodeType.OR, NodeType.NOT
        ]
        
        # Occasionally add meta-operations
        if random.random() < 0.1:
            non_terminals.extend([
                NodeType.CREATE_GENE, NodeType.MODIFY_GENE,
                NodeType.SPAWN_GOAL, NodeType.ABSTRACT
            ])
        
        node_type = random.choice(non_terminals)
        arity = NODE_ARITY.get(node_type, 0)
        
        children = [
            self._generate_random_program(max_depth, depth + 1)
            for _ in range(arity)
        ]
        
        return ProgramNode(node_type, children=children)
    
    def _mutate_gene(self, gene: Gene):
        """Mutate a gene's program."""
        gene.mutations += 1
        self.total_mutations += 1
        
        # Choose mutation type
        mutation_type = random.choice([
            'point', 'subtree', 'hoist', 'shrink', 'expand'
        ])
        
        if mutation_type == 'point':
            # Change a single node
            self._point_mutate(gene.program)
        elif mutation_type == 'subtree':
            # Replace a subtree
            self._subtree_mutate(gene.program)
        elif mutation_type == 'hoist':
            # Promote a subtree to root
            if gene.program.children:
                gene.program = random.choice(gene.program.children).clone()
        elif mutation_type == 'shrink':
            # Replace node with terminal
            self._shrink_mutate(gene.program)
        elif mutation_type == 'expand':
            # Replace terminal with subtree
            self._expand_mutate(gene.program)
    
    def _point_mutate(self, node: ProgramNode):
        """Mutate a single node."""
        if random.random() < 0.3:
            # Mutate this node
            if node.node_type == NodeType.CONSTANT:
                node.value = node.value + random.gauss(0, 0.5) if node.value else random.uniform(-1, 1)
            elif node.node_type in [NodeType.ADD, NodeType.SUB, NodeType.MUL, NodeType.DIV]:
                node.node_type = random.choice([NodeType.ADD, NodeType.SUB, NodeType.MUL, NodeType.DIV])
        
        # Recurse
        for child in node.children:
            self._point_mutate(child)
    
    def _subtree_mutate(self, node: ProgramNode):
        try:
                """Replace a random subtree."""
                if node.children and random.random() < 0.3:
                    idx = random.randrange(len(node.children))
                    node.children[idx] = self._generate_random_program(max_depth=3)
                else:
                    for child in node.children:
                        self._subtree_mutate(child)
        except Exception as e:
            raise  # Extended with error handling
    
    def _shrink_mutate(self, node: ProgramNode):
        """Replace a node with a terminal."""
        if node.children and random.random() < 0.2:
            idx = random.randrange(len(node.children))
            node.children[idx] = ProgramNode(NodeType.CONSTANT, value=random.uniform(-1, 1))
        else:
            for child in node.children:
                self._shrink_mutate(child)
    
    def _expand_mutate(self, node: ProgramNode):
        """Replace a terminal with a subtree."""
        if not node.children and random.random() < 0.3:
            # Can't expand in place, mutation happens at parent level
            pass
        
        for i, child in enumerate(node.children):
            if not child.children and random.random() < 0.2:
                node.children[i] = self._generate_random_program(max_depth=2)
            else:
                self._expand_mutate(child)
    
    def _crossover(self, parent1: Gene, parent2: Gene) -> Gene:
        """Create offspring through crossover."""
        child_program = parent1.program.clone()
        
        # Swap a random subtree from parent2
        if parent2.program.children:
            donor = random.choice(parent2.program.children).clone()
            self._inject_subtree(child_program, donor)
        
        return Gene(
            id=hashlib.sha256(f"child:{parent1.id}:{parent2.id}:{random.random()}".encode()).hexdigest()[:12],
            name=f"child_{parent1.name}_{parent2.name}"[:30],
            program=child_program,
            gene_type=random.choice([parent1.gene_type, parent2.gene_type]),
            base_expression=(parent1.base_expression + parent2.base_expression) / 2,
            parent_ids=[parent1.id, parent2.id],
            generation=max(parent1.generation, parent2.generation) + 1
        )
    
    def _inject_subtree(self, target: ProgramNode, subtree: ProgramNode):
        """Inject a subtree at a random position."""
        if target.children and random.random() < 0.5:
            idx = random.randrange(len(target.children))
            target.children[idx] = subtree
        elif target.children:
            self._inject_subtree(random.choice(target.children), subtree)
    
    def update_fitness(self, gene_fitnesses: Dict[str, float]):
        """Update gene fitness contributions."""
        for gene_id, fitness in gene_fitnesses.items():
            if gene_id in self.genes:
                gene = self.genes[gene_id]
                gene.fitness_contribution = 0.9 * gene.fitness_contribution + 0.1 * fitness
                gene.fitness_history.append(fitness)
                if len(gene.fitness_history) > 50:
                    gene.fitness_history = gene.fitness_history[-50:]
        
        self.total_fitness = sum(g.fitness_contribution for g in self.genes.values())
        self.fitness_history.append(self.total_fitness)
    
    def get_stats(self) -> Dict:
        """Get genome statistics."""
        gene_types = {}
        for gene in self.genes.values():
            gene_types[gene.gene_type] = gene_types.get(gene.gene_type, 0) + 1
        
        return {
            'total_genes': len(self.genes),
            'gene_types': gene_types,
            'total_fitness': self.total_fitness,
            'genes_created': self.genes_created,
            'genes_deleted': self.genes_deleted,
            'total_mutations': self.total_mutations,
            'avg_generation': sum(g.generation for g in self.genes.values()) / max(1, len(self.genes)),
            'avg_expression_count': sum(g.expression_count for g in self.genes.values()) / max(1, len(self.genes)),
            'regulatory_connections': sum(len(g.regulators) for g in self.genes.values())
        }
    
    def to_dict(self) -> Dict:
        return {
            'genes': {gid: g.to_dict() for gid, g in self.genes.items()},
            'expression_order': self.expression_order,
            'total_fitness': self.total_fitness,
            'fitness_history': self.fitness_history[-100:],
            'genes_created': self.genes_created,
            'genes_deleted': self.genes_deleted,
            'total_mutations': self.total_mutations,
            'max_genes': self.max_genes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MetaGenome':
        genome = cls(max_genes=data.get('max_genes', 1000))
        genome.genes = {gid: Gene.from_dict(g) for gid, g in data.get('genes', {}).items()}
        genome.expression_order = data.get('expression_order', [])
        genome.total_fitness = data.get('total_fitness', 0.0)
        genome.fitness_history = data.get('fitness_history', [])
        genome.genes_created = data.get('genes_created', 0)
        genome.genes_deleted = data.get('genes_deleted', 0)
        genome.total_mutations = data.get('total_mutations', 0)
        
        if not genome.expression_order:
            genome._update_expression_order()
        
        return genome
