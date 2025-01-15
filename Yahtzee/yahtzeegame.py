import state as st
import random as rand
import RL_AI

from Yahtzee.utils import convert_to_score_sheet


class YahtzeeGame:
    def __init__(self):
        self.state = st.State()

    def start_round(self):
        """Start a new round based on the current player."""
        if self.state.is_final_state():
            return "Game Over"

        current_player = self.state.get_player()
        if current_player == 0:
            return "player_turn"
        else:
            return "ai_turn"

    def player_first_roll(self):
        """Handle the player's first roll."""
        self.state.first_roll()

    def player_roll_dice(self):
        """Handle rolling the dice for the player."""
        if self.state.can_roll():
            self.state.next_turn()
            return True
        return False

    def ai_turn(self):
        self.with_rl_ai()


    def with_rl_ai(self):
        self.state.first_roll()

        while self.state.throw_turn < 3:
            action_data = RL_AI.show_best_move(
                self.state.play.table_dices,
                convert_to_score_sheet(self.state.categories),
                self.state.throw_turn
            )

            if isinstance(action_data, tuple) and action_data[0] == "Reroll":
                _, reroll_pattern = action_data
                self.state.play.hand_to_table_list(reroll_pattern)
                self.state.play.roll()
                self.state.next_turn()
                self.state.play.transfer_to_table()
                print("Rerolling dice...")
            elif action_data is not None:
                print("Choosing category...")
                self.state.play.transfer_to_hand()
                self.choose_category(action_data.lower())
                break
            else:
                print("No valid action. Skipping turn.")
                break
            print("self categories: " + str(self.state.categories))
            print("converted categories: " + str(convert_to_score_sheet(self.state.categories)))

    def choose_category(self, category):
        """Player or AI selects a category after their turn."""
        if self.state.is_valid_category(category):
            self.state.choose_category(category)
            self.state.next_player()
            return True
        return False

    def move_dice_hand_to_table(self, index):
        """Move dice from hand to table."""
        if 0 <= index < len(self.state.play.hand_dices):
            self.state.play.hand_to_table(index)

    def move_dice_table_to_hand(self, index):
        """Move dice from table to hand."""
        if 0 <= index < len(self.state.play.table_dices):
            self.state.play.table_to_hand(index)

    def get_hand_dices(self):
        """Return the current dice in hand."""
        return self.state.play.hand_dices

    def get_table_dices(self):
        """Return the current dice on the table."""
        return self.state.play.table_dices

    def get_scores(self):
        """Return the current player and AI scores."""
        player_score = sum(val[0] for val in self.state.categories.values() if val[0] is not None)
        ai_score = sum(val[1] for val in self.state.categories.values() if val[1] is not None)
        return player_score, ai_score

    def is_game_over(self):
        """Check if the game has reached a final state."""
        return self.state.is_final_state()