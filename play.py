from ur.game import UrGame
import random

class RandomBot:
    def choose(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None
        return random.choice(moves)

def play(bot1, bot2):
    game = UrGame()

    while game.winner is None:
        roll = game.roll_dice()
        moves = game.legal_moves(roll)

        if not moves:
            game.turn = 1 - game.turn
            continue

        bot = bot1 if game.turn == 0 else bot2
        choice = bot.choose(game, roll)
        game.play_move(choice, roll)

    print("Winner:", game.winner+1)

if __name__ == "__main__":
    play(RandomBot(), RandomBot())
