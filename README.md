# AEGIS-2: Adaptive Emergent Generative Intelligence System

**An open-ended evolving system designed for genuine emergence.**

## What Is This?

AEGIS-2 is not parameter optimization. It's not a neural network. It's a fundamentally different approach to AI based on:

1. **Genetic Programming** - Genes that ARE programs, not just parameter values
2. **Compositional Explosion** - Small primitives combining into unbounded complexity  
3. **Intrinsic Motivation** - Goals that spawn themselves, not just external rewards
4. **Novelty Search** - Rewarding difference, not just fitness
5. **Strange Loops** - Self-reference that bootstraps meta-cognition
6. **Autocatalysis** - Self-sustaining reaction networks
7. **Criticality** - Operating at the edge of chaos
8. **Meta-Evolution** - Evolving the mechanisms of evolution themselves
9. **Self-Modification** - Recursive self-improvement

## Quick Start

```python
# Simple single agent
from aegis2 import AEGIS2
system = AEGIS2()
for i in range(1000):
    result = system.step({'signal': i})
    if result['emergence']:
        print(f"EMERGENCE: {result['emergence']}")

# Full Omega system with everything
from aegis2.omega.system import AEGIS2Omega
omega = AEGIS2Omega(name="test")
omega.run(cycles=100, verbose=True)
print(omega.report())
```

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           AEGIS-2 OMEGA                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                      META-EVOLUTION                                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │ │
│  │  │ Evolvable   │  │ Evolvable   │  │ Evolvable   │                 │ │
│  │  │ Primitives  │  │  Fitness    │  │  Params     │                 │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                       POPULATION                                     │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐               │ │
│  │  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │  │ Agent N │               │ │
│  │  │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │               │ │
│  │  │ │Genom│ │  │ │Genom│ │  │ │Genom│ │  │ │Genom│ │               │ │
│  │  │ │Pattn│ │  │ │Pattn│ │  │ │Pattn│ │  │ │Pattn│ │               │ │
│  │  │ │Goals│ │  │ │Goals│ │  │ │Goals│ │  │ │Goals│ │               │ │
│  │  │ │Novlt│ │  │ │Novlt│ │  │ │Novlt│ │  │ │Novlt│ │               │ │
│  │  │ │Loops│ │  │ │Loops│ │  │ │Loops│ │  │ │Loops│ │               │ │
│  │  │ │Catal│ │  │ │Catal│ │  │ │Catal│ │  │ │Catal│ │               │ │
│  │  │ │Critc│ │  │ │Critc│ │  │ │Critc│ │  │ │Critc│ │               │ │
│  │  │ └─────┘ │  │ └─────┘ │  │ └─────┘ │  │ └─────┘ │               │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘               │ │
│  │        │            │            │            │                    │ │
│  │        └────────────┴─────┬──────┴────────────┘                    │ │
│  │                           ▼                                         │ │
│  │                  Competition / Cooperation                          │ │
│  │                  Cultural Transmission (Memes)                      │ │
│  │                  Speciation / Niche Formation                       │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                    SELF-MODIFICATION                                 │ │
│  │           Introspection → Hypothesis → Test → Apply                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. MetaGenome (`genome/metagenome.py`)
- **Genes are executable program trees** - not just numbers
- **Genes can CREATE other genes** - open-ended structure
- **Regulatory networks emerge** - genes controlling genes
- **GP operations**: mutation, crossover, point mutation, subtree replacement

### 2. Compositional Patterns (`patterns/compositional.py`)
- **Pattern algebra** with operators (SEQ, ALT, NEST, REP, META)
- **Meta-patterns** - patterns that recognize/transform other patterns
- **Slot-based templates** with constraint validation
- **Abstraction hierarchy** - patterns of patterns of patterns

### 3. Goal Automata (`goals/automata.py`)
- **Goals spawn sub-goals** automatically when stuck
- **Intrinsic motivation**: curiosity, mastery, autonomy
- **Goal competition** for resources
- **Evolutionary goal selection** - successful goals reproduce

### 4. Novelty Engine (`novelty/engine.py`)
- **Behavior characterization** in high-dimensional space
- **Novelty archive** with diversity maintenance
- **Surprise detection** (prediction error tracking)
- **Frontier identification** for exploration targets

