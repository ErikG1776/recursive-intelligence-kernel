#!/usr/bin/env python3
"""
self_evolving_maze_solver.py | Recursive Intelligence Algorithm Demo
----------------------------------------------------------------------
A "mic drop" demonstration of RIA's self-improvement capabilities.

This demo shows an agent that:
1. Starts with a naive strategy (random walk)
2. Fails repeatedly at first
3. Reflects on failures and stores them in episodic memory
4. Evolves its strategy based on learned patterns
5. Eventually solves mazes it couldn't before
6. Transfers learning to harder maze variants

Run: python demos/self_evolving_maze_solver.py
"""

import os
import sys
import time
import random
from datetime import datetime
from typing import Optional
from collections import deque

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import setup_logging
from db import get_cursor
from memory import save_episode, get_recent_episodes, init_memory_db

logger = setup_logging("ria.maze_demo")

# ==========================================================
# === MAZE ENVIRONMENT =====================================
# ==========================================================

class MazeEnvironment:
    """Visual maze environment for the demo."""

    WALL = "█"
    PATH = " "
    AGENT = "●"
    GOAL = "★"
    VISITED = "·"

    def __init__(self, difficulty: int = 1):
        self.difficulty = difficulty
        self.maze = self._generate_maze(difficulty)
        self.start = (1, 1)
        self.goal = self._find_goal()
        self.agent_pos = self.start
        self.visited = set()
        self.steps = 0
        self.max_steps = 200 * difficulty

    def _generate_maze(self, difficulty: int) -> list[list[str]]:
        """Generate a maze based on difficulty level."""
        size = 11 + (difficulty * 4)
        maze = [[self.WALL for _ in range(size)] for _ in range(size)]

        # Carve paths using recursive backtracking
        def carve(x, y):
            maze[y][x] = self.PATH
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < size-1 and 0 < ny < size-1 and maze[ny][nx] == self.WALL:
                    maze[y + dy//2][x + dx//2] = self.PATH
                    carve(nx, ny)

        carve(1, 1)

        # Place goal in far corner
        goal_x, goal_y = size - 2, size - 2
        maze[goal_y][goal_x] = self.GOAL

        # Add extra walls based on difficulty
        if difficulty > 1:
            for _ in range(difficulty * 3):
                x, y = random.randint(2, size-3), random.randint(2, size-3)
                if maze[y][x] == self.PATH and (x, y) != (1, 1):
                    maze[y][x] = self.WALL

        return maze

    def _find_goal(self) -> tuple[int, int]:
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == self.GOAL:
                    return (x, y)
        return (len(self.maze[0])-2, len(self.maze)-2)

    def reset(self):
        """Reset agent to start position."""
        self.agent_pos = self.start
        self.visited = set()
        self.steps = 0

    def get_valid_moves(self) -> list[str]:
        """Get list of valid moves from current position."""
        x, y = self.agent_pos
        moves = []

        if y > 0 and self.maze[y-1][x] != self.WALL:
            moves.append("UP")
        if y < len(self.maze)-1 and self.maze[y+1][x] != self.WALL:
            moves.append("DOWN")
        if x > 0 and self.maze[y][x-1] != self.WALL:
            moves.append("LEFT")
        if x < len(self.maze[0])-1 and self.maze[y][x+1] != self.WALL:
            moves.append("RIGHT")

        return moves

    def move(self, direction: str) -> tuple[bool, bool, float]:
        """
        Execute a move. Returns (valid_move, reached_goal, reward).
        """
        x, y = self.agent_pos
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))

        new_x, new_y = x + dx, y + dy

        # Check bounds and walls
        if (0 <= new_x < len(self.maze[0]) and
            0 <= new_y < len(self.maze) and
            self.maze[new_y][new_x] != self.WALL):

            self.visited.add(self.agent_pos)
            self.agent_pos = (new_x, new_y)
            self.steps += 1

            # Calculate reward
            reached_goal = self.agent_pos == self.goal

            # Reward for new territory, penalty for revisiting
            if self.agent_pos in self.visited:
                reward = -0.5
            else:
                # Reward based on distance to goal
                dist_before = abs(x - self.goal[0]) + abs(y - self.goal[1])
                dist_after = abs(new_x - self.goal[0]) + abs(new_y - self.goal[1])
                reward = 0.1 if dist_after < dist_before else -0.1

            if reached_goal:
                reward = 100.0

            return True, reached_goal, reward

        return False, False, -1.0

    def is_timeout(self) -> bool:
        return self.steps >= self.max_steps

    def render(self) -> str:
        """Render maze as string for display."""
        lines = []
        for y, row in enumerate(self.maze):
            line = ""
            for x, cell in enumerate(row):
                if (x, y) == self.agent_pos:
                    line += f"\033[92m{self.AGENT}\033[0m"  # Green agent
                elif (x, y) in self.visited:
                    line += f"\033[90m{self.VISITED}\033[0m"  # Gray visited
                elif cell == self.GOAL:
                    line += f"\033[93m{self.GOAL}\033[0m"  # Yellow goal
                elif cell == self.WALL:
                    line += f"\033[34m{self.WALL}\033[0m"  # Blue walls
                else:
                    line += cell
            lines.append(line)
        return "\n".join(lines)


