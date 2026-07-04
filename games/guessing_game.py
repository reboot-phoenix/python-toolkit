"""
Number Guessing Game
====================
A terminal game with three difficulty levels, hint system, and session scoring.

Run with:  python -m games.guessing_game
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional


# ─── Colours ─── #

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


# ─── Difficulty configuration ─── #

@dataclass
class Difficulty:
    name: str
    low: int
    high: int
    max_attempts: int
    hint_penalty: int   # points lost per hint used


DIFFICULTIES = {
    "1": Difficulty("Easy",   low=1,   high=50,   max_attempts=10, hint_penalty=5),
    "2": Difficulty("Medium", low=1,   high=100,  max_attempts=7,  hint_penalty=10),
    "3": Difficulty("Hard",   low=1,   high=500,  max_attempts=6,  hint_penalty=20),
}


# ─── Scoring ─── #

@dataclass
class SessionStats:
    wins: int = 0
    losses: int = 0
    total_score: int = 0
    best_score: int = 0
    games_played: int = 0
    history: list = field(default_factory=list)

    def record(self, won: bool, score: int, secret: int, guesses: int) -> None:
        self.games_played += 1
        self.total_score += score
        if won:
            self.wins += 1
            self.best_score = max(self.best_score, score)
        else:
            self.losses += 1
        self.history.append({
            "won": won, "score": score,
            "secret": secret, "guesses": guesses,
        })


def _calculate_score(
    difficulty: Difficulty,
    attempts_used: int,
    hints_used: int,
    elapsed: float,
) -> int:
    """
    Score formula:
    - Base points scale with difficulty range
    - Bonus for fewer attempts
    - Bonus for speed (capped)
    - Penalty for hints
    """
    base = (difficulty.high - difficulty.low) * 2
    attempt_bonus = max(0, (difficulty.max_attempts - attempts_used) * 15)
    speed_bonus = max(0, 30 - int(elapsed))     # up to 30 pts for finishing quickly
    hint_penalty = hints_used * difficulty.hint_penalty
    return max(0, base + attempt_bonus + speed_bonus - hint_penalty)


# ─── Display helpers ─── #

def _progress_bar(current: int, maximum: int, width: int = 20) -> str:
    filled = int(width * current / maximum)
    bar = "█" * filled + "░" * (width - filled)
    colour = GREEN if filled > width // 2 else YELLOW if filled > width // 4 else RED
    return f"{colour}{bar}{RESET}"


def _show_banner() -> None:
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════╗
║     NUMBER GUESSING GAME     ║
╚══════════════════════════════╝{RESET}
""")


def _show_stats(stats: SessionStats) -> None:
    if stats.games_played == 0:
        return
    win_rate = (stats.wins / stats.games_played) * 100
    avg = stats.total_score / stats.games_played if stats.games_played else 0
    print(f"""
{BOLD}── Session Stats ──────────────{RESET}
  Games played : {stats.games_played}
  Wins / Losses: {GREEN}{stats.wins}{RESET} / {RED}{stats.losses}{RESET}
  Win rate     : {win_rate:.0f}%
  Total score  : {stats.total_score}
  Best score   : {CYAN}{stats.best_score}{RESET}
  Average score: {avg:.0f}
{BOLD}───────────────────────────────{RESET}
""")


# ─── Game loop ─── #

