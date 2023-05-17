# [flex](https://github.com/westes/flex)

## Download Instructions

We obtain the latest version at the time of our test (flex-2.6.4).
The source file is provided here for reference under the [src](./src) directory.
However, if you wish to download the source file yourself, you can try this 
[link](https://github.com/westes/flex/archive/refs/tags/v2.6.4.tar.gz), or 
you can search for the same version in the [releases page](https://github.com/westes/flex/releases).

## Application Stats

```bash
$ cloc --not-match-f=test .
     456 text files.
     360 unique files.                                          
     274 files ignored.

github.com/AlDanial/cloc v 1.70  T=1.72 s (106.7 files/s, 75154.9 lines/s)
--------------------------------------------------------------------------------
Language                      files          blank        comment           code
--------------------------------------------------------------------------------
Bourne Shell                     16           4741           5672          30688
C                                36           3825           4161          21209
m4                               39           1214            534          12557
Bourne Again Shell                2           1791           2693           9736
make                             18           1190            894           8794
TeX                               1            751           3231           6097
lex                              46            706           1165           2612
C/C++ Header                     11            477            912           1026
yacc                              6            309            246            990
Perl                              1             49             84            239
Markdown                          2             27              0             87
awk                               1             15             32             72
C++                               1              7             24             25
sed                               2              0              0             16
Prolog                            1              0              0             15
--------------------------------------------------------------------------------
SUM:                            183          15102          19648          94163
--------------------------------------------------------------------------------
```

We only count code of C, C++, and C/C++ Headers (given *test* files are excluded).
Thus, 21209 + 1026 + 25 = 22,260 SLoC.

## Manually Build the Source Code

After decompressing the file `tar -xvf flex-2.6.4.tar.gz`, and within the new directory, follow these steps.

1. Install flex binary as it is a dependency itself! `apt-get install flex` (dumb/smart way to collect build dependencies).
2. Generate the configuration file `./autogen.sh`.
3. Generate the Makefile using AFL compiler `CXX=/home/git/perffuzz/afl-clang-fast++ CC=/home/git/perffuzz/afl-clang-fast ./configure`.
4. Run `make`.
5. Within the `src` dir test that the version of flex is the one we downloaded `./flex --version`.
6. Remove the un-instrumented binary for flex to avoid any confusion `apt-get remove flex`.

## Sample Run Without Fuzzing

To test that the installation was successfully completed. You can run `flex` (found under src) based on 
[seed](inputs/seed) (shown below) by simply passing the file to flex `/src/flex ../inputs/seed`. A correct
run should result on file named `lex.yy.c` written to disk. The file [seed](inputs/seed) is based on the example
given in [flex documentation](http://dinosaur.compilertools.net/flex/flex_5.html#SEC5). Other seeds are based on our
input generator!

```lexer
%%
username    printf( "%s", getlogin() );
%%
```

## Run With AFL

To manually run the AFL listener on the target application you use a command similar to the one below.

```bash
afl-socket -i /home/slackline/target_apps/flex/inputs/ -o /home/results/flex-test -p -N 60 -d /home/slackline/target_apps/flex/src/flex-2.6.4/src/flex
```
