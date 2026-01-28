import random
import pickle
from ur.game import UrGame
from bots.random_bot import RandomBot

class QBot:
    def __init__(self, qtable=None, epsilon=0.1):
        self.q = qtable if qtable else {}
        self.epsilon = epsilon

    def state_key(self, game):
        return tuple(game.pos[0] + game.pos[1] + [game.turn])

    def choose_move(self, game, roll):
        moves = game.legal_moves(roll)
        if not moves:
            return None

        if random.random() < self.epsilon:
            return random.choice(moves)

        best, best_q = None, -1e9
        for m in moves:
            key = (self.state_key(game), roll, m)
            val = self.q.get(key, 0)
            if val > best_q:
                best_q = val
                best = m
        return best

def train(episodes=50000, out_file="qbot.pkl"):
    qbot = QBot()
    opponent = RandomBot()
    alpha = 0.3
    gamma = 0.9

    for ep in range(episodes):
        game = UrGame()
        bots = [qbot, opponent]

        while not game.winner():
            roll = game.roll()
            moves = game.legal_moves(roll)

            if not moves:
                game.turn ^= 1
                continue

            bot = bots[game.turn]
            move = bot.choose_move(game.clone(), roll)

            state = qbot.state_key(game)
            game.play_move(move, roll)
            reward = 0

            if game.winner() == 0:
                reward = 1
            elif game.winner() == 1:
                reward = -1

            next_state = qbot.state_key(game)
            key = (state, roll, move)
            old = qbot.q.get(key, 0)
            qbot.q[key] = old + alpha * (reward + gamma * old - old)

        if ep % 5000 == 0:
            print("Episode", ep)

    with open(out_file, "wb") as f:
        pickle.dump(qbot.q, f)

    print("Saved trained bot to", out_file)

if __name__ == "__main__":
    train()
