from random import seed

import pytest

from dilemma import Strategy, Action, Game, Player, payoff, Competition, CooperationStrategy

shorthand = {
    "CC": (Action.COOPERATE, Action.COOPERATE),
    "CD": (Action.COOPERATE, Action.DEFECT),
    "DC": (Action.DEFECT, Action.COOPERATE),
    "DD": (Action.DEFECT, Action.DEFECT),
}

@pytest.fixture
def strategy():
    length = 3
    seed(10)
    return Strategy(length)

@pytest.fixture
def game():
    return Game()

class TestStrategy:
    def _convert_shorthand(self, sequence):
        return tuple(shorthand[el] for el in sequence)

    def test_generate(self, strategy):
        length = 3
        assert len(strategy.actions) == strategy.num_states
        assert strategy.actions[0] == Action.COOPERATE
        assert strategy.actions[1] == Action.DEFECT
        assert strategy.actions[2] == Action.DEFECT
        assert strategy.actions[3] == Action.COOPERATE
        assert strategy.actions[4] == Action.COOPERATE
        assert strategy.actions[5] == Action.DEFECT
        assert strategy.actions[6] == Action.DEFECT
        assert strategy.actions[7] == Action.DEFECT

    def test_index(self, strategy):
        sequences = {
            ("CC",): 1, ("CD",): 2, ("DC",): 3, ("DD",): 4,
            ("CC", "CC"): 5, ("CC", "CD"): 6, ("CC", "DC",): 7, ("CC", "DD",): 8,
            ("CD", "CC"): 9, ("CD", "CD"): 10, ("CD", "DC",): 11, ("CD", "DD",): 12,
            ("DC", "CC"): 13, ("DC", "CD"): 14, ("DC", "DC",): 15, ("DC", "DD",): 16,
            ("DD", "CC"): 17, ("DD", "CD"): 18, ("DD", "DC",): 19, ("DD", "DD",): 20,
            ("CC", "CC", "CC"): 21, ("CC", "CC", "CD"): 22, ("CC", "CC", "DC",): 23, ("CC", "CC", "DD",): 24,
        }

        for sequence, index in sequences.items():
            converted_sequences = self._convert_shorthand(sequence)
            assert strategy.get_index(converted_sequences) == index

    def test_get_sequence(self, strategy):
        assert strategy.get_sequence(0) == []
        assert strategy.get_sequence(1) == ((shorthand["CC"]), )
        assert strategy.get_sequence(2) == ((shorthand["CD"]), )
        assert strategy.get_sequence(3) == ((shorthand["DC"]), )
        assert strategy.get_sequence(4) == ((shorthand["DD"]), )
        assert strategy.get_sequence(5) == tuple(shorthand[el] for el in ["CC", "CC"])
        assert strategy.get_sequence(6) == tuple(shorthand[el] for el in ["CC", "CD"])
        assert strategy.get_sequence(9) == tuple(shorthand[el] for el in ["CD", "CC"])
        assert strategy.get_sequence(22) == tuple(shorthand[el] for el in ["CC", "CC", "CD"])

    def test_get_action(self):
        length = 3
        test_sequence = 26
        strategy = CooperationStrategy(length)
        strategy._actions[test_sequence] = Action.DEFECT

        history = (
            strategy.get_sequence(10)
            + strategy.get_sequence(15)
            + strategy.get_sequence(test_sequence)
        )
        assert strategy.get_action(history) == Action.DEFECT

class TestGame:
    def test_history(self, game):
        assert len(game.history) == 0

        game.play_round(Action.COOPERATE, Action.DEFECT)
        assert len(game.history) == 1
        assert game.history[0] == (Action.COOPERATE, Action.DEFECT)

        game.play_round(Action.DEFECT, Action.DEFECT)
        assert len(game.history) == 2
        assert game.history[0] == (Action.COOPERATE, Action.DEFECT)
        assert game.history[1] == (Action.DEFECT, Action.DEFECT)

    def test_play_round(self, game):
        length = 3
        #p1 = Player(Strategy(3)
        #p2 = Player(Strategy(3))

        assert game.play_round(Action.COOPERATE, Action.COOPERATE) == payoff[Action.COOPERATE, Action.COOPERATE]


class TestPlayer:
    def test_score(self, strategy):
        p = Player(strategy)
        assert p.score == 0

        p.add_score(5)
        assert p.score == 5

        p.add_score(-2)
        assert p.score == 3

class TestCompetition:
    def test_create_players(self):
        num_players = 10
        history_length = 3

        c = Competition(num_players, history_length)
        assert len(c.players) == num_players

        for p in c.players:
            assert len(p.strategy.actions) == p.strategy.num_states
