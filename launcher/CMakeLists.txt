cmake_minimum_required(VERSION 3.20)
project(cwm_launcher CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(cwm-launcher src/launcher_main.cpp)
add_custom_command(TARGET cwm-launcher POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink cwm-launcher cwm-coordinator
)
