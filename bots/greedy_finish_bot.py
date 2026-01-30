import random
from bots.utils import landing_square, is_rosette

class GreedyFinishBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        player = game.turn
        final_step = len(game.path(player))

        for m in moves:
            if game.pos[player][m] + roll == final_step:
                return m

        rosettes = []
        for m in moves:
            sq = landing_square(game, player, m, roll)
            if sq is not None and is_rosette(game, sq):
                rosettes.append(m)
        if rosettes:
            return random.choice(rosettes)

        return random.choice(moves)
