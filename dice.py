import random as rand

class Dice:
    def __init__(self):
        self.table_dices = []
        self.hand_dices = [1, 2, 3, 4, 5]

    def first_roll(self):
        self.hand_dices = []
        self.table_dices = [rand.randint(1, 6) for _ in range(5)]

    def roll(self):
        self.table_dices = [rand.randint(1, 6) for _ in range(len(self.table_dices))]

    def table_to_hand(self, pos):
        self.hand_dices.append(self.table_dices[pos])
        self.table_dices.pop(pos)

    def hand_to_table(self, pos):
        self.table_dices.append(self.hand_dices[pos])
        self.hand_dices.pop(pos)

    def print_hand(self):
        print(self.hand_dices)

    def print_table(self):
        print(self.table_dices)