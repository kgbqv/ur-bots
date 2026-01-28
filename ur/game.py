import random
import copy

ROSETTES = {3,7,13,19}

P1_PATH = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
P2_PATH = [14,15,16,3,4,5,6,7,8,9,10,11,17,18]

class UrGame:
    def __init__(self):
        self.pos = [[-1]*7, [-1]*7]
        self.turn = 0

    def clone(self):
        return copy.deepcopy(self)

    def roll(self):
        return sum(random.randint(0,1) for _ in range(4))

    def board_occupant(self, board_index):
        for p in (0,1):
            for i,pos in enumerate(self.pos[p]):
                if pos >= 0:
                    path = P1_PATH if p==0 else P2_PATH
                    if path[pos] == board_index:
                        return (p,i)
        return None

    def legal_moves(self, roll):
        p = self.turn
        path = P1_PATH if p==0 else P2_PATH
        moves = []

        for i,pos in enumerate(self.pos[p]):
            new = pos + roll
            if new > 13:
                continue
            if new == 13:
                moves.append(i)
                continue

            board_sq = path[new]
            occ = self.board_occupant(board_sq)
            if occ:
                op,_ = occ
                if op == p: 
                    continue
                if board_sq in ROSETTES:
                    continue
            moves.append(i)

        return moves

    def play_move(self, piece, roll):
        p = self.turn
        path = P1_PATH if p==0 else P2_PATH
        pos = self.pos[p][piece]
        new = pos + roll

        if new < 13:
            board_sq = path[new]
            occ = self.board_occupant(board_sq)
            if occ:
                op,oi = occ
                self.pos[op][oi] = -1

        self.pos[p][piece] = new

        extra = (new < 13 and path[new] in ROSETTES)
        if not extra:
            self.turn ^= 1

    def winner(self):
        for p in (0,1):
            if all(pos == 13 for pos in self.pos[p]):
                return p
        return None
