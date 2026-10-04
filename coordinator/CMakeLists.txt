cmake_minimum_required(VERSION 3.20)
project(cwm_coordinator CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(cwm-coordinator ../launcher/src/launcher_main.cpp)
set(CWM_PROJECT_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." CACHE PATH "Integration supervisor checkout")
target_compile_definitions(cwm-coordinator PRIVATE CWM_PROJECT_ROOT="${CWM_PROJECT_ROOT}")
