class ProgressBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        player = game.turn

        best = None
        best_pos = 999
        for m in moves:
            pos = game.pos[player][m]
            if pos < best_pos:
                best_pos = pos
                best = m
        return best