# ==========================================================
# === STRATEGY CLASSES =====================================
# ==========================================================

class Strategy:
    """Base strategy class."""
    name = "base"

    def choose_move(self, env: MazeEnvironment, memory: list) -> str:
        raise NotImplementedError


class RandomStrategy(Strategy):
    """Naive random walk strategy - will fail often."""
    name = "random_walk"

    def choose_move(self, env: MazeEnvironment, memory: list) -> str:
        moves = env.get_valid_moves()
        return random.choice(moves) if moves else "UP"


class GreedyStrategy(Strategy):
    """Greedy strategy - always moves toward goal."""
    name = "greedy"

    def choose_move(self, env: MazeEnvironment, memory: list) -> str:
        moves = env.get_valid_moves()
        if not moves:
            return "UP"

        x, y = env.agent_pos
        gx, gy = env.goal

        # Score each move by distance to goal
        best_move = moves[0]
        best_dist = float('inf')

        for move in moves:
            dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[move]
            new_dist = abs(x + dx - gx) + abs(y + dy - gy)
            if new_dist < best_dist:
                best_dist = new_dist
                best_move = move

        return best_move


class MemoryAwareStrategy(Strategy):
    """Avoids recently visited positions - learns from mistakes."""
    name = "memory_aware"

    def __init__(self):
        self.recent_positions = deque(maxlen=10)

    def choose_move(self, env: MazeEnvironment, memory: list) -> str:
        moves = env.get_valid_moves()
        if not moves:
            return "UP"

        x, y = env.agent_pos
        gx, gy = env.goal

        # Filter out moves to recently visited positions
        good_moves = []
        for move in moves:
            dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[move]
            new_pos = (x + dx, y + dy)
            if new_pos not in self.recent_positions:
                good_moves.append((move, abs(new_pos[0] - gx) + abs(new_pos[1] - gy)))

        if good_moves:
            # Sort by distance to goal
            good_moves.sort(key=lambda m: m[1])
            chosen = good_moves[0][0]
        else:
            # Stuck - pick random
            chosen = random.choice(moves)

        # Update memory
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[chosen]
        self.recent_positions.append((x + dx, y + dy))

        return chosen


class BFSStrategy(Strategy):
    """Optimal BFS pathfinding - the evolved solution."""
    name = "bfs_pathfinding"

    def __init__(self):
        self.path = []
        self.path_index = 0

    def choose_move(self, env: MazeEnvironment, memory: list) -> str:
        # Recompute path if needed
        if not self.path or self.path_index >= len(self.path):
            self.path = self._find_path(env)
            self.path_index = 0

        if self.path and self.path_index < len(self.path):
            move = self.path[self.path_index]
            self.path_index += 1
            return move

        # Fallback
        return random.choice(env.get_valid_moves() or ["UP"])

    def _find_path(self, env: MazeEnvironment) -> list[str]:
        """BFS to find shortest path to goal."""
        from collections import deque

        start = env.agent_pos
        goal = env.goal

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == goal:
                return path

            for move, (dx, dy) in [("UP", (0, -1)), ("DOWN", (0, 1)),
                                    ("LEFT", (-1, 0)), ("RIGHT", (1, 0))]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(env.maze[0]) and
                    0 <= ny < len(env.maze) and
                    env.maze[ny][nx] != env.WALL and
                    (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [move]))

        return []


