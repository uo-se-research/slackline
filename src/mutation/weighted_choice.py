"""Make weighted random choices from a collection.
Based on Vose Alias method:
    Vose, Michael D. "A linear algorithm for generating random numbers with a given distribution."
    IEEE Transactions on software engineering 17.9 (1991): 972-975.

Modeled partly on vose_sampler by asmith26
    https://pypi.org/project/Vose-Alias-Method/
and on the detailed description by Keith Schwartz
    https://www.keithschwarz.com/darts-dice-coins/

This implementation has been specialized to the case where we have
scores for each item, rather than probabilities.  Scaled probabilities
are then n * score(e) / sum(score(e) for e in collection).

The Vose alias algorithm has O(n) pre-processing time and O(1) time to
draw an element, so pre-processing should be done occasionally,
not before each draw.  Assume weights change slowly, and we
have d draws from collection of size n, n^2 >> d >> n.
(Not quite true ... scores can change quickly in MCTS.)
If we pre-process after each n draws, we'll get total processing
time (d/n) * n, roughly proportional to d.

The code here closely follows Schwartz' description, and could
be simplified and accelerated with small changes.  It is designed to
be read together with Schartz' description.  I'll optimize it later if needed.
"""
from typing import List
import random


class Scorable:
    """Abstract base class: Things that have scores
    that can be used to make a weighted choice.
    """
    def score(self) -> float:
        raise NotImplementedError(f"Class {self.__class__.__name__} needs a 'score' method")


class Sampler:
    """Weighted sampler using Vose alias algorithm,
     see "Darts, Dice, and Coins: Sampling from a Discrete Distribution"
     by Keith Schwarz at https://www.keithschwarz.com/darts-dice-coins/ .
     See also https://pypi.org/project/Vose-Alias-Method/ for a well-tested
     implementation that has not been specialized to the use case of mutation search.
     """

    def __init__(self, collection: List[Scorable]):
        self.elements = collection.copy()
        # Names consistent with Schwarz, "Darts,  Dice, and Coins"
        n = len(self.elements)
        self.probs = n * [0.0]
        self.alias = n * [0]
        scores = [e.score() for e in collection]
        tot = sum(scores)
        p = [n * e / tot for e in scores]
        small = []
        large = []
        for i in range(n):
            if p[i] < 1.0:
                small.append(i)
            else:
                large.append(i)

        while small and large:
            l = small.pop()
            g = large.pop()
            self.probs[l] = p[l]
            self.alias[l] = g
            p[g] = (p[g] + p[l]) - 1.0
            if p[g] < 1.0:
                small.append(g)
            else:
                large.append(g)

        while large:
            g = large.pop()
            self.probs[g] = 1.0
        while small:
            l = small.pop()
            self.probs[l] = 1.0

        return

    def draw(self) -> Scorable:
        i = random.randrange(len(self.elements))
        if random.random() < self.probs[i]:
            return self.elements[i]
        else:
            return self.elements[self.alias[i]]


class _I:
    def __init__(self, s: str, w: float):
        self.s = s
        self.w = w

    def score(self) -> float:
        return self.w

    def __repr__(self) -> str:
        return str((self.s, self.w))


def simple_test():
    dist = Sampler([_I("a", 8), _I("c", 1), _I("b", 4)])
    counts = {"a": 0, "b": 0, "c": 0}
    for i in range(1000):
        s = dist.draw().s
        counts[s] += 1
    print(counts)


if __name__ == "__main__":
    simple_test()
