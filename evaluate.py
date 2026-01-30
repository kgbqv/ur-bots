# evaluate.py
import sys
import importlib
from pathlib import Path

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

def run_tournament(games_per_pair=100):
    bot_classes = load_bots()
    names = list(bot_classes.keys())
    M = len(names)

    overall_wins = {n: 0 for n in names}
    overall_games = {n: 0 for n in names}

    pairwise = np.full((M, M), np.nan)

    total_pairs = M * (M - 1) // 2
    pbar = tqdm(total=total_pairs, desc="Pairings")

    for i in range(M):
        for j in range(i + 1, M):
            nameA = names[i]
            nameB = names[j]

            winsA = 0

            for k in range(games_per_pair):
                # Alternate who is player 0
                if k % 2 == 0:
                    bot0 = make_bot(bot_classes[nameA])
                    bot1 = make_bot(bot_classes[nameB])

                    mapA_player = 0
                else:
                    bot0 = make_bot(bot_classes[nameA])
                    bot1 = make_bot(bot_classes[nameB])

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
    return names, overall_wins, overall_games, pairwise


# ---------------------------
# Plot + Save
# ---------------------------

def save_results(names, overall_wins, overall_games, pairwise):
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


# ---------------------------
# Main
# ---------------------------

if __name__ == "__main__":
    names, wins, games, pairwise = run_tournament(games_per_pair=100)
    save_results(names, wins, games, pairwise)
