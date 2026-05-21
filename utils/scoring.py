from utils.metrics import (
    atom_economy,
    e_factor,
    solvent_toxicity,
    intermediate_complexity,
)


def green_score(reaction):
    score = 75

    score -= e_factor(reaction) * 6
    score -= solvent_toxicity(reaction) * 8
    score -= reaction.steps * 5
    score -= intermediate_complexity(reaction) * 6

    if reaction.temperature > 80:
        score -= 10
    elif reaction.temperature > 50:
        score -= 5

    score += atom_economy(reaction) * 0.15

    return round(max(0, min(score, 100)), 2)