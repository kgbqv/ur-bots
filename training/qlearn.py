# training/qlearn.py
import random
import pickle
from pathlib import Path

from ur.game import UrGame


SAVE_DIR = Path("trained")
SAVE_DIR.mkdir(exist_ok=True)
SAVE_FILE = SAVE_DIR / "QBot.pkl"


# -----------------------------
# Q-learning Bot
# -----------------------------

class QBot:
    def __init__(self, filename=SAVE_FILE):
        self.filename = filename
        self.Q = {}
        if Path(filename).exists():
            with open(filename, "rb") as f:
                self.Q = pickle.load(f)

    def save(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.Q, f)

    def choose(self, game, roll, epsilon=0.1):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        state = self.encode_state(game)

        # epsilon-greedy
        if random.random() < epsilon:
            return random.choice(moves)

        qs = [self.Q.get((state, m), 0.0) for m in moves]
        maxq = max(qs)
        best = [m for m, q in zip(moves, qs) if q == maxq]
        return random.choice(best)

    def encode_state(self, game):
        # simple tuple representation
        return (
            tuple(game.pos[0]),
            tuple(game.pos[1]),
            game.turn
        )


# -----------------------------
# Training Loop
# -----------------------------

def train(episodes=50000, alpha=0.3, gamma=0.9):
    bot = QBot()
    opponent = RandomOpponent()

    for ep in range(episodes):
        game = UrGame()

        last_state = None
        last_action = None

        while game.winner is None:
            roll = game.roll_dice()
            moves = game.legal_moves(roll)

            if not moves:
                game.turn = 1 - game.turn
                continue

            if game.turn == 0:
                action = bot.choose(game, roll)
            else:
                action = opponent.choose(game, roll)

            state = bot.encode_state(game)

            game.play_move(action, roll)

            reward = 0
            if game.winner == 0:
                reward = 1
            elif game.winner == 1:
                reward = -1

            if last_state is not None:
                old = bot.Q.get((last_state, last_action), 0.0)
                future = 0.0

                if game.winner is None:
                    next_moves = game.legal_moves(game.roll_dice())
                    if next_moves:
                        future = max(bot.Q.get((state, m), 0.0) for m in next_moves)

                newval = old + alpha * (reward + gamma * future - old)
                bot.Q[(last_state, last_action)] = newval

            last_state = state
            last_action = action

        # final update for terminal state
        old = bot.Q.get((last_state, last_action), 0.0)
        bot.Q[(last_state, last_action)] = old + alpha * (reward - old)

        if (ep + 1) % 5000 == 0:
            print(f"Episode {ep+1}/{episodes}")

    bot.save()
    print("Training complete. Saved to", SAVE_FILE)


# -----------------------------
# Simple Random Opponent
# -----------------------------

class RandomOpponent:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        return random.choice(moves)


# -----------------------------
# Run via python -m training.qlearn
# -----------------------------

if __name__ == "__main__":
    train()
