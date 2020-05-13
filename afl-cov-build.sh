#!/bin/sh

test -z "$1" -o "$1" = "-h" && {
  echo "Syntax: $0 <command> [options]"
  echo Sets build options for coverage instrumentation with gcov/lcov.
  echo Example: "$0 ./configure --disable-shared"
}

test -z "$CC" && export CC=gcc
test -z "$CXX" && export CXX=g++
export CFLAGS="-fprofile-arcs -ftest-coverage"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="-lgcov --coverage"

$*
