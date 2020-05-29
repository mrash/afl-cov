#!/bin/sh

test -z "$1" -o "$1" = "-h" && {
  echo "Syntax: $0 <command> [options]"
  echo Sets build options for coverage instrumentation with gcov/lcov.
  echo Set CC/CXX environment variables if you do not want gcc/g++.
  echo Example: "$0 ./configure --disable-shared"
  exit 1
}

test -z "$CC" && export CC=gcc
test -z "$CXX" && export CXX=g++
export CFLAGS="-fprofile-arcs -ftest-coverage"
export CXXFLAGS="$CFLAGS"
export CPPFLAGS="$CFLAGS"
export LDFLAGS="-lgcov --coverage"

$*
