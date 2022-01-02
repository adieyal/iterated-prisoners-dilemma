from enum import Enum
from collections import defaultdict
from random import choice, random
from itertools import product

class Action(Enum):
    COOPERATE = 1
    DEFECT = 2

shorthand1 = {
    Action.COOPERATE: "C",
    Action.DEFECT: "D",
}

shorthand2 = {
    (Action.COOPERATE, Action.COOPERATE): "CC",
    (Action.COOPERATE, Action.DEFECT): "CD",
    (Action.DEFECT, Action.COOPERATE): "DC",
    (Action.DEFECT, Action.DEFECT): "DD",
}


payoff = {
        (Action.COOPERATE, Action.COOPERATE): (-1, -1),
        (Action.COOPERATE, Action.DEFECT): (-3, 0),
        (Action.DEFECT, Action.COOPERATE): (0, -3),
        (Action.DEFECT, Action.DEFECT): (-2, -2),
}


moves = {
    (Action.COOPERATE, Action.COOPERATE): 0,
    (Action.COOPERATE, Action.DEFECT): 1,
    (Action.DEFECT, Action.COOPERATE): 2,
    (Action.DEFECT, Action.DEFECT): 3,
}

def get_bit(value, bit_index):
    return (value >> bit_index) & 1

class Strategy:
    def __init__(self, length):
        self._length = length
        self._actions = []

        self._generate()

    @property
    def num_states(self):
        acc = 0
        for i in range(self._length + 1):
            acc += 4 ** i

        return acc

    def _generate(self):
        for i in range(self.num_states):
            self._actions.append(choice([Action.COOPERATE, Action.DEFECT]))

    def get_index(self, sequence):
        if len(sequence) == 0:
            return 0

        reversed = list(sequence)[::-1]
        shift = 0
        for i in range(len(sequence)):
            shift += 4 ** i
        acc = 0 
        for idx, move in enumerate(reversed):
            acc += 4 ** idx * moves[reversed[idx]]

        return shift + acc 

    def get_sequence(self, index):
        if index == 0:
            return []

        acc = 0
        for i in range(1, index + 1):
            products = list(product(moves.keys(), repeat=i))
            for p in products:
                acc += 1
                if acc == index:
                    return p

        return None



    def get_action(self, sequence):
        look_back_history = sequence[-self._length:]
        index = self.get_index(look_back_history)
        return self.actions[index]

    @property
    def action_stats(self):
        return {
            Action.COOPERATE: sum(1 for el in self._actions if el == Action.COOPERATE),
            Action.DEFECT: sum(1 for el in self._actions if el == Action.DEFECT),
        }

    @property
    def actions(self):
        return self._actions

    def __str__(self):
        return " ".join(shorthand1[el] for el in self._actions)

class ActionStrategy(Strategy):

    def _generate(self):
        self._actions = []
        for i in range(self.num_states):
            sequence = self.get_sequence(i)
            if len(sequence) == 0:
                self._actions.append(Action.COOPERATE)
            else:
                last_round = sequence[-1]
                opponent_move = last_round[1]
                action = self.get_action(sequence)
                self._actions.append(action)

class CooperationStrategy(ActionStrategy):
    def get_action(self, sequence):
        return Action.COOPERATE

class DefectionStrategy(ActionStrategy):
    def get_action(self, sequence):
        return Action.DEFECT

class TitForTatStrategy(ActionStrategy):

    def get_action(self, sequence):
        if len(sequence) == 0:
            return Action.COOPERATE

        last_round = sequence[-1]
        other_player_move = last_round[1]

        if other_player_move == Action.DEFECT:
            return Action.DEFECT
        return Action.COOPERATE

class TitForNTatStrategy(ActionStrategy):
    def __init__(self, n_tats, *args, **kwargs):
        self._tat_count = 0
        self._ntat = n_tats

        super().__init__(*args, **kwargs)

    def get_action(self, sequence):
        if len(sequence) == 0:
            self._tat_count = 0
            return Action.COOPERATE

        last_round = sequence[-1]
        other_player_move = last_round[1]

        if other_player_move == Action.DEFECT:
            self._tat_count += 1
        else:
            self._tat_count = 0

        if self._tat_count >= self._ntat:
            return Action.DEFECT
        else:
            return Action.COOPERATE

