from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from threading import Lock

import chess
import numpy as np

from constants.config import Config, flip_policy
from env.chess_env import ChessEnv, Winner

logger = getLogger(__name__)


class VisitStats:
    def __init__(self):
        self.a = defaultdict(ActionStats)
        self.sum_n = 0


class ActionStats:
    def __init__(self):
        self.n = 0
        self.w = 0
        self.q = 0
        self.p = 0


class ChessPlayer:
    # dot = False
    def __init__(self, config: Config, pipes=None, play_config=None, dummy=False):
        self.moves = []

        self.tree = defaultdict(VisitStats)
        self.config = config
        self.play_config = play_config or self.config.play
        self.labels_n = config.n_labels
        self.labels = config.labels
        self.move_lookup = {move: i for move, i in zip(self.labels, range(self.labels_n))}
        if dummy:
            return

        self.pipe_pool = pipes
        self.node_lock = defaultdict(Lock)

    def reset(self):
        self.tree = defaultdict(VisitStats)

    def deboog(self, env):
        print(env.testeval())

        state = state_key(env)
        my_visit_stats = self.tree[state]
        stats = []
        for action, a_s in my_visit_stats.a.items():
            moi = self.move_lookup[action]
            stats.append(np.asarray([a_s.n, a_s.w, a_s.q, a_s.p, moi]))
        stats = np.asarray(stats)
        a = stats[stats[:,0].argsort()[::-1]]

        for s in a:
            print(f'{self.labels[int(s[4])]:5}: '
                  f'n: {s[0]:3.0f} '
                  f'w: {s[1]:7.3f} '
                  f'q: {s[2]:7.3f} '
                  f'p: {s[3]:7.5f}')

    def action(self, env, can_stop = True) -> str:
        self.reset()

        # for tl in range(self.play_config.thinking_loop):
        root_value, naked_value = self.search_moves(env)
        policy = self.calc_policy(env)
        my_action = int(np.random.choice(range(self.labels_n), p = self.apply_temperature(policy, env.num_halfmoves)))

        if can_stop and self.play_config.resign_threshold is not None and \
                        root_value <= self.play_config.resign_threshold \
                        and env.num_halfmoves > self.play_config.min_resign_turn:
            # noinspection PyTypeChecker
            return None
        else:
            self.moves.append([env.observation, list(policy)])
            return self.config.labels[my_action]

    def search_moves(self, env) -> (float, float):
        futures = []
        with ThreadPoolExecutor(max_workers=self.play_config.search_threads) as executor:
            for i in range(self.play_config.simulation_num_per_move):
                futures.append(executor.submit(self.search_my_move,env=env.copy(),is_root_node=True))

        vals = [f.result() for f in futures]

        return np.max(vals), vals[0] # vals[0] is kind of racy

    def search_my_move(self, env: ChessEnv, is_root_node=False, action="") -> float:
        if env.done:
            if env.winner == Winner.draw:
                return 0
            return -1

        state = state_key(env)

        with self.node_lock[state]:
            if state not in self.tree:
                leaf_p, leaf_v = self.expand_and_evaluate(env)
                self.tree[state].p = leaf_p
                return leaf_v

            # SELECT STEP
            action_t = self.select_action_q_and_u(env, is_root_node, action)

            virtual_loss = self.play_config.virtual_loss

            my_visit_stats = self.tree[state]
            my_stats = my_visit_stats.a[action_t]

            my_visit_stats.sum_n += virtual_loss
            my_stats.n += virtual_loss
            my_stats.w += -virtual_loss
            my_stats.q = my_stats.w / my_stats.n

        env.step(action_t)
        leaf_v = self.search_my_move(env, action_t)  # next move from enemy POV
        leaf_v = -leaf_v

        # BACKUP STEP
        # on returning search path
        # update: N, W, Q
        with self.node_lock[state]:
            my_visit_stats.sum_n += -virtual_loss + 1
            my_stats.n += -virtual_loss + 1
            my_stats.w += virtual_loss + leaf_v
            my_stats.q = my_stats.w / my_stats.n

        return leaf_v

    def expand_and_evaluate(self, env) -> (np.ndarray, float):
        state_planes = env.canonical_input_planes()

        leaf_p, leaf_v = self.predict(state_planes)

        if not env.white_to_move:
            leaf_p = flip_policy(leaf_p)

        return leaf_p, leaf_v

    def predict(self, state_planes):
        pipe = self.pipe_pool.pop()
        pipe.send(state_planes)
        ret = pipe.recv()
        self.pipe_pool.append(pipe)
        return ret


    def select_action_q_and_u(self, env: ChessEnv, is_root_node, action=""):
        # this method is called with state locked
        state = state_key(env)

        my_visitstats = self.tree[state]

        try:
            if my_visitstats.p is not None: #push p to edges
                tot_p = 1e-8
                for mov in env.board.legal_moves:
                    mov_p = my_visitstats.p[self.move_lookup[mov]]
                    my_visitstats.a[mov].p = mov_p
                    tot_p += mov_p
                for a_s in my_visitstats.a.values():
                    a_s.p /= tot_p
                my_visitstats.p = None

        except AttributeError as ae:
            print(ae)
            print(env.board)
            print(action)

        xx_ = np.sqrt(my_visitstats.sum_n + 1)  # sqrt of sum(N(s, b); for all b)

        e = self.play_config.noise_eps
        c_puct = self.play_config.c_puct
        dir_alpha = self.play_config.dirichlet_alpha

        best_s = -999
        best_a = None
        if is_root_node:
            noise = np.random.dirichlet([dir_alpha] * len(my_visitstats.a))

        i = 0
        for action, a_s in my_visitstats.a.items():
            p_ = a_s.p
            if is_root_node:
                p_ = (1-e) * p_ + e * noise[i]
                i += 1
            b = a_s.q + c_puct * p_ * xx_ / (1 + a_s.n)
            if b > best_s:
                best_s = b
                best_a = action

        return best_a

    def apply_temperature(self, policy, turn):
        """
        Applies a random fluctuation to probability of choosing various actions
        :param policy: list of probabilities of taking each action
        :param turn: number of turns that have occurred in the game so far
        :return: policy, randomly perturbed based on the temperature. High temp = more perturbation. Low temp
            = less.
        """
        tau = np.power(self.play_config.tau_decay_rate, turn + 1)
        if tau < 0.1:
            tau = 0
        if tau == 0:
            action = np.argmax(policy)
            ret = np.zeros(self.labels_n)
            ret[action] = 1.0
            return ret
        else:
            ret = np.power(policy, 1/tau)
            ret /= np.sum(ret)
            return ret

    def calc_policy(self, env):
        """calc π(a|s0)
        :return list(float): a list of probabilities of taking each action, calculated based on visit counts.
        """
        state = state_key(env)
        my_visitstats = self.tree[state]
        policy = np.zeros(self.labels_n)
        for action, a_s in my_visitstats.a.items():
            policy[self.move_lookup[action]] = a_s.n

        policy /= np.sum(policy)
        return policy


    def finish_game(self, z):
        """
        When game is done, updates the value of all past moves based on the result.

        :param self:
        :param z: win=1, lose=-1, draw=0
        :return:
        """
        for move in self.moves:  # add this game winner result to all past moves.
            move += [z]


def state_key(env: ChessEnv) -> str:
    """
    :param ChessEnv env: env to encode
    :return str: a str representation of the game state
    """
    fen = env.board.fen().rsplit(' ', 1) # drop the move clock
    return fen[0]
