from env.chess_env import ChessEnv
from constants.config import Config

EPISODE = 1000

class SelfPlayWorker:

    def __init__(self, config: Config):
        pass

    def run(self):
        pass


if __name__ == '__main__':
    c = Config()
    ep = 0
    env = ChessEnv()
    env.reset()

    while not env.done:
        env.render()
        print(env.fen)

        action = input("uci -> ")
        try:
            env.step(action)
        except AssertionError as e:
            print(e)






