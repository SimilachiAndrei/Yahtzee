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

class State:
    def __init__(self):
        round = 0
        score = [0,0]
        player = rand.randint(0,1)
        throw_turn = 3
        play = Dice()
    def get_is_played(self):
        return round == 13


class game:
    def __init__(self):
        state = State()
    # def start_game(self):






# round = Dice()
#
# round.first_roll()
# round.print_table()
# round.table_to_hand(2)
# round.print_table()
# round.print_hand()