class OppositeStrategy(ActionStrategy):
    def get_action(self, sequence):
        if len(sequence) == 0:
            return Action.COOPERATE

        last_round = sequence[-1]
        other_player_move = last_round[1]

        if other_player_move == Action.DEFECT:
            return Action.COOPERATE
        else:
            return Action.DEFECT

class BiasStrategy(ActionStrategy):
    def __init__(self, bias, *args, **kwargs):
        self._bias = bias
        super().__init__(*args, **kwargs)

    def get_action(self, sequence):
        if random() < self._bias:
            return Action.COOPERATE
        return Action.DEFECT

class Game:
    def __init__(self):
        self._history = []

    @property
    def history(self):
        return self._history

    @property
    def reversed_history(self):
        return [(x2, x1) for (x1, x2) in self._history]

    def play_round(self, action1, action2):
        self._history.append((action1, action2))
        return payoff[(action1, action2)]

class Player:
    def __init__(self, strategy=None, name=""):
        self._score = 0
        self._strategy = strategy
        self._name = name

    @property
    def score(self):
        return self._score

    @property
    def strategy(self):
        return self._strategy

    @property
    def name(self):
        return self._name

    def add_score(self, score):
        self._score += score

class Competition:
    def __init__(self, num_players, history_length, num_rounds=10):
        self._players = []
        self._num_rounds = num_rounds
        for i in range(num_players):
            strategy = Strategy(history_length)
            strategy = BiasStrategy(i/num_players, history_length)
            self._players.append(Player(strategy, name=f"{i/num_players} bias"))
            #self._players.append(Player(strategy, name=str(i)))

        p_cooperate = Player(CooperationStrategy(history_length), name=f"Cooperate")
        self._players.append(p_cooperate)


        p_defect = Player(DefectionStrategy(history_length), name="Defect")
        self._players.append(p_defect)

        p_tit_for_tat = Player(TitForTatStrategy(history_length), name="Tit for tat")
        self._players.append(p_tit_for_tat)

        p_tit_for_1tat = Player(TitForNTatStrategy(1, history_length), name="Tit for 1 tat")
        self._players.append(p_tit_for_1tat)

        p_tit_for_2tat = Player(TitForNTatStrategy(2, history_length), name="Tit for 2 tat")
        self._players.append(p_tit_for_2tat)

        p_tit_for_3tat = Player(TitForNTatStrategy(3, history_length), name="Tit for 3 tat")
        self._players.append(p_tit_for_3tat)

        p_opposite = Player(OppositeStrategy(history_length), name="Opposite strategy")
        self._players.append(p_opposite)

        p_bias0_2 = Player(BiasStrategy(0.2, history_length), name="20% bias")
        self._players.append(p_bias0_2)

        p_bias0_4 = Player(BiasStrategy(0.4, history_length), name="40% bias")
        self._players.append(p_bias0_4)

        p_bias0_6 = Player(BiasStrategy(0.6, history_length), name="60% bias")
        self._players.append(p_bias0_6)

        p_bias0_8 = Player(BiasStrategy(0.8, history_length), name="80% bias")
        self._players.append(p_bias0_8)

        print(p_bias0_8.strategy)

    @property
    def players(self):
        return self._players

    def start_competition(self):
        game_history = defaultdict(list)

        for idx1, p1 in enumerate(self.players):
            for idx2, p2 in enumerate(self.players):
                if p1 == p2:
                    continue
                game = Game()
                for r in range(self._num_rounds):
                    action1 = p1.strategy.get_action(game.history)
                    action2 = p2.strategy.get_action(game.reversed_history)
                    res = game.play_round(action1, action2)
                    p1.add_score(res[0])
                    p2.add_score(res[1])
                    game_history[(idx1, idx2)].append(res)

        sorted_players = sorted(self.players, key=lambda x: x.score)
        print("position,score,average cooperate,name")
        for idx, player in enumerate(sorted_players):
            stats = player.strategy.action_stats
            avg = stats[Action.COOPERATE] / (sum(stats.values()))
            #print(f"Player {idx} score - {player.score} - avg cooperate {avg}")
            #print(player.strategy)
            print(f"{idx},{player.score},{avg},{player.name}")

if __name__ == "__main__":
    c = Competition(100, 4, 50)
    c.start_competition()
