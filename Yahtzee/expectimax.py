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


class ExpectimaxYahtzee:
    def __init__(self, max_depth=2, num_samples=50):
        self.max_depth = max_depth
        self.num_samples = num_samples
        self.cache = {}

    def sample_dice_combinations(self, current_dice, keep_mask):
        combinations = []
        num_reroll = sum(not k for k in keep_mask)

        if num_reroll == 0:
            return [tuple(current_dice)]

        for _ in range(self.num_samples):
            new_dice = []
            for i, keep in enumerate(keep_mask):
                if keep:
                    new_dice.append(current_dice[i])
                else:
                    new_dice.append(random.randint(1, 6))
            combinations.append(tuple(sorted(new_dice)))
        return combinations

    def expectimax(self, game_state, depth=0, is_chance_node=False):
        if depth >= self.max_depth:
            return self.evaluate_state(game_state)

        if is_chance_node:
            value = 0
            dice_combinations = self.sample_dice_combinations(game_state['dice'], game_state['keep_mask'])
            prob = 1.0 / len(dice_combinations)

            for dice_combo in dice_combinations:
                new_state = {
                    'dice': dice_combo,
                    'score_sheet': game_state['score_sheet'],
                    'rerolls_left': game_state['rerolls_left'] - 1,
                    'keep_mask': game_state['keep_mask']
                }
                value += prob * self.expectimax(new_state, depth + 1, False)
            return value
        else:
            if game_state['rerolls_left'] > 0:
                keep_patterns = self.generate_strategic_keep_patterns(game_state['dice'])
                return max(
                    self.expectimax(
                        {
                            'dice': game_state['dice'],
                            'score_sheet': game_state['score_sheet'],
                            'rerolls_left': game_state['rerolls_left'],
                            'keep_mask': keep_mask
                        },
                        depth,
                        True
                    )
                    for keep_mask in keep_patterns
                )
            else:
                return max(
                    CATEGORY_SCORES[category](game_state['dice'])
                    for category in CATEGORIES
                    if game_state['score_sheet'][category] is None
                )

    def generate_strategic_keep_patterns(self, dice):
        patterns = []
        dice_counts = [dice.count(i) for i in range(1, 7)]

        patterns.append([True] * 5)

        patterns.append([False] * 5)

        dice_list = list(dice)
        for value in range(1, 7):
            if dice_counts[value - 1] >= 2:
                pattern = [d == value for d in dice_list]
                patterns.append(pattern)

        if len(set(dice)) >= 3:
            pattern = [True if dice_list.count(d) == 1 else False for d in dice_list]
            patterns.append(pattern)

        return patterns

    def evaluate_state(self, game_state):
        current_score = sum(score for score in game_state['score_sheet'].values() if score is not None)
        potential_scores = [
            CATEGORY_SCORES[cat](game_state['dice'])
            for cat in CATEGORIES
            if game_state['score_sheet'][cat] is None
        ]
        return current_score + (max(potential_scores) if potential_scores else 0)

    def get_best_action(self, game):
        game_state = {
            'dice': tuple(sorted(game.dice)),
            'score_sheet': game.score_sheet.copy(),
            'rerolls_left': game.rerolls_left,
            'keep_mask': [False] * NUM_DICE
        }

        current_best_score = float('-inf')
        best_category = None
        for category in CATEGORIES:
            if game.score_sheet[category] is None:
                score = CATEGORY_SCORES[category](game.dice)
                if score > current_best_score:
                    current_best_score = score
                    best_category = category

        if game.rerolls_left > 0:
            best_value = current_best_score
            best_keep_mask = None
            should_reroll = False
            keep_patterns = self.generate_strategic_keep_patterns(game.dice)

            for keep_mask in keep_patterns:
                new_state = game_state.copy()
                new_state['keep_mask'] = keep_mask
                value = self.expectimax(new_state, 0, True)
                if value > best_value:
                    best_value = value
                    best_keep_mask = keep_mask
                    should_reroll = True

            if should_reroll:
                return ('reroll', best_keep_mask)
            else:
                return ('score', best_category)
        else:
            return ('score', best_category)

def show_best_move(dice, score_sheet, rerolls_left):
    game = YahtzeeGame()
    game.dice = dice
    game.score_sheet = score_sheet
    game.rerolls_left = rerolls_left

    ai = ExpectimaxYahtzee(max_depth=2, num_samples=50)
    action, param = ai.get_best_action(game)

    # Interpret the action and return in the format expected by with_rl_ai
    if action == 'reroll':
        return ("Reroll", param)
    elif action == 'score':
        # Convert category name to match the format expected by the game
        category_mapping = {
            "Aces": "ones",
            "Twos": "twos",
            "Threes": "threes",
            "Fours": "fours",
            "Fives": "fives",
            "Sixes": "sixes",
            "Three of a Kind": "three_of_a_kind",
            "Four of a Kind": "four_of_a_kind",
            "Full House": "full_house",
            "Small Straight": "small_straight",
            "Large Straight": "large_straight",
            "Yahtzee": "yahtzee",
            "Chance": "chance"
        }
        return category_mapping[param]
    else:
        return None

    final_score = sum(score for score in game.score_sheet.values() if score is not None)
    print(f"Game Over! Final score: {final_score}")
    return final_score