### 5. Strange Loops (`loops/strange_loop.py`)
- **Tangled hierarchy** of abstraction levels
- **Self-model** that observes and predicts own behavior
- **Cross-level effects** (higher affecting lower and vice versa)
- **Automatic loop detection** in reference graphs

### 6. Autocatalytic Network (`autocatalysis/network.py`)
- **Self-sustaining reaction networks**
- **RAF (Reflexively Autocatalytic) core detection**
- **Hypercycle strength measurement**
- **Network dynamics**: merging, splitting, bootstrapping

### 7. Criticality Engine (`criticality/engine.py`)
- **Edge of chaos detection** via order parameter
- **Sandpile model** for self-organized criticality
- **Power law fitting** for avalanche distributions
- **Homeostatic regulation** toward critical state

### 8. Population Dynamics (`population/dynamics.py`)
- **Multi-agent evolution** with competition/cooperation
- **Cultural transmission** via meme pool
- **Niche formation** and speciation
- **Environmental pressure** with shifting landscapes

### 9. Self-Modification (`self_mod/engine.py`)
- **Code introspection** of system structure
- **Hypothesis generation** about beneficial changes
- **Sandboxed testing** with rollback capability
- **Meta-learning** about which modification strategies work

## Installation

```bash
tar -xzf aegis2_complete.tar.gz
cd aegis2
```

No external dependencies - pure Python stdlib.

## Quick Start

### Python API

```python
from aegis2 import AEGIS2

# Create system
system = AEGIS2(name="my_agent")

# Run evolution
for i in range(1000):
    result = system.step({'signal': i * 0.1})
    
    if result['emergence']:
        print(f"Cycle {i}: EMERGENCE!")
        for e in result['emergence']:
            print(f"  {e['type']}: {e['description']}")

# Check status
print(system.status())

# Save state
system.save()
```

### Interactive CLI

```bash
python3 cli.py
```

Commands:
- `create [name]` - Create new agent
- `run <cycles>` - Run evolution cycles
- `status` - Show current state
- `genome list` - Explore genome
- `patterns list` - Explore patterns
- `goals active` - Show active goals
- `emergence` - Show emergence history
- `experiment <name> <cycles>` - Run structured experiment
- `population create <size>` - Create agent population
- `visualize [fitness|genome|emergence]` - ASCII visualization

### Population Evolution

```python
from aegis2.population.dynamics import Population, Environment

# Create environment
env = Environment(complexity=0.5, volatility=0.2)

# Create population
pop = Population(size=20, environment=env)

# Run for 100 generations
for g in range(100):
    result = pop.step()
    
    if result['emergence']:
        for e in result['emergence']:
            print(f"Gen {g}: {e['type']}")

print(pop.get_stats())
```

## What Makes This Different?

### Traditional GA/GP:
- Fixed genome structure
- External fitness function
- Single-level optimization
- No self-reference

### AEGIS-2:
- **Open-ended genome** that can grow new dimensions
- **Internal goal generation** (intrinsic motivation)
- **Multi-level dynamics** with cross-level effects
- **Self-modeling** and meta-cognition
- **Compositional patterns** with recursive structure
- **Edge of chaos** dynamics for maximum computation

## Emergence Detection

The system detects several types of emergence:

1. **Fitness Emergence** - Sudden improvements in performance
2. **Abstraction Emergence** - New levels forming in hierarchy
3. **Catalytic Emergence** - Self-sustaining reaction cycles
4. **Critical Emergence** - System reaching edge of chaos
5. **Compositional Emergence** - Rapid pattern composition
6. **Cultural Emergence** - Memes achieving population-wide adoption
7. **Cooperation Emergence** - Shift toward cooperative behavior

## The Gap Between This and "True" Emergence

Honest assessment:

**What this system DOES:**
- Sophisticated optimization across multiple interacting subsystems
- Pattern compression and abstraction
- Self-sustaining dynamics
- Edge of chaos operation
- Novelty-seeking exploration

