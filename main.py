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
        self.round = 0
        self.player = rand.randint(0,1)
        self.throw_turn = 3
        self.play = Dice()
        self.categories = {"aces": [0, 0], "twos": [0, 0], "threes": [0, 0], "fours": [0, 0], "fives": [0, 0], "sixes": [0, 0],
                           "three of a kind": [0, 0], "four of a kind": [0, 0], "full house": [0, 0], "small straight": [0, 0],
                           "large straight": [0, 0], "yahtzee": [0, 0], "chance": [0, 0]}
    # def get_is_played(self):
    #     return round != 13
    def get_player(self):
        return self.player

    def is_final_state(self):
        return self.round >=13

    def choose_category(self, category, player_number):
        score = self.calculate_score(category)
        self.categories[category][player_number] = score

    def print_player_score(self, player):
        print(sum(val[player] for val in self.categories))

    def calculate_score(self, category):
        dice = self.play.hand_dices
        if category == "aces":
            return sum(die for die in dice if die == 1)
        elif category == "twos":
            return sum(die for die in dice if die == 2)
        elif category == "3 of a kind":
            if any(dice.count(die) >= 3 for die in dice):
                return sum(dice)
        ## TO DO: the rest of them
            else:
                return 0

    def next_turn(self):
        if self.throw_turn == 0:
            self.round += 1
            self.throw_turn = 3
            self.player = (self.player + 1) % 2  # Switch player
    def can_roll(self):
        return self.throw_turn > 0

class Game:
    def __init__(self):
        self.state = State()
    def start_game(self):
        while(self.state.get_is_played()):
            if self.state.get_player() == 0:
                command = input("What move would you like to do ?")
                if(command == "roll" ):self.state.play.first_roll()
                self.state.play.print_table()
                self.state.play.print_hand()
                self.state.player = (self.state.player + 1) % 2
            else:
                decision = rand.randint(0,1)
                self.state.play.first_roll()
                self.state.play.print_table()
                self.state.play.print_hand()
                if decision:
                    self.state.play.table_to_hand(2)
                    self.state.play.print_table()
                    self.state.play.print_hand()
                    self.state.play.roll()
                    self.state.play.print_table()
                    self.state.play.print_hand()
                    self.state.play.hand_to_table(0)
                    self.state.play.print_table()
                    self.state.play.print_hand()
                self.state.player = (self.state.player + 1) % 2


game = Game()
game.start_game()