"""
AEGIS-2 Primordial: Bootstrap from Almost Nothing

This module implements a bootstrap process where the system
starts with minimal structure and discovers/builds its own complexity.

The idea: Instead of pre-defining all the subsystems, we start with
just a few primitives and let the system discover useful structures
through exploration.

Starting conditions:
- A small set of atomic operations
- Random combination rules
- Selection pressure toward "interestingness"
- No pre-defined goals, patterns, or structures

The system must discover:
- Useful patterns through random combination
- Goal-like behavior through selection
- Self-organization through feedback

This is closer to genuine emergence because the structures
aren't designed - they're discovered.
"""

import random
import math
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any, Optional, Callable
from datetime import datetime
import json
from pathlib import Path


# ============================================================================
# ATOMIC PRIMITIVES - The minimal starting point
# ============================================================================

@dataclass
class Atom:
    """The most basic unit - an atomic operation."""
    id: str
    name: str
    arity: int  # Number of inputs
    operation: str  # Simple operation string
    
    def execute(self, inputs: List[float]) -> float:
        """Execute the atomic operation."""
        try:
            if self.operation == 'add' and len(inputs) >= 2:
                return inputs[0] + inputs[1]
            elif self.operation == 'mul' and len(inputs) >= 2:
                return inputs[0] * inputs[1]
            elif self.operation == 'sub' and len(inputs) >= 2:
                return inputs[0] - inputs[1]
            elif self.operation == 'div' and len(inputs) >= 2:
                return inputs[0] / (inputs[1] + 0.001)
            elif self.operation == 'neg':
                return -inputs[0] if inputs else 0
            elif self.operation == 'abs':
                return abs(inputs[0]) if inputs else 0
            elif self.operation == 'sin':
                return math.sin(inputs[0]) if inputs else 0
            elif self.operation == 'cos':
                return math.cos(inputs[0]) if inputs else 0
            elif self.operation == 'exp':
                return math.exp(min(inputs[0], 10)) if inputs else 1
            elif self.operation == 'log':
                return math.log(abs(inputs[0]) + 0.001) if inputs else 0
            elif self.operation == 'max' and len(inputs) >= 2:
                return max(inputs[0], inputs[1])
            elif self.operation == 'min' and len(inputs) >= 2:
                return min(inputs[0], inputs[1])
            elif self.operation == 'avg' and inputs:
                return sum(inputs) / len(inputs)
            elif self.operation == 'id':
                return inputs[0] if inputs else 0
            elif self.operation == 'const':
                return 1.0
            elif self.operation == 'rand':
                return random.random()
            else:
                return 0.0
        except:
            return 0.0


# The primordial soup - basic atoms that exist at the start
PRIMORDIAL_ATOMS = [
    Atom('a_add', 'add', 2, 'add'),
    Atom('a_mul', 'mul', 2, 'mul'),
    Atom('a_sub', 'sub', 2, 'sub'),
    Atom('a_div', 'div', 2, 'div'),
    Atom('a_neg', 'neg', 1, 'neg'),
    Atom('a_abs', 'abs', 1, 'abs'),
    Atom('a_sin', 'sin', 1, 'sin'),
    Atom('a_cos', 'cos', 1, 'cos'),
    Atom('a_max', 'max', 2, 'max'),
    Atom('a_min', 'min', 2, 'min'),
    Atom('a_id', 'id', 1, 'id'),
    Atom('a_const', 'const', 0, 'const'),
    Atom('a_rand', 'rand', 0, 'rand'),
]


# ============================================================================
# EMERGENT STRUCTURES - Built from atoms
# ============================================================================

