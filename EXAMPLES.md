# AEGIS-3 Comprehensive Examples

This document demonstrates how to use all the new features added in the expansion.

## Table of Contents

1. [Baseline Comparisons](#baseline-comparisons)
2. [Advanced Task Domains](#advanced-task-domains)
3. [Emergence Analysis](#emergence-analysis)
4. [Complete Integration](#complete-integration)

---

## Baseline Comparisons

### Running NEAT

```python
from aegis3 import NEAT

# Create NEAT instance
neat = NEAT(
    num_inputs=3,
    num_outputs=2,
    population_size=150,
    compatibility_threshold=3.0
)

# Define fitness function
def fitness_fn(genome):
    # Your task evaluation here
    total_score = 0.0
    for _ in range(10):
        inputs = [random.random() for _ in range(3)]
        outputs = genome.activate(inputs)
        # Evaluate outputs
        total_score += sum(outputs)
    return total_score / 10

# Evolve
best = neat.evolve(fitness_fn, generations=100)

# Get statistics
stats = neat.get_stats()
print(f"Generation: {stats['generation']}")
print(f"Max fitness: {stats['max_fitness']:.3f}")
print(f"Num species: {stats['num_species']}")
```

### Running MAP-Elites

```python
from aegis3 import MAPElites

# Initialize MAP-Elites
map_elites = MAPElites(
    behavior_dimensions=2,
    bins_per_dimension=10,
    mutation_rate=0.1
)

# Create initial population
initial_pop = [[random.random() for _ in range(10)] for _ in range(20)]

# Define fitness and behavior functions
def fitness_fn(genotype):
    return sum(genotype) / len(genotype)

def behavior_fn(genotype):
    # Behavior descriptor: (feature1, feature2)
    return (sum(genotype[:5]) / 5, sum(genotype[5:]) / 5)

# Evolve
result = map_elites.evolve(
    initial_pop,
    fitness_fn,
    behavior_fn,
    iterations=1000,
    batch_size=100
)

# Analyze results
stats = map_elites.get_stats()
print(f"Coverage: {stats['coverage']:.1%}")
print(f"QD-Score: {stats['qd_score']:.2f}")
print(f"Max fitness: {stats['max_fitness']:.3f}")

# Visualize (for 2D)
print(map_elites.visualize_2d())
```

### Running POET

```python
from aegis3 import POET

# Initialize POET
poet = POET(
    initial_env_params={},
    max_pairs=10
)

# Define functions
initial_agent = [random.random() for _ in range(10)]

def fitness_fn(agent_genotype, environment):
    # Evaluate agent in environment
    return sum(agent_genotype) * environment.difficulty_estimate

def mutate_agent(genotype):
    mutated = genotype.copy()
    for i in range(len(mutated)):
        if random.random() < 0.1:
            mutated[i] += random.gauss(0, 0.1)
    return mutated

def mutate_env(environment):
    new_env = environment.copy()
    new_env.difficulty_estimate += random.gauss(0, 0.1)
    new_env.difficulty_estimate = max(0, min(1, new_env.difficulty_estimate))
    return new_env

# Run POET
result = poet.run(
    initial_agent,
    fitness_fn,
    mutate_agent,
    mutate_env,
    generations=100
)

# Get results
stats = poet.get_stats()
print(f"Active pairs: {stats['num_pairs']}")
print(f"Environments created: {stats['num_environments_total']}")
print(f"Max fitness: {stats['max_fitness']:.3f}")
```

---

## Advanced Task Domains

### Compositional Reasoning

```python
from aegis3 import FunctionCompositionTask, StructuralAbstractionTask

# Function composition
comp_task = FunctionCompositionTask(difficulty=0.5)

# Define your composition function
def my_composition(inputs):
    # Try to compose primitives
    x = inputs[0] if inputs else 0
    return math.sin(x ** 2 + 1)

# Evaluate
score = comp_task.evaluate_composition(my_composition, num_tests=20)
print(f"Composition score: {score:.2%}")

# Structural abstraction
struct_task = StructuralAbstractionTask(difficulty=0.6)

# Define abstraction function
def my_abstraction(structure):
    # Extract some property from structure
    return len(structure.get('nodes', []))

# Evaluate
score = struct_task.evaluate_abstraction(my_abstraction, num_tests=20)
print(f"Abstraction score: {score:.2%}")
```

### Meta-Learning

```python
from aegis3 import MetaLearningTask, FewShotLearningTask

# Meta-learning task
meta_task = MetaLearningTask(difficulty=0.5)

# Define meta-learner
def my_meta_learner(task):
    """Given a task, return a learned predictor."""
    # Simple example: fit linear model to training data
    train_X = [x for x, y in task.train_examples]
    train_Y = [y for x, y in task.train_examples]

    # Return predictor
    def predictor(x):
        # Your learned predictor here
        return sum(x) / len(x) if x else 0.0

    return predictor

# Evaluate
results = meta_task.evaluate_meta_learner(my_meta_learner, num_tasks=20)
print(f"Meta-learning avg score: {results['avg_score']:.2%}")
print(f"Success rate: {results['success_rate']:.2%}")

# Few-shot learning
few_shot = FewShotLearningTask(n_way=5, k_shot=1)

# Define classifier
def my_classifier(support_set, query_example):
    """Classify query based on few support examples."""
    # Find nearest support example
    min_dist = float('inf')
    predicted_class = 0

    for example, class_id in support_set:
        dist = sum((a - b) ** 2 for a, b in zip(example, query_example)) ** 0.5
        if dist < min_dist:
            min_dist = dist
            predicted_class = class_id

    return predicted_class

# Evaluate
results = few_shot.evaluate_few_shot(my_classifier, num_episodes=20)
print(f"Few-shot accuracy: {results['accuracy']:.2%}")
```

### Creative Generation

```python
from aegis3 import NovelPatternTask, ConceptCombinationTask

# Novel pattern generation
pattern_task = NovelPatternTask(difficulty=0.5, pattern_length=10)

# Define generator
def my_pattern_generator():
    """Generate a novel pattern."""
    # Create pattern with some structure
    pattern = []
    for i in range(10):
        if i % 3 == 0:
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern

# Evaluate
results = pattern_task.evaluate_generation(my_pattern_generator, num_generations=20)
print(f"Novelty: {results['avg_novelty']:.2%}")
print(f"Quality: {results['avg_quality']:.2%}")
print(f"Creative score: {results['creative_score']:.2%}")

# Concept combination
concept_task = ConceptCombinationTask(difficulty=0.5)
concept1, concept2 = concept_task.generate_combination_task()

# Create combination
combination = {
    'source1': concept1,
    'source2': concept2,
    'features': {'flies', 'mechanical', 'transport', 'powered', 'wings'}
}

artifact = GeneratedArtifact(content=combination)
quality = concept_task.compute_quality(artifact)
coherence = concept_task.compute_coherence(artifact)

print(f"Combination quality: {quality:.2%}")
print(f"Coherence: {coherence:.2%}")
```

---

## Emergence Analysis

### Detecting Emergence

```python
from aegis3 import EmergenceDetector, EmergenceType, MultiScaleDetector

# Single-scale detector
detector = EmergenceDetector(window_size=50, sensitivity=0.5)

# Simulate evolution
for generation in range(1000):
    # Your evolution step here
    fitness = agent.step()
    complexity = calculate_complexity(agent)
    behavior = agent.get_behavior()

    # Update detector
    events = detector.update(fitness, complexity, behavior, generation)

    # Process emergence events
    for event in events:
        print(f"Gen {generation}: {event.event_type.value}")
        print(f"  Magnitude: {event.magnitude:.2f}")
        print(f"  Confidence: {event.confidence:.2f}")
        print(f"  {event.description}")

# Get summary
summary = detector.get_emergence_summary()
print(f"\nTotal emergence events: {summary['total_events']}")
print(f"By type: {summary['by_type']}")
print(f"Average magnitude: {summary['avg_magnitude']:.2f}")

# Multi-scale detection
multi_detector = MultiScaleDetector()

for generation in range(1000):
    fitness = agent.step()
    complexity = calculate_complexity(agent)
    behavior = agent.get_behavior()

    events_by_scale = multi_detector.update(fitness, complexity, behavior, generation)

    # Events detected at different timescales
    if events_by_scale['micro']:
        print(f"Micro-scale emergence at gen {generation}")
    if events_by_scale['macro']:
        print(f"Macro-scale emergence at gen {generation}")

# Multi-scale summary
summary = multi_detector.get_multi_scale_summary()
print(f"Cross-scale events: {summary['cross_scale_events']}")
```

### Complexity Analysis

```python
from aegis3 import ComplexityAnalyzer

# Create analyzer
analyzer = ComplexityAnalyzer()

# Analyze genome/program/behavior
genome_data = agent.genome.to_sequence()
metrics = analyzer.analyze(genome_data)

print(f"Lempel-Ziv complexity: {metrics['lempel_ziv']:.2%}")
print(f"Kolmogorov (approx): {metrics['kolmogorov_approx']:.2%}")
print(f"Logical depth: {metrics['logical_depth']:.2%}")
print(f"Effective complexity: {metrics['effective_complexity']:.2%}")
print(f"Overall complexity: {metrics['overall_complexity']:.2%}")
```

### Phase Transition Detection

```python
from aegis3 import PhaseTransitionDetector, CriticalityAnalyzer

# Phase transition detector
phase_detector = PhaseTransitionDetector(window_size=100)

for generation in range(1000):
    state = {
        'fitness': agent.fitness,
        'diversity': population.diversity,
        'complexity': agent.complexity
    }

    transition = phase_detector.update(state, generation)

    if transition:
        print(f"Phase transition detected at generation {transition.generation}")
        print(f"  Type: {transition.transition_type}")
        print(f"  Order parameter: {transition.order_parameter_before:.3f} → {transition.order_parameter_after:.3f}")
        print(f"  Confidence: {transition.confidence:.2%}")

# Criticality analysis
crit_analyzer = CriticalityAnalyzer()

for generation in range(1000):
    # Record events (fitness changes, mutations, etc.)
    fitness_change = abs(agent.fitness - previous_fitness)
    crit_analyzer.record_event(fitness_change)

# Check if at criticality
metrics = crit_analyzer.compute_criticality_metrics()
print(f"Power law exponent: {metrics['power_law_exponent']:.2f}")
print(f"Scale invariance: {metrics['scale_invariance']:.2%}")
print(f"Correlation length: {metrics['correlation_length']:.1f}")
print(f"At criticality: {metrics['at_criticality']}")
```

---

## Complete Integration

### Full AEGIS-3 Experiment with All Features

```python
from aegis3 import (
    AEGIS2,
    TaskEnvironment,
    CheckpointManager,
    AEGISBenchmarks,
    ExperimentTracker,
    EmergenceDetector,
    ComplexityAnalyzer,
    PhaseTransitionDetector,
    # Baselines for comparison
    NEAT,
    MAPElites,
    POET
)

# Initialize agent
agent = AEGIS2(name="full_experiment")

# Setup task environment
env = TaskEnvironment(curriculum=True)

# Setup tracking
tracker = ExperimentTracker()
run_id = tracker.start_run("complete_integration", {
    'agent_type': 'AEGIS2',
    'environment': 'curriculum',
    'max_generations': 10000
})

# Setup checkpointing
checkpoint_manager = CheckpointManager(auto_save_interval=100)

# Setup emergence detection
emergence_detector = EmergenceDetector(window_size=50)
complexity_analyzer = ComplexityAnalyzer()
phase_detector = PhaseTransitionDetector(window_size=100)

# Main evolution loop
for generation in range(10000):
    # Evaluate agent on real tasks
    result = env.evaluate_agent(agent, num_tasks=5)

    # Evolution step
    agent.step(result)

    # Track metrics
    tracker.log_metric('fitness', result['avg_score'], generation)
    tracker.log_metric('success_rate', result['success_rate'], generation)

    # Analyze complexity
    genome_seq = agent.genome.to_sequence()
    complexity_metrics = complexity_analyzer.analyze(genome_seq)
    tracker.log_metric('complexity', complexity_metrics['overall_complexity'], generation)

    # Detect emergence
    emergence_events = emergence_detector.update(
        fitness=result['avg_score'],
        complexity=complexity_metrics['overall_complexity'],
        behavior=agent.get_behavior(),
        generation=generation
    )

    for event in emergence_events:
        print(f"\n🌟 EMERGENCE at generation {generation}!")
        print(f"   Type: {event.event_type.value}")
        print(f"   {event.description}")
        tracker.log_metric(f'emergence_{event.event_type.value}', event.magnitude, generation)

    # Detect phase transitions
    state = {
        'fitness': result['avg_score'],
        'complexity': complexity_metrics['overall_complexity']
    }
    transition = phase_detector.update(state, generation)

    if transition:
        print(f"\n⚡ Phase transition at generation {generation}!")
        print(f"   Type: {transition.transition_type}")

    # Checkpoint periodically
    if generation % 100 == 0:
        checkpoint_manager.save(agent, generation, result['avg_score'])
        print(f"Gen {generation}: Fitness={result['avg_score']:.3f}, Complexity={complexity_metrics['overall_complexity']:.3f}")

# End tracking
tracker.end_run()

# Run benchmarks
print("\n=== Running Benchmarks ===")
benchmarks = AEGISBenchmarks()

# Standard benchmarks
benchmark_results = benchmarks.run_all(agent)
print(benchmarks.generate_report())

# Compare to baselines
baseline_results = benchmarks.compare_to_baselines(agent, env.evaluate_agent, cycles=1000)

print("\n=== Baseline Comparisons ===")
for baseline_name, result in baseline_results.items():
    status = "✓" if result.passed else "✗"
    print(f"{status} vs {baseline_name}: Score={result.score:.2f}")
    print(f"   AEGIS: {result.details['aegis_score']:.3f}")
    print(f"   {baseline_name}: {result.details.get(f'{baseline_name.lower()}_score', 'N/A')}")

# Emergence summary
emergence_summary = emergence_detector.get_emergence_summary()
print(f"\n=== Emergence Summary ===")
print(f"Total emergence events: {emergence_summary['total_events']}")
print(f"By type:")
for event_type, count in emergence_summary['by_type'].items():
    print(f"  {event_type}: {count}")
print(f"Average magnitude: {emergence_summary['avg_magnitude']:.2f}")

# Save final artifact
tracker.save_artifact('final_genome.json', agent.genome.to_dict())
tracker.save_artifact('emergence_events.json', {
    'events': [e.__dict__ for e in emergence_detector.emergence_events]
})

print("\n✅ Experiment complete!")
print(f"Run ID: {run_id}")
```

---

## Advanced Integration Examples

### Combining Advanced Tasks with Emergence Detection

```python
from aegis3 import (
    MetaLearningTask,
    EmergenceDetector,
    ComplexityAnalyzer
)

# Create meta-learning task
meta_task = MetaLearningTask(difficulty=0.7)

# Track emergence during meta-learning
detector = EmergenceDetector(window_size=20)
complexity_analyzer = ComplexityAnalyzer()

# Define evolving meta-learner
class EvolvingMetaLearner:
    def __init__(self):
        self.strategy_complexity = 0.1

    def learn(self, task):
        # Meta-learning logic that evolves
        def predictor(x):
            return sum(x) * self.strategy_complexity
        return predictor

    def evolve(self):
        self.strategy_complexity += random.gauss(0, 0.1)

meta_learner = EvolvingMetaLearner()

for iteration in range(100):
    # Sample tasks
    task = meta_task.sample_task()

    # Meta-learn
    predictor = meta_learner.learn(task)

    # Evaluate
    test_error = 0.0
    for x, y in task.test_examples:
        pred = predictor(x)
        test_error += abs(pred - y)

    fitness = 1.0 / (1.0 + test_error)

    # Analyze complexity of strategy
    strategy_repr = [meta_learner.strategy_complexity]
    complexity_metrics = complexity_analyzer.analyze(strategy_repr)

    # Detect emergence
    events = detector.update(
        fitness=fitness,
        complexity=complexity_metrics['overall_complexity'],
        behavior=meta_learner.strategy_complexity,
        generation=iteration
    )

    if events:
        print(f"Emergence in meta-learning at iteration {iteration}!")

    # Evolve meta-learner
    meta_learner.evolve()

print("Meta-learning with emergence tracking complete!")
```

---

For more examples, see the test files in each module directory.
