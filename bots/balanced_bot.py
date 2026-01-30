import random
from bots.utils import (
    landing_square, is_rosette,
    will_capture, can_opp_capture_after_move
)

class BalancedBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        player = game.turn
        final_step = len(game.path(player))

        # finish if possible
        for m in moves:
            if game.pos[player][m] + roll == final_step:
                return m

        safe_moves = [m for m in moves
                      if not can_opp_capture_after_move(game, player, m, roll)]

        captures = [m for m in safe_moves if will_capture(game, player, m, roll)]
        if captures:
            return random.choice(captures)

        rosettes = []
        for m in safe_moves:
            sq = landing_square(game, player, m, roll)
            if sq is not None and is_rosette(game, sq):
                rosettes.append(m)
        if rosettes:
            return random.choice(rosettes)

        if safe_moves:
            return random.choice(safe_moves)

        return random.choice(moves)
