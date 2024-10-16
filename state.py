import dice as dc
import random as rand

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
        score = self.calculate_score(category)
        self.categories[category][self.get_player()] = score

    def print_player_score(self, player):
        print(f"Player {player} score: {sum(val[player] for val in self.categories.values())}")

    def calculate_score(self, category):
        dice = self.play.table_dices
        if category == "aces":
            return sum(die for die in dice if die == 1)
        elif category == "twos":
            return sum(die for die in dice if die == 2)
        elif category == "threes":
            return sum(die for die in dice if die == 3)
        elif category == "fours":
            return sum(die for die in dice if die == 4)
        elif category == "fives":
            return sum(die for die in dice if die == 5)
        elif category == "sixes":
            return sum(die for die in dice if die == 6)
        elif category == "three of a kind":
            if any(dice.count(die) >= 3 for die in dice):
                return sum(dice)
            else:
                return 0
        elif category == "four of a kind":
            if any(dice.count(die) >= 4 for die in dice):
                return sum(dice)
        elif category == "full house":
            unique_dice = set(dice)
            if len(unique_dice) == 2 and (dice.count(list(unique_dice)[0]) in [2, 3]):
                return 25
            else:
                return 0
        elif category == "small straight":
            if set([1, 2, 3, 4]).issubset(set(dice)) or set([2, 3, 4, 5]).issubset(set(dice)) or set([3, 4, 5, 6]).issubset(set(dice)):
                return 30
            else:
                return 0
        elif category == "large straight":
            if set([1, 2, 3, 4, 5]) == set(dice) or set([2, 3, 4, 5, 6]) == set(dice):
                return 40
            else:
                return 0
        elif category == "yahtzee":
            if dice.count(dice[0]) == 5:
                return 50
            else:
                return 0
        elif category == "chance":
            return sum(dice)
        else:
            return 0
