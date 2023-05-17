#!/bin/bash

# maintained by Ziyad Alsaeed
# A script to run PerfFuzz for a given duration and a given number of times and report the run 
# a well as the result to slack. 
# don't forget to chmod +x it first!

# declare an array of benchmark configuration. Each benchmark is an element in the array.
# for each element we split the configuration by a semicolon as the following: 
# "<seed_location>;<app_name>;<binary_location>"

declare -a benchmarks=(
  # "libxml2/perffuzz-seeds/60/;libxml2;/home/slackline/target_apps/libxml2/src/libxml2-2.9.7/xmllint @@"
  # "word-frequency/perffuzz-seeds/60/;wf;/home/slackline/target_apps/word-frequency/src/wf-0.41/src/wf"
  # "graphviz/perffuzz-seeds/60/;graphviz;dot"
  # "flex/perffuzz-seeds/;flex;/home/slackline/target_apps/flex/src/flex-2.6.4/src/flex"
  # "lunasvg/inputs;lunasvg;svg2png @@"
  )

budget=60
input_timeout=10000
duration=1

# now loop through the above configs with the same timeout
for benchmark in "${benchmarks[@]}"
do

  # break benchmarks configs by ;
  IFS=";" read -r -a configs <<< "${benchmark}"

  seeds="${configs[0]}"
  app_name="${configs[1]}"
  bin_location="${configs[2]}"

  for i in $(seq 1 5);  # how many experiments/benchmark
  do

    # get date
    date=$(date '+%m%d%Y')
    time=$(date '+%H%M%S')

    # for decoration only!
    if (($i < 10));
    then 
      id="0$i"
    else
      id="$i"
    fi

    outputlocation="/home/results/app:${app_name}-budget:${budget}-dur:${duration}h-date:${date}-time:${time}-id:${id}"
    command="afl-fuzz -i /home/slackline/target_apps/${seeds} -o ${outputlocation} -p -t ${input_timeout} -N ${budget} -d ${bin_location}"
    
    # inform us on what is about to run and where.
    python3 perffuzz-reporting.py m "PerfFuzz running new experiment on \`${app_name}\` for \`${duration}\` hours."
    python3 perffuzz-reporting.py m "Exact command is ..."
    python3 perffuzz-reporting.py c "timeout ${duration}h ${command}"
    
    # run the experiment
    timeout "${duration}h" $command

    # go over all the inputs and using afl-showmax to find the one with the max cost    
    declare -i cost=0
    declare -i max_cost=0
    inputname=""
    exeutable=$(echo "${bin_location}" | sed 's/\ @@//')  # remove the ' @@', if any, for showmax execution
    for inputfilename in $outputlocation/queue/id*; do
      cost=$(afl-showmax -t 10000 "$exeutable" "$inputfilename")
      if ((cost > max_cost));
      then
        max_cost=$cost
        inputname=$inputfilename
      fi
    done

    # read the statistics from the experiment files to pass it to slack. 
    stats=$(<"${outputlocation}/fuzzer_stats")
    input_content=$(<$inputname)

    # inform us on all the experiment essential results.
    python3 perffuzz-reporting.py m "Run found in \`${outputlocation}\` just finished!"
    python3 perffuzz-reporting.py m "Max found input location/name: \`${inputname}\`"
    python3 perffuzz-reporting.py m "Max found input cost: \`${max_cost}\`"
    python3 perffuzz-reporting.py m "Max found input content:"
    python3 perffuzz-reporting.py c "${input_content}"
    python3 perffuzz-reporting.py m "The following is the run statistics"
    python3 perffuzz-reporting.py c "${stats}}"

  done
done
