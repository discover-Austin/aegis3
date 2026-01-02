"""
Advanced RAF (Reflexively Autocatalytic and Food-generated) Set Detection

Implements sophisticated algorithms for detecting and analyzing autocatalytic closure:
1. RAF set detection (complete closure analysis)
2. maxRAF computation (largest RAF subset)
3. irreducible RAF (cannot be decomposed)
4. subRAF enumeration
5. Catalytic closure verification
6. Critical pathway analysis

Based on research by Hordijk, Steel, and Kauffman on autocatalytic sets.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any, FrozenSet
from collections import defaultdict, deque


@dataclass
class Reaction:
    """A catalyzed reaction in the network."""
    id: str
    reactants: Set[str]  # Input molecules
    products: Set[str]  # Output molecules
    catalysts: Set[str]  # Molecules that catalyze this reaction
    rate: float = 1.0

    def is_enabled(self, available: Set[str]) -> bool:
        """Check if reaction can occur given available molecules."""
        return self.reactants.issubset(available)

    def is_catalyzed(self, available: Set[str]) -> bool:
        """Check if at least one catalyst is available."""
        return len(self.catalysts & available) > 0


@dataclass
class RAFSet:
    """A Reflexively Autocatalytic and Food-generated set."""
    reactions: Set[str]  # Reaction IDs in this RAF
    molecules: Set[str]  # Molecules producible by this RAF
    food_set: Set[str]  # Food molecules (externally provided)
    is_raf: bool = False  # Whether this is a valid RAF
    is_max_raf: bool = False  # Whether this is maximal
    is_irreducible: bool = False  # Whether this is irreducible

    def size(self) -> int:
        """Number of reactions in RAF."""
        return len(self.reactions)

    def diversity(self) -> int:
        """Number of distinct molecules."""
        return len(self.molecules)


class RAFDetector:
    """
    Detects and analyzes RAF sets in catalytic networks.

    A set R of reactions is RAF if:
    1. Each reaction in R is catalyzed by at least one molecule produced by R
    2. All reactants can be produced starting from food set F
    """

    def __init__(
        self,
        reactions: List[Reaction],
        food_set: Set[str]
    ):
        """
        Initialize RAF detector.

        Args:
            reactions: List of all possible reactions
            food_set: Set of externally available molecules
        """
        self.reactions = {r.id: r for r in reactions}
        self.food_set = food_set

        # Build dependency graphs
        self._build_graphs()

    def _build_graphs(self):
        """Build dependency graphs for efficient RAF detection."""
        # Reaction -> products mapping
        self.reaction_products: Dict[str, Set[str]] = {}
        for rid, rxn in self.reactions.items():
            self.reaction_products[rid] = rxn.products

        # Molecule -> reactions that produce it
        self.producers: Dict[str, Set[str]] = defaultdict(set)
        for rid, rxn in self.reactions.items():
            for product in rxn.products:
                self.producers[product].add(rid)

        # Molecule -> reactions that need it as reactant
        self.consumers: Dict[str, Set[str]] = defaultdict(set)
        for rid, rxn in self.reactions.items():
            for reactant in rxn.reactants:
                self.consumers[reactant].add(rid)

        # Molecule -> reactions it catalyzes
        self.catalyst_map: Dict[str, Set[str]] = defaultdict(set)
        for rid, rxn in self.reactions.items():
            for catalyst in rxn.catalysts:
                self.catalyst_map[catalyst].add(rid)

    def closure(self, reaction_subset: Set[str]) -> Set[str]:
        """
        Compute closure: all molecules producible from food set using reactions.

        Returns set of reachable molecules.
        """
        reachable = self.food_set.copy()
        changed = True

        while changed:
            changed = False
            for rid in reaction_subset:
                rxn = self.reactions[rid]
                if rxn.is_enabled(reachable):
                    new_molecules = rxn.products - reachable
                    if new_molecules:
                        reachable.update(new_molecules)
                        changed = True

        return reachable

    def is_raf(self, reaction_subset: Set[str]) -> Tuple[bool, Set[str]]:
        """
        Check if a set of reactions forms a RAF.

        Returns:
            (is_raf, producible_molecules)
        """
        if not reaction_subset:
            return False, set()

        # Compute closure
        producible = self.closure(reaction_subset)

        # Check catalytic requirement
        for rid in reaction_subset:
            rxn = self.reactions[rid]

            # Must be catalyzed by something producible
            if not rxn.is_catalyzed(producible):
                return False, producible

            # Must be enabled by producible molecules
            if not rxn.is_enabled(producible):
                return False, producible

        return True, producible

    def find_raf_greedy(self) -> Optional[RAFSet]:
        """
        Find a RAF using greedy forward search.

        Starts with food set and adds reactions that:
        1. Can be enabled
        2. Are catalyzed by existing molecules
        3. Produce new molecules
        """
        raf_reactions = set()
        producible = self.food_set.copy()

        changed = True
        while changed:
            changed = False

            # Find candidate reactions
            candidates = []
            for rid, rxn in self.reactions.items():
                if rid in raf_reactions:
                    continue

                # Can it be enabled?
                if not rxn.is_enabled(producible):
                    continue

                # Is it catalyzed?
                if not rxn.is_catalyzed(producible):
                    continue

                # Does it produce something new?
                new_products = rxn.products - producible
                if new_products:
                    candidates.append((rid, len(new_products)))

            if candidates:
                # Add reaction that produces most new molecules
                best_rid = max(candidates, key=lambda x: x[1])[0]
                raf_reactions.add(best_rid)
                producible.update(self.reactions[best_rid].products)
                changed = True

        if raf_reactions:
            is_valid, molecules = self.is_raf(raf_reactions)
            return RAFSet(
                reactions=raf_reactions,
                molecules=molecules,
                food_set=self.food_set,
                is_raf=is_valid
            )

        return None

    def find_max_raf(self) -> Optional[RAFSet]:
        """
        Find maximal RAF (maxRAF) - largest possible RAF.

        Uses iterative expansion from RAF seed.
        """
        # Start with greedy RAF
        seed_raf = self.find_raf_greedy()
        if not seed_raf or not seed_raf.is_raf:
            return None

        max_reactions = seed_raf.reactions.copy()
        max_molecules = seed_raf.molecules.copy()

        # Try to expand
        changed = True
        while changed:
            changed = False

            for rid, rxn in self.reactions.items():
                if rid in max_reactions:
                    continue

                # Can we add this reaction?
                if rxn.is_enabled(max_molecules) and rxn.is_catalyzed(max_molecules):
                    # Tentatively add it
                    test_reactions = max_reactions | {rid}
                    is_valid, test_molecules = self.is_raf(test_reactions)

                    if is_valid:
                        max_reactions = test_reactions
                        max_molecules = test_molecules
                        changed = True

        return RAFSet(
            reactions=max_reactions,
            molecules=max_molecules,
            food_set=self.food_set,
            is_raf=True,
            is_max_raf=True
        )

    def find_all_rafs(self, max_size: Optional[int] = None) -> List[RAFSet]:
        """
        Enumerate all RAF subsets (expensive - use sparingly!).

        Args:
            max_size: Only check subsets up to this size

        Returns:
            List of all RAFs found
        """
        rafs = []
        reaction_ids = list(self.reactions.keys())

        if max_size is None:
            max_size = min(len(reaction_ids), 20)  # Limit to prevent explosion

        # Check all subsets (combinatorially expensive!)
        def check_subsets(current: Set[str], remaining: List[str], start: int):
            if len(current) > max_size:
                return

            # Check if current is RAF
            if current:
                is_valid, molecules = self.is_raf(current)
                if is_valid:
                    rafs.append(RAFSet(
                        reactions=current.copy(),
                        molecules=molecules,
                        food_set=self.food_set,
                        is_raf=True
                    ))

            # Try adding more reactions
            for i in range(start, len(remaining)):
                check_subsets(current | {remaining[i]}, remaining, i + 1)

        check_subsets(set(), reaction_ids, 0)
        return rafs

    def is_irreducible(self, raf: RAFSet) -> bool:
        """
        Check if RAF is irreducible (cannot remove any reaction).

        An irrRAF cannot be decomposed into smaller RAFs.
        """
        if not raf.is_raf:
            return False

        # Try removing each reaction
        for rid in raf.reactions:
            reduced = raf.reactions - {rid}
            if reduced:
                is_valid, _ = self.is_raf(reduced)
                if is_valid:
                    return False  # Can remove this reaction -> reducible

        return True

    def find_critical_molecules(self, raf: RAFSet) -> Set[str]:
        """
        Find critical molecules: removing them breaks the RAF.
        """
        critical = set()

        # Try removing each non-food molecule
        for molecule in raf.molecules - self.food_set:
            # Remove all reactions producing this molecule
            reactions_without = raf.reactions.copy()
            for rid in raf.reactions:
                if molecule in self.reactions[rid].products:
                    reactions_without.discard(rid)

            # Check if still RAF
            if reactions_without:
                is_valid, _ = self.is_raf(reactions_without)
                if not is_valid:
                    critical.add(molecule)

        return critical

    def find_core_raf(self, raf: RAFSet) -> RAFSet:
        """
        Find the core (irreducible) RAF within a larger RAF.

        Removes reactions until no more can be removed.
        """
        current_reactions = raf.reactions.copy()

        changed = True
        while changed:
            changed = False

            for rid in list(current_reactions):
                test_reactions = current_reactions - {rid}
                if test_reactions:
                    is_valid, molecules = self.is_raf(test_reactions)
                    if is_valid:
                        current_reactions = test_reactions
                        changed = True
                        break  # Start over

        is_valid, molecules = self.is_raf(current_reactions)
        return RAFSet(
            reactions=current_reactions,
            molecules=molecules,
            food_set=self.food_set,
            is_raf=is_valid,
            is_irreducible=True
        )

    def compute_raf_statistics(self, raf: RAFSet) -> Dict[str, Any]:
        """Compute statistics about a RAF."""
        if not raf.is_raf:
            return {'valid': False}

        # Catalytic structure
        catalytic_pairs = 0
        for rid in raf.reactions:
            rxn = self.reactions[rid]
            # Count how many products of this RAF catalyze this reaction
            for catalyst in rxn.catalysts:
                if catalyst in raf.molecules:
                    catalytic_pairs += 1

        # Dependency depth
        depth = self._compute_dependency_depth(raf)

        # Critical components
        critical_molecules = self.find_critical_molecules(raf)

        return {
            'valid': True,
            'size': len(raf.reactions),
            'diversity': len(raf.molecules),
            'food_items': len(self.food_set),
            'catalytic_pairs': catalytic_pairs,
            'dependency_depth': depth,
            'critical_molecules': len(critical_molecules),
            'critical_molecule_fraction': len(critical_molecules) / len(raf.molecules) if raf.molecules else 0,
            'is_irreducible': self.is_irreducible(raf),
            'autocatalytic_density': catalytic_pairs / len(raf.reactions) if raf.reactions else 0
        }

    def _compute_dependency_depth(self, raf: RAFSet) -> int:
        """Compute longest dependency chain from food to products."""
        # BFS from food molecules
        depth_map = {mol: 0 for mol in self.food_set}
        queue = deque(list(self.food_set))
        max_depth = 0

        while queue:
            mol = queue.popleft()
            current_depth = depth_map[mol]

            # Find reactions this molecule enables or catalyzes
            for rid in raf.reactions:
                rxn = self.reactions[rid]

                if mol in rxn.reactants or mol in rxn.catalysts:
                    # This reaction might produce new molecules
                    if rxn.is_enabled(set(depth_map.keys())) and rxn.is_catalyzed(set(depth_map.keys())):
                        for product in rxn.products:
                            if product not in depth_map:
                                depth_map[product] = current_depth + 1
                                max_depth = max(max_depth, current_depth + 1)
                                queue.append(product)

        return max_depth


def create_random_catalytic_network(
    num_molecules: int = 20,
    num_reactions: int = 30,
    food_size: int = 5,
    max_reactants: int = 3,
    max_products: int = 2,
    catalyst_probability: float = 0.3
) -> Tuple[List[Reaction], Set[str]]:
    """
    Create a random catalytic reaction network for testing.

    Returns:
        (reactions, food_set)
    """
    molecules = [f"M{i}" for i in range(num_molecules)]
    food_set = set(random.sample(molecules, food_size))

    reactions = []
    for i in range(num_reactions):
        # Random reactants and products
        num_r = random.randint(1, max_reactants)
        num_p = random.randint(1, max_products)

        reactants = set(random.sample(molecules, num_r))
        products = set(random.sample(molecules, num_p))

        # Random catalysts
        catalysts = set()
        for mol in molecules:
            if random.random() < catalyst_probability:
                catalysts.add(mol)

        reactions.append(Reaction(
            id=f"R{i}",
            reactants=reactants,
            products=products,
            catalysts=catalysts
        ))

    return reactions, food_set
