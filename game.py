import state as st
import random as rand

class Game:
    def __init__(self):
        self.state = st.State()

    def start_game(self):
        while not self.state.is_final_state():
            if self.state.get_player() == 0:
                self.player_turn()
            else:
                self.ai_turn()

    def player_turn(self):
        """Handle player moves."""
        self.state.first_roll()
        while self.state.can_roll():
            self.state.play.print_hand()
            self.state.play.print_table()

            command = input("What move would you like to do? (move/roll/select): ").strip().lower()

            if command == "move":
                move_command = input("Move from (table/hand): ").strip().lower()
                if move_command == "table":
                    pos = int(input("Which table dice.py to move to hand (0-4): "))
                    if 0 <= pos < len(self.state.play.table_dices):
                        self.state.play.table_to_hand(pos)
                    else:
                        print("Invalid position.")
                elif move_command == "hand":
                    pos = int(input("Which hand dice.py to move to table (0-4): "))
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

    def ai_turn(self):
        """Handle AI moves."""
        print("AI is playing...")
        self.state.first_roll()

        while self.state.can_roll():
            decision = rand.randint(0, 2)

            if decision == 0:
                if self.state.play.table_dices and rand.randint(0, 1) == 0:
                    pos = rand.randint(0, len(self.state.play.table_dices) - 1)
                    print(f"AI moves table dice.py {self.state.play.table_dices[pos]} to hand.")
                    self.state.play.table_to_hand(pos)
                elif self.state.play.hand_dices:
                    pos = rand.randint(0, len(self.state.play.hand_dices) - 1)
                    print(f"AI moves hand dice.py {self.state.play.hand_dices[pos]} to table.")
                    self.state.play.hand_to_table(pos)

            elif decision == 1 and self.state.can_roll():
                print("AI decides to reroll.")
                self.state.next_turn()

        select = self.state.get_random_valid_key()
        if select is not None:
            print(f"AI selects category: {select}")
            self.state.choose_category(select)
            self.state.play.print_hand()
            self.state.play.print_table()
            self.state.print_player_score(1)
        else:
            print("No valid categories left for AI.")
        self.state.next_player()