import dice as dc
import random as rand
import utils as util

class State:
    def __init__(self):
        self.round = 0
        self.player = rand.randint(0, 1)
        self.throw_turn = 3
        self.play = dc.Dice()
        self.categories = {
            "aces": [0, 0], "twos": [0, 0], "threes": [0, 0], "fours": [0, 0], "fives": [0, 0],
            "sixes": [0, 0], "three of a kind": [0, 0], "four of a kind": [0, 0], "full house": [0, 0],
            "small straight": [0, 0], "large straight": [0, 0], "yahtzee": [0, 0], "chance": [0, 0]
        }

    def get_player(self):
        return self.player

    def get_random_valid_key(self):
        available_categories = [category for category in self.categories if
                                self.categories[category][self.get_player()] == 0]
        return rand.choice(available_categories) if available_categories else None

    # Validations
    def is_final_state(self):
        return self.round >= 13

    def can_roll(self):
        return self.throw_turn > 0

    def is_valid_category(self, category):
        return self.categories[category][self.get_player()] == 0

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
        print(f"Player {player} score: {sum(val[player] for val in self.categories.values())}")