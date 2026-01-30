# ur/game.py
import random
import copy

# Board mapping and paths (as agreed)
P1_PATH = [3,2,1,0,6,7,8,9,10,11,12,5,4]
P2_PATH = [16,15,14,13,6,7,8,9,10,11,12,18,17]

FINAL_STEP = len(P1_PATH)  # number of on-board steps before finishing

ROSETTES = {0, 4, 9, 13, 17}
SAFE_SQUARES = {9}  # only central rosette is safe from capture

class UrGame:
    def __init__(self):
        self.reset()

    def reset(self):
        # positions: -1 = offboard, 0..FINAL_STEP-1 = on path step index, FINAL_STEP = finished
        N = 50
        self.pos = [[-1] * N, [-1] * N]
        self.turn = 0
        self.winner = None

    def clone(self):
        # deep copy of full game state for safe simulation by bots
        return copy.deepcopy(self)

    def roll_dice(self):
        # four binary dice with 3/4 chance of 1, 1/4 chance of 0
        return sum(random.choices((0, 1), weights=(1, 3), k=4))

    def path(self, player):
        return P1_PATH if player == 0 else P2_PATH

    def occupied_by(self, player):
        """Return set of board-square indices occupied by player's pieces (only on-board)."""
        occ = set()
        path = self.path(player)
        for sp in self.pos[player]:
            if 0 <= sp < FINAL_STEP:
                occ.add(path[sp])
        return occ

    def legal_moves(self, roll):
        """
        Return list of piece indices that can legally move given the roll.
        Enforces:
         - roll == 0 -> no moves
         - cannot overshoot final (exact-roll to finish)
         - cannot land on own piece
         - cannot capture on SAFE_SQUARES (move is illegal if target is SAFE and occupied by opponent)
        """
        if roll == 0:
            return []

        moves = []
        p = self.turn
        path = self.path(p)
        opp = 1 - p

        for i, pos in enumerate(self.pos[p]):
            if pos == FINAL_STEP:
                continue  # already finished
            new = pos + roll
            if new > FINAL_STEP:
                continue  # overshoot illegal
            # finishing square is always legal if exact
            if new == FINAL_STEP:
                moves.append(i)
                continue
            target_sq = path[new]
            # own-piece blocking
            if target_sq in self.occupied_by(p):
                continue
            # if target is safe and opponent occupies it, move is illegal (can't capture safe)
            if target_sq in SAFE_SQUARES and target_sq in self.occupied_by(opp):
                continue
            moves.append(i)
        return moves

    def play_move(self, piece, roll):
        """
        Apply move for current player:
         - update piece position
         - perform capture (unless SAFE_SQUARES)
         - award extra turn if landing on any ROSETTE (but only SAFE prevents capture)
         - update winner if finished
        """
        p = self.turn
        pos = self.pos[p][piece]
        new = pos + roll

        # move piece
        self.pos[p][piece] = new

        # if finished
        if new == FINAL_STEP:
            if all(x == FINAL_STEP for x in self.pos[p]):
                self.winner = p
            # finishing does not grant extra turn; switch turn
            self.turn = 1 - p
            return

        # landing square index on board
        target = self.path(p)[new]

        # capture opponent piece at target unless target is in SAFE_SQUARES
        if target not in SAFE_SQUARES:
            opp = 1 - p
            for idx, opp_pos in enumerate(self.pos[opp]):
                if 0 <= opp_pos < FINAL_STEP and self.path(opp)[opp_pos] == target:
                    # send opponent piece to start
                    self.pos[opp][idx] = -1

        # if landed on a rosette, player gets another turn (do not switch)
        if target in ROSETTES:
            return

        # otherwise switch turn
        self.turn = 1 - p

    # convenience: string representation for debugging
    def __repr__(self):
        return f"<UrGame turn={self.turn} pos={self.pos} winner={self.winner}>"
