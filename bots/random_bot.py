import random

class RandomBot:
    def choose_move(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        return random.choice(moves)
