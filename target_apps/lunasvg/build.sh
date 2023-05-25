cd src
tar -xf lunasvg-2.3.2.tar.gz
cd lunasvg-2.3.2

mkdir build
cd build
cmake -D CMAKE_C_COMPILER=/home/git/perffuzz/afl-clang-fast -D CMAKE_CXX_COMPILER=/home/git/perffuzz/afl-clang-fast++ ..
make -j 2
make install
cd ../example
cmake -D CMAKE_C_COMPILER=/home/git/perffuzz/afl-clang-fast -D CMAKE_CXX_COMPILER=/home/git/perffuzz/afl-clang-fast++ .
make
cp svg2png /usr/local/bin/
cd ../../
