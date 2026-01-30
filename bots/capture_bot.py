import random
from bots.utils import will_capture

class CaptureFirstBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        player = game.turn
        captures = [m for m in moves if will_capture(game, player, m, roll)]
        if captures:
            return random.choice(captures)
        return random.choice(moves)
