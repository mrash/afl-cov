#!/bin/bash

test -z "$1" -o "$1" = "-h" && {
  echo "Syntax: $0 [-c] <command> [options]"
  echo Sets build options for coverage instrumentation with gcov/lcov.
  echo Set CC/CXX environment variables if you do not want gcc/g++.
  echo Specify the -c parameter if you want to use clang/clang++ instead.
  echo Example: "$0 ./configure --disable-shared"
  exit 1
}

echo " $CC $CXX" | grep -q afl && { echo Error: AFL++ compiler is set.; exit 1; }

CLANG=
test "$1" = "-c" && { CLANG=yes ; shift ; }

test -z "$CC" -a -z "$CLANG" && export CC=gcc
test -z "$CXX" -a -z "$CLANG" && export CXX=g++
test -z "$CC" -a -n "$CLANG" && export CC=clang
test -z "$CXX" -a -n "$CLANG" && export CXX=clang++

export CFLAGS="-fprofile-arcs -ftest-coverage -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION"
export CXXFLAGS="$CFLAGS"
export CPPFLAGS="$CFLAGS"
test -z "$CLANG" && export LDFLAGS="-lgcov --coverage"
test -n "$CLANG" && export LDFLAGS="--coverage"

$*
