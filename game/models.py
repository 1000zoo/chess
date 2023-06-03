"""
Defines the actual model for making policy and value predictions given an observation.
"""

import ftplib
import hashlib
import json
import os
from logging import getLogger

from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.regularizers import l2
from keras import Input
from keras.layers import BatchNormalization, Activation, Dense, Flatten, Add

# noinspection PyPep8Naming

logger = getLogger(__name__)

## https://github.com/Zeta36/chess-alpha-zero/blob/master/src/chess_zero/agent/model_chess.py
class ChessModel:
    """
    The model which can be trained to take observations of a game of chess and return value and policy
    predictions.

    Attributes:
        :ivar Config config: configuration to use
        :ivar Model model: the Keras model to use for predictions
        :ivar digest: basically just a hash of the file containing the weights being used by this model
        :ivar ChessModelAPI api: the api to use to listen for and then return this models predictions (on a pipe).
    """

    def __init__(self):
        self.model = None  # type: Model
        self.digest = None
        self.api = None

        self.cnn_filter_num = 256
        self.cnn_first_filter_size = 5
        self.cnn_filter_size = 3
        self.res_layer_num = 7
        self.l2_reg = 1e-4
        self.value_fc_size = 256
        self.distributed = False
        self.input_depth = 18
        self.n_labels = 1968
        self.build()

    def build(self):
        """
        Builds the full Keras model and stores it in self.model.
        """
        in_x = x = Input((18, 8, 8))

        # (batch, channels, height, width)
        x = Conv2D(filters=self.cnn_filter_num, kernel_size=self.cnn_first_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.l2_reg),
                   name="input_conv-" + str(self.cnn_first_filter_size) + "-" + str(self.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="input_batchnorm")(x)
        x = Activation("relu", name="input_relu")(x)

        for i in range(self.res_layer_num):
            x = self._build_residual_block(x, i + 1)

        res_out = x

        # for policy output
        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", use_bias=False,
                   kernel_regularizer=l2(self.l2_reg),
                   name="policy_conv-1-2")(res_out)
        x = BatchNormalization(axis=1, name="policy_batchnorm")(x)
        x = Activation("relu", name="policy_relu")(x)
        x = Flatten(name="policy_flatten")(x)
        # no output for 'pass'
        policy_out = Dense(self.n_labels, kernel_regularizer=l2(self.l2_reg), activation="softmax",
                           name="policy_out")(x)

        # for value output
        x = Conv2D(filters=4, kernel_size=1, data_format="channels_first", use_bias=False,
                   kernel_regularizer=l2(self.l2_reg),
                   name="value_conv-1-4")(res_out)
        x = BatchNormalization(axis=1, name="value_batchnorm")(x)
        x = Activation("relu", name="value_relu")(x)
        x = Flatten(name="value_flatten")(x)
        x = Dense(self.value_fc_size, kernel_regularizer=l2(self.l2_reg), activation="relu", name="value_dense")(x)
        value_out = Dense(1, kernel_regularizer=l2(self.l2_reg), activation="tanh", name="value_out")(x)

        self.model = Model(in_x, [policy_out, value_out], name="chess_model")

    def _build_residual_block(self, x, index):
        in_x = x
        res_name = "res" + str(index)
        x = Conv2D(filters=self.cnn_filter_num, kernel_size=self.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.l2_reg),
                   name=res_name + "_conv1-" + str(self.cnn_filter_size) + "-" + str(self.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name=res_name + "_batchnorm1")(x)
        x = Activation("relu", name=res_name + "_relu1")(x)
        x = Conv2D(filters=self.cnn_filter_num, kernel_size=self.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.l2_reg),
                   name=res_name + "_conv2-" + str(self.cnn_filter_size) + "-" + str(self.cnn_filter_num))(x)
        x = BatchNormalization(axis=1, name="res" + str(index) + "_batchnorm2")(x)
        x = Add(name=res_name + "_add")([in_x, x])
        x = Activation("relu", name=res_name + "_relu2")(x)
        return x

if __name__ == "__main__":
    cm = ChessModel()
    cm.model.summary()