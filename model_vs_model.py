import os
import json
import numpy as np

from keras.models import load_model
from keras.engine.training import Model

from chess_game.board import *
from constants.config import *
from constants.constant import Player, Done
from env.chess_env import ChessEnv
from agent.player_chess import ChessPlayer
from agent.model_chess import ChessModel




def load(path="trained_model", model="model_best_weight.h5", config="model_best_config.json"):
    model_path = os.path.join(path, model)
    config_path = os.path.join(path, config)

    with open(config_path, "rt") as f:
        model = Model.from_config(json.load(f))

    model.load_weights(model_path)
    model.make_predict_function()
    model.summary()
    return model


def start(white=False):
    env = ChessEnv()
    player = Player.WHITE if white else Player.BLACK
    mw = load()
    mb = load(model="model_weight.h5", config="model_config.json")
    white = ChessPlayer(Config(), model=mw)
    black = ChessPlayer(Config(), model=mb)

    white_label = Config().labels
    black_label = Config().flipped_labels

    env.reset()

    while not env.done:
        print(env.num_halfmoves)
        print(env.fen)
        env.render()
        if player == env.turn:
            action = white.action(env)

        else:
            action = black.action(env)

        env.step(action)

    print(env.winner)


if __name__ == '__main__':
    start()

