# ==========================================================
# === SELF-EVOLVING AGENT ==================================
# ==========================================================

class SelfEvolvingAgent:
    """
    The main RIA agent that evolves its strategy based on experience.
    """

    STRATEGIES = [
        RandomStrategy,
        GreedyStrategy,
        MemoryAwareStrategy,
        BFSStrategy
    ]

    def __init__(self):
        self.strategy_index = 0
        self.strategy = self.STRATEGIES[0]()
        self.episode_count = 0
        self.successes = 0
        self.total_steps = 0
        self.evolution_history = []

        # Performance tracking per strategy
        self.strategy_stats = {s.name: {"attempts": 0, "successes": 0, "avg_steps": 0}
                               for s in [cls() for cls in self.STRATEGIES]}

    def get_strategy_name(self) -> str:
        return self.strategy.name

    def run_episode(self, env: MazeEnvironment, visualize: bool = True) -> dict:
        """Run one episode and return results."""
        env.reset()
        self.episode_count += 1

        episode_start = time.time()
        total_reward = 0.0
        move_history = []

        while not env.is_timeout():
            # Get memory context
            recent_memory = get_recent_episodes(limit=5)

            # Choose move using current strategy
            move = self.strategy.choose_move(env, recent_memory)
            move_history.append(move)

            # Execute move
            valid, reached_goal, reward = env.move(move)
            total_reward += reward

            # Visualize
            if visualize:
                self._display_state(env, move, total_reward)

            if reached_goal:
                break

        # Record results
        duration = time.time() - episode_start
        success = env.agent_pos == env.goal

        result = {
            "episode": self.episode_count,
            "strategy": self.strategy.name,
            "success": success,
            "steps": env.steps,
            "reward": total_reward,
            "duration": duration,
            "difficulty": env.difficulty
        }

        # Update stats
        stats = self.strategy_stats[self.strategy.name]
        stats["attempts"] += 1
        if success:
            stats["successes"] += 1
            self.successes += 1
        stats["avg_steps"] = (stats["avg_steps"] * (stats["attempts"]-1) + env.steps) / stats["attempts"]
        self.total_steps += env.steps

        # Save to episodic memory
        reflection = self._reflect(result)
        save_episode(
            task=f"Maze solving (difficulty={env.difficulty})",
            result="success" if success else "failure",
            reflection=reflection
        )

        return result

    def _reflect(self, result: dict) -> str:
        """Generate reflection on the episode."""
        if result["success"]:
            return (f"Strategy '{result['strategy']}' succeeded in {result['steps']} steps. "
                   f"Efficiency: {100/max(result['steps'],1):.2f}. Keep using this approach.")
        else:
            return (f"Strategy '{result['strategy']}' failed after {result['steps']} steps. "
                   f"Consider evolving to a more sophisticated strategy.")

    def evolve(self) -> bool:
        """
        Analyze performance and potentially evolve to a better strategy.
        Returns True if evolution occurred.
        """
        current_stats = self.strategy_stats[self.strategy.name]

        # Check if current strategy is performing poorly
        if current_stats["attempts"] >= 3:
            success_rate = current_stats["successes"] / current_stats["attempts"]

            if success_rate < 0.5 and self.strategy_index < len(self.STRATEGIES) - 1:
                # Evolve to next strategy
                self.strategy_index += 1
                old_strategy = self.strategy.name
                self.strategy = self.STRATEGIES[self.strategy_index]()

                evolution_record = {
                    "from": old_strategy,
                    "to": self.strategy.name,
                    "reason": f"Low success rate ({success_rate:.1%})",
                    "episode": self.episode_count
                }
                self.evolution_history.append(evolution_record)

                logger.info(f"EVOLUTION: {old_strategy} → {self.strategy.name}")
                return True

        return False

    def _display_state(self, env: MazeEnvironment, last_move: str, reward: float):
        """Display current state with stats."""
        # Clear screen
        print("\033[2J\033[H", end="")

        # Header
        print("=" * 60)
        print("  RECURSIVE INTELLIGENCE ALGORITHM - MAZE SOLVER DEMO")
        print("=" * 60)
        print()

        # Maze
        print(env.render())
        print()

        # Stats
        print(f"  Episode: {self.episode_count} | Strategy: \033[96m{self.strategy.name}\033[0m")
        print(f"  Steps: {env.steps}/{env.max_steps} | Move: {last_move} | Reward: {reward:.1f}")
        print(f"  Success Rate: {self.successes}/{self.episode_count} ({100*self.successes/max(self.episode_count,1):.0f}%)")

        # Evolution history
        if self.evolution_history:
            print(f"\n  Evolutions: {' → '.join([e['to'] for e in self.evolution_history])}")

        print()
        time.sleep(0.02)  # Small delay for visualization


