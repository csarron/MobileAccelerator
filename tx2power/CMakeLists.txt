cmake_minimum_required(VERSION 2.6)

project("tx2power")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c11 -O3 -Wall")

add_executable(tx2power tx2power.h tx2power.c)

