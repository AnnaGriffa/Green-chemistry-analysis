from data.reactions import load_reactions
from utils.scoring import green_score


def rank_reactions():
    reactions = load_reactions()

    ranking = []

    for reaction in reactions.values():
        ranking.append(
            {
                "name": reaction.name,
                "score": green_score(reaction),
            }
        )

    ranking.sort(key=lambda x: x["score"], reverse=True)

    return ranking