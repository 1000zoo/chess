import os
import json
import numpy as np

from keras.models import load_model
from keras.engine.training import Model

from chess_game.board import *
from constants.config import *
from constants.constant import Player, Done
from env.chess_env import ChessEnv
from agent.model_chess import ChessModel




def load(path="trained_model", model="model_weight.h5", config="model_config.json"):
    model_path = os.path.join(path, model)
    config_path = os.path.join(path, config)

    with open(config_path, "rt") as f:
        model = Model.from_config(json.load(f))

    model.load_weights(model_path)
    model.make_predict_function()
    model.summary()
    return model


def start():
    env = ChessEnv()
    white = load()
    black = load()
    white_label = Config().labels
    black_label = Config().flipped_labels
    env.reset()
    turns = 2

    while not env.done:
        state = env.canonical_input_planes().reshape((-1, 18, 8, 8))
        if env.white_to_move:
            print("-" * 30)
            print(turns // 2)
            print("-" * 30)
            mp = white.predict(state, verbose=0)[0] * env.all_legal_moves_onehot
            mp /= mp.sum()
            action = np.argmax(mp)
            action = white_label[action]
            print(white.predict(state, verbose=0)[1])
        else:
            mp = black.predict(state, verbose=0)[0] * env.all_legal_moves_onehot
            mp /= mp.sum()
            action = np.argmax(mp)
            action = black_label[action]
            print(-1 * white.predict(state, verbose=0)[1])

        env.step(action)
        env.render()

        turns += 1

    print(env.winner)


if __name__ == '__main__':
    start()

























