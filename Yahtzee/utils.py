def calculate_score(dices, category):
    dice = dices.hand_dices
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
        if len(dice) == 0: return 0
        if any(dice.count(die) >= 3 for die in dice):
            return sum(dice)
        else:
            return 0
    elif category == "four of a kind":
        if len(dice) == 0: return 0
        if any(dice.count(die) >= 4 for die in dice):
            return sum(dice)
    elif category == "full house":
        unique_dice = set(dice)
        if len(unique_dice) == 2 and (dice.count(list(unique_dice)[0]) in [2, 3]):
            return 25
        else:
            return 0
    elif category == "small straight":
        if {1, 2, 3, 4}.issubset(set(dice)) or {2, 3, 4, 5}.issubset(set(dice)) or {3, 4, 5, 6}.issubset(
                set(dice)):
            return 30
        else:
            return 0
    elif category == "large straight":
        if {1, 2, 3, 4, 5} == set(dice) or {2, 3, 4, 5, 6} == set(dice):
            return 40
        else:
            return 0
    elif category == "yahtzee":
        if len(dice) != 0 and dice.count(dice[0]) == 5:
            return 50
        else:
            return 0
    elif category == "chance":
        return sum(dice)
    else:
        return 0

def convert_to_score_sheet(categories):
    score_sheet = {
        "Aces": None, "Twos": None, "Threes": None, "Fours": None, "Fives": None,
        "Sixes": None, "Three of a Kind": None, "Four of a Kind": None, "Full House": None,
        "Small Straight": None, "Large Straight": None, "Yahtzee": None, "Chance": None
    }

    # Mapping of the categories from input to the score_sheet keys
    category_mapping = {
        "aces": "Aces", "twos": "Twos", "threes": "Threes", "fours": "Fours", "fives": "Fives",
        "sixes": "Sixes", "three of a kind": "Three of a Kind", "four of a kind": "Four of a Kind",
        "full house": "Full House", "small straight": "Small Straight", "large straight": "Large Straight",
        "yahtzee": "Yahtzee", "chance": "Chance"
    }

    # Populate the score_sheet with None (default value)
    for category, value in categories.items():
        score_sheet_name = category_mapping.get(category)
        if score_sheet_name:
            score_sheet[score_sheet_name] = None  # Initialize each category in score_sheet as None

    return score_sheet