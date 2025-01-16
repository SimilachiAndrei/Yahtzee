import tkinter as tk
import dqn
import yahtzeegame as yz
from chatbot import chatbot_response
from utils import convert_to_score_sheet


class YahtzeeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Yahtzee Game")
        self.game = yz.YahtzeeGame()

        # Initialize the menu screen
        self.init_menu_screen()

    def init_menu_screen(self):
        """Set up the initial menu screen with buttons RL, DQN, and ExpectiMax."""
        self.menu_frame = tk.Frame(self.master)
        self.menu_frame.pack(expand=True, fill=tk.BOTH)

        self.menu_label = tk.Label(self.menu_frame, text="Choose an option to start:", font=('Arial', 16))
        self.menu_label.pack(pady=20)

        # Button names and their actions
        menu_options = [("RL", 1), ("DQN", 2), ("ExpectiMax", 3)]

        self.menu_buttons = []
        for name, value in menu_options:
            button = tk.Button(self.menu_frame, text=name, font=('Arial', 14),
                               command=lambda num=value: self.handle_menu_choice(num))
            button.pack(pady=10)
            self.menu_buttons.append(button)

    def handle_menu_choice(self, number):
        """Handle the menu choice and transition to the main game."""
        print(f"Option chosen: {['RL', 'DQN', 'ExpectiMax'][number - 1]}")
        self.game.ai_type = number - 1
        self.menu_frame.destroy()  # Remove the menu frame
        self.init_game_screen()  # Initialize the full game screen

    def init_game_screen(self):
        """Set up the full game interface."""
        with open("feedback.txt", "w") as file:
            file.write("")

        self.main_pane = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # Left frame for game content
        self.left_frame = tk.Frame(self.main_pane)
        self.main_pane.add(self.left_frame)

        # Right frame for chat content
        self.right_frame = tk.Frame(self.main_pane, padx=20, pady=10)
        self.main_pane.add(self.right_frame)

        # Title
        self.title_frame = tk.Frame(self.left_frame)
        self.title_frame.pack()
        self.title_label = tk.Label(self.title_frame, text='Yahtzee!', font=('Arial', 16))
        self.title_label.pack()

        # Player's dice hands and table frame
        self.dice_frame = tk.Frame(self.left_frame)
        self.dice_frame.pack()
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
            table_label.bind("<Button-1>", lambda event, idx=i: self.move_dice_table_to_hand(idx))
            self.table_labels.append(table_label)

        # Roll and Select Category buttons
        self.roll_button = tk.Button(self.left_frame, text="Roll", command=self.roll_dice, state=tk.DISABLED)
        self.roll_button.pack()

        # Category selection
        self.category_frame = tk.Frame(self.left_frame)
        self.category_frame.pack()
        self.category_buttons = []
        self.create_category_table()

        # AI status label
        self.status_label = tk.Label(self.left_frame, text="AI Status: Waiting", font=('Arial', 16))
        self.status_label.pack()

        # Score display
        self.score_frame = tk.Frame(self.left_frame)
        self.score_frame.pack()
        self.player_score_label = tk.Label(self.score_frame, text='Player Score: 0', font=('Arial', 16))
        self.player_score_label.grid(row=0, column=0)
        self.ai_score_label = tk.Label(self.score_frame, text='AI Score: 0', font=('Arial', 16))
        self.ai_score_label.grid(row=0, column=1)

        # Category score table
        self.category_table_frame = tk.Frame(self.left_frame)
        self.category_table_frame.pack(pady=10)
        self.category_table = []
        self.create_category_score_table()

        # Chat box on the right
        self.text_entry = tk.Entry(self.right_frame, font=('Arial', 14), width=30)
        self.text_entry.pack(pady=5)
        self.text_submit_button = tk.Button(self.right_frame, text="Submit", command=self.submit_text)
        self.text_submit_button.pack(pady=5)
        self.response_label = tk.Label(self.right_frame, text='', font=('Arial', 14), justify=tk.LEFT, wraplength=300)
        self.response_label.pack(pady=10, fill=tk.BOTH, expand=True)

        # Start the first round
        self.start_round()

    def submit_text(self):
        """Handle text submission from the user."""
        user_input = self.text_entry.get()
        if user_input == "help":
            action_data = dqn.show_best_move(
                self.game.state.play.table_dices,
                convert_to_score_sheet(self.game.state.categories),
                self.game.state.throw_turn
            )
            if isinstance(action_data, tuple) and action_data[0] == "Reroll":
                response = "Reroll the following dice: "
                for idx, die in enumerate(action_data[1]):
                    if not die:
                        response += f" {idx + 1}"
            else: response = action_data
        else:
            response = chatbot_response(user_input)
        self.response_label.config(text=response)

    def create_category_score_table(self):
        """Create the category score table with 3 columns: Category, Player Score, AI Score."""
        categories = self.game.state.categories.keys()
        tk.Label(self.category_table_frame, text="Category", font=("Arial", 12), width=20, anchor="w").grid(row=0, column=0)
        tk.Label(self.category_table_frame, text="Player Score", font=("Arial", 12), width=15, anchor="w").grid(row=0, column=1)
        tk.Label(self.category_table_frame, text="AI Score", font=("Arial", 12), width=15, anchor="w").grid(row=0, column=2)
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
        print("player turn")
        """Handle the player's turn (first roll is automatic)."""
        self.game.player_first_roll()
        self.update_dice_display()

        # Enable player controls
        self.roll_button.config(state=tk.NORMAL)
        for button in self.category_buttons:
            button.config(state=tk.NORMAL)

    def roll_dice(self):
        self.feedback("Reroll")  # Send feedback to the feedback method
        if self.game.player_roll_dice():
            self.update_dice_display()
        else:
            self.feedback("No rolls left.")  # Send feedback to the feedback method

    def choose_category(self, category):
        self.feedback(category)  # Send feedback to the feedback method
        if self.game.choose_category(category):
            self.update_score_display()
            self.update_category_score_table()  # Update category score table
            self.disable_player_controls()
            self.start_round()
        else:
            self.feedback(
                f"Category '{category}' has already been selected or is invalid.")  # Send feedback to the feedback method

    def feedback(self, message):
        action_data = dqn.show_best_move(
            self.game.state.play.table_dices,
            convert_to_score_sheet(self.game.state.categories),
            self.game.state.throw_turn
        )
        dices = self.game.state.play.get_table_and_hand()
        if isinstance(action_data, tuple) and action_data[0] == "Reroll":
            if message != "Reroll":
                with open("feedback.txt", "a") as file:
                    file.write(f"For this dices {dices} you choose {message} but we advise you to select Reroll\n")
        elif action_data is not None:
            if action_data.lower() != message:
                with open("feedback.txt", "a") as file:
                    file.write(f"For this dices {dices} you choose {message} but we advise you to select {action_data}\n")

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
        """End the game and display the final scores with options to play again or exit."""
        # Clear any previous widgets in the left and right frames
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Set up the end game frame in the left part of the screen
        end_game_frame = tk.Frame(self.left_frame)
        end_game_frame.pack(expand=True)

        player_score, ai_score = self.game.get_scores()
        winner = "Player" if player_score > ai_score else "AI"

        # Display Game Over and scores
        tk.Label(
            end_game_frame,
            text="Game Over!",
            font=('Arial', 24, 'bold')
        ).pack(pady=20)

        tk.Label(
            end_game_frame,
            text=f"Final Scores:\nPlayer: {player_score}\nAI: {ai_score}\nWinner: {winner}",
            font=('Arial', 18)
        ).pack(pady=20)

        # Add buttons to play again or exit
        button_frame = tk.Frame(end_game_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Play Again",
            command=self.restart_game,
            font=('Arial', 14),
            width=15
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Exit",
            command=self.master.quit,
            font=('Arial', 14),
            width=15
        ).pack(side=tk.LEFT, padx=10)

        # Set up the right frame for displaying the feedback
        feedback_frame = tk.Frame(self.right_frame, padx=20, pady=10)
        feedback_frame.pack(fill=tk.BOTH, expand=True)

        # Try to read feedback from the feedback.txt file
        try:
            with open("feedback.txt", "r") as file:
                feedback_content = file.read()

            # Create a Text widget with a scrollbar for the feedback content
            feedback_text = tk.Text(feedback_frame, font=('Arial', 12), wrap=tk.WORD, width=40, height=15)
            feedback_text.insert(tk.END, feedback_content)
            feedback_text.config(state=tk.DISABLED)  # Make it read-only

            # Add a scrollbar to the Text widget
            scrollbar = tk.Scrollbar(feedback_frame, command=feedback_text.yview)
            feedback_text.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            feedback_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        except FileNotFoundError:
            # If feedback.txt doesn't exist, show a default message
            feedback_text = tk.Label(feedback_frame, text="No feedback available.", font=('Arial', 12))
            feedback_text.pack(pady=20)

    def restart_game(self):
        """Reset the game and return to the initial menu screen."""
        for widget in self.master.winfo_children():
            widget.destroy()

        self.game = yz.YahtzeeGame()

        self.init_menu_screen()
