from ur.game import UrGame
from bots.random_bot import RandomBot
from bots.greedy_bot import GreedyBot

def play(botA, botB):
    game = UrGame()
    bots = [botA, botB]

    while not game.winner():
        roll = game.roll()
        moves = game.legal_moves(roll)
        if not moves:
            game.turn ^= 1
            continue
        move = bots[game.turn].choose_move(game.clone(), roll)
        game.play_move(move, roll)

    print("Winner:", game.winner())

if __name__ == "__main__":
    play(RandomBot(), GreedyBot())
