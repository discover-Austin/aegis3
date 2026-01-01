"""
AEGIS Visualization Dashboard

Real-time visualization of evolution.
ASCII-based for terminal compatibility.
"""

from typing import List, Dict, Any


class AEGISDashboard:
    """ASCII-based dashboard for monitoring evolution."""

    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height

    def plot_fitness_landscape(self, fitnesses: List[float]) -> str:
        """ASCII plot of fitness over time."""
        if not fitnesses:
            return "No fitness data"

        max_fit = max(fitnesses)
        min_fit = min(fitnesses)
        range_fit = max_fit - min_fit if max_fit > min_fit else 1

        lines = []
        lines.append("Fitness Landscape")
        lines.append("=" * self.width)

        # Plot area height
        plot_height = 15

        for i in range(plot_height):
            line = []
            threshold = max_fit - (i / plot_height) * range_fit

            for fit in fitnesses[-self.width:]:
                if fit >= threshold:
                    line.append('█')
                else:
                    line.append(' ')

            lines.append(''.join(line))

        lines.append("─" * self.width)
        lines.append(f"Min: {min_fit:.2f}  Max: {max_fit:.2f}  Latest: {fitnesses[-1]:.2f}")

        return '\n'.join(lines)

    def show_genealogy_tree(self, population: List[Dict]) -> str:
        """ASCII genealogy tree."""
        lines = ["Genealogy Tree", "=" * self.width]

        for i, agent in enumerate(population[:10]):  # Show top 10
            fitness = agent.get('fitness', 0)
            bar_length = int((fitness / max(a.get('fitness', 1) for a in population)) * 40)
            bar = '█' * bar_length

            lines.append(f"Agent {i:2d}: {bar} {fitness:.3f}")

        return '\n'.join(lines)

    def animate_emergence_events(self, events: List[Dict]) -> str:
        """Display recent emergence events."""
        lines = ["Recent Emergence Events", "=" * self.width]

        for event in events[-10:]:
            event_type = event.get('type', 'unknown')
            description = event.get('description', '')[:60]
            lines.append(f"[{event_type}] {description}")

        return '\n'.join(lines)

    def display_attractor_dynamics(self, states: List[List[float]]) -> str:
        """Display attractor dynamics."""
        lines = ["Attractor Dynamics", "=" * self.width]

        if not states or len(states[0]) < 2:
            return '\n'.join(lines + ["No data"])

        # 2D projection
        grid = [[' ' for _ in range(40)] for _ in range(15)]

        for state in states[-100:]:
            x = int((state[0] + 1) * 20) % 40
            y = int((state[1] + 1) * 7.5) % 15
            grid[y][x] = '●'

        for row in grid:
            lines.append(''.join(row))

        return '\n'.join(lines)

    def full_dashboard(self, agent) -> str:
        """Complete dashboard."""
        lines = []
        lines.append("╔" + "═" * (self.width - 2) + "╗")
        lines.append("║" + "AEGIS-3 Dashboard".center(self.width - 2) + "║")
        lines.append("╚" + "═" * (self.width - 2) + "╝")
        lines.append("")

        # Status
        if hasattr(agent, 'get_metrics'):
            metrics = agent.get_metrics()
            lines.append(f"Generation: {metrics.get('generation', 0)}")
            lines.append(f"Fitness: {metrics.get('fitness', 0):.4f}")
            lines.append("")

        return '\n'.join(lines)
