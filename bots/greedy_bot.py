class GreedyBot:
    def choose_move(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        best = None
        best_score = -1

        for m in moves:
            g2 = game.clone()
            g2.play_move(m, roll)
            score = sum(g2.pos[g2.turn ^ 1])  # simple race heuristic
            if score > best_score:
                best_score = score
                best = m

        return best