@dataclass
class Molecule:
    """
    A molecule - combination of atoms.
    
    These emerge from random combination of atoms.
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    
    # Structure
    atoms: List[str] = field(default_factory=list)  # Atom IDs in execution order
    connections: List[Tuple[int, int, int]] = field(default_factory=list)  # (from_idx, to_idx, input_slot)
    
    # Metrics
    fitness: float = 0.5
    complexity: float = 1.0
    uses: int = 0
    created_at: int = 0
    
    def execute(self, inputs: List[float], atom_lookup: Dict[str, Atom]) -> float:
        """Execute the molecule."""
        if not self.atoms:
            return 0.0
        
        # Build execution buffer
        values = list(inputs) + [0.0] * len(self.atoms)
        input_count = len(inputs)
        
        # Execute each atom
        for i, atom_id in enumerate(self.atoms):
            atom = atom_lookup.get(atom_id)
            if not atom:
                continue
            
            # Gather inputs for this atom
            atom_inputs = []
            for (from_idx, to_idx, slot) in self.connections:
                if to_idx == i:
                    if from_idx < len(values):
                        atom_inputs.append(values[from_idx])
            
            # Fill with zeros if not enough inputs
            while len(atom_inputs) < atom.arity:
                atom_inputs.append(0.0)
            
            # Execute and store result
            result = atom.execute(atom_inputs)
            values[input_count + i] = result
        
        # Return last value
        return values[-1] if values else 0.0


@dataclass
class Organism:
    """
    An organism - collection of molecules with behavior.
    
    These emerge from selection of useful molecule combinations.
    """
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    
    # Structure
    molecules: Dict[str, Molecule] = field(default_factory=dict)
    active_molecule: Optional[str] = None
    
    # State
    energy: float = 100.0
    age: int = 0
    
    # Memory (emergent)
    memory: List[float] = field(default_factory=list)
    
    # Metrics
    fitness: float = 0.5
    novelty: float = 0.5
    
    def step(self, inputs: List[float], atom_lookup: Dict[str, Atom]) -> float:
        """Take one step."""
        self.age += 1
        
        if not self.molecules:
            return 0.0
        
        # Select molecule to use
        if self.active_molecule and self.active_molecule in self.molecules:
            mol = self.molecules[self.active_molecule]
        else:
            mol = random.choice(list(self.molecules.values()))
        
        # Execute
        mol.uses += 1
        result = mol.execute(inputs + self.memory[-5:], atom_lookup)
        
        # Update memory
        self.memory.append(result)
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
        
        # Energy cost
        self.energy -= 0.1 + mol.complexity * 0.01
        
        return result


# ============================================================================
# THE PRIMORDIAL SOUP - Where it all happens
# ============================================================================

class PrimordialSoup:
    """
    The primordial soup where structures emerge from nothing.
    
    This is the main simulation environment. It contains:
    - Atoms (fixed primitives)
    - Molecules (emerging combinations)
    - Organisms (selected collections)
    
    New structures emerge through:
    - Random combination
    - Mutation
    - Selection based on "interestingness"
    """
    
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        
        # Configuration
        self.max_molecules = config.get('max_molecules', 1000)
        self.max_organisms = config.get('max_organisms', 50)
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.combination_rate = config.get('combination_rate', 0.2)
        
        # The atoms - our fixed primitives
        self.atoms: Dict[str, Atom] = {a.id: a for a in PRIMORDIAL_ATOMS}
        
        # Molecules - emerging structures
        self.molecules: Dict[str, Molecule] = {}
        
        # Organisms - selected collections
        self.organisms: Dict[str, Organism] = {}
        
        # State
        self.cycle: int = 0
        self.total_molecules_created: int = 0
        self.total_organisms_created: int = 0
        
        # History
        self.behavior_archive: List[Tuple[float, ...]] = []
        self.emergence_events: List[Dict] = []
        
        # Metrics
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Bootstrap
        self._initialize()
    
    def _initialize(self):
        """Create initial random molecules and organisms."""
        # Create some random molecules
        for _ in range(20):
            mol = self._random_molecule()
            self.molecules[mol.id] = mol
        
        # Create initial organisms
        for _ in range(10):
            org = self._random_organism()
            self.organisms[org.id] = org
    
    def _random_molecule(self, complexity: int = 3) -> Molecule:
        """Create a random molecule."""
        atom_ids = [random.choice(list(self.atoms.keys())) 
                   for _ in range(complexity)]
        
        # Create random connections
        connections = []
        for i in range(len(atom_ids)):
            # Connect from previous outputs or inputs
            num_inputs = self.atoms[atom_ids[i]].arity
            for slot in range(num_inputs):
                source = random.randint(0, i + 1)  # +1 for input
                connections.append((source, i, slot))
        
        mol = Molecule(
            atoms=atom_ids,
            connections=connections,
            complexity=len(atom_ids),
            created_at=self.cycle
        )
        
        self.total_molecules_created += 1
        return mol
    
    def _random_organism(self) -> Organism:
        """Create a random organism."""
        org = Organism()
        
        # Give it some random molecules
        for _ in range(random.randint(1, 5)):
            if self.molecules:
                mol = random.choice(list(self.molecules.values()))
                org.molecules[mol.id] = mol
            else:
                mol = self._random_molecule()
                org.molecules[mol.id] = mol
        
        self.total_organisms_created += 1
        return org
    
    def _combine_molecules(self, mol1: Molecule, mol2: Molecule) -> Molecule:
        """Combine two molecules into a new one."""
        new_atoms = mol1.atoms[:len(mol1.atoms)//2] + mol2.atoms[len(mol2.atoms)//2:]
        
        # Rebuild connections
        connections = []
        for i in range(len(new_atoms)):
            num_inputs = self.atoms[new_atoms[i]].arity
            for slot in range(num_inputs):
                source = random.randint(0, i + 1)
                connections.append((source, i, slot))
        
        mol = Molecule(
            atoms=new_atoms,
            connections=connections,
            complexity=len(new_atoms),
            created_at=self.cycle
        )
        
        self.total_molecules_created += 1
        return mol
    
    def _mutate_molecule(self, mol: Molecule) -> Molecule:
        """Mutate a molecule."""
        new_atoms = list(mol.atoms)
        new_connections = list(mol.connections)
        
        mutation_type = random.choice(['add', 'remove', 'change', 'reconnect'])
        
        if mutation_type == 'add' and len(new_atoms) < 10:
            new_atoms.append(random.choice(list(self.atoms.keys())))
            i = len(new_atoms) - 1
            num_inputs = self.atoms[new_atoms[i]].arity
            for slot in range(num_inputs):
                source = random.randint(0, i)
                new_connections.append((source, i, slot))
        
        elif mutation_type == 'remove' and len(new_atoms) > 1:
            idx = random.randint(0, len(new_atoms) - 1)
            new_atoms.pop(idx)
            new_connections = [(f, t, s) for f, t, s in new_connections 
                              if f != idx + 1 and t != idx]
        
        elif mutation_type == 'change' and new_atoms:
            idx = random.randint(0, len(new_atoms) - 1)
            new_atoms[idx] = random.choice(list(self.atoms.keys()))
        
        elif mutation_type == 'reconnect' and new_connections:
            idx = random.randint(0, len(new_connections) - 1)
            f, t, s = new_connections[idx]
            new_connections[idx] = (random.randint(0, t), t, s)
        
        new_mol = Molecule(
            atoms=new_atoms,
            connections=new_connections,
            complexity=len(new_atoms),
            created_at=self.cycle
        )
        
        self.total_molecules_created += 1
        return new_mol
    
    def _evaluate_behavior(self, organism: Organism, test_inputs: List[List[float]]) -> Tuple[float, ...]:
        """Evaluate organism behavior on test inputs."""
        outputs = []
        for inputs in test_inputs:
            out = organism.step(inputs, self.atoms)
            outputs.append(out)
        
        return tuple(outputs)
    
    def _novelty_score(self, behavior: Tuple[float, ...]) -> float:
        """Calculate novelty of behavior relative to archive."""
        if not self.behavior_archive:
            return 1.0
        
        # Distance to nearest neighbors
        distances = []
        for archived in self.behavior_archive[-100:]:
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(behavior, archived)))
            distances.append(dist)
        
        distances.sort()
        k = min(5, len(distances))
        
        return sum(distances[:k]) / k if k > 0 else 1.0
    
    def _interestingness(self, organism: Organism, behavior: Tuple[float, ...]) -> float:
        """
        Calculate "interestingness" of an organism.
        
        This is our fitness function, but it rewards:
        - Novelty (being different)
        - Complexity (but not too much)
        - Consistency (not just noise)
        """
        novelty = self._novelty_score(behavior)
        
        # Complexity bonus
        total_complexity = sum(m.complexity for m in organism.molecules.values())
        complexity_score = 1.0 / (1.0 + abs(total_complexity - 5))  # Sweet spot around 5
        
        # Consistency (low variance in output)
        if len(behavior) > 1:
            mean = sum(behavior) / len(behavior)
            variance = sum((x - mean) ** 2 for x in behavior) / len(behavior)
            consistency = 1.0 / (1.0 + variance)
        else:
            consistency = 0.5
        
        # Non-trivial output (not all zeros or ones)
        if all(abs(x) < 0.01 for x in behavior):
            non_trivial = 0.1
        elif all(abs(x - 1.0) < 0.01 for x in behavior):
            non_trivial = 0.1
        else:
            non_trivial = 1.0
        
        return (novelty * 0.4 + complexity_score * 0.2 + 
                consistency * 0.2 + non_trivial * 0.2)
    
    def step(self) -> Dict[str, Any]:
        """Run one step of the primordial soup."""
        self.cycle += 1
        
        results = {
            'cycle': self.cycle,
            'molecules': len(self.molecules),
            'organisms': len(self.organisms),
            'emergence': []
        }
        
        # Generate test inputs
        test_inputs = [[random.random() * 2 - 1 for _ in range(3)] 
                      for _ in range(5)]
        
        # Evaluate all organisms
        organism_scores = []
        for org_id, org in list(self.organisms.items()):
            behavior = self._evaluate_behavior(org, test_inputs)
            score = self._interestingness(org, behavior)
            org.fitness = score
            org.novelty = self._novelty_score(behavior)
            organism_scores.append((org_id, score, behavior))
            
            # Archive novel behaviors
            if org.novelty > 0.5:
                self.behavior_archive.append(behavior)
        
        # Selection - remove low-fitness organisms
        organism_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top organisms
        survivors = set(org_id for org_id, _, _ in organism_scores[:self.max_organisms // 2])
        
        for org_id in list(self.organisms.keys()):
            if org_id not in survivors and self.organisms[org_id].energy <= 0:
                del self.organisms[org_id]
        
        # Reproduction - create offspring from top organisms
        for org_id, score, _ in organism_scores[:10]:
            if org_id in self.organisms and len(self.organisms) < self.max_organisms:
                parent = self.organisms[org_id]
                
                # Create offspring with mutations
                child = Organism()
                child.molecules = {mid: self._mutate_molecule(mol) 
                                  for mid, mol in parent.molecules.items()
                                  if random.random() > 0.3}
                
                if child.molecules:
                    self.organisms[child.id] = child
                    self.total_organisms_created += 1
        
        # Molecule evolution
        if random.random() < self.combination_rate and len(self.molecules) >= 2:
            mol1, mol2 = random.sample(list(self.molecules.values()), 2)
            new_mol = self._combine_molecules(mol1, mol2)
            if len(self.molecules) < self.max_molecules:
                self.molecules[new_mol.id] = new_mol
        
        # Molecule mutation
        if random.random() < self.mutation_rate and self.molecules:
            mol = random.choice(list(self.molecules.values()))
            new_mol = self._mutate_molecule(mol)
            if len(self.molecules) < self.max_molecules:
                self.molecules[new_mol.id] = new_mol
        
        # Random new molecules
        if random.random() < 0.1:
            new_mol = self._random_molecule(random.randint(2, 6))
            if len(self.molecules) < self.max_molecules:
                self.molecules[new_mol.id] = new_mol
        
        # Prune unused molecules
        used_mols = set()
        for org in self.organisms.values():
            used_mols.update(org.molecules.keys())
        
        unused = [mid for mid in self.molecules if mid not in used_mols]
        for mid in unused[:len(unused)//2]:  # Remove half of unused
            if mid in self.molecules and self.molecules[mid].uses == 0:
                del self.molecules[mid]
        
        # Check for emergence
        if organism_scores:
            best_score = organism_scores[0][1]
            if best_score > 0.8:
                results['emergence'].append({
                    'type': 'high_fitness_organism',
                    'score': best_score,
                    'cycle': self.cycle
                })
                self.emergence_events.append(results['emergence'][-1])
        
        # Track metrics
        self.metrics['avg_fitness'].append(
            sum(s for _, s, _ in organism_scores) / len(organism_scores) if organism_scores else 0
        )
        self.metrics['molecule_count'].append(len(self.molecules))
        self.metrics['organism_count'].append(len(self.organisms))
        
        results['avg_fitness'] = self.metrics['avg_fitness'][-1]
        
        return results
    
    def run(self, cycles: int = 500, verbose: bool = True) -> List[Dict]:
        """Run the primordial soup simulation."""
        results = []
        
        if verbose:
            print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗ ██╗███╗   ███╗ ██████╗ ██████╗ ██████╗ ██╗ █████╗ ██╗     ║
║   ██╔══██╗██╔══██╗██║████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║██╔══██╗██║     ║
║   ██████╔╝██████╔╝██║██╔████╔██║██║   ██║██████╔╝██║  ██║██║███████║██║     ║
║   ██╔═══╝ ██╔══██╗██║██║╚██╔╝██║██║   ██║██╔══██╗██║  ██║██║██╔══██║██║     ║
║   ██║     ██║  ██║██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██████╔╝██║██║  ██║███████╗║
║   ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝║
║                                                                              ║
║                    Bootstrap from Almost Nothing                             ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Starting with:                                                              ║
║    • """ + f"{len(self.atoms):>3}" + """ atomic primitives (add, mul, sin, cos, ...)                      ║
║    • """ + f"{len(self.molecules):>3}" + """ random molecules                                                  ║
║    • """ + f"{len(self.organisms):>3}" + """ random organisms                                                  ║
║                                                                              ║
║  Selection pressure: "interestingness"                                       ║
║    = novelty + appropriate_complexity + consistency + non_triviality        ║
║                                                                              ║
║  Let's see what emerges...                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        for i in range(cycles):
            result = self.step()
            results.append(result)
            
            if verbose and i % 50 == 0:
                print(f"  Cycle {self.cycle:5d} │ "
                      f"Mols {len(self.molecules):4d} │ "
                      f"Orgs {len(self.organisms):3d} │ "
                      f"Fit {result['avg_fitness']:.3f} │ "
                      f"Archive {len(self.behavior_archive):4d}")
        
        if verbose:
            self._print_report()
        
        return results
    
    def _print_report(self):
        """Print final report."""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        PRIMORDIAL SOUP RESULTS                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Cycles run:              {self.cycle:>8}                                          ║
║  Total molecules created: {self.total_molecules_created:>8}                                          ║
║  Total organisms created: {self.total_organisms_created:>8}                                          ║
║                                                                              ║
║  Current state:                                                              ║
║    Molecules alive: {len(self.molecules):>8}                                               ║
║    Organisms alive: {len(self.organisms):>8}                                               ║
║    Behavior archive: {len(self.behavior_archive):>7}                                               ║
║                                                                              ║
║  Emergence events: {len(self.emergence_events):>9}                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        # Show best organisms
        if self.organisms:
            print("  Top organisms by fitness:")
            sorted_orgs = sorted(self.organisms.values(), 
                               key=lambda o: o.fitness, reverse=True)[:5]
            for i, org in enumerate(sorted_orgs):
                mol_count = len(org.molecules)
                total_complexity = sum(m.complexity for m in org.molecules.values())
                print(f"    {i+1}. {org.id[:10]} │ "
                      f"fitness={org.fitness:.3f} │ "
                      f"molecules={mol_count} │ "
                      f"complexity={total_complexity:.1f}")
        
        print()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            'cycle': self.cycle,
            'atoms': len(self.atoms),
            'molecules': len(self.molecules),
            'organisms': len(self.organisms),
            'total_molecules_created': self.total_molecules_created,
            'total_organisms_created': self.total_organisms_created,
            'behavior_archive_size': len(self.behavior_archive),
            'emergence_events': len(self.emergence_events),
            'avg_fitness': self.metrics['avg_fitness'][-1] if self.metrics['avg_fitness'] else 0
        }


def demo():
    """Demonstrate the primordial soup."""
    soup = PrimordialSoup()
    soup.run(cycles=500, verbose=True)
    
    print(f"\nFinal status:")
    status = soup.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    return soup


if __name__ == "__main__":
    demo()
