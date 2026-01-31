# bots/expectimax2_bot.py
import math

DICE_PROBS = {
    0: 1/16,
    1: 4/16,
    2: 6/16,
    3: 4/16,
    4: 1/16,
}

class Expectimax2Bot:
    """
    2-ply expectimax:
    - our move
    - opponent expected move
    - our expected response
    """

    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        best_val = -math.inf
        best_move = None

        for m in moves:
            g2 = game.clone()
            g2.play_move(m, roll)

            val = self.expect_opp(g2)
            if val > best_val:
                best_val = val
                best_move = m

        return best_move

    def expect_opp(self, game):
        val = 0.0
        for r, p in DICE_PROBS.items():
            g2 = game.clone()
            moves = g2.legal_moves(r)

            if not moves:
                g2.turn ^= 1
                val += p * self.expect_self(g2)
            else:
                worst = math.inf
                for m in moves:
                    g3 = g2.clone()
                    g3.play_move(m, r)
                    worst = min(worst, self.expect_self(g3))
                val += p * worst
        return val

    def expect_self(self, game):
        val = 0.0
        for r, p in DICE_PROBS.items():
            g2 = game.clone()
            moves = g2.legal_moves(r)

            if not moves:
                g2.turn ^= 1
                val += p * self.eval(g2)
            else:
                best = -math.inf
                for m in moves:
                    g3 = g2.clone()
                    g3.play_move(m, r)
                    best = max(best, self.eval(g3))
                val += p * best
        return val

    def eval(self, game):
        me = game.turn
        opp = me ^ 1

        my_path = game.path(me)
        opp_path = game.path(opp)
        Lm = len(my_path)
        Lo = len(opp_path)

        score = 0.0

        # progress
        score += 2.0 * sum(p for p in game.pos[me] if p >= 0)
        score -= 2.0 * sum(p for p in game.pos[opp] if p >= 0)

        # finished pieces (huge)
        score += 15 * sum(p == Lm for p in game.pos[me])
        score -= 15 * sum(p == Lo for p in game.pos[opp])

        # rosettes
        ROSETTES = {0, 4, 9, 13, 17}

        for p in game.pos[me]:
            if 0 <= p < Lm and my_path[p] in ROSETTES:
                score += 3

        for p in game.pos[opp]:
            if 0 <= p < Lo and opp_path[p] in ROSETTES:
                score -= 3

        return score