def _pick_difficulty() -> Difficulty:
    print(f"{BOLD}Choose difficulty:{RESET}")
    for key, diff in DIFFICULTIES.items():
        print(
            f"  [{key}] {diff.name:8s} "
            f"Range: 1-{diff.high}  "
            f"Attempts: {diff.max_attempts}  "
            f"Hint penalty: -{diff.hint_penalty} pts"
        )
    while True:
        choice = input("\nEnter 1, 2, or 3: ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print(f"{YELLOW}Please enter 1, 2, or 3.{RESET}")


def _get_hint(secret: int, guesses: list[int], low: int, high: int) -> str:
    """Return a contextual hint based on previous guesses."""
    last = guesses[-1] if guesses else None
    diff = abs(secret - last) if last is not None else None

    if diff is not None and diff <= 5:
        return "🔥 Very hot — you're extremely close!"
    if diff is not None and diff <= 15:
        return "♨️  Warm — getting closer."

    # Divisibility hint
    hints = []
    if secret % 2 == 0:
        hints.append("the number is even")
    else:
        hints.append("the number is odd")
    if secret % 5 == 0:
        hints.append("it's divisible by 5")

    midpoint = (low + high) // 2
    if secret < midpoint:
        hints.append(f"it's in the lower half of the range ({low}–{midpoint})")
    else:
        hints.append(f"it's in the upper half of the range ({midpoint}–{high})")

    return "💡 Hint: " + "; ".join(hints) + "."


def play_round(difficulty: Difficulty, stats: SessionStats) -> None:
    """Play one complete round and update session stats."""
    secret = random.randint(difficulty.low, difficulty.high)
    guesses: list[int] = []
    hints_used = 0
    start = time.time()

    print(f"\n{BOLD}I'm thinking of a number between "
          f"{difficulty.low} and {difficulty.high}.{RESET}")
    print(f"You have {CYAN}{difficulty.max_attempts}{RESET} attempts. "
          f"Type {YELLOW}'hint'{RESET} for a clue (costs {difficulty.hint_penalty} pts).\n")

    for attempt in range(1, difficulty.max_attempts + 1):
        remaining = difficulty.max_attempts - attempt + 1
        bar = _progress_bar(remaining, difficulty.max_attempts)
        print(f"  Attempts left: {bar} {remaining}/{difficulty.max_attempts}")

        raw = input(f"  Guess #{attempt}: ").strip().lower()

        if raw == "hint":
            hints_used += 1
            print(f"  {YELLOW}{_get_hint(secret, guesses, difficulty.low, difficulty.high)}{RESET}\n")
            # Don't count this as an attempt — let them guess again
            attempt -= 1
            # but guard against infinite hinting with no guesses
            if attempt < 0:
                attempt = 0
            continue

        try:
            guess = int(raw)
        except ValueError:
            print(f"  {RED}Please enter a whole number or 'hint'.{RESET}\n")
            attempt -= 1
            continue

        if not (difficulty.low <= guess <= difficulty.high):
            print(f"  {YELLOW}Out of range! Enter a number between "
                  f"{difficulty.low} and {difficulty.high}.{RESET}\n")
            attempt -= 1
            continue

        guesses.append(guess)

        if guess == secret:
            elapsed = time.time() - start
            score = _calculate_score(difficulty, attempt, hints_used, elapsed)
            stats.record(won=True, score=score, secret=secret, guesses=attempt)

            print(f"\n  {GREEN}{BOLD}🎉 Correct! The number was {secret}.{RESET}")
            print(f"  Solved in {attempt} attempt(s) and {elapsed:.1f}s.")
            print(f"  Hints used: {hints_used}")
            print(f"  {CYAN}{BOLD}Score: {score} points{RESET}\n")
            return

        elif guess < secret:
            gap = secret - guess
            if gap > difficulty.high // 5:
                print(f"  {RED}Too low! Way off.{RESET}\n")
            else:
                print(f"  {YELLOW}Too low! Getting closer.{RESET}\n")
        else:
            gap = guess - secret
            if gap > difficulty.high // 5:
                print(f"  {RED}Too high! Way off.{RESET}\n")
            else:
                print(f"  {YELLOW}Too high! Getting closer.{RESET}\n")

    # Out of attempts
    elapsed = time.time() - start
    stats.record(won=False, score=0, secret=secret, guesses=difficulty.max_attempts)
    print(f"\n  {RED}{BOLD}💀 Out of attempts! The number was {secret}.{RESET}\n")


def main() -> None:
    _show_banner()
    stats = SessionStats()

    while True:
        difficulty = _pick_difficulty()
        play_round(difficulty, stats)
        _show_stats(stats)

        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print(f"\n{CYAN}Thanks for playing! Final score: {stats.total_score} pts{RESET}\n")
            break


if __name__ == "__main__":
    main()
