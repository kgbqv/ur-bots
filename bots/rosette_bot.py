import random
from bots.utils import landing_square, is_rosette

class RosetteFirstBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        player = game.turn
        rosettes = []
        for m in moves:
            sq = landing_square(game, player, m, roll)
            if sq is not None and is_rosette(game, sq):
                rosettes.append(m)
        if rosettes:
            return random.choice(rosettes)
        return random.choice(moves)
