"""A simple checker for duplication of strings,
intended to be used with gen_tree to prevent creating the same string
many times.

We keep a set of hashes rather than the set of generated
strings, although it probably doesn't matter for a few million strings.
"""


class History:
    """A record of previously generated hashable objects.  The only operations
    are 'record' and 'is_dup'.   May very rarely report that a unique object
    is actually a duplicate, due to hash collisions.
    """

    def __init__(self):
        self.hashes: set[int] = set()

    def record(self, obj: object):
        self.hashes.add(hash(obj))

    def is_dup(self, obj: object):
        return hash(obj) in self.hashes
