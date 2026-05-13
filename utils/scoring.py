from utils.metrics import (
    atom_economy,
    e_factor,
    solvent_toxicity,
    intermediate_complexity,
)


def green_score(reaction):
    score = 100

    score -= e_factor(reaction) * 5
    score -= solvent_toxicity(reaction) * 5
    score -= reaction.steps * 3
    score -= intermediate_complexity(reaction) * 4

    if reaction.temperature > 100:
        score -= 10

    score += atom_economy(reaction) * 0.2

    return round(max(0, min(score, 100)), 2)