import dice as dc
import random as rand
import utils as util

class State:
    def __init__(self):
        self.round = 0
        self.player = 0
        self.throw_turn = 3
        self.play = dc.Dice()
        self.categories = {
            "aces": [None, None], "twos": [None, None], "threes": [None, None], "fours": [None, None], "fives": [None, None],
            "sixes": [None, None], "three of a kind": [None, None], "four of a kind": [None, None], "full house": [None, None],
            "small straight": [None, None], "large straight": [None, None], "yahtzee": [None, None], "chance": [None, None]
        }

    def get_player(self):
        return self.player

    def get_random_valid_key(self):
        available_categories = [category for category in self.categories if
                                self.categories[category][self.get_player()] is not None]
        return rand.choice(available_categories) if available_categories else None

    # Validations
    def is_final_state(self):
        return self.round >= 13

    def can_roll(self):
        return self.throw_turn > 0

    def is_valid_category(self, category):
        if category not in self.categories: return False
        return self.categories[category][self.get_player()] is None

    # Transitions
    def next_player(self):
        if self.player == 1:
            self.round += 1
        self.throw_turn = 3
        self.player = (self.player + 1) % 2

    def next_turn(self):
        if self.can_roll():
            self.play.roll()
            self.throw_turn -= 1

    def first_roll(self):
        self.play.first_roll()
        self.throw_turn -= 1

    def choose_category(self, category):
        score = util.calculate_score(self.play, category)
        print(f"Category: {category}, Score calculated: {score}")
        self.categories[category][self.get_player()] = score

    def print_player_score(self, player):
        total_score = sum(val[player] for val in self.categories.values() if val[player] is not None)
        print(f"Player {player} score: {total_score}")
