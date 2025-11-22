#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - Self-Evolving Snake Game

A snake game agent that evolves its decision-making strategy:
1. Starts with basic strategies (random, greedy)
2. Analyzes failures (wall hits, self-collisions)
3. Evolves more sophisticated strategies
4. Improves score over generations

This demonstrates RIA applied to game-playing AI.
"""

import sys
import time
import random
import argparse
from enum import Enum
from collections import deque
from typing import List, Tuple, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import init_memory_db, save_episode


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SnakeGame:
    """Simple snake game implementation."""

    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        """Reset the game state."""
        # Start snake in center
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake = deque([(center_x, center_y)])
        self.direction = Direction.RIGHT
        self.food = self._spawn_food()
        self.score = 0
        self.game_over = False
        self.death_reason = None
        self.moves = 0
        self.moves_without_food = 0

    def _spawn_food(self) -> Tuple[int, int]:
        """Spawn food at random location not on snake."""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def step(self, direction: Direction) -> bool:
        """Take one step in the given direction. Returns True if alive."""
        if self.game_over:
            return False

        # Prevent 180-degree turns
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if direction != opposite.get(self.direction):
            self.direction = direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        self.moves += 1
        self.moves_without_food += 1

        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            self.death_reason = "wall"
            return False

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            self.death_reason = "self"
            return False

        # Check starvation (too many moves without food)
        if self.moves_without_food > self.width * self.height * 2:
            self.game_over = True
            self.death_reason = "starvation"
            return False

        # Move snake
        self.snake.appendleft(new_head)

        # Check food
        if new_head == self.food:
            self.score += 1
            self.moves_without_food = 0
            self.food = self._spawn_food()
        else:
            self.snake.pop()

        return True

    def get_state(self) -> dict:
        """Get current game state for the agent."""
        head = self.snake[0]

        # Distances to walls
        dist_up = head[1]
        dist_down = self.height - head[1] - 1
        dist_left = head[0]
        dist_right = self.width - head[0] - 1

        # Direction to food
        food_dx = self.food[0] - head[0]
        food_dy = self.food[1] - head[1]

        # Danger detection (immediate collision)
        def is_danger(dx, dy):
            new_pos = (head[0] + dx, head[1] + dy)
            if new_pos[0] < 0 or new_pos[0] >= self.width:
                return True
            if new_pos[1] < 0 or new_pos[1] >= self.height:
                return True
            if new_pos in self.snake:
                return True
            return False

        return {
            "head": head,
            "food": self.food,
            "snake_length": len(self.snake),
            "direction": self.direction,
            "food_dx": food_dx,
            "food_dy": food_dy,
            "dist_up": dist_up,
            "dist_down": dist_down,
            "dist_left": dist_left,
            "dist_right": dist_right,
            "danger_up": is_danger(0, -1),
            "danger_down": is_danger(0, 1),
            "danger_left": is_danger(-1, 0),
            "danger_right": is_danger(1, 0),
            "snake_body": list(self.snake)
        }

    def render(self) -> str:
        """Render the game as ASCII art."""
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                grid[y][x] = '@'  # Head
            else:
                grid[y][x] = 'O'  # Body

        # Draw food
        fx, fy = self.food
        grid[fy][fx] = '*'

        # Build string
        border = '+' + '-' * self.width + '+'
        lines = [border]
        for row in grid:
            lines.append('|' + ''.join(row) + '|')
        lines.append(border)
        lines.append(f'Score: {self.score}  Moves: {self.moves}')

        return '\n'.join(lines)


class SnakeAgent:
    """Agent that plays snake using evolving strategies."""

    STRATEGIES = [
        "random",
        "greedy",
        "greedy_safe",
        "lookahead",
        "pathfinding"
    ]

    def __init__(self):
        self.strategy = "random"
        self.generation = 0
        self.history = []
        self.strategy_scores = {s: [] for s in self.STRATEGIES}

    def decide(self, state: dict) -> Direction:
        """Decide next direction based on current strategy."""
        if self.strategy == "random":
            return self._random_strategy(state)
        elif self.strategy == "greedy":
            return self._greedy_strategy(state)
        elif self.strategy == "greedy_safe":
            return self._greedy_safe_strategy(state)
        elif self.strategy == "lookahead":
            return self._lookahead_strategy(state)
        elif self.strategy == "pathfinding":
            return self._pathfinding_strategy(state)
        else:
            return self._random_strategy(state)

    def _random_strategy(self, state: dict) -> Direction:
        """Random movement - baseline strategy."""
        return random.choice(list(Direction))

    def _greedy_strategy(self, state: dict) -> Direction:
        """Always move toward food - ignores danger."""
        food_dx = state["food_dx"]
        food_dy = state["food_dy"]

        if abs(food_dx) > abs(food_dy):
            return Direction.RIGHT if food_dx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if food_dy > 0 else Direction.UP

    def _greedy_safe_strategy(self, state: dict) -> Direction:
        """Move toward food but avoid immediate danger."""
        food_dx = state["food_dx"]
        food_dy = state["food_dy"]

        # Preferred directions based on food position
        preferences = []
        if food_dx > 0:
            preferences.append(Direction.RIGHT)
        elif food_dx < 0:
            preferences.append(Direction.LEFT)
        if food_dy > 0:
            preferences.append(Direction.DOWN)
        elif food_dy < 0:
            preferences.append(Direction.UP)

        # Add remaining directions
        for d in Direction:
            if d not in preferences:
                preferences.append(d)

        # Check danger for each direction
        danger_map = {
            Direction.UP: state["danger_up"],
            Direction.DOWN: state["danger_down"],
            Direction.LEFT: state["danger_left"],
            Direction.RIGHT: state["danger_right"]
        }

        # Return first safe direction
        for d in preferences:
            if not danger_map[d]:
                return d

        # All directions dangerous, pick first preference
        return preferences[0]

    def _lookahead_strategy(self, state: dict) -> Direction:
        """Look ahead multiple steps to avoid traps."""
        head = state["head"]
        snake_body = set(state["snake_body"])
        food = state["food"]

        def simulate_move(pos, direction, body):
            """Simulate a move and return new position."""
            dx, dy = direction.value
            return (pos[0] + dx, pos[1] + dy)

        def is_valid(pos, body, width=20, height=15):
            """Check if position is valid."""
            if pos[0] < 0 or pos[0] >= width:
                return False
            if pos[1] < 0 or pos[1] >= height:
                return False
            if pos in body:
                return False
            return True

        def count_reachable(start, body, width=20, height=15):
            """Count reachable spaces using flood fill."""
            visited = set()
            queue = deque([start])
            while queue:
                pos = queue.popleft()
                if pos in visited:
                    continue
                if not is_valid(pos, body, width, height):
                    continue
                visited.add(pos)
                for d in Direction:
                    dx, dy = d.value
                    queue.append((pos[0] + dx, pos[1] + dy))
            return len(visited)

        best_direction = None
        best_score = -1

        for direction in Direction:
            new_pos = simulate_move(head, direction, snake_body)

            if not is_valid(new_pos, snake_body):
                continue

            # Score based on food distance and space available
            food_dist = abs(new_pos[0] - food[0]) + abs(new_pos[1] - food[1])
            space = count_reachable(new_pos, snake_body)

            # Prefer moves that keep more space available
            score = space * 10 - food_dist

            if score > best_score:
                best_score = score
                best_direction = direction

        return best_direction or Direction.RIGHT

    def _pathfinding_strategy(self, state: dict) -> Direction:
        """Use BFS pathfinding to find optimal path to food."""
        head = state["head"]
        snake_body = set(state["snake_body"])
        food = state["food"]

        # BFS to find path to food
        queue = deque([(head, [])])
        visited = {head}

        while queue:
            pos, path = queue.popleft()

            if pos == food:
                if path:
                    return path[0]
                break

            for direction in Direction:
                dx, dy = direction.value
                new_pos = (pos[0] + dx, pos[1] + dy)

                if new_pos in visited:
                    continue
                if new_pos[0] < 0 or new_pos[0] >= 20:
                    continue
                if new_pos[1] < 0 or new_pos[1] >= 15:
                    continue
                if new_pos in snake_body:
                    continue

                visited.add(new_pos)
                new_path = path + [direction] if path else [direction]
                queue.append((new_pos, new_path))

        # No path to food, use lookahead to survive
        return self._lookahead_strategy(state)

    def record_game(self, score: int, moves: int, death_reason: str):
        """Record game result for evolution."""
        self.history.append({
            "strategy": self.strategy,
            "score": score,
            "moves": moves,
            "death_reason": death_reason,
            "generation": self.generation
        })
        self.strategy_scores[self.strategy].append(score)

    def evolve(self) -> bool:
        """Evolve to a better strategy based on performance."""
        if not self.history:
            return False

        # Get recent performance
        recent = self.history[-5:] if len(self.history) >= 5 else self.history
        avg_score = sum(g["score"] for g in recent) / len(recent)

        # Analyze death patterns
        death_counts = {}
        for g in recent:
            reason = g["death_reason"]
            death_counts[reason] = death_counts.get(reason, 0) + 1

        current_idx = self.STRATEGIES.index(self.strategy)
        evolved = False
        new_strategy = self.strategy

        # Evolution logic based on performance
        if self.strategy == "random":
            # Random is baseline, always evolve
            if len(self.history) >= 3:
                new_strategy = "greedy"
                evolved = True

        elif self.strategy == "greedy":
            # Greedy dies from collisions, evolve to safe version
            if death_counts.get("wall", 0) + death_counts.get("self", 0) >= 2:
                new_strategy = "greedy_safe"
                evolved = True

        elif self.strategy == "greedy_safe":
            # If still dying, need to look ahead
            if avg_score < 5 or death_counts.get("self", 0) >= 2:
                new_strategy = "lookahead"
                evolved = True

        elif self.strategy == "lookahead":
            # If doing well, try pathfinding for optimization
            if avg_score >= 5:
                new_strategy = "pathfinding"
                evolved = True

        if evolved:
            self.strategy = new_strategy
            self.generation += 1

        return evolved


def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   Self-Evolving Snake Game                               ║
    ║                                                          ║
    ║   Watch an agent evolve its snake-playing strategy:      ║
    ║   1. Starts with random movements                        ║
    ║   2. Learns to seek food (greedy)                        ║
    ║   3. Learns to avoid danger (greedy_safe)                ║
    ║   4. Learns to avoid traps (lookahead)                   ║
    ║   5. Optimizes path to food (pathfinding)                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print("\033[2J\033[H")  # Clear screen
    print(banner)


def run_game(agent: SnakeAgent, game: SnakeGame, visualize: bool = False, delay: float = 0.05):
    """Run a single game with the agent."""
    game.reset()

    while not game.game_over:
        state = game.get_state()
        direction = agent.decide(state)
        game.step(direction)

        if visualize:
            print("\033[2J\033[H")  # Clear screen
            print(f"  Generation {agent.generation} | Strategy: {agent.strategy}")
            print()
            print(game.render())
            time.sleep(delay)

    return game.score, game.moves, game.death_reason


def main():
    parser = argparse.ArgumentParser(description="Self-evolving Snake Game Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically")
    parser.add_argument("--games", type=int, default=30, help="Number of games to play")
    parser.add_argument("--visualize", action="store_true", help="Show game visualization")
    parser.add_argument("--delay", type=float, default=0.03, help="Delay between frames")
    args = parser.parse_args()

    # Initialize
    init_memory_db()
    print_banner()

    if not args.auto:
        input("  Press Enter to start evolution...")
    else:
        time.sleep(1)

    # Create agent and game
    agent = SnakeAgent()
    game = SnakeGame(width=20, height=15)

    # Track evolution
    evolution_history = []
    games_per_strategy = {}

    # Run games
    for game_num in range(1, args.games + 1):
        # Run game
        score, moves, death_reason = run_game(
            agent, game,
            visualize=args.visualize,
            delay=args.delay
        )

        # Record result
        agent.record_game(score, moves, death_reason)

        # Track per-strategy performance
        if agent.strategy not in games_per_strategy:
            games_per_strategy[agent.strategy] = []
        games_per_strategy[agent.strategy].append(score)

        # Display progress
        if not args.visualize:
            print("\033[2J\033[H")  # Clear screen
            print(f"\n  Generation {agent.generation} | Strategy: \033[96m{agent.strategy}\033[0m")
            print(f"\n  Game {game_num}/{args.games}")
            print(f"  Score: {score} | Moves: {moves} | Death: {death_reason}")

            # Show recent scores
            recent = agent.history[-5:]
            if recent:
                scores = [g["score"] for g in recent]
                print(f"\n  Recent scores: {scores}")
                print(f"  Average: {sum(scores)/len(scores):.1f}")

        # Try to evolve
        if agent.evolve():
            evolution_history.append({
                "generation": agent.generation,
                "strategy": agent.strategy,
                "game": game_num
            })

            # Save evolution episode
            save_episode(
                task=f"snake_evolution_gen{agent.generation}",
                result="evolved",
                reflection=f"Evolved to {agent.strategy} after {game_num} games"
            )

            if not args.visualize:
                print(f"\n  \033[92m✓ EVOLVED to {agent.strategy}!\033[0m")
                time.sleep(0.5)

        time.sleep(0.1)

    # Final summary
    print("\033[2J\033[H")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 EVOLUTION COMPLETE                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    print("  STRATEGY PERFORMANCE:")
    print("  " + "─" * 56)

    for strategy in agent.STRATEGIES:
        if strategy in games_per_strategy:
            scores = games_per_strategy[strategy]
            avg = sum(scores) / len(scores)
            max_score = max(scores)
            print(f"    {strategy:15} | Avg: {avg:5.1f} | Max: {max_score:3} | Games: {len(scores)}")

    print("\n  EVOLUTION HISTORY:")
    print("  " + "─" * 56)

    for evo in evolution_history:
        print(f"    Gen {evo['generation']}: {evo['strategy']:15} (game {evo['game']})")

    # Calculate improvement
    if "random" in games_per_strategy and len(games_per_strategy) > 1:
        random_avg = sum(games_per_strategy["random"]) / len(games_per_strategy["random"])
        final_strategy = agent.strategy
        if final_strategy in games_per_strategy:
            final_avg = sum(games_per_strategy[final_strategy]) / len(games_per_strategy[final_strategy])
            improvement = ((final_avg - random_avg) / max(random_avg, 0.1)) * 100

            print(f"\n  IMPROVEMENT:")
            print("  " + "─" * 56)
            print(f"    Random avg:  {random_avg:.1f}")
            print(f"    Final avg:   {final_avg:.1f}")
            print(f"    Improvement: \033[92m{improvement:+.0f}%\033[0m")

    print("\n  KEY INSIGHT:")
    print("  " + "─" * 56)
    print("    The agent learned to play snake through evolution,")
    print("    discovering better strategies by analyzing failures.")
    print("\n    \033[96mThis is Recursive Intelligence in action.\033[0m\n")

    # Log final result
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ria.snake")
    logger.info(f"Evolution complete: {agent.generation} generations, final strategy: {agent.strategy}")


if __name__ == "__main__":
    main()
