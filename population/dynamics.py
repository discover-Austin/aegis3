"""
AEGIS-2 Population: Multi-Agent Emergence

Key insight: Many emergent phenomena require POPULATIONS.
- Competition creates selection pressure
- Cooperation creates synergies
- Communication creates shared meaning
- Imitation creates culture

This module implements:
- Population of AEGIS2 agents
- Competitive fitness landscapes
- Cooperative task structures
- Agent communication/imitation
- Cultural evolution (meme transfer)
- Speciation and niche formation
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime
from collections import defaultdict
import json
from pathlib import Path

# Import core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import AEGIS2, EmergentEvent


@dataclass
class AgentStats:
    """Statistics for an agent in the population."""
    agent_id: str
    generation: int = 0
    age: int = 0
    fitness: float = 0.0
    offspring_count: int = 0
    
    # Interaction stats
    cooperations: int = 0
    competitions: int = 0
    communications: int = 0
    
    # Lineage
    parent_ids: List[str] = field(default_factory=list)
    
    # Niche
    niche_id: Optional[str] = None
    specialization: Dict[str, float] = field(default_factory=dict)


@dataclass
class Message:
    """A message passed between agents."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    sender_id: str = ""
    receiver_id: Optional[str] = None  # None = broadcast
    content: Any = None
    message_type: str = "signal"  # signal, pattern, goal, knowledge
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    # Meme tracking (for cultural evolution)
    origin_id: str = ""  # Original creator
    copies: int = 0
    mutations: int = 0


