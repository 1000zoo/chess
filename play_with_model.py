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


def start(white=True):
    env = ChessEnv()
    player = Player.WHITE if white else Player.BLACK
    action_label = Config().flipped_labels if white else Config().labels
    model = load()
    env.reset()

    while not env.done:
        env.render()
        action = None
        if player == env.turn:
            action = input("uci => ")

        else:
            state = env.canonical_input_planes().reshape((-1, 18, 8, 8))
            mp = model.predict(state, verbose=0)[0]
            action = np.argmax(mp)
            action = action_label[action]

        env.step(action)




if __name__ == '__main__':
    start()

























