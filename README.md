# SlackLine

<img align="left" src="slackline-logo.png" width=100 alt="TreeLine Logo">
Finding slow input faster using mutational splicing and application provided context-free grammar. 

This is a testing version of the code SlackLine (the exact code used for experimentation). We are aware that it is not
user-friendly. The repository will change drastically after paper submission. We will refactor most of the code and
add all the necessary documentation.

## Related Publication(s):

TBA

## How _SlackLine_ Works:

TBA

## Usage:

- Build the Docker image:
```sh
docker build -t slackline-img:latest .
```

- Run a new container
```sh
docker run -p 2300:2300 --name slackline -it slackline-img /bin/bash
```
- From the container run the AFL listener for one of the target applications using the commands provided in their 
documentation ([wf](target_apps/word-frequency/README.md), [libxml](target_apps/libxml2/README.md), 
[graphviz](target_apps/graphviz/README.md), [flex](target_apps/flex/README.md)).
e.g. , 
```shell
afl-socket -i /home/treeline/target_apps/graphviz/inputs/ -o /home/results/graphviz-001 -p -N 500 -d dot
```

Run [mcts_expr](mcts_exper.py) with the configuration you want form your local machine or the `fse` container itself. 
```shell
python3.9 slackline.py 
```

## Example Outputs:




## Dependencies:

All the dependencies are managed by the docker file provided. However, a major requirements for building and running
_SlackLine_ is to build it on x86 processor. This is required for AFL's instrumentation to work. 
