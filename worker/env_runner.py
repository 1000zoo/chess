from env.chess_env import ChessEnv
import random
import time

if __name__ == '__main__':
    env = ChessEnv()
    env.reset()

    starttime = time.time()

    while not env.done:
        action = random.choice(env.all_legal_moves)
        print(env.all_legal_moves)

        if env.num_halfmoves >= 1000:
            env.adjudicate()

        try:
            env.step(action)
        except AssertionError as e:
            print(e)

        except TypeError as te:
            print(te)
            print(action)
            exit()

        # except KeyError as ke:
        #     print(ke)
        #     print(action)
        #     exit()

        env.render()
        print(env.fen)

    print(env.winner)
    print(time.time() - starttime)