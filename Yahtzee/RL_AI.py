import random
import matplotlib.pyplot as plt

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
            self.dice = sorted([die if keep[i] else random.randint(1, NUM_SIDES) for i, die in enumerate(self.dice)])
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

        best_reward, reroll_indices = self._strategize_reroll()
        return best_reward, reroll_indices

    def _strategize_reroll(self):
        available_categories = [cat for cat in CATEGORIES if self.score_sheet[cat] is None]
        best_reroll = [False] * NUM_DICE
        if not available_categories:
            return best_reroll

        current_scores = {cat: CATEGORY_SCORES[cat](self.dice) for cat in available_categories}
        best_current_cat = max(current_scores, key=current_scores.get)
        best_score = current_scores[best_current_cat]

        for i in range(1 << NUM_DICE):
            temp_reroll = [(i >> bit) & 1 for bit in range(NUM_DICE)]
            temp_dice = [
                die if not temp_reroll[d_idx] else random.randint(1, NUM_SIDES)
                for d_idx, die in enumerate(self.dice)
            ]
            temp_scores = {cat: CATEGORY_SCORES[cat](temp_dice) for cat in available_categories}
            if temp_scores and max(temp_scores.values()) > best_score:
                best_score = max(temp_scores.values())
                best_reroll = temp_reroll

        return best_score, best_reroll

    def get_state(self):
        dice_state = tuple(sorted(self.dice))
        return dice_state


class QLearningAgent:
    def __init__(self, alpha=0.01, gamma=0.9, epsilon=1, epsilon_decay=0.99):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0)

    def update_q_value(self, state, action, reward):
        available_actions_next_state = [a for a in CATEGORIES]
        max_next_q = max(self.get_q_value(state, a) for a in available_actions_next_state)
        current_q = self.get_q_value(state, action)
        self.q_table[(state, action)] = (current_q + self.alpha * (reward + self.gamma * max_next_q - current_q))

    def choose_action(self, state, game):
        available_categories = [cat for cat in CATEGORIES if game.score_sheet[cat] is None]

        if random.random() < self.epsilon:
            reroll_reward, reroll_indices = game.simulate_reroll()
            category_rewards = {cat: CATEGORY_SCORES[cat](game.dice) for cat in available_categories}
            best_category = max(category_rewards, key=category_rewards.get, default=None)

            if game.rerolls_left > 0 and reroll_reward > (
                    category_rewards.get(best_category, 0) if best_category else 0):
                return "Reroll", reroll_indices
            else:
                return best_category
        else:
            if not available_categories:
                return None
            q_values = {action: self.get_q_value(state, action) for action in available_categories}
            return max(q_values, key=q_values.get)

    def decay_epsilon(self):
        if self.epsilon_decay > 0:
            self.epsilon = max(0.5, self.epsilon * self.epsilon_decay)


def train_agent(episodes=1000):
    agent = QLearningAgent()
    rewards_per_episode = []

    for episode in range(episodes):
        game = YahtzeeGame()
        total_reward = 0

        while not game.is_game_over():
            state = game.get_state()
            action_data = agent.choose_action(state, game)

            if isinstance(action_data, tuple) and action_data[0] == "Reroll":
                action, reroll_pattern = action_data
                reroll_reward, _ = game.simulate_reroll()
                game.roll_dice(reroll_pattern)
                reward = reroll_reward
            elif action_data is not None:
                action = action_data
                reward = game.score_roll(action)
            else:
                break

            total_reward += reward
            agent.update_q_value(state, action, reward)

        rewards_per_episode.append(total_reward)
        agent.decay_epsilon()

    return agent, rewards_per_episode


def show_best_move(dice, score_sheet, rerolls_left):
    # Train the agent first
    print("Training the agent...")
    trained_agent, _ = train_agent(episodes=10)

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



# Example usage
if __name__ == "__main__":
    dice = [1, 3, 3, 5, 6]
    score_sheet = {
        "Aces": None, "Twos": None, "Threes": None, "Fours": None, "Fives": None, "Sixes": None,
        "Three of a Kind": None, "Four of a Kind": None, "Full House": None, "Small Straight": None,
        "Large Straight": None, "Yahtzee": None, "Chance": None
    }
    rerolls_left = 2

    show_best_move(dice, score_sheet, rerolls_left)
