## Structure:

- [Analysis](analysis): 
- [mutation](mutation): is a package where all the main tree mutation algorithms lives.
- [pygramm](pygramm): a submodule to read grammar files and return them as objects we can work with.
- [collect_cost](collect_costs.py) A script to collect the search result from the inputs files names then save it in
  csv format for analysis.
- [default.yaml](defaults.yaml): The default configurations for running _SlackLine_.
- [helpers.py](helpers.py): Helper functions for different tasks (search, analysis, plot, etc).
- [slack.py](slack.py): An experiment monitoring script. Useful for long runs.
- [slackline.py](slackline.py): The _SlackLine_ CLI interface.
- [slackline_configure.py](slackline_configure.py): A script to read run configurations. 
- ~~[slackline_gen.py](slackline_gen.py): The _SlackLine_ CLI interface.~~
- [targetAppConnect.py](targetAppConnect.py): A cript to connect to AFL socket for inputs runs.