# [LunaSVG](https://github.com/sammycage/lunasvg)

We obtain the latest version at the time of our test (2.3.2).
The source file is provided here for reference under the [src](./src) directory.
However, if you wish to download the source file yourself, you can try the official release 
[download link](https://github.com/sammycage/lunasvg/archive/refs/tags/v2.3.2.tar.gz).

## Application Stats

```bash
$ cloc --not-match-f=test .
     134 text files.
     123 unique files.                                          
      41 files ignored.

github.com/AlDanial/cloc v 1.70  T=0.88 s (106.3 files/s, 24926.5 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
C++                             22           1068             54           5419
C                               10           1284            519           5387
C/C++ Header                    28            793           1329           2961
make                             6            577            354           1041
CMake                           24            112             70            721
Markdown                         1             25              0             64
YAML                             2              4              1             30
-------------------------------------------------------------------------------
SUM:                            93           3863           2327          15623
-------------------------------------------------------------------------------
```

We only count code of C, C++, and C/C++ Headers (given *test* files are excluded).
Thus, 5,419 + 5,387 + 2,961 = 13,767 SLoC.

## Manually Build the Source Code

After decompressing the file `tar -xf lunasvg-2.3.2.tar.gz`, and within the new directory,
follow these steps to build with AFL.

1. ```bash
   mkdir build && cd build
   ```

2. ```bash
   cmake -D CMAKE_C_COMPILER=/home/git/perffuzz/afl-clang-fast -D CMAKE_CXX_COMPILER=/home/git/perffuzz/afl-clang-fast++ ..
   ```

3. ```bash
   make -j 2
   ```

4. ```bash
   make install
   ```

5. ```bash
   cd ../example
   ```

6. ```bash
   cmake -D CMAKE_C_COMPILER=/home/git/perffuzz/afl-clang-fast -D CMAKE_CXX_COMPILER=/home/git/perffuzz/afl-clang-fast++ .
   ```

7. ```bash
   make
   ```

The final step will generate an `svg2png` binary that is a simple interface to LunaSVG.

## Sample Run Without Fuzzing

To test the that the installation was successfully completed. You can run `svg2png` based on 
[sample svg fle](inputs/path.svg) (shown below) by simply passing the file to svg2png `svg2png path.svg`.

###### path.svg
```svg
<svg><path d="M150 0 L75 200 L225 200 Z" /></svg>
```

The output will a png file of the passed file.

## Run With AFL

To manually run the AFL listener on the target application you use a command similar to the one below.

```bash
afl-socket -i /home/slackline/target_apps/lunasvg/inputs -o /home/results/lunasvg-001 -p -N 60 -d svg2png @@
```
