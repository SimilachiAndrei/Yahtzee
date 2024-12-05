import state as st
import random as rand


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
        """Automate AI moves."""
        self.state.first_roll()

        while self.state.can_roll():
            decision = rand.randint(0, 2)
            if decision == 0:
                if self.state.play.table_dices and rand.randint(0, 1) == 0:
                    pos = rand.randint(0, len(self.state.play.table_dices) - 1)
                    self.state.play.table_to_hand(pos)
                elif self.state.play.hand_dices:
                    pos = rand.randint(0, len(self.state.play.hand_dices) - 1)
                    self.state.play.hand_to_table(pos)
            elif decision == 1 and self.state.can_roll():
                self.state.play.roll()
                self.state.next_turn()

        select = self.state.get_random_valid_key()
        if select is not None:
            self.state.choose_category(select)
        self.state.next_player()

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
