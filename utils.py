def calculate_score(dice, category):
    dice = dice.hand_dices
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
    elif category == "full house":
        unique_dice = set(dice)
        if len(unique_dice) == 2 and (dice.count(list(unique_dice)[0]) in [2, 3]):
            return 25
        else:
            return 0
    elif category == "small straight":
        if set([1, 2, 3, 4]).issubset(set(dice)) or set([2, 3, 4, 5]).issubset(set(dice)) or set([3, 4, 5, 6]).issubset(
                set(dice)):
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
    else:
        return 0