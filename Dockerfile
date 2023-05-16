FROM debian:9.8

MAINTAINER Ziyad Alsaeed "zalsaeed@cs.uoregon.edu"

# adding the needed sources for the package manager
COPY resources/sources.list /etc/apt/

# all packages needed by all perffuzz glade, or us.
RUN apt-get update
RUN apt-get install -y --no-install-recommends --fix-missing \
	build-essential \
	make \
	cmake \
	git \
	curl \
	unzip \
	rpm2cpio \
	cpio \
	vim \
	wget \
	libssl-dev \
	libbz2-dev \
	libreadline-dev \
	libsqlite3-dev \
	libncurses5-dev \
	libncursesw5-dev \
	libgdbm-dev \
	libc6-dev \
	zlib1g-dev \
	libffi-dev \
	tk-dev \
	ca-certificates \
	libjpeg-dev \
	libpng-dev && \
	rm -rf /var/lib/apt/lists/*

# packages needed for flex (one of the benchmarks)
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    bison \
    texinfo \
    help2man

# installing python3.9.13
WORKDIR /opt
RUN wget https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tgz
RUN tar xzf Python-3.9.13.tgz
RUN rm Python-3.9.13.tgz
WORKDIR /opt/Python-3.9.13
RUN ./configure --enable-optimizations --enable-shared
RUN make
RUN make install
RUN ln -sf /usr/local/bin/python3.9 /usr/local/bin/python3
RUN ln -sf /usr/local/bin/pip3.9 /usr/local/bin/pip3

# installing clang
RUN apt-get update
RUN apt-get install -y clang-3.8

# building some dependencies needed by perffuzz benchmarks
RUN apt-get update
RUN apt-get build-dep python-lxml -y

# updating the main compilers based on the newly installed clang version
RUN update-alternatives --install /usr/bin/cc cc /usr/bin/clang-3.8 100
RUN update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++-3.8 100
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-3.8 100
RUN update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-3.8 100

RUN update-alternatives --install /usr/bin/llvm-config llvm-config /usr/bin/llvm-config-3.8 100

# cloning, building, and installing perfffuz and its test subjects.
RUN mkdir /home/git
WORKDIR /home/git/

# cloning PerfFuzz then reset to the known working version of the repo (a commit on Feb 20, 2020)
RUN git clone https://github.com/carolemieux/perffuzz.git
WORKDIR /home/git/perffuzz/
RUN git reset --hard f937f370555d0c54f2109e3b1aa5763f8defe337

# Use our file before the build, the files we copy are edited versions of PerfFuzz to work with SlackLine
COPY resources/afl-socket.c .
COPY resources/Makefile .
COPY resources/afl-showmax.c .
COPY resources/afl-perffuzz.c ./afl-fuzz.c
RUN make clean all  # build edited PerfFuzz
RUN make afl-showmax  # build the edited analysis file.
WORKDIR /home/git/perffuzz/llvm_mode/
RUN make

# Copy the source of this repository (and all submodules) to build target_apps and be ready for runs
WORKDIR /home
RUN mkdir slackline
WORKDIR /home/slackline
COPY src ./src
COPY docs ./docs

# update the PATH
ENV PATH $PATH:/home/git/perffuzz/

# install python packages
WORKDIR /home/packages
COPY resources/requirements.txt .
RUN pip3 install -r requirements.txt

# copy the target apps dir and build all the apps with AFL instrumenter
COPY target_apps /home/slackline/target_apps

# build all target apps (this will take a while)
WORKDIR /home/slackline/target_apps
RUN sh build_targets.sh

# make a result root diroctry
RUN mkdir /home/results

# change the workdir to /home for convenience
WORKDIR /home

# ports we are exposing (2300: AFL socket). This is requiered only in case one would like to run SlackLine from a local
# machine while the targer-app runerer (AFL) is running on this docker container.
EXPOSE 2300
