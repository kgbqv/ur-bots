# evaluate.py
import sys
import importlib
from pathlib import Path
import time
from collections import defaultdict


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from ur.game import UrGame


# ---------------------------
# Load all bot classes
# ---------------------------

BOTS_DIR = Path("bots")

def load_bots():
    bot_classes = {}

    for file in BOTS_DIR.glob("*.py"):
        if file.name in ("__init__.py", "utils.py","qbot.py"):
            continue

        modname = f"bots.{file.stem}"
        mod = importlib.import_module(modname)

        found_class = None

        for attr in dir(mod):
            obj = getattr(mod, attr)
            # Only accept actual bot classes with choose()
            if isinstance(obj, type) and hasattr(obj, "choose"):
                found_class = obj
                break

        if found_class is None:
            raise RuntimeError(f"No bot class found in {file.name}")

        bot_classes[file.stem] = found_class

    return bot_classes




# ---------------------------
# Play one game
# ---------------------------

def play_game(bot0, bot1):
    game = UrGame()
    bots = [bot0, bot1]

    while game.winner is None:
        roll = game.roll_dice()
        moves = game.legal_moves(roll)

        if not moves:
            game.turn = 1 - game.turn
            continue

        choice = bots[game.turn].choose(game, roll)

        if choice is None:
            game.turn = 1 - game.turn
            continue

        game.play_move(choice, roll)

    return game.winner


# ---------------------------
# Tournament
# ---------------------------
from pathlib import Path

def make_bot(cls):
    # Try no-arg constructor first
    try:
        return cls()
    except TypeError:
        # Otherwise assume it needs a filename
        filename = Path("trained") / f"{cls.__name__}.pkl"
        return cls(filename)
    
class TimedBot:
    def __init__(self, bot, name, stats):
        self.bot = bot
        self.name = name
        self.stats = stats

    def choose(self, game, roll):
        t0 = time.perf_counter()
        move = self.bot.choose(game, roll)
        dt = time.perf_counter() - t0

        self.stats[self.name]["time"] += dt
        self.stats[self.name]["calls"] += 1

        return move

def run_tournament(games_per_pair=100):
    bot_classes = load_bots()
    names = list(bot_classes.keys())
    M = len(names)

    overall_wins = {n: 0 for n in names}
    overall_games = {n: 0 for n in names}

    pairwise = np.full((M, M), np.nan)

    # timing stats
    timing_stats = defaultdict(lambda: {"time": 0.0, "calls": 0})

    total_pairs = M * (M - 1) // 2
    pbar = tqdm(total=total_pairs)

    for i in range(M):
        for j in range(i + 1, M):
            nameA = names[i]
            nameB = names[j]

            winsA = 0

            for k in range(games_per_pair):
                pbar.set_description(f"{nameA} vs {nameB}")
                # alternate starting player
                if k % 2 == 0:
                    bot0 = TimedBot(make_bot(bot_classes[nameA]), nameA, timing_stats)
                    bot1 = TimedBot(make_bot(bot_classes[nameB]), nameB, timing_stats)
                    mapA_player = 0
                else:
                    bot0 = TimedBot(make_bot(bot_classes[nameB]), nameB, timing_stats)
                    bot1 = TimedBot(make_bot(bot_classes[nameA]), nameA, timing_stats)
                    mapA_player = 1

                winner = play_game(bot0, bot1)

                if winner == mapA_player:
                    winsA += 1

            winsB = games_per_pair - winsA

            pairwise[i][j] = winsA / games_per_pair
            pairwise[j][i] = winsB / games_per_pair

            overall_wins[nameA] += winsA
            overall_wins[nameB] += winsB

            overall_games[nameA] += games_per_pair
            overall_games[nameB] += games_per_pair

            pbar.update(1)

    pbar.close()
    return names, overall_wins, overall_games, pairwise, timing_stats

# ---------------------------
# Plot + Save
# ---------------------------

def save_results(names, overall_wins, overall_games, pairwise,timing_stats):
    # ---- overall dataframe ----
    rows = []
    for n in names:
        wr = overall_wins[n] / overall_games[n]
        rows.append([n, overall_wins[n], overall_games[n], wr])

    df = pd.DataFrame(rows, columns=["bot","wins","games","winrate"])
    df = df.sort_values("winrate", ascending=False)
    df.to_csv("overall_winrates.csv", index=False)

    # ---- bar plot ----
    plt.figure(figsize=(10,6))
    plt.bar(df["bot"], df["winrate"])
    plt.ylabel("Win rate")
    plt.title("Overall Win Rates")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("overall_winrates.png")
    plt.close()

    # ---- heatmap ----
    plt.figure(figsize=(10,8))
    plt.imshow(pairwise, aspect="auto")
    plt.colorbar()
    plt.xticks(range(len(names)), names, rotation=45, ha="right")
    plt.yticks(range(len(names)), names)
    plt.title("Pairwise Winrate (row beats column)")
    plt.tight_layout()
    plt.savefig("pairwise_heatmap.png")
    plt.close()

    # ---- pairwise csv ----
    dfp = pd.DataFrame(pairwise, index=names, columns=names)
    dfp.to_csv("pairwise_matrix.csv")

    print("\nSaved:")
    print("overall_winrates.csv")
    print("overall_winrates.png")
    print("pairwise_matrix.csv")
    print("pairwise_heatmap.png")
        # ---- timing stats ----
    timing_rows = []
    for n in names:
        calls = timing_stats[n]["calls"]
        total = timing_stats[n]["time"]
        avg = total / calls if calls > 0 else 0.0
        timing_rows.append([n, calls, total, avg])

    tdf = pd.DataFrame(
        timing_rows,
        columns=["bot", "calls", "total_time_sec", "avg_time_per_call_sec"]
    )
    tdf = tdf.sort_values("avg_time_per_call_sec", ascending=False)
    tdf.to_csv("bot_timings.csv", index=False)

    # ---- timing bar plot ----
    plt.figure(figsize=(10,6))
    plt.bar(tdf["bot"], tdf["avg_time_per_call_sec"])
    plt.ylabel("Avg time per move (seconds)")
    plt.title("Bot Decision Time (Bottleneck Analysis)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("bot_avg_time.png")
    plt.close()

    print("bot_timings.csv")
    print("bot_avg_time.png")



# ---------------------------
# Main
# ---------------------------

if __name__ == "__main__":
    names, wins, games, pairwise,timing_stats = run_tournament(games_per_pair=20)
    save_results(names, wins, games, pairwise,timing_stats)
