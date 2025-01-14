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
    def get_table_and_hand(self):
        return self.hand_dices + self.table_dices

    def transfer_to_table(self):
        if not self.hand_dices:
            print("No dice in hand to transfer.")
            return
        self.table_dices.extend(self.hand_dices)
        self.hand_dices.clear()

    def transfer_to_hand(self):
        if not self.table_dices:
            print("No dice in table to transfer.")
            return
        self.hand_dices.extend(self.table_dices)
        self.table_dices.clear()

    def hand_to_table_list(self, pos):
        for i, transfer in enumerate(pos):
            if transfer == 1:
                if i < len(self.table_dices):
                    self.hand_dices.append(self.table_dices[i])
                    self.table_dices.pop(i)
                    break
