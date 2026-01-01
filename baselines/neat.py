"""
NEAT: NeuroEvolution of Augmenting Topologies

Kenneth O. Stanley and Risto Miikkulainen, 2002

Evolves both network topology and weights through:
- Complexification (starting minimal, adding structure)
- Historical markings for crossover alignment
- Speciation to protect innovation
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum


class NodeType(Enum):
    """Type of neural network node."""
    INPUT = "input"
    HIDDEN = "hidden"
    OUTPUT = "output"
    BIAS = "bias"


@dataclass
class NEATNode:
    """Node in NEAT network."""
    node_id: int
    node_type: NodeType
    activation: float = 0.0
    bias: float = 0.0

    def activate(self, x: float) -> float:
        """Sigmoid activation function."""
        return 1.0 / (1.0 + math.exp(-4.9 * (x + self.bias)))


@dataclass
class NEATConnection:
    """Connection gene in NEAT."""
    innovation_number: int
    from_node: int
    to_node: int
    weight: float
    enabled: bool = True

    def copy(self) -> 'NEATConnection':
        """Create a copy of this connection."""
        return NEATConnection(
            innovation_number=self.innovation_number,
            from_node=self.from_node,
            to_node=self.to_node,
            weight=self.weight,
            enabled=self.enabled
        )


@dataclass
class NEATGenome:
    """NEAT genome encoding a neural network."""
    genome_id: int
    nodes: Dict[int, NEATNode] = field(default_factory=dict)
    connections: Dict[int, NEATConnection] = field(default_factory=dict)
    fitness: float = 0.0
    adjusted_fitness: float = 0.0
    species_id: Optional[int] = None

    def activate(self, inputs: List[float]) -> List[float]:
        """
        Activate the network with given inputs.

        Returns outputs from output nodes.
        """
        # Reset all activations
        for node in self.nodes.values():
            node.activation = 0.0

        # Set input nodes
        input_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.INPUT]
        for i, node in enumerate(input_nodes):
            if i < len(inputs):
                node.activation = inputs[i]

        # Set bias node
        bias_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.BIAS]
        for node in bias_nodes:
            node.activation = 1.0

        # Propagate through network (assumes feed-forward)
        # Sort nodes by type: input, bias, hidden, output
        sorted_nodes = []
        for node_type in [NodeType.INPUT, NodeType.BIAS, NodeType.HIDDEN, NodeType.OUTPUT]:
            sorted_nodes.extend([n for n in self.nodes.values() if n.node_type == node_type])

        # Activate each node
        for node in sorted_nodes:
            if node.node_type in [NodeType.INPUT, NodeType.BIAS]:
                continue

            # Sum incoming connections
            incoming_sum = 0.0
            for conn in self.connections.values():
                if conn.enabled and conn.to_node == node.node_id:
                    from_node = self.nodes[conn.from_node]
                    incoming_sum += from_node.activation * conn.weight

            node.activation = node.activate(incoming_sum)

        # Return output activations
        output_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.OUTPUT]
        return [node.activation for node in sorted(output_nodes, key=lambda n: n.node_id)]

    def copy(self) -> 'NEATGenome':
        """Create a deep copy of this genome."""
        new_genome = NEATGenome(genome_id=self.genome_id)

        # Copy nodes
        for node_id, node in self.nodes.items():
            new_genome.nodes[node_id] = NEATNode(
                node_id=node.node_id,
                node_type=node.node_type,
                activation=0.0,
                bias=node.bias
            )

        # Copy connections
        for inn_num, conn in self.connections.items():
            new_genome.connections[inn_num] = conn.copy()

        new_genome.fitness = self.fitness
        new_genome.adjusted_fitness = self.adjusted_fitness
        new_genome.species_id = self.species_id

        return new_genome

    def distance(self, other: 'NEATGenome', c1: float = 1.0, c2: float = 1.0, c3: float = 0.4) -> float:
        """
        Calculate genetic distance for speciation.

        δ = c1*E/N + c2*D/N + c3*W̄

        E: excess genes, D: disjoint genes, W̄: average weight difference
        """
        # Get innovation numbers
        innovations1 = set(self.connections.keys())
        innovations2 = set(other.connections.keys())

        if not innovations1 and not innovations2:
            return 0.0

        # Find matching, disjoint, and excess
        matching = innovations1 & innovations2
        max_inn1 = max(innovations1) if innovations1 else 0
        max_inn2 = max(innovations2) if innovations2 else 0

        # Disjoint: non-matching within range of both genomes
        # Excess: beyond range of smaller genome
        disjoint = 0
        excess = 0

        for inn in innovations1 - matching:
            if inn < max_inn2:
                disjoint += 1
            else:
                excess += 1

        for inn in innovations2 - matching:
            if inn < max_inn1:
                disjoint += 1
            else:
                excess += 1

        # Average weight difference for matching genes
        weight_diff = 0.0
        if matching:
            for inn in matching:
                weight_diff += abs(self.connections[inn].weight - other.connections[inn].weight)
            weight_diff /= len(matching)

        # Normalize by genome size
        N = max(len(innovations1), len(innovations2), 1)

        distance = c1 * excess / N + c2 * disjoint / N + c3 * weight_diff

        return distance


@dataclass
class Species:
    """Species in NEAT population."""
    species_id: int
    representative: NEATGenome
    members: List[NEATGenome] = field(default_factory=list)
    age: int = 0
    best_fitness: float = 0.0
    generations_since_improvement: int = 0
    offspring_allocation: int = 0


class InnovationTracker:
    """Tracks innovation numbers for structural mutations."""

    def __init__(self):
        self.innovations: Dict[Tuple[int, int], int] = {}
        self.next_innovation = 0
        self.next_node_id = 0

    def get_innovation(self, from_node: int, to_node: int) -> int:
        """Get or create innovation number for connection."""
        key = (from_node, to_node)
        if key not in self.innovations:
            self.innovations[key] = self.next_innovation
            self.next_innovation += 1
        return self.innovations[key]

    def get_node_id(self) -> int:
        """Get next node ID."""
        node_id = self.next_node_id
        self.next_node_id += 1
        return node_id


class NEAT:
    """
    NEAT: NeuroEvolution of Augmenting Topologies

    Key features:
    - Start with minimal structure, complexify through evolution
    - Historical markings for crossover alignment
    - Speciation to protect innovation
    """

    def __init__(
        self,
        num_inputs: int,
        num_outputs: int,
        population_size: int = 150,
        compatibility_threshold: float = 3.0,
        weight_mutate_rate: float = 0.8,
        add_node_rate: float = 0.03,
        add_connection_rate: float = 0.05,
        crossover_rate: float = 0.75
    ):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.population_size = population_size
        self.compatibility_threshold = compatibility_threshold
        self.weight_mutate_rate = weight_mutate_rate
        self.add_node_rate = add_node_rate
        self.add_connection_rate = add_connection_rate
        self.crossover_rate = crossover_rate

        self.innovation_tracker = InnovationTracker()
        self.population: List[NEATGenome] = []
        self.species: List[Species] = []
        self.generation = 0
        self.next_genome_id = 0
        self.next_species_id = 0

        # Initialize population
        self._initialize_population()

    def _initialize_population(self):
        """Create initial minimal population."""
        for _ in range(self.population_size):
            genome = self._create_minimal_genome()
            self.population.append(genome)

    def _create_minimal_genome(self) -> NEATGenome:
        """Create minimal genome with inputs and outputs only."""
        genome = NEATGenome(genome_id=self.next_genome_id)
        self.next_genome_id += 1

        # Create input nodes
        for i in range(self.num_inputs):
            node_id = self.innovation_tracker.get_node_id()
            genome.nodes[node_id] = NEATNode(node_id, NodeType.INPUT)

        # Create bias node
        bias_id = self.innovation_tracker.get_node_id()
        genome.nodes[bias_id] = NEATNode(bias_id, NodeType.BIAS)

        # Create output nodes
        output_start = len(genome.nodes)
        for i in range(self.num_outputs):
            node_id = self.innovation_tracker.get_node_id()
            genome.nodes[node_id] = NEATNode(node_id, NodeType.OUTPUT)

        # Create initial connections (inputs to outputs)
        input_ids = [nid for nid, n in genome.nodes.items() if n.node_type in [NodeType.INPUT, NodeType.BIAS]]
        output_ids = [nid for nid, n in genome.nodes.items() if n.node_type == NodeType.OUTPUT]

        for in_id in input_ids:
            for out_id in output_ids:
                inn = self.innovation_tracker.get_innovation(in_id, out_id)
                weight = random.uniform(-1.0, 1.0)
                genome.connections[inn] = NEATConnection(inn, in_id, out_id, weight)

        return genome

    def evolve(self, fitness_fn, generations: int = 100) -> NEATGenome:
        """
        Evolve population for given generations.

        fitness_fn: function that takes genome and returns fitness
        """
        for gen in range(generations):
            # Evaluate fitness
            for genome in self.population:
                genome.fitness = fitness_fn(genome)

            # Speciate
            self._speciate()

            # Calculate adjusted fitness
            self._calculate_adjusted_fitness()

            # Reproduce
            self.population = self._reproduce()

            self.generation += 1

        # Return best genome
        return max(self.population, key=lambda g: g.fitness)

    def _speciate(self):
        """Assign genomes to species based on compatibility."""
        # Clear existing species members
        for species in self.species:
            species.members = []

        # Assign each genome to a species
        for genome in self.population:
            # Try to find compatible species
            placed = False
            for species in self.species:
                distance = genome.distance(species.representative)
                if distance < self.compatibility_threshold:
                    species.members.append(genome)
                    genome.species_id = species.species_id
                    placed = True
                    break

            # Create new species if no compatible one found
            if not placed:
                new_species = Species(
                    species_id=self.next_species_id,
                    representative=genome.copy()
                )
                self.next_species_id += 1
                new_species.members.append(genome)
                genome.species_id = new_species.species_id
                self.species.append(new_species)

        # Remove empty species
        self.species = [s for s in self.species if s.members]

        # Update species age and best fitness
        for species in self.species:
            species.age += 1
            best = max(species.members, key=lambda g: g.fitness)
            if best.fitness > species.best_fitness:
                species.best_fitness = best.fitness
                species.generations_since_improvement = 0
            else:
                species.generations_since_improvement += 1

    def _calculate_adjusted_fitness(self):
        """Calculate fitness sharing within species."""
        for species in self.species:
            for genome in species.members:
                # Fitness sharing: divide by species size
                genome.adjusted_fitness = genome.fitness / len(species.members)

    def _reproduce(self) -> List[NEATGenome]:
        """Create next generation through reproduction."""
        new_population = []

        # Calculate total adjusted fitness
        total_adjusted = sum(g.adjusted_fitness for g in self.population)
        if total_adjusted == 0:
            total_adjusted = 1.0

        # Allocate offspring to species
        for species in self.species:
            species_adjusted = sum(g.adjusted_fitness for g in species.members)
            species.offspring_allocation = int(
                (species_adjusted / total_adjusted) * self.population_size
            )

        # Produce offspring for each species
        for species in self.species:
            if not species.members:
                continue

            # Sort by fitness
            species.members.sort(key=lambda g: g.fitness, reverse=True)

            # Elite: always keep best
            if species.offspring_allocation > 0:
                new_population.append(species.members[0].copy())

            # Produce remaining offspring
            for _ in range(species.offspring_allocation - 1):
                if random.random() < self.crossover_rate and len(species.members) > 1:
                    # Crossover
                    parent1 = self._tournament_select(species.members)
                    parent2 = self._tournament_select(species.members)
                    child = self._crossover(parent1, parent2)
                else:
                    # Mutation only
                    parent = self._tournament_select(species.members)
                    child = parent.copy()

                # Mutate
                self._mutate(child)
                new_population.append(child)

        # Fill remaining slots
        while len(new_population) < self.population_size:
            if self.population:
                parent = random.choice(self.population)
                child = parent.copy()
                self._mutate(child)
                new_population.append(child)
            else:
                new_population.append(self._create_minimal_genome())

        return new_population[:self.population_size]

    def _tournament_select(self, genomes: List[NEATGenome], k: int = 3) -> NEATGenome:
        """Select genome via tournament selection."""
        tournament = random.sample(genomes, min(k, len(genomes)))
        return max(tournament, key=lambda g: g.fitness)

    def _crossover(self, parent1: NEATGenome, parent2: NEATGenome) -> NEATGenome:
        """Crossover two genomes, aligning by innovation numbers."""
        # More fit parent contributes disjoint/excess genes
        if parent1.fitness >= parent2.fitness:
            fit_parent = parent1
            other_parent = parent2
        else:
            fit_parent = parent2
            other_parent = parent1

        child = NEATGenome(genome_id=self.next_genome_id)
        self.next_genome_id += 1

        # Copy nodes from fit parent
        for node_id, node in fit_parent.nodes.items():
            child.nodes[node_id] = NEATNode(
                node_id=node.node_id,
                node_type=node.node_type,
                bias=node.bias
            )

        # Crossover connections
        innovations1 = set(parent1.connections.keys())
        innovations2 = set(parent2.connections.keys())
        matching = innovations1 & innovations2

        # Matching genes: random choice
        for inn in matching:
            conn = random.choice([parent1.connections[inn], parent2.connections[inn]])
            child.connections[inn] = conn.copy()

        # Disjoint/excess genes from fit parent
        for inn in innovations1 - matching:
            child.connections[inn] = parent1.connections[inn].copy()

        if parent2.fitness > parent1.fitness:
            for inn in innovations2 - matching:
                child.connections[inn] = parent2.connections[inn].copy()

        return child

    def _mutate(self, genome: NEATGenome):
        """Apply mutations to genome."""
        # Weight mutation
        if random.random() < self.weight_mutate_rate:
            self._mutate_weights(genome)

        # Add node mutation
        if random.random() < self.add_node_rate:
            self._mutate_add_node(genome)

        # Add connection mutation
        if random.random() < self.add_connection_rate:
            self._mutate_add_connection(genome)

    def _mutate_weights(self, genome: NEATGenome):
        """Mutate connection weights."""
        for conn in genome.connections.values():
            if random.random() < 0.9:
                # Perturb
                conn.weight += random.gauss(0, 0.5)
                conn.weight = max(-5.0, min(5.0, conn.weight))
            else:
                # Replace
                conn.weight = random.uniform(-1.0, 1.0)

    def _mutate_add_node(self, genome: NEATGenome):
        """Add a node by splitting a connection."""
        if not genome.connections:
            return

        # Pick random connection
        conn = random.choice(list(genome.connections.values()))

        # Disable old connection
        conn.enabled = False

        # Create new node
        new_node_id = self.innovation_tracker.get_node_id()
        genome.nodes[new_node_id] = NEATNode(new_node_id, NodeType.HIDDEN)

        # Create two new connections
        # Connection from old source to new node (weight 1.0)
        inn1 = self.innovation_tracker.get_innovation(conn.from_node, new_node_id)
        genome.connections[inn1] = NEATConnection(inn1, conn.from_node, new_node_id, 1.0)

        # Connection from new node to old target (old weight)
        inn2 = self.innovation_tracker.get_innovation(new_node_id, conn.to_node)
        genome.connections[inn2] = NEATConnection(inn2, new_node_id, conn.to_node, conn.weight)

    def _mutate_add_connection(self, genome: NEATGenome):
        """Add a new connection between nodes."""
        # Get all possible connections
        input_hidden = [nid for nid, n in genome.nodes.items()
                       if n.node_type in [NodeType.INPUT, NodeType.BIAS, NodeType.HIDDEN]]
        hidden_output = [nid for nid, n in genome.nodes.items()
                        if n.node_type in [NodeType.HIDDEN, NodeType.OUTPUT]]

        if not input_hidden or not hidden_output:
            return

        # Try to find valid connection (avoiding recurrent for now)
        for _ in range(20):
            from_node = random.choice(input_hidden)
            to_node = random.choice(hidden_output)

            if from_node == to_node:
                continue

            # Check if connection already exists
            inn = self.innovation_tracker.get_innovation(from_node, to_node)
            if inn in genome.connections:
                continue

            # Add connection
            weight = random.uniform(-1.0, 1.0)
            genome.connections[inn] = NEATConnection(inn, from_node, to_node, weight)
            break

    def get_stats(self) -> Dict[str, Any]:
        """Get current population statistics."""
        if not self.population:
            return {}

        fitnesses = [g.fitness for g in self.population]

        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'num_species': len(self.species),
            'max_fitness': max(fitnesses),
            'avg_fitness': sum(fitnesses) / len(fitnesses),
            'min_fitness': min(fitnesses),
            'avg_genome_size': sum(len(g.connections) for g in self.population) / len(self.population)
        }
