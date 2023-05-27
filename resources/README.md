# [afl-perffuzz](afl-perffuzz.c)

The fuzzing file (originally named `afl-fuzz.c`) as it is found in [PerfFuzz](https://github.com/carolemieux/perffuzz/blob/master/afl-fuzz.c) with a minor change on how generated inputs are named. We change the naming of the generated inputs slightly to help us analyze the result after the search process. 

# [afl-showmax](afl-showmax.c)

The result collector file as it is given by AFL with minor changes on how to handle timeouts.

# [afl-socket](afl-socket.c)

A compact version of the original `afl-fuzz.c` file used by SlackLine algorithm to run inputs using socket. This version removes all the fuzzing features while maintaining the well-engineered target application runner.

# [Makefile](Makefile)

The same makefile that is found in PerfFuzz with a minor change to build both `afl-socket` and `afl-fuzz` at the same time. 

# [Requirements](requierments.txt)

All the needed python dependencies by TreeLine/SlackLine. 

# [sources.list](sources.list)

Re-configuring apt sources. 