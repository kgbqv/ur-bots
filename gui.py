import tkinter as tk
import random
from ur.game import UrGame, ROSETTES, SAFE_SQUARES, FINAL_STEP

CELL = 60

BOARD_COORDS = {
    0:(0,0), 1:(0,1), 2:(0,2), 3:(0,3), 4:(0,5), 5:(0,6),
    6:(1,0), 7:(1,1), 8:(1,2), 9:(1,3),10:(1,4),11:(1,5),12:(1,6),
    13:(2,0),14:(2,1),15:(2,2),16:(2,3),17:(2,5),18:(2,6)
}

# ---------------- Bots ----------------

class RandomBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        return random.choice(moves)

BOT1 = RandomBot()
BOT2 = RandomBot()

# ---------------- GUI ----------------

class UrGUI:
    def __init__(self):
        self.game = UrGame()
        self.root = tk.Tk()
        self.root.title("Royal Game of Ur — Animated Bots")

        self.canvas = tk.Canvas(self.root, width=7*CELL, height=3*CELL, bg="burlywood3")
        self.canvas.pack()

        self.info = tk.Label(self.root, font=("Arial",14))
        self.info.pack()

        self.draw_board()
        self.update()

        self.animating = False
        self.root.after(800, self.autoplay)

        self.root.mainloop()

    def draw_board(self):
        self.canvas.delete("all")
        for sq,(r,c) in BOARD_COORDS.items():
            x1 = c*CELL
            y1 = r*CELL
            x2 = x1+CELL
            y2 = y1+CELL

            color = "burlywood2"
            if sq in ROSETTES:
                color = "gold"
            if sq in SAFE_SQUARES:
                color = "orange"

            self.canvas.create_rectangle(x1,y1,x2,y2,fill=color,outline="black")
            self.canvas.create_text(x1+4,y1+4,anchor="nw",text=str(sq),font=("Arial",8))

    def draw_pieces(self):
        for p in [0,1]:
            color = "red" if p==0 else "blue"
            text_color = "white"
            for idx, sp in enumerate(self.game.pos[p]):
                if 0 <= sp < FINAL_STEP:
                    sq = self.game.path(p)[sp]
                    r,c = BOARD_COORDS[sq]
                    x = c*CELL + CELL/2
                    y = r*CELL + CELL/2

                    # piece circle
                    self.canvas.create_oval(x-14,y-14,x+14,y+14,fill=color,outline="black")

                    # piece index number
                    self.canvas.create_text(x, y, text=str(idx), fill=text_color, font=("Arial",10,"bold"))

    def autoplay(self):
        if self.animating:
            return

        if self.game.winner is not None:
            self.info.config(text=f"Winner: Player {self.game.winner+1} — restarting...")
            self.root.after(2000, self.new_game)
            return

        roll = self.game.roll_dice()
        moves = self.game.legal_moves(roll)

        if not moves:
            self.game.turn = 1 - self.game.turn
            self.update()
            self.root.after(400, self.autoplay)
            return

        bot = BOT1 if self.game.turn == 0 else BOT2
        piece = bot.choose(self.game, roll)

        # start animation
        self.animating = True
        self.animate_move(piece, roll, step=1)

    def animate_move(self, piece, roll, step):
        p = self.game.turn
        start_step = self.game.pos[p][piece]
        target_step = start_step + roll

        if step > roll:
            # finalize move in engine
            self.game.play_move(piece, roll)
            self.animating = False
            self.update()
            self.root.after(400, self.autoplay)
            return

        # temporarily move piece visually
        temp_step = start_step + step
        path = self.game.path(p)
        if temp_step < FINAL_STEP:
            sq = path[temp_step]
            r,c = BOARD_COORDS[sq]

            self.draw_board()
            self.draw_pieces()

            # draw moving piece on top
            x = c*CELL + CELL/2
            y = r*CELL + CELL/2
            color = "red" if p==0 else "blue"
            self.canvas.create_oval(x-14,y-14,x+14,y+14,fill=color)

        self.root.after(150, lambda: self.animate_move(piece, roll, step+1))

    def update(self):
        self.draw_board()
        self.draw_pieces()
        self.info.config(text=f"Player {self.game.turn+1}'s turn")

    def new_game(self):
        self.game.reset()
        self.animating = False
        self.update()
        self.root.after(800, self.autoplay)


if __name__ == "__main__":
    UrGUI()
