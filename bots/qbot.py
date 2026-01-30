# bots/qbot.py
import pickle
from pathlib import Path
import random

class QBot:
    def __init__(self, filename="trained/QBot.pkl"):
        self.Q = {}
        if Path(filename).exists():
            with open(filename, "rb") as f:
                self.Q = pickle.load(f)

    def encode_state(self, game):
        return (
            tuple(game.pos[0]),
            tuple(game.pos[1]),
            game.turn
        )

    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        state = self.encode_state(game)
        qs = [self.Q.get((state, m), 0.0) for m in moves]
        maxq = max(qs)
        best = [m for m, q in zip(moves, qs) if q == maxq]
        return random.choice(best)