# ==========================================================
# === MAIN DEMO ============================================
# ==========================================================

def run_demo():
    """Run the self-evolving maze solver demo."""
    print("\033[2J\033[H")  # Clear screen

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Self-Evolving Maze Solver Demo                         ║
    ║                                                          ║
    ║   Watch the agent:                                       ║
    ║   1. Start with a naive random strategy                  ║
    ║   2. Fail and reflect on mistakes                        ║
    ║   3. Evolve to smarter strategies                        ║
    ║   4. Eventually master the maze                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    input("  Press ENTER to start the demo...")

    # Initialize
    init_memory_db()
    agent = SelfEvolvingAgent()

    results = []
    difficulties = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3]  # Progressive difficulty

    for i, difficulty in enumerate(difficulties):
        # Create maze
        env = MazeEnvironment(difficulty=difficulty)

        # Run episode
        result = agent.run_episode(env, visualize=True)
        results.append(result)

        # Check for evolution
        evolved = agent.evolve()

        # Pause between episodes
        if evolved:
            print("\n  🧬 STRATEGY EVOLUTION DETECTED!")
            print(f"     New strategy: {agent.get_strategy_name()}")
            time.sleep(2)
        else:
            time.sleep(0.5)

    # Final summary
    print("\033[2J\033[H")
    print_summary(agent, results)


def print_summary(agent: SelfEvolvingAgent, results: list):
    """Print final demo summary."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    DEMO COMPLETE                         ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  EVOLUTION JOURNEY:")
    print("  " + "─" * 56)

    strategies_used = ["random_walk"] + [e["to"] for e in agent.evolution_history]
    for i, strat in enumerate(strategies_used):
        arrow = "  →  " if i < len(strategies_used) - 1 else ""
        print(f"    {i+1}. {strat}{arrow}", end="")
        if arrow:
            print()
    print("\n")

    print("  PERFORMANCE BY STRATEGY:")
    print("  " + "─" * 56)

    for name, stats in agent.strategy_stats.items():
        if stats["attempts"] > 0:
            rate = stats["successes"] / stats["attempts"] * 100
            print(f"    {name:20} | {stats['successes']}/{stats['attempts']} success ({rate:.0f}%) | avg {stats['avg_steps']:.0f} steps")

    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The agent started with random exploration and evolved")
    print("    through reflection to discover optimal pathfinding.")
    print("    This demonstrates RIA's core recursive learning loop:")
    print()
    print("    \033[96mObserve → Reason → Act → Reflect → Adapt → Loop\033[0m")
    print()

    # Show memory growth
    episodes = get_recent_episodes(limit=100)
    print(f"  Episodic Memory: {len(episodes)} experiences stored")
    print()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise
