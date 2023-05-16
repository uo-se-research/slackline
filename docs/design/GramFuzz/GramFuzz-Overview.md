# SlackLine overview

TreeLine overall is a project on performance fuzzing using Monte 
Carlo methods.  SlackLine is a branch of TreeLine in which the 
primary way of generating new inputs is by substituting subtrees of 
derivation trees.  It draws ideas from at least three prior projects: 

- Nautilus showed the utility of substituting previously generated 
  subtrees into derivation trees. 
- Alphuzz showed that Monte Carlo
  Tree Search could be used for seed selection for mutation, 
  despite mutation being not being a sequential decision domain with 
  a natural distinction between intermediate states and final states.
- SlowFuzz used mutation for performance fuzzing, and PerfFuzz 
  greatly improved over SlowFuzz with richer feedback, in particular 
  selecting inputs that increased counts at "hot spots" rather than 
  only total execution time. 

Also, like much prior work, we build on AFL (with the additional 
measurements developed by the PerfFuzz researchers). 

## SlackLine input generation 

As in Nautilus, we generate derivation trees rather than strings.  A 
derivation tree or subtree is represented by a `DTreeNode` in
`src/mutation/gen_tree.py`.   The derivation process differs from 
Nautilus:  We generate subtrees with length bounds (see method 
`expand` of `DTreeNode`).   The approach used in SlackLine, which uses a 
fixed point calculation to determine the _shortest_ string that can 
be generated from any non-terminal, does not exhibit the performance 
problems reported by Nautilus researchers for controlling the length 
of generated strings.   This is especially important for performance 
fuzzing, in which we must avoid false performance feedback obtained 
merely by making inputs longer and longer.

As in Nautilus, we maintain a collection of previously generated 
derivation subtrees.  This is called the chunk store 
(`chunk_store.py`) after the name of the similar collection in 
Nautilus.  In SlackLine the chunk store is a dict mapping 
non-terminals to lists of subtrees.  When an input receives positive 
feedback, the whole derivation tree is added to the frontier of the 
search, and all subtrees of the derivation tree are added to the 
chunk store. 

