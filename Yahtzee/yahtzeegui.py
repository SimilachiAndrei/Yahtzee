import tkinter as tk
import yahtzeegame as yz


class YahtzeeGUI:
    def __init__(self, master):
        self.game = yz.YahtzeeGame()
        self.master = master
        master.title("Yahtzee Game")

        # Title
        self.title_frame = tk.Frame(master)
        self.title_frame.pack()

        self.title_label = tk.Label(self.title_frame, text='Yahtzee!', font=('Arial', 16))
        self.title_label.pack()

        # Player's dice hands and table frame
        self.dice_frame = tk.Frame(master)
        self.dice_frame.pack()

        # Hand and table dice labels
        self.hand_labels = []
        self.table_labels = []

        # Create hand dice labels
        for i in range(5):
            hand_label = tk.Label(self.dice_frame, text='0', font=('Arial', 20), width=5, borderwidth=2,
                                  relief="groove")
            hand_label.grid(row=0, column=i)
            hand_label.bind("<Button-1>", lambda event, idx=i: self.move_dice_hand_to_table(idx))
            self.hand_labels.append(hand_label)

        # Create table dice labels
        for i in range(5):
            table_label = tk.Label(self.dice_frame, text='0', font=('Arial', 20), width=5, borderwidth=2,
                                   relief="groove")
            table_label.grid(row=1, column=i)
            table_label.bind("<Button-1>", lambda event, idx=i: self.move_dice_table_to_hand(idx))  # bind click event
            self.table_labels.append(table_label)

        # Roll and Select Category buttons
        self.roll_button = tk.Button(master, text="Roll", command=self.roll_dice, state=tk.DISABLED)
        self.roll_button.pack()

        # Category selection
        self.category_frame = tk.Frame(master)
        self.category_frame.pack()
        self.category_buttons = []
        self.create_category_table()

        # AI status label
        self.status_label = tk.Label(master, text="AI Status: Waiting", font=('Arial', 16))
        self.status_label.pack()

        # Score display
        self.score_frame = tk.Frame(master)
        self.score_frame.pack()

        self.player_score_label = tk.Label(self.score_frame, text='Player Score: 0', font=('Arial', 16))
        self.player_score_label.grid(row=0, column=0)

        self.ai_score_label = tk.Label(self.score_frame, text='AI Score: 0', font=('Arial', 16))
        self.ai_score_label.grid(row=0, column=1)

        # Category score table
        self.category_table_frame = tk.Frame(master)
        self.category_table_frame.pack(pady=10)

        self.category_table = []
        self.create_category_score_table()

        # Start the first round
        self.start_round()

    def create_category_score_table(self):
        """Create the category score table with 3 columns: Category, Player Score, AI Score."""
        categories = self.game.state.categories.keys()

        # Header Row
        tk.Label(self.category_table_frame, text="Category", font=("Arial", 12), width=20, anchor="w").grid(row=0,
                                                                                                            column=0)
        tk.Label(self.category_table_frame, text="Player Score", font=("Arial", 12), width=15, anchor="w").grid(row=0,
                                                                                                                column=1)
        tk.Label(self.category_table_frame, text="AI Score", font=("Arial", 12), width=15, anchor="w").grid(row=0,
                                                                                                            column=2)

        # Rows for categories and their scores
        row = 1
        for category in categories:
            category_name_label = tk.Label(self.category_table_frame, text=category.capitalize(), width=20, anchor="w")
            category_name_label.grid(row=row, column=0)

            player_score_label = tk.Label(self.category_table_frame, text="0", width=15, anchor="w")
            player_score_label.grid(row=row, column=1)

            ai_score_label = tk.Label(self.category_table_frame, text="0", width=15, anchor="w")
            ai_score_label.grid(row=row, column=2)

            self.category_table.append((category_name_label, player_score_label, ai_score_label))
            row += 1

    def update_category_score_table(self):
        """Update the category score table for both the player and AI."""
        categories = self.game.state.categories
        for i, (category_name, (player_score, ai_score)) in enumerate(categories.items()):
            player_score_label, ai_score_label = self.category_table[i][1], self.category_table[i][2]
            player_score_label.config(text=str(player_score) if player_score is not None else "-")
            ai_score_label.config(text=str(ai_score) if ai_score is not None else "-")

    def create_category_table(self):
        categories = self.game.state.categories.keys()
        row = 0
        col = 0
        for category in categories:
            button = tk.Button(self.category_frame, text=category.capitalize(), width=15, height=2,
                               command=lambda cat=category: self.choose_category(cat), state=tk.DISABLED)
            button.grid(row=row, column=col, padx=5, pady=5)
            self.category_buttons.append(button)
            col += 1
            if col % 4 == 0:
                row += 1
                col = 0

    def start_round(self):
        """Start a new round."""
        status = self.game.start_round()
        if status == "Game Over":
            self.end_game()
        elif status == "player_turn":
            self.player_turn()
        elif status == "ai_turn":
            self.ai_turn()

    def player_turn(self):
        """Handle the player's turn (first roll is automatic)."""
        self.game.player_first_roll()
        self.update_dice_display()

        # Enable player controls
        self.roll_button.config(state=tk.NORMAL)
        for button in self.category_buttons:
            button.config(state=tk.NORMAL)

    def roll_dice(self):
        """Handle rolling the dice for the player."""
        if self.game.player_roll_dice():
            self.update_dice_display()
        else:
            print("No rolls left.")

    def choose_category(self, category):
        if self.game.choose_category(category):
            self.update_score_display()
            self.update_category_score_table()  # Update category score table
            self.disable_player_controls()
            self.start_round()
        else:
            print(f"Category '{category}' has already been selected or is invalid.")

    def ai_turn(self):
        """Automate AI moves."""
        self.status_label.config(text="AI Status: Playing...")
        self.game.ai_turn()
        self.update_dice_display()
        self.update_score_display()
        self.update_category_score_table()  # Update category score table
        self.status_label.config(text="AI Status: Waiting")
        self.start_round()

    def move_dice_hand_to_table(self, index):
        """Move dice from hand to table when hand dice is clicked."""
        self.game.move_dice_hand_to_table(index)
        self.update_dice_display()

    def move_dice_table_to_hand(self, index):
        """Move dice from table to hand when table dice is clicked."""
        self.game.move_dice_table_to_hand(index)
        self.update_dice_display()

    def update_dice_display(self):
        """Update the hand and table dice display."""
        hand_dices = self.game.get_hand_dices()
        table_dices = self.game.get_table_dices()

        for i in range(5):
            self.hand_labels[i].config(text=str(hand_dices[i]) if i < len(hand_dices) else '0')
            self.table_labels[i].config(text=str(table_dices[i]) if i < len(table_dices) else '0')

    def update_score_display(self):
        """Update the score display for player and AI."""
        player_score, ai_score = self.game.get_scores()
        self.player_score_label.config(text=f'Player Score: {player_score}')
        self.ai_score_label.config(text=f'AI Score: {ai_score}')

    def disable_player_controls(self):
        """Disable the buttons during the AI's turn or after the player selects a category."""
        self.roll_button.config(state=tk.DISABLED)
        for button in self.category_buttons:
            button.config(state=tk.DISABLED)

    def end_game(self):
        """End the game and display the final scores."""
        player_score, ai_score = self.game.get_scores()
        winner = "Player" if player_score > ai_score else "AI"
        print(f"Game Over! Final Scores - Player: {player_score}, AI: {ai_score}. Winner: {winner}")
