"""Basic configuration constants, lower level than search_conf.py,
and imported into search.py directly as well as mutant_search.py indirectly.
"""

# # C = 1.4   # ratio of exploration to exploitation factors in UCT
# C = 3.0
#
# HOT_BUF_SIZE = 300 # 50   # Was 300
#
# # Winnowing is discarding inputs that have not proved
# # useful, in particular inputs that were retained because of
# # new coverage but which are no longer unique in achieving that
# # coverage (i.e., superseded by other inputs discovered later)
#
# WINNOW_TRIGGER_SIZE = 1000   # Initially 1000, fairly conservative to avoid overshoot
# WINNOW_TRIGGER_GROW = 1.5    # Lower bound on how much frontier must grow before next winnow
#
# WINNOW_CHUNKS = True  # Should we also discard recorded subtrees in the chunk store?
#
# # Quantile gain is (child - parent)/(1 - parent), i.e., how much of
# # the gap has been closed toward top ranking?  Is it better enough?
# BETTER_ENOUGH = 0.35
# # Winnowing, we keep candidates in the top k%, with k expressed
# # as an integer.
# RETAIN_COST_PCNT = 98
#
#
# # Weighting factors for "wins", instead of 1/0
# #
# WEIGHT_NEWCOV = 1.0
# WEIGHT_NEWMAX = 5.0
# WEIGHT_NEWCOST = 10.0
