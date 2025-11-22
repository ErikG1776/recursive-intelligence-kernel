"""
rik_logger.py | Visual Cognitive Loop Logger
------------------------------------------------------------
Provides colorful, verbose output showing RIK's cognitive processes.
"""

import sys
from datetime import datetime

# ANSI color codes
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def log_task_start(task: str):
    """Log task initiation."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}[🎯 TASK] {task}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def log_embedding(task: str, embedding_dim: int = 384):
    """Log embedding generation."""
    print(f"{Colors.MAGENTA}[🧠 EMBEDDING]{Colors.RESET} Task embedded to {embedding_dim}-dim semantic space")
    # Show abbreviated vector
    print(f"{Colors.DIM}   Vector: [0.234, -0.156, 0.891, ... , 0.442]{Colors.RESET}")


def log_memory_retrieval(context: dict, similarity: float = None):
    """Log memory context retrieval."""
    if context.get("context"):
        print(f"{Colors.BLUE}[📚 MEMORY]{Colors.RESET} Retrieved similar episode from memory")
        if similarity:
            print(f"{Colors.DIM}   Similarity: {similarity:.3f}{Colors.RESET}")
        ctx_preview = str(context.get("context", ""))[:80]
        print(f"{Colors.DIM}   Context: \"{ctx_preview}...\"{Colors.RESET}")
    else:
        print(f"{Colors.BLUE}[📚 MEMORY]{Colors.RESET} No prior context found (first run)")


def log_abstraction(cluster_count: int = 0):
    """Log abstraction formation."""
    if cluster_count > 0:
        print(f"{Colors.YELLOW}[🔗 ABSTRACTION]{Colors.RESET} Formed {cluster_count} pattern cluster(s) from history")
    else:
        print(f"{Colors.DIM}[🔗 ABSTRACTION] Insufficient history for clustering{Colors.RESET}")


def log_execution_start():
    """Log execution phase."""
    print(f"\n{Colors.WHITE}[⚡ EXECUTING]{Colors.RESET} Running task...")


def log_success():
    """Log successful completion."""
    print(f"{Colors.GREEN}[✅ SUCCESS]{Colors.RESET} Task completed successfully")


def log_failure(error_msg: str):
    """Log failure detection."""
    print(f"\n{Colors.RED}[❌ FAILURE]{Colors.RESET} {error_msg}")


def log_diagnosis(error_type: str, message: str):
    """Log error diagnosis."""
    print(f"\n{Colors.YELLOW}[🩺 DIAGNOSING]{Colors.RESET} Analyzing failure...")
    print(f"{Colors.DIM}   Error Type: {error_type}{Colors.RESET}")
    print(f"{Colors.DIM}   Message: {message}{Colors.RESET}")


def log_strategy_generation(strategies: list):
    """Log strategy generation."""
    print(f"\n{Colors.MAGENTA}[⚙️  STRATEGIES]{Colors.RESET} Generated {len(strategies)} recovery strategies:")
    for i, s in enumerate(strategies, 1):
        print(f"{Colors.DIM}   {i}. {s}{Colors.RESET}")


def log_counterfactual_simulation(simulations: list):
    """Log counterfactual simulation with visual confidence bars."""
    print(f"\n{Colors.CYAN}[🔮 SIMULATING]{Colors.RESET} Predicting outcomes...")

    best_idx = 0
    best_score = 0
    for i, sim in enumerate(simulations):
        score = sim["predicted_success"]
        if score > best_score:
            best_score = score
            best_idx = i

    for i, sim in enumerate(simulations):
        score = sim["predicted_success"]
        bar_len = int(score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        if i == best_idx:
            marker = f"{Colors.GREEN}← BEST{Colors.RESET}"
            color = Colors.GREEN
        else:
            marker = ""
            color = Colors.DIM

        print(f"   {color}[{bar}] {score:.2f} - {sim['strategy'][:40]} {marker}{Colors.RESET}")


def log_strategy_execution(strategy: str, confidence: float):
    """Log strategy execution."""
    print(f"\n{Colors.GREEN}[🚀 EXECUTING]{Colors.RESET} {strategy}")
    print(f"{Colors.DIM}   Confidence: {confidence:.2f}{Colors.RESET}")


def log_recovery_success():
    """Log successful recovery."""
    print(f"{Colors.GREEN}[✅ RECOVERED]{Colors.RESET} Fallback strategy succeeded!")


def log_reflection(reflection: str):
    """Log reflection phase."""
    print(f"\n{Colors.BLUE}[💭 REFLECTION]{Colors.RESET}")
    # Word wrap reflection
    words = reflection.split()
    line = "   "
    for word in words:
        if len(line) + len(word) > 70:
            print(f"{Colors.DIM}{line}{Colors.RESET}")
            line = "   "
        line += word + " "
    if line.strip():
        print(f"{Colors.DIM}{line}{Colors.RESET}")


def log_fitness(score: float, previous: float = None):
    """Log fitness score with change indicator."""
    if previous is not None:
        delta = score - previous
        if delta > 0:
            change = f"{Colors.GREEN}↑ +{delta:.3f}{Colors.RESET}"
        elif delta < 0:
            change = f"{Colors.RED}↓ {delta:.3f}{Colors.RESET}"
        else:
            change = f"{Colors.DIM}→ 0.000{Colors.RESET}"
        print(f"\n{Colors.YELLOW}[📈 FITNESS]{Colors.RESET} {previous:.3f} → {Colors.BOLD}{score:.3f}{Colors.RESET} ({change})")
    else:
        print(f"\n{Colors.YELLOW}[📈 FITNESS]{Colors.RESET} {Colors.BOLD}{score:.3f}{Colors.RESET}")


def log_episode_saved():
    """Log episode storage."""
    print(f"{Colors.DIM}[💾 SAVED] Episode stored to memory{Colors.RESET}")


def log_task_complete(task_num: int = None, total: int = None):
    """Log task completion."""
    if task_num and total:
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")
        print(f"{Colors.DIM}Completed task {task_num}/{total}{Colors.RESET}")
    else:
        print(f"\n{Colors.CYAN}{'─'*60}{Colors.RESET}")


def log_learning_transfer(from_task: str, to_task: str, similarity: float):
    """Log cross-task learning."""
    print(f"\n{Colors.MAGENTA}[🔄 TRANSFER]{Colors.RESET} Learning from similar task")
    print(f"{Colors.DIM}   From: \"{from_task[:40]}...\"{Colors.RESET}")
    print(f"{Colors.DIM}   Similarity: {similarity:.3f}{Colors.RESET}")


# Demo banner
def print_banner():
    """Print RIK demo banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ██╗██╗  ██╗                                   ║
║   ██╔══██╗██║██║ ██╔╝                                   ║
║   ██████╔╝██║█████╔╝                                    ║
║   ██╔══██╗██║██╔═██╗                                    ║
║   ██║  ██║██║██║  ██╗                                   ║
║   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝                                   ║
║                                                          ║
║   Recursive Intelligence Kernel                          ║
║   Cognitive RPA Demo                                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)