@dataclass  
class Niche:
    """An ecological niche that agents can specialize in."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:8])
    name: str = ""
    
    # Niche characteristics
    traits: Dict[str, float] = field(default_factory=dict)
    
    # Carrying capacity
    capacity: int = 10
    
    # Current occupants
    occupant_ids: List[str] = field(default_factory=list)
    
    # Niche fitness function parameters
    optimal_traits: Dict[str, float] = field(default_factory=dict)
    
    def fitness_for(self, agent_traits: Dict[str, float]) -> float:
        """Compute fitness of an agent in this niche."""
        if not self.optimal_traits:
            return 0.5
        
        total_diff = 0.0
        for trait, optimal in self.optimal_traits.items():
            actual = agent_traits.get(trait, 0.5)
            total_diff += (optimal - actual) ** 2
        
        return math.exp(-total_diff)


class Environment:
    """
    The environment in which agents exist and compete.
    
    Provides:
    - Resources for agents to compete over
    - Tasks for agents to solve
    - Selection pressure
    - Environmental change (shifting fitness landscapes)
    """
    
    def __init__(self, complexity: float = 0.5, volatility: float = 0.1):
        self.complexity = complexity
        self.volatility = volatility
        
        # Resources
        self.resources: Dict[str, float] = {
            'energy': 100.0,
            'information': 100.0,
            'novelty': 100.0
        }
        
        # Niches
        self.niches: Dict[str, Niche] = {}
        
        # Tasks
        self.tasks: List[Dict] = []
        self.completed_tasks: int = 0
        
        # Environmental state
        self.state: Dict[str, float] = {}
        self.state_history: List[Dict] = []
        
        # Time
        self.tick: int = 0
        
        # Initialize
        self._initialize_niches()
        self._generate_tasks()
        self._update_state()
    
    def _initialize_niches(self):
        """Create initial ecological niches."""
        niche_configs = [
            ("explorer", {"novelty_seeking": 0.8, "stability": 0.2}),
            ("optimizer", {"novelty_seeking": 0.2, "stability": 0.8}),
            ("generalist", {"novelty_seeking": 0.5, "stability": 0.5}),
            ("innovator", {"creativity": 0.9, "efficiency": 0.3}),
            ("executor", {"creativity": 0.3, "efficiency": 0.9}),
        ]
        
        for name, traits in niche_configs:
            niche = Niche(
                name=name,
                optimal_traits=traits,
                capacity=5 + int(10 * self.complexity)
            )
            self.niches[niche.id] = niche
    
    def _generate_tasks(self, count: int = 10):
        """Generate tasks for agents to solve."""
        task_types = ['pattern_match', 'goal_achieve', 'novelty_find', 'optimize', 'cooperate']
        
        for i in range(count):
            task = {
                'id': f"task_{self.tick}_{i}",
                'type': random.choice(task_types),
                'difficulty': random.random() * self.complexity,
                'reward': random.uniform(1.0, 10.0),
                'deadline': self.tick + random.randint(10, 100),
                'required_agents': 1 if random.random() > 0.3 else random.randint(2, 4),
                'completed': False,
                'assigned_to': []
            }
            self.tasks.append(task)
    
    def _update_state(self):
        """Update environmental state."""
        # Base state
        self.state = {
            'signal': math.sin(self.tick / 10) * 0.5 + 0.5,
            'noise': random.random() * self.volatility,
            'pressure': 0.5 + 0.3 * math.sin(self.tick / 50),
            'opportunity': random.random()
        }
        
        # Add complexity-dependent features
        for i in range(int(self.complexity * 5)):
            self.state[f'feature_{i}'] = random.random()
        
        self.state_history.append(dict(self.state))
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def step(self):
        """Advance environment by one tick."""
        self.tick += 1
        
        # Regenerate resources
        for resource in self.resources:
            self.resources[resource] = min(100.0, self.resources[resource] + 1.0)
        
        # Update state (with volatility)
        self._update_state()
        
        # Occasionally shift niches (environmental change)
        if random.random() < self.volatility * 0.1:
            self._shift_niches()
        
        # Generate new tasks occasionally
        if random.random() < 0.1:
            self._generate_tasks(count=random.randint(1, 3))
        
        # Expire old tasks
        self.tasks = [t for t in self.tasks if t['deadline'] > self.tick or t['completed']]
    
    def _shift_niches(self):
        """Shift niche optimal traits (environmental change)."""
        for niche in self.niches.values():
            for trait in niche.optimal_traits:
                # Small random shift
                shift = random.gauss(0, self.volatility * 0.5)
                niche.optimal_traits[trait] = max(0, min(1, niche.optimal_traits[trait] + shift))
    
    def consume_resource(self, resource: str, amount: float) -> float:
        """Consume a resource, return actual amount consumed."""
        if resource not in self.resources:
            return 0.0
        
        actual = min(amount, self.resources[resource])
        self.resources[resource] -= actual
        return actual
    
    def get_available_tasks(self, agent_traits: Optional[Dict] = None) -> List[Dict]:
        """Get tasks available for an agent."""
        available = [t for t in self.tasks if not t['completed'] and t['deadline'] > self.tick]
        
        if agent_traits:
            # Sort by suitability
            def suitability(task):
                base = 1.0 - task['difficulty']
                if task['type'] == 'novelty_find':
                    base *= agent_traits.get('novelty_seeking', 0.5)
                elif task['type'] == 'optimize':
                    base *= agent_traits.get('efficiency', 0.5)
                return base
            
            available.sort(key=suitability, reverse=True)
        
        return available
    
    def complete_task(self, task_id: str, agent_ids: List[str]) -> float:
        """Mark a task as completed, return reward."""
        for task in self.tasks:
            if task['id'] == task_id and not task['completed']:
                if len(agent_ids) >= task['required_agents']:
                    task['completed'] = True
                    task['assigned_to'] = agent_ids
                    self.completed_tasks += 1
                    return task['reward']
        return 0.0
    
    def get_stats(self) -> Dict:
        return {
            'tick': self.tick,
            'resources': dict(self.resources),
            'niches': len(self.niches),
            'active_tasks': len([t for t in self.tasks if not t['completed']]),
            'completed_tasks': self.completed_tasks,
            'volatility': self.volatility,
            'complexity': self.complexity
        }


class Population:
    """
    A population of AEGIS2 agents that evolve together.
    
    This enables:
    - Competitive evolution
    - Cooperative emergence
    - Cultural transmission
    - Speciation
    """
    
    def __init__(
        self,
        size: int = 10,
        environment: Optional[Environment] = None,
        data_dir: Optional[str] = None
    ):
        self.target_size = size
        self.environment = environment or Environment()
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / ".population_data"
        
        # Agents
        self.agents: Dict[str, AEGIS2] = {}
        self.agent_stats: Dict[str, AgentStats] = {}
        
        # Communication
        self.message_queue: List[Message] = []
        self.message_history: List[Message] = []
        
        # Meme pool (cultural knowledge)
        self.meme_pool: Dict[str, Dict] = {}  # meme_id -> {content, fitness, copies}
        
        # Statistics
        self.generation: int = 0
        self.total_agents_created: int = 0
        self.total_deaths: int = 0
        self.total_reproductions: int = 0
        
        # History
        self.fitness_history: List[Dict] = []
        self.diversity_history: List[float] = []
        self.emergence_events: List[Dict] = []
        
        # Initialize population
        self._initialize_population()
    
    def _initialize_population(self):
        """Create initial population."""
        for i in range(self.target_size):
            agent = self._create_agent(f"agent_{i}")
            self.agents[agent.name] = agent
            self.agent_stats[agent.name] = AgentStats(
                agent_id=agent.name,
                generation=0
            )
    
    def _create_agent(self, name: str, parent_ids: Optional[List[str]] = None) -> AEGIS2:
        """Create a new agent."""
        agent = AEGIS2(name=name, data_dir=str(self.data_dir / name))
        self.total_agents_created += 1
        
        # If has parents, inherit some structure
        if parent_ids:
            parents = [self.agents.get(pid) for pid in parent_ids if pid in self.agents]
            if parents:
                self._inherit(agent, parents)
        
        return agent
    
    def _inherit(self, child: AEGIS2, parents: List[AEGIS2]):
        """Inherit genetic material from parents."""
        # Inherit genes from random parent
        parent = random.choice(parents)
        
        for gene_id, gene in list(parent.genome.genes.items())[:5]:
            if gene_id not in child.genome.genes:
                cloned = gene.clone()
                child.genome.genes[cloned.id] = cloned
        
        # Inherit patterns
        for pattern_id, pattern in list(parent.patterns.patterns.items())[:5]:
            if pattern_id not in child.patterns.patterns:
                child.patterns.register(pattern.clone())
    
    def step(self) -> Dict:
        """Run one step of population dynamics."""
        results = {
            'generation': self.generation,
            'population_size': len(self.agents),
            'agent_results': {},
            'interactions': [],
            'births': [],
            'deaths': [],
            'emergence': []
        }
        
        # Step environment
        self.environment.step()
        
        # === AGENT STEPS ===
        for agent_id, agent in list(self.agents.items()):
            # Prepare inputs from environment
            inputs = {
                **self.environment.state,
                'population_size': len(self.agents),
                'generation': self.generation,
                'agent_age': self.agent_stats[agent_id].age
            }
            
            # Step agent
            agent_result = agent.step(inputs)
            results['agent_results'][agent_id] = agent_result
            
            # Update stats
            self.agent_stats[agent_id].age += 1
            self.agent_stats[agent_id].fitness = agent.fitness
            
            # Check for emergence
            if agent_result.get('emergence'):
                for e in agent_result['emergence']:
                    e['agent_id'] = agent_id
                    results['emergence'].append(e)
                    self.emergence_events.append(e)
        
        # === INTERACTIONS ===
        interactions = self._run_interactions()
        results['interactions'] = interactions
        
        # === COMMUNICATION ===
        self._process_messages()
        
        # === SELECTION ===
        deaths = self._selection()
        results['deaths'] = deaths
        
        # === REPRODUCTION ===
        births = self._reproduction()
        results['births'] = births
        
        # === CULTURAL EVOLUTION ===
        self._evolve_memes()
        
        # === RECORD HISTORY ===
        self._record_history()
        
        # Check for population-level emergence
        pop_emergence = self._detect_population_emergence()
        results['emergence'].extend(pop_emergence)
        
        return results
    
    def _run_interactions(self) -> List[Dict]:
        """Run interactions between agents."""
        interactions = []
        
        agent_list = list(self.agents.keys())
        if len(agent_list) < 2:
            return interactions
        
        # Random pairwise interactions
        num_interactions = min(len(agent_list), 5)
        
        for _ in range(num_interactions):
            a1, a2 = random.sample(agent_list, 2)
            
            # Determine interaction type based on task availability
            available_tasks = self.environment.get_available_tasks()
            coop_tasks = [t for t in available_tasks if t['required_agents'] > 1]
            
            if coop_tasks and random.random() < 0.3:
                # Cooperation
                interaction = self._cooperate(a1, a2, coop_tasks[0])
            elif random.random() < 0.5:
                # Competition
                interaction = self._compete(a1, a2)
            else:
                # Communication
                interaction = self._communicate(a1, a2)
            
            interactions.append(interaction)
        
        return interactions
    
    def _cooperate(self, agent1_id: str, agent2_id: str, task: Dict) -> Dict:
        """Two agents cooperate on a task."""
        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]
        
        # Combined fitness determines success
        combined = (agent1.fitness + agent2.fitness) / 2
        success = random.random() < combined
        
        interaction = {
            'type': 'cooperation',
            'agents': [agent1_id, agent2_id],
            'task': task['id'],
            'success': success
        }
        
        if success:
            reward = self.environment.complete_task(task['id'], [agent1_id, agent2_id])
            interaction['reward'] = reward
            
            # Boost both agents' goals
            agent1.goals.update_goal(
                random.choice(list(agent1.goals.goals.keys())),
                progress=0.3
            )
            agent2.goals.update_goal(
                random.choice(list(agent2.goals.goals.keys())),
                progress=0.3
            )
        
        self.agent_stats[agent1_id].cooperations += 1
        self.agent_stats[agent2_id].cooperations += 1
        
        return interaction
    
    def _compete(self, agent1_id: str, agent2_id: str) -> Dict:
        """Two agents compete for resources."""
        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]
        
        # Fitness determines winner
        if agent1.fitness > agent2.fitness:
            winner, loser = agent1_id, agent2_id
        elif agent2.fitness > agent1.fitness:
            winner, loser = agent2_id, agent1_id
        else:
            winner, loser = random.choice([(agent1_id, agent2_id), (agent2_id, agent1_id)])
        
        # Winner gets resources
        resource = random.choice(list(self.environment.resources.keys()))
        amount = self.environment.consume_resource(resource, 5.0)
        
        interaction = {
            'type': 'competition',
            'agents': [agent1_id, agent2_id],
            'winner': winner,
            'resource': resource,
            'amount': amount
        }
        
        self.agent_stats[agent1_id].competitions += 1
        self.agent_stats[agent2_id].competitions += 1
        
        return interaction
    
    def _communicate(self, sender_id: str, receiver_id: str) -> Dict:
        """One agent sends a message to another."""
        sender = self.agents[sender_id]
        
        # Determine what to communicate
        message_type = random.choice(['pattern', 'goal', 'knowledge'])
        
        if message_type == 'pattern' and sender.patterns.patterns:
            pattern = random.choice(list(sender.patterns.patterns.values()))
            content = pattern.to_dict()
        elif message_type == 'goal' and sender.goals.goals:
            goal = random.choice(list(sender.goals.goals.values()))
            content = goal.to_dict()
        else:
            content = {'fitness': sender.fitness, 'cycle': sender.cycle}
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            origin_id=sender_id
        )
        
        self.message_queue.append(message)
        
        interaction = {
            'type': 'communication',
            'sender': sender_id,
            'receiver': receiver_id,
            'message_type': message_type
        }
        
        self.agent_stats[sender_id].communications += 1
        self.agent_stats[receiver_id].communications += 1
        
        return interaction
    
    def _process_messages(self):
        """Process message queue."""
        for message in self.message_queue:
            receiver = self.agents.get(message.receiver_id)
            if not receiver:
                continue
            
            # Receiver potentially adopts content (imitation/learning)
            if message.message_type == 'pattern' and random.random() < 0.3:
                # Try to learn the pattern
                try:
                    from patterns.compositional import pattern_from_dict
                    pattern = pattern_from_dict(message.content)
                    receiver.patterns.register(pattern)
                    message.copies += 1
                    
                    # Track meme
                    meme_id = message.origin_id + "_" + message.id
                    if meme_id not in self.meme_pool:
                        self.meme_pool[meme_id] = {
                            'content': message.content,
                            'copies': 0,
                            'origin': message.origin_id
                        }
                    self.meme_pool[meme_id]['copies'] += 1
                except:
                    pass
        
        self.message_history.extend(self.message_queue)
        self.message_queue = []
        
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
    
    def _selection(self) -> List[str]:
        """Natural selection - remove unfit agents."""
        deaths = []
        
        if len(self.agents) <= self.target_size // 2:
            return deaths  # Don't kill if population too small
        
        # Rank by fitness
        ranked = sorted(
            self.agent_stats.items(),
            key=lambda x: x[1].fitness
        )
        
        # Kill bottom performers with some probability
        for agent_id, stats in ranked[:len(ranked)//4]:
            if random.random() < 0.3:
                del self.agents[agent_id]
                del self.agent_stats[agent_id]
                deaths.append(agent_id)
                self.total_deaths += 1
        
        # Age-based death
        for agent_id, stats in list(self.agent_stats.items()):
            if stats.age > 1000 and random.random() < 0.1:
                if agent_id in self.agents:
                    del self.agents[agent_id]
                    del self.agent_stats[agent_id]
                    deaths.append(agent_id)
                    self.total_deaths += 1
        
        return deaths
    
    def _reproduction(self) -> List[str]:
        """Reproduction - create new agents from fit parents."""
        births = []
        
        if len(self.agents) >= self.target_size * 1.5:
            return births  # Population cap
        
        # Top performers reproduce
        ranked = sorted(
            self.agent_stats.items(),
            key=lambda x: x[1].fitness,
            reverse=True
        )
        
        for agent_id, stats in ranked[:len(ranked)//3]:
            if random.random() < stats.fitness * 0.3:
                # Create offspring
                child_name = f"agent_{self.total_agents_created}"
                
                # Maybe sexual reproduction
                potential_mates = [a for a, _ in ranked[:len(ranked)//2] if a != agent_id]
                if potential_mates and random.random() < 0.5:
                    other_id = random.choice(potential_mates)
                    parent_ids = [agent_id, other_id]
                else:
                    parent_ids = [agent_id]
                
                child = self._create_agent(child_name, parent_ids)
                self.agents[child_name] = child
                self.agent_stats[child_name] = AgentStats(
                    agent_id=child_name,
                    generation=self.generation + 1,
                    parent_ids=parent_ids
                )
                
                stats.offspring_count += 1
                births.append(child_name)
                self.total_reproductions += 1
        
        return births
    
    def _evolve_memes(self):
        """Evolve cultural memes."""
        # Prune unsuccessful memes
        to_remove = []
        for meme_id, meme in self.meme_pool.items():
            if meme['copies'] < 1 and random.random() < 0.1:
                to_remove.append(meme_id)
        
        for meme_id in to_remove:
            del self.meme_pool[meme_id]
    
    def _record_history(self):
        """Record population history."""
        # Fitness distribution
        fitnesses = [s.fitness for s in self.agent_stats.values()]
        if fitnesses:
            self.fitness_history.append({
                'generation': self.generation,
                'mean': sum(fitnesses) / len(fitnesses),
                'max': max(fitnesses),
                'min': min(fitnesses)
            })
        
        # Diversity (based on genome similarity)
        diversity = self._compute_diversity()
        self.diversity_history.append(diversity)
        
        if len(self.fitness_history) > 1000:
            self.fitness_history = self.fitness_history[-1000:]
        if len(self.diversity_history) > 1000:
            self.diversity_history = self.diversity_history[-1000:]
    
    def _compute_diversity(self) -> float:
        """Compute genetic diversity of population."""
        if len(self.agents) < 2:
            return 0.0
        
        # Simple diversity: variance in gene counts
        gene_counts = [len(a.genome.genes) for a in self.agents.values()]
        if len(gene_counts) < 2:
            return 0.0
        
        mean = sum(gene_counts) / len(gene_counts)
        variance = sum((c - mean) ** 2 for c in gene_counts) / len(gene_counts)
        
        return math.sqrt(variance) / max(1, mean)
    
    def _detect_population_emergence(self) -> List[Dict]:
        """Detect population-level emergent phenomena."""
        phenomena = []
        
        # 1. Speciation (subpopulations with distinct traits)
        if len(self.agent_stats) >= 5:
            generations = [s.generation for s in self.agent_stats.values()]
            if max(generations) - min(generations) > 5:
                phenomena.append({
                    'type': 'speciation',
                    'description': 'Population showing generation stratification',
                    'generation_range': (min(generations), max(generations))
                })
        
        # 2. Cultural transmission (memes spreading)
        high_copy_memes = [m for m in self.meme_pool.values() if m['copies'] > len(self.agents) * 0.5]
        if high_copy_memes:
            phenomena.append({
                'type': 'cultural_emergence',
                'description': 'Memes achieving widespread adoption',
                'meme_count': len(high_copy_memes)
            })
        
        # 3. Cooperation emergence
        total_coop = sum(s.cooperations for s in self.agent_stats.values())
        total_comp = sum(s.competitions for s in self.agent_stats.values())
        if total_coop > total_comp * 2:
            phenomena.append({
                'type': 'cooperation_emergence',
                'description': 'Population favoring cooperation',
                'ratio': total_coop / max(1, total_comp)
            })
        
        # 4. Fitness explosion
        if len(self.fitness_history) > 10:
            recent = self.fitness_history[-5:]
            older = self.fitness_history[-10:-5]
            if recent and older:
                recent_mean = sum(r['mean'] for r in recent) / len(recent)
                older_mean = sum(r['mean'] for r in older) / len(older)
                if recent_mean > older_mean * 1.5:
                    phenomena.append({
                        'type': 'fitness_explosion',
                        'description': 'Rapid population-wide fitness increase',
                        'improvement': recent_mean / max(0.01, older_mean)
                    })
        
        return phenomena
    
    def run(self, generations: int = 100, verbose: bool = True) -> List[Dict]:
        """Run population for multiple generations."""
        results = []
        
        for g in range(generations):
            self.generation = g
            result = self.step()
            results.append(result)
            
            if verbose and result['emergence']:
                print(f"Generation {g}: {len(result['emergence'])} emergence events")
                for e in result['emergence']:
                    print(f"  - {e.get('type', 'unknown')}: {e.get('description', '')}")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get population statistics."""
        fitnesses = [s.fitness for s in self.agent_stats.values()]
        
        return {
            'population_size': len(self.agents),
            'target_size': self.target_size,
            'generation': self.generation,
            'total_created': self.total_agents_created,
            'total_deaths': self.total_deaths,
            'total_reproductions': self.total_reproductions,
            'mean_fitness': sum(fitnesses) / max(1, len(fitnesses)),
            'max_fitness': max(fitnesses) if fitnesses else 0,
            'diversity': self.diversity_history[-1] if self.diversity_history else 0,
            'meme_pool_size': len(self.meme_pool),
            'emergence_events': len(self.emergence_events),
            'environment': self.environment.get_stats()
        }
    
    def save(self):
        """Save population state."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save each agent
        for agent_id, agent in self.agents.items():
            agent.save()
        
        # Save population state
        state = {
            'target_size': self.target_size,
            'generation': self.generation,
            'total_agents_created': self.total_agents_created,
            'total_deaths': self.total_deaths,
            'total_reproductions': self.total_reproductions,
            'agent_stats': {aid: {
                'agent_id': s.agent_id,
                'generation': s.generation,
                'age': s.age,
                'fitness': s.fitness,
                'parent_ids': s.parent_ids
            } for aid, s in self.agent_stats.items()},
            'fitness_history': self.fitness_history[-100:],
            'emergence_events': self.emergence_events[-50:]
        }
        
        with open(self.data_dir / "population_state.json", 'w') as f:
            json.dump(state, f, indent=2)


def demo():
    """Demonstrate population dynamics."""
    print("=" * 70)
    print("   AEGIS-2 Population Dynamics")
    print("=" * 70)
    print()
    
    # Create environment
    env = Environment(complexity=0.5, volatility=0.2)
    
    # Create population
    pop = Population(size=10, environment=env)
    
    print(f"Initial population: {len(pop.agents)} agents")
    print()
    
    # Run for 50 generations
    print("Running 50 generations...")
    results = pop.run(generations=50, verbose=True)
    
    print()
    print("=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    stats = pop.get_stats()
    print(f"""
  Population: {stats['population_size']} agents
  Generations: {stats['generation']}
  
  Created: {stats['total_created']}
  Deaths: {stats['total_deaths']}
  Reproductions: {stats['total_reproductions']}
  
  Mean Fitness: {stats['mean_fitness']:.4f}
  Max Fitness: {stats['max_fitness']:.4f}
  Diversity: {stats['diversity']:.4f}
  
  Meme Pool: {stats['meme_pool_size']} memes
  Emergence Events: {stats['emergence_events']}
""")
    
    return pop


if __name__ == "__main__":
    demo()