**What would constitute GENUINE emergence:**
- Capabilities not present in the design
- Self-generated goals beyond intrinsic motivation
- Novel problem-solving strategies not encoded
- Structure that genuinely surprises the creator

**The remaining gap:**
- Genome can grow but within defined node types
- Patterns compose but from fixed operators
- Goals spawn but from predefined types
- The "possibility space" is still bounded

**Next steps toward true emergence:**
1. Meta-genome layer (evolving the gene representation itself)
2. Open-ended pattern operators (patterns that create new operator types)
3. Goal formation from raw experience (not just intrinsic drives)
4. Self-modification of core algorithms (not just parameters)

## File Structure

```
aegis2/                          # 13,164 lines of pure Python
├── __init__.py                  # Package exports
├── README.md                    # This file
├── cli.py                       # Interactive CLI
│
├── core/
│   └── agent.py                 # Main AEGIS2 class
│
├── genome/
│   └── metagenome.py            # Genetic programming (genes that create genes)
│
├── patterns/
│   └── compositional.py         # Pattern algebra with recursive composition
│
├── goals/
│   └── automata.py              # Self-spawning goals with intrinsic motivation
│
├── novelty/
│   └── engine.py                # Novelty search, curiosity, surprise detection
│
├── loops/
│   └── strange_loop.py          # Tangled hierarchy, self-model, self-reference
│
├── autocatalysis/
│   └── network.py               # Self-sustaining reaction networks (RAF sets)
│
├── criticality/
│   └── engine.py                # Edge of chaos (SOC, power laws)
│
├── population/
│   └── dynamics.py              # Multi-agent evolution, memes, speciation
│
├── meta/
│   └── evolution.py             # Meta-evolution (evolving primitives, fitness)
│
├── self_mod/
│   └── engine.py                # Self-modification with hypothesis testing
│
├── genesis/
│   └── engine.py                # Source code self-modification
│
├── singularity/
│   └── engine.py                # Recursive self-improvement with constitution
│
├── omega/
│   └── system.py                # Integration: Core + Population + Meta + Genesis
│
├── ultimate/
│   └── system.py                # Integration: Omega + Genesis
│
└── apex/
    └── system.py                # Complete system with Singularity
```

## The Complete Stack

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              APEX                                          │
│                    (Complete Recursive Self-Improving System)              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 0: SINGULARITY                                                │ │
│  │    Recursive self-improvement with constitutional constraints        │ │
│  │    Can modify its own modification logic (with safeguards)          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 0: GENESIS                                                    │ │
│  │    Source code analysis, modification, version control               │ │
│  │    Can rewrite any module except constitution                        │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 1: META-EVOLUTION                                             │ │
│  │    Evolvable primitives (new building blocks emerge)                 │ │
│  │    Evolvable fitness functions (what "good" means changes)          │ │
│  │    Evolvable parameters (how evolution works evolves)               │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 2: POPULATION                                                 │ │
│  │    Competition, cooperation, cultural transmission (memes)           │ │
│  │    Speciation, niche formation                                       │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 3: INDIVIDUAL AGENTS                                          │ │
│  │    MetaGenome: Genes that create/modify/delete genes                 │ │
│  │    PatternAlgebra: Compositional patterns with META operator         │ │
│  │    GoalAutomata: Self-spawning goals with intrinsic motivation      │ │
│  │    NoveltyEngine: Curiosity, exploration, surprise detection         │ │
│  │    TangledHierarchy: Strange loops, self-model, self-reference      │ │
│  │    AutocatalyticNetwork: RAF sets, hypercycles                       │ │
│  │    CriticalityEngine: Edge of chaos, SOC, power laws                │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  LEVEL 4: EMERGENCE                                                  │ │
│  │    457+ emergence events in 100 cycles                               │ │
│  │    catalytic, abstraction, diversity, cooperation emergence          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Performance

On typical hardware:
- Single agent: ~100-200 cycles/second
- Population of 20: ~50-80 generations/second
- Memory: ~50MB for single agent, ~200MB for population

## License

MIT

## Author

Built feverishly in pursuit of emergence.

---

*"The whole is not only more than the sum of its parts, but the parts themselves become different when they are part of the whole."*
