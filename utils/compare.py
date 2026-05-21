from utils.scoring import green_score


def rank_reactions(reactions):
    ranking = []

    for reaction in reactions:
        ranking.append(
            {
                "name": reaction.name,
                "score": green_score(reaction),
            }
        )

    ranking.sort(key=lambda x: x["score"], reverse=True)

    return ranking