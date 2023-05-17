# [Word Frequency](https://fedora.pkgs.org/34/fedora-x86_64/wf-0.41-26.fc34.x86_64.rpm.html)

## Download Instructions

Similar to PerfFuzz we use version wf-0.41 of Word Frequency.
The source file is provided here for reference under the [src](./src) directory.
However, if you wish to download the source file yourself, you can try this
[link](http://ftp.altlinux.org/pub/distributions/ALTLinux/Sisyphus/x86_64/SRPMS.classic/wf-0.41-alt2.src.rpm).

## Application Stats

```bash
$ cloc --not-match-f=test .
      32 text files.
      25 unique files.                              
      16 files ignored.

github.com/AlDanial/cloc v 1.70  T=0.16 s (98.6 files/s, 59516.1 lines/s)
--------------------------------------------------------------------------------
Language                      files          blank        comment           code
--------------------------------------------------------------------------------
Bourne Shell                      5            666            754           4709
make                              4            110             41            916
Bourne Again Shell                2             91            111            843
m4                                1             92             14            768
C                                 2             66             49            279
C/C++ Header                      2             19             13            115
--------------------------------------------------------------------------------
SUM:                             16           1044            982           7630
--------------------------------------------------------------------------------
```

We only count code of C, C++, and C/C++ Headers (given *test* files are excluded).
Thus, 279 + 115 = 394 SLoC.

## Manually Build the Source Code

After decompressing the file
```bash
rpm2cpio wf-0.41-alt1.qa1.src.rpm | cpio -idmv
tar -xvf wf-0.41.tar
```
From within the new source directory `wf-0.41`, use AFL's compiler to 
generate the appropriate Makefile.

```bash
CC=/home/git/perffuzz/afl-clang-fast ./configure
```

Then run `make` to build the application with the appropriate instrumentation.

If things compiled successfully, you should find a file named `wf` under `target_apps/word-frequency/src/wf-0.41/src`.

## Sample Run Without Fuzzing

To test the that the installation was successfully completed. You can run `wf` based on 
[seed.txt](inputs/seed.txt) (shown below) by simply passing the file to wf `./src/wf-0.41/src/wf inputs/seed.txt`.
A correct run should result on a report of how many times a word was repeated (ones in this case). 

```text
dummy seed input for perffuzz
```

## Run With AFL

To manually run the AFL listener on the target application you use a command similar to the one below.

```bash
afl-socket -i /home/slackline/target_apps/word-frequency/inputs/ -o /home/results/wf-001 -p -N 60 -d /home/slackline/target_apps/word-frequency/src/wf-0.41/src/wf
```
