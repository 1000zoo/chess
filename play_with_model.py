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
    model = load()
    computer = ChessPlayer(Config(), model=model)
    action_label = Config().flipped_labels if white else Config().labels

    env.reset()

    while not env.done:
        env.render()
        if player == env.turn:
            try:
                action = input("uci => ")
            except KeyError as err:
                print(err)
                continue
            except ValueError as err:
                print(err)
                continue

        else:
            action = computer.action(env)

        try:
            env.step(action)
        except KeyError as err:
            print(err)
            continue
        except ValueError as err:
            print(err)
            continue




if __name__ == '__main__':
    start()

























