cmake_minimum_required(VERSION 3.20)
project(cdda_mineclonia_workspace CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Protocol library and test suite
add_subdirectory(protocol)

# Standalone process supervisor / launcher
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launcher/CMakeLists.txt")
    add_subdirectory(launcher)
endif()

# CDDA bridge / headless server (when present)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cdda/CMakeLists.txt")
    message(STATUS "CDDA source detected at ${CMAKE_CURRENT_SOURCE_DIR}/cdda")
endif()

# Luanti 3D client with C++ bridge (when present)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/luanti/CMakeLists.txt")
    message(STATUS "Luanti source detected at ${CMAKE_CURRENT_SOURCE_DIR}/luanti")
endif()
