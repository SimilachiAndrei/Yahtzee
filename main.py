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
        self.player = rand.randint(0, 1)
        self.throw_turn = 3
        self.play = Dice()
        self.categories = {"aces": [0, 0], "twos": [0, 0], "threes": [0, 0], "fours": [0, 0], "fives": [0, 0],
                           "sixes": [0, 0],
                           "three of a kind": [0, 0], "four of a kind": [0, 0], "full house": [0, 0],
                           "small straight": [0, 0],
                           "large straight": [0, 0], "yahtzee": [0, 0], "chance": [0, 0]}

    def get_player(self):
        return self.player

    def get_random_valid_key(self):
        available_categories = [category for category in self.categories if
                                self.categories[category][self.get_player()] == 0]
        if available_categories:
            return rand.choice(available_categories)
        else:
            return None

    # validations
    def is_final_state(self):
        return self.round >= 13

    def can_roll(self):
        return self.throw_turn > 0

    def is_valid_category(self, category):
        if self.categories[category][self.get_player()] == 0:
            return True
        return False

    # transitions
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
        print(sum(val[player] for val in self.categories.values()))

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
            else:
                return 0
        elif category == "full house":
            unique_dice = set(dice)
            if len(unique_dice) == 2 and (dice.count(list(unique_dice)[0]) in [2, 3]):
                return 25
            else:
                return 0
        elif category == "small straight":
            if set([1, 2, 3, 4]).issubset(set(dice)) or set([2, 3, 4, 5]).issubset(set(dice)) or set(
                    [3, 4, 5, 6]).issubset(set(dice)):
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


class Game:
    def __init__(self):
        self.state = State()

    def start_game(self):
        while not self.state.is_final_state():
            if self.state.get_player() == 0:
                self.state.first_roll()
                while self.state.can_roll():
                    self.state.play.print_hand()
                    self.state.play.print_table()

                    command = input("What move would you like to do? (move/roll/select): ").strip().lower()

                    if command == "move":
                        move_command = input("Move from (table/hand): ").strip().lower()
                        if move_command == "table":
                            pos = int(input("Which table dice to move to hand (0-4): "))
                            if 0 <= pos < len(self.state.play.table_dices):
                                self.state.play.table_to_hand(pos)
                            else:
                                print("Invalid position.")
                        elif move_command == "hand":
                            pos = int(input("Which hand dice to move to table (0-4): "))
                            if 0 <= pos < len(self.state.play.hand_dices):
                                self.state.play.hand_to_table(pos)
                            else:
                                print("Invalid position.")
                        else:
                            print("Invalid move command.")

                    elif command == "roll":
                        if self.state.can_roll():
                            self.state.next_turn()
                            self.state.play.print_hand()
                            self.state.play.print_table()
                        else:
                            print("No rolls left.")

                    elif command == "select":
                        category = input("Select a category: ").strip().lower()
                        if self.state.is_valid_category(category):
                            self.state.choose_category(category)
                            self.state.print_player_score(0)
                            self.state.next_player()
                            break
                        else:
                            print("Invalid category or already chosen.")

                    else:
                        print("Invalid command.")
            else:
                print("AI is playing...")
                self.state.first_roll()
                while self.state.can_roll():
                    decision = rand.randint(0, 1)
                    if decision:
                        select = self.state.get_random_valid_key()
                        if select is not None:
                            print(f"AI selects category: {select}")
                            self.state.choose_category(select)
                            self.state.print_player_score(1)
                            self.state.next_player()
                            break
                        else:
                            print("No valid categories left for AI.")
                            self.state.next_player()
                            break
                    else:
                        decision2 = rand.randint(0, 1)
                        if decision2:
                            decision3 = rand.randint(0, 1)
                            if decision3:
                                if self.state.play.table_dices:
                                    pos = rand.randint(0, len(self.state.play.table_dices) - 1)
                                    print(f"AI moves table dice {self.state.play.table_dices[pos]} to hand.")
                                    self.state.play.table_to_hand(pos)
                            else:
                                if self.state.play.hand_dices:
                                    pos = rand.randint(0, len(self.state.play.hand_dices) - 1)
                                    print(f"AI moves hand dice {self.state.play.hand_dices[pos]} to table.")
                                    self.state.play.hand_to_table(pos)
                        else:
                            if self.state.can_roll():
                                print("AI decides to reroll.")
                                self.state.next_turn()
                            else:
                                print("AI cannot reroll.")
                self.state.next_player()


game = Game()
game.start_game()
