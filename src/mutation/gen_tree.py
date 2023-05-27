"""Generate and mutate derivation trees.
Compare to "generator.py", which works on sentential forms
(sequences of terminal and non-terminal symbols), gen_tree.py works
on an explicit parse tree  (following terminology from the Dragon Book),
or more descriptively, a derivation tree.  By preserving the tree structure,
we make it easier to apply mutations by rewriting selected subtrees,
and thereby come close to a re-implementation of the approach embodied
in the Nautilus tool.
"""

import pygramm.grammar as grammar
import pygramm.llparse

import random
from typing import Optional, List

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DTreeNode:
    """A node in a derivation tree (parse tree), in which nodes
    have an RHSItem as a "head" and, if non-terminal, may or may
    not have already been expanded with children.  "Expand" is the
    operation of creating a subtree from an RHSItem.
    (Nothing is gained, I think, by making separate peer subclasses
    for each subclass of grammar.RHSItem, as we would just move the
    case analysis from DTreeNode.expand to DTreeNode.__init__.)
    """
    def __init__(self, item: grammar.RHSItem):
        """An unexpanded node."""
        self.head = item
        self.children: List["DTreeNode"] = []
        self.cached_str = None

    def sub_children(self, children: List["DTreeNode"]):
        self.children = children
        self.cached_str = None

    def copy(self) -> "DTreeNode":
        """Do this before mutating to avoid side effects."""
        copied = DTreeNode(self.head)
        copied.children = [child.copy() for child in self.children]
        return copied

    def __len__(self) -> int:
        """The length of the derived sentence"""
        return len(str(self))

    def __str__(self) -> str:
        """The derived sentence"""
        # if self.cached_str:
        #    return self.cached_str
        if isinstance(self.head, grammar._Literal):
            self.cached_str = str(self.head.text)
            return self.cached_str
        self.cached_str = "".join(str(child) for child in self.children)
        return self.cached_str

    def __repr__(self) -> str:
        """In S-expression form"""
        if self.head.is_terminal():
            return repr(self.head)
        arg_reprs = ", ".join(repr(child) for child in self.children)
        return f"[{self.head} {arg_reprs}]"

    def expand(self, budget: int):
        """Recursively expand the head item ... all the way
        down, not just one level.  Calling "expand" again will
        replace the current expansion by another, which is one
        way to mutate a derivation tree.
        """
        # Retaining a cached string can cause trouble!
        self.cached_str = None
        # This might be a terminal node, a sequence, a choice, etc. ...
        # we just do an exhaustive case analysis.
        #
        if self.head.is_terminal():
            return
        head = self.head
        while isinstance(head, grammar._Symbol):
            head = head.expansions
            # Loop will unwind any unit productions
        if head.is_terminal():
            self.children = [DTreeNode(head)]
        elif isinstance(head, grammar._Seq):
            self.children = [DTreeNode(i) for i in head.items]
            margin = budget - sum(i.min_tokens() for i in head.items)
            for child in self.children:
                child.expand(child.head.min_tokens() + margin)
                excess = len(child) - child.head.min_tokens()
                margin -= excess
            assert margin >= 0
            assert len(self) <= budget
        elif isinstance(head, grammar._Choice) or isinstance(head, grammar._Kleene):
            # Just one child, which is the selected choice
            child = DTreeNode(random.choice(head.choices(budget)))
            self.children = [child]
            child.expand(budget)
            assert len(child) <= budget, "Exceeded budget in expansion of _Choice"
        else:
            assert False, "Case analysis was not exhaustive!"

    def mutation_points(self) -> List["DTreeNode"]:
        """Following example of Nautilus, we consider only
        occurrences of non-terminal symbols as potential
        points to replace a subtree.  (To mutate at more points,
        normalize the grammar, e.g., Greibach Normal Form or a
        stricter BNF rather than EBNF.)
        """
        if self.head.is_terminal():
            return []
        else:
            points: List[DTreeNode] = []
            for child in self.children:
                ch_points = child.mutation_points()
                if ch_points:
                    points.extend(ch_points)
            if (isinstance(self.head, grammar._Symbol)):
                points.append(self)
            return points


def derive(g: grammar.Grammar, budget: int = 20) -> DTreeNode:
    """Returns a single random derivation"""
    tree = DTreeNode(g.start)
    tree.expand(budget=budget)
    return tree


def cli() -> object:
    """Command line argument is path to grammar file"""
    import argparse
    parser = argparse.ArgumentParser("Generate sample sentences from grammar")
    parser.add_argument("grammar", type=argparse.FileType("r"))
    parser.add_argument("--length", type=int, default=60,
                        help="Upper bound on generated sentence length")
    parser.add_argument("--tokens", help="Limit by token count",
                        action="store_true")
    return parser.parse_args()


def main():
    """Smoke test"""
    args = cli()
    length = args.length
    f = args.grammar
    gram = gramm.llparse.parse(f, len_based_size=True)
    gram.finalize()
    print(f"LR Grammar: \n{gram.dump()}")

    for fresh_trees in range(5):
        print("Fresh tree:")
        t = derive(gram, budget=length)
        # print(repr(t))
        print("=>")
        print(t)


if __name__ == "__main__":
    main()
