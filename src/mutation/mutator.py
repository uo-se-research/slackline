"""Mutation of derivation trees styled after Nautilus (roughly).
Two kinds of mutation at a non-terminal symbol in the derivation tree:
   (a)  Generate a random substitute subtree
   (b)  Splice a previously seen tree

December 2022:  Refactoring to separate identification of potential mutations or hybrids
  from selecting one, so that selection and adjustment of weights ("learning") can be
  put in one place where we can measure and calibrate.
"""

import mutation.gen_tree as gen_tree
import mutation.chunk_store as chunk_store

import random
from typing import Optional

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Mutator:
    """The mutator has internal state to splice previously seen subtrees,
    as in Nautilus.
    """
    def __init__(self):
        self.seen = chunk_store.Chunkstore()

    def mutant(self, tree: gen_tree.DTreeNode,  budget: int) -> Optional[gen_tree.DTreeNode]:
        """A copy with one choice replaced by a fresh expansion,
        staying within budget.
        NO guarantee of uniqueness ... do that outside, where you can compare to
        all previously generated trees (not the chunkstore, which is subtrees).
        """
        # Tactic:  Compare the length of the whole sentence to
        #    the budget.  This gives a margin, which can be
        #    added to the length of the subtree we are replacing.
        mutated = tree.copy()
        # How much can a mutated subtree exceed its
        # minimum requirement?
        margin = budget - len(tree)
        assert margin >= 0, "Asked to expand a tree that is too long already"
        mutable_node: gen_tree.DTreeNode = random.choice(mutated.mutation_points())
        assert mutable_node is not None
        mutable_node.expand(len(mutable_node) + margin)
        assert len(mutated) <= budget, (f"Exceeded budget expanding '{tree}' ({len(tree)}) to '{mutated}' "
                                        f"({len(mutated)})\n margin was {margin}")
        return mutated

    # Todo: Breaking one method "hybrid" which selected and applied mutations into
    #   at least two, to allow tuning:
    #    - Identify mutation points  (here)
    #    - Select mutation points - maybe here or in search
    #    - Identify candidate replacements (here)
    #    - Select one or more (maybe in search?)
    #    - Apply to one or more
    #    - Reward successful mutation points
    #
    # First (identify mutation points) already exists. We need to modify it to
    #    be able to keep "score" of which subtrees are worth mutating.
    # Selection is currently random.  We'll defer that to elsewhere.
    #
    def hybrid(self, tree: gen_tree.DTreeNode, budget: int) -> Optional[gen_tree.DTreeNode]:
        """A copy with one choice replaced by a spliced
        subtree to form a new tree.  Guaranteed not to return the
        same tree, but could produce a previously seen tree.
        """
        assert isinstance(tree, gen_tree.DTreeNode)
        # Tactic:  Compare the length of the whole sentence to
        #    the budget.  This gives a margin, which can be
        #    added to the length of the subtree we are replacing.
        mutated = tree.copy()
        # How much can a mutated subtree exceed its
        # minimum requirement?
        margin = budget - len(tree)
        assert margin >= 0, f"Margin < 0, budget {budget}, len {len(tree)}, tree '{tree}'"

        choices = mutated.mutation_points()
        # This random choice might return a list instead
        splice_point: gen_tree.DTreeNode = random.choice(choices)
        assert isinstance(splice_point, gen_tree.DTreeNode)
        assert splice_point is not None
        # Splicing at root would just be substituting another (sub)tree that
        # has already been seen, so we prefer any other node.
        if len(choices) > 1 and splice_point == mutated:
            for again in range(3):
                # TODO:  Here is where we could learn which splice points
                #   are more or less fruitful, and/or generate several mutants
                #   rather than just one.
                splice_point: gen_tree = random.choice(choices)
                if splice_point != mutated:
                    break
        if splice_point == mutated:
            # Will still occasionally happen by bad luck
            log.debug(f"No mutable nodes except root in {mutated}\n ( {repr(mutated)} )")
            return None
        # Debugging info only
        splice_original = splice_point.copy()
        # Head is ok, but the children need to be replaced
        # Todo: We are choosing a subtree (a "chunk") to substitute into the derivation
        #    tree.  We should remember it so that we can record whether this substitution
        #    was successful, to learn how to make better substitutions.
        substitute = self.seen.get_sub(splice_point, len(splice_point) + margin)
        if substitute is None:
            # log.debug(f"No compatible substitutes for '{splice_point}'")
            # log.debug(f"Because: {self.seen.why_not(splice_point, len(splice_point) + margin)}\n")
            return None
        assert isinstance(substitute, gen_tree.DTreeNode)
        assert len(substitute) <= len(splice_point) + margin, "Substitute is too long!"
        # log.debug(f"Splicing '{substitute}' into '{mutated}' for '{splice_point}'")
        # log.debug(f"Splice point was '{splice_point}")
        splice_point.sub_children(substitute.children)
        # log.debug(f"Now splice point is '{splice_point}'")
        # log.debug(f"Resulting in '{mutated}'")
        if len(mutated) > budget:  # DEBUG
            log.error(f"Length of hybridized tree '{mutated}' is {len(mutated)}")
            log.error(f"Original tree '{tree}' had length {len(tree)}")
            log.error(f"Margin was {margin}")
            log.error(f"Splice point subtree was '{splice_original}', length {len(splice_original)}")
            log.error(f"Provided substitute was '{substitute}', length {len(substitute)}")
            log.error(f"get_sub was called with length limit {len(splice_point) + margin}")
            assert False, "Hybridized tree is too long"
        return mutated

    # Note: we probably don't want to stash all subtrees all the time,
    # just newly generated subtrees that were useful.
    def stash(self, t: gen_tree.DTreeNode):
        """Save all subtrees that could be used in splicing"""
        for m in t.mutation_points():
            self.seen.put(m)


def cli() -> object:
    """Command line argument is path to grammar file"""
    import argparse
    parser = argparse.ArgumentParser("Mutating and splicing derivation trees")
    parser.add_argument("grammar", type=argparse.FileType("r"))
    parser.add_argument("--length_limit", type=int, default=60,
                        help="Upper bound on generated sentence length")
    parser.add_argument("--tokens", help="Limit by token count",
                        action="store_true")
    return parser.parse_args()


def demo():
    """Obsolete ... this was the test script for an earlier version."""
    from gramm.llparse import parse
    # from gramm.char_classes import CharClasses
    # from gramm.unit_productions import UnitProductions
    args = cli()
    limit = args.limit
    f = args.grammar
    gram = parse(f, len_based_size=True)
    gram.finalize()
    print(f"LL grammar: \n{gram.dump()}")

    # xform = UnitProductions(gram)
    # xform.transform_all(gram)

    # xform = CharClasses(gram)
    # xform.transform_all(gram)

    trees = []
    for fresh_trees in range(5):
        t = gen_tree.derive(gram, budget=limit)
        trees.append(t)
        log.debug(f"Fresh tree: {repr(t)}")
        print(f"Fresh tree: '{t}'")
        for m in t.mutation_points():
            SEEN.put(m)

        # print("Mutants:")
        for _ in range(3):
            mut = mutant(t, budget=limit)
            log.debug(f"Mutant tree: \n{repr(mut)}")
            print(f"Mutant: {mut}")
            trees.append(mut)
            stash(mut)

    print("The following chunks have been recorded")
    print(SEEN)

    print("\nSplices:")
    for t in trees:
        print(f"\nHybridizing {t}")
        for _ in range(3):
            mut = hybrid(t, budget=limit)
            # assert mut is not None
            print(f"'{t}' =>\n'{mut}'")


if __name__ == "__main__":
    demo()
