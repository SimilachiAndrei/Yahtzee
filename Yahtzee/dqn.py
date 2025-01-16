import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

NUM_DICE = 5
NUM_SIDES = 6
CATEGORIES = ["Aces", "Twos", "Threes", "Fours", "Fives", "Sixes",
              "Three of a Kind", "Four of a Kind", "Full House",
              "Small Straight", "Large Straight", "Yahtzee", "Chance"]
CATEGORY_SCORES = {
    "Aces": lambda dice: sum(d for d in dice if d == 1),
    "Twos": lambda dice: sum(d for d in dice if d == 2),
    "Threes": lambda dice: sum(d for d in dice if d == 3),
    "Fours": lambda dice: sum(d for d in dice if d == 4),
    "Fives": lambda dice: sum(d for d in dice if d == 5),
    "Sixes": lambda dice: sum(d for d in dice if d == 6),
    "Three of a Kind": lambda dice: sum(dice) if max(dice.count(x) for x in set(dice)) >= 3 else 0,
    "Four of a Kind": lambda dice: sum(dice) if max(dice.count(x) for x in set(dice)) >= 4 else 0,
    "Full House": lambda dice: 25 if sorted(dice.count(x) for x in set(dice)) == [2, 3] else 0,
    "Small Straight": lambda dice: 30 if len(set(dice) & {1, 2, 3, 4}) == 4 or len(
        set(dice) & {2, 3, 4, 5}) == 4 or len(set(dice) & {3, 4, 5, 6}) == 4 else 0,
    "Large Straight": lambda dice: 40 if set(dice) in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}] else 0,
    "Yahtzee": lambda dice: 50 if len(set(dice)) == 1 else 0,
    "Chance": lambda dice: sum(dice),
}


class YahtzeeGame:
    def __init__(self, dice=None, score_sheet=None, rerolls_left=2):
        self.dice = dice if dice else [random.randint(1, NUM_SIDES) for _ in range(NUM_DICE)]
        self.score_sheet = score_sheet if score_sheet else {category: None for category in CATEGORIES}
        self.rerolls_left = rerolls_left

    def roll_dice(self, keep):
        if self.rerolls_left > 0:
            self.dice = [die if keep[i] else random.randint(1, NUM_SIDES) for i, die in enumerate(self.dice)]
            self.rerolls_left -= 1

    def score_roll(self, category):
        if self.score_sheet[category] is not None:
            return 0
        score = CATEGORY_SCORES[category](self.dice)
        self.score_sheet[category] = score
        self.rerolls_left = 2
        self.dice = [random.randint(1, NUM_SIDES) for _ in range(NUM_DICE)]
        return score

    def is_game_over(self):
        return all(value is not None for value in self.score_sheet.values())

    def simulate_reroll(self, num_simulations=100):
        if self.rerolls_left <= 0:
            return 0, [False] * NUM_DICE

        best_reward = 0
        total = 0
        best_reroll = [False] * NUM_DICE

        for _ in range(num_simulations):
            reroll_indices = [random.choice([True, False]) for _ in range(NUM_DICE)]
            simulated_dice = [
                die if not reroll_indices[i] else random.randint(1, NUM_SIDES)
                for i, die in enumerate(self.dice)
            ]

            reward = max(
                CATEGORY_SCORES[cat](simulated_dice)
                for cat in CATEGORIES if self.score_sheet[cat] is None
            )
            total += max(
                CATEGORY_SCORES[cat](simulated_dice)
                for cat in CATEGORIES if self.score_sheet[cat] is None
            )
            if reward > best_reward:
                best_reward = reward
                best_reroll = reroll_indices

        return total / num_simulations, best_reroll

    def get_state(self):
        dice_state = tuple(sorted(self.dice))
        categories_state = tuple(int(self.score_sheet[cat] is not None) for cat in CATEGORIES)
        return dice_state + categories_state + (self.rerolls_left,)


class QNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(QNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.network(x)


class DQNAgent:
    def __init__(self, state_size, action_size, hidden_size=128, alpha=0.001, gamma=0.9, epsilon=1.0,
                 epsilon_min=0.01, epsilon_decay_steps=1000):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay_steps = epsilon_decay_steps
        self.epsilon_decay_rate = (epsilon - epsilon_min) / epsilon_decay_steps
        self.step_counter = 0

        self.q_network = QNetwork(state_size, hidden_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=alpha)
        self.criterion = nn.MSELoss()

    def state_to_tensor(self, state):
        return torch.FloatTensor(state)

    def get_q_value(self, state, action):
        state_tensor = self.state_to_tensor(state)
        q_values = self.q_network(state_tensor)
        if isinstance(action, tuple) and action[0] == "Reroll":
            return q_values[len(CATEGORIES)].item()
        return q_values[CATEGORIES.index(action)].item()

    def choose_action(self, state, game):
        available_categories = [cat for cat in CATEGORIES if game.score_sheet[cat] is None]

        if random.random() < self.epsilon:
            reroll_reward, reroll_indices = game.simulate_reroll()
            if game.rerolls_left > 0:
                category_rewards = {cat: CATEGORY_SCORES[cat](game.dice) for cat in available_categories}
                best_category_reward = max(category_rewards.values()) if category_rewards else 0

                if reroll_reward > best_category_reward:
                    return "Reroll", reroll_indices

            return max(available_categories, key=lambda cat: CATEGORY_SCORES[cat](game.dice))
        else:
            state_tensor = self.state_to_tensor(state)
            q_values = self.q_network(state_tensor)

            if game.rerolls_left > 0:
                reroll_action_index = len(CATEGORIES)
                if q_values[reroll_action_index] > max(q_values[:len(CATEGORIES)]):
                    _, reroll_indices = game.simulate_reroll()
                    return "Reroll", reroll_indices

            available_indices = [CATEGORIES.index(cat) for cat in available_categories]
            best_action_index = max(available_indices, key=lambda i: q_values[i].item())
            return CATEGORIES[best_action_index]

    def update(self, state, action, reward, next_state):
        state_tensor = self.state_to_tensor(state)
        next_state_tensor = self.state_to_tensor(next_state)

        current_q_values = self.q_network(state_tensor)

        target_q_values = current_q_values.clone()

        with torch.no_grad():
            next_q_values = self.q_network(next_state_tensor)
            max_next_q = torch.max(next_q_values)

        if isinstance(action, tuple) and action[0] == "Reroll":
            action_index = len(CATEGORIES)
        else:
            action_index = CATEGORIES.index(action)

        target_q_values[action_index] = reward + self.gamma * max_next_q

        self.optimizer.zero_grad()
        loss = self.criterion(current_q_values, target_q_values)
        loss.backward()
        self.optimizer.step()

    def decay_epsilon(self):
        self.step_counter += 1
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon - self.epsilon_decay_rate
        )

    def save_model(self, filename):
        torch.save(self.q_network.state_dict(), filename)

    def load_model(self, filename):
        self.q_network.load_state_dict(torch.load(filename))

def train_agent(episodes=1000):
    state_size = NUM_DICE + len(CATEGORIES) + 1
    action_size = len(CATEGORIES) + 1
    agent = DQNAgent(state_size, action_size)

    for episode in range(episodes):
        game = YahtzeeGame()
        total_reward = 0

        while not game.is_game_over():
            state = game.get_state()
            action_data = agent.choose_action(state, game)

            if isinstance(action_data, tuple) and action_data[0] == "Reroll":
                _, reroll_pattern = action_data
                reroll_reward, _ = game.simulate_reroll()
                game.roll_dice(reroll_pattern)
                reward = reroll_reward
                action = ("Reroll", True)
            else:
                action = action_data
                reward = game.score_roll(action)

            total_reward += reward
            next_state = game.get_state()
            agent.update(state, action, reward, next_state)

        agent.decay_epsilon()

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{episodes}, Total Reward: {total_reward}")

    agent.save_model("dqn_models/dqn_model" + ".pth")
    return agent


def test_agent(agent, num_games=100, verbose=False):
    scores = []

    for game_num in range(num_games):
        game = YahtzeeGame()
        game_score = 0

        if verbose:
            print(f"\nGame {game_num + 1}")
            print("Initial dice:", game.dice)

        while not game.is_game_over():
            state = game.get_state()
            action_data = agent.choose_action(state, game)

            if isinstance(action_data, tuple) and action_data[0] == "Reroll":
                _, reroll_pattern = action_data
                if verbose:
                    print(f"Rerolling dice: {game.dice} -> ", end="")
                game.roll_dice(reroll_pattern)
                if verbose:
                    print(f"{game.dice}")
            else:
                category = action_data
                score = game.score_roll(category)
                game_score += score
                if verbose:
                    print(f"Scoring {category}: {score} points (Dice: {game.dice})")

        scores.append(game_score)

        if verbose:
            print(f"Game {game_num + 1} finished with score: {game_score}")
            print("Final scoresheet:", game.score_sheet)

    print("\nTest Results:")
    print(f"Number of games: {num_games}")
    print(f"Average score: {sum(scores) / len(scores):.2f}")
    print(f"Max score: {max(scores)}")
    print(f"Min score: {min(scores)}")

def show_best_move(dice, score_sheet, rerolls_left):
    print("Training the agent...")
    state_size = NUM_DICE + len(CATEGORIES) + 1
    action_size = len(CATEGORIES) + 1
    trained_agent = DQNAgent(state_size, action_size)

    try:
        trained_agent.load_model("dqn_models/dqn_model.pth")
        print("Model loaded successfully!")
    except FileNotFoundError:
        print("No pre-trained model found. Please train the agent first.")
        exit()

    game = YahtzeeGame(dice=dice, score_sheet=score_sheet, rerolls_left=rerolls_left)
    state = game.get_state()
    action_data = trained_agent.choose_action(state, game)

    if isinstance(action_data, tuple) and action_data[0] == "Reroll":
        _, reroll_pattern = action_data
        print(f"Recommended move: Reroll dice {reroll_pattern} (Current dice: {game.dice}, Rerolls left: {game.rerolls_left})")
        return action_data
    elif action_data is not None:
        print(f"Recommended move: Score in category '{action_data}'")
        return action_data
    else:
        print("No valid move available")
        return action_data

if __name__ == "__main__":
    # state_size = NUM_DICE + len(CATEGORIES) + 1
    # action_size = len(CATEGORIES) + 1
    # trained_agent = DQNAgent(state_size, action_size)
    #
    # try:
    #     trained_agent.load_model("dqn_models/dqn_model.pth")
    #     print("Model loaded successfully!")
    # except FileNotFoundError:
    #     print("No pre-trained model found. Please train the agent first.")
    #     exit()

    trained_agent = train_agent(1000)

    test_agent(trained_agent, num_games=100, verbose=False)
