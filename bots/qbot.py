import pickle
import random

class QBot:
    def __init__(self, filename):
        with open(filename,"rb") as f:
            self.q = pickle.load(f)

    def state_key(self, game):
        return tuple(game.pos[0] + game.pos[1] + [game.turn])

    def choose_move(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        best, best_q = None, -1e9
        for m in moves:
            key = (self.state_key(game), roll, m)
            val = self.q.get(key, 0)
            if val > best_q:
                best_q = val
                best = m
        return best if best is not None else random.choice(moves)
