cmake_minimum_required(VERSION 3.20)
project(cwm_protocol CXX)
include(${CMAKE_CURRENT_SOURCE_DIR}/cwm.cmake)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_program(FLATC_EXECUTABLE NAMES flatc PATHS /home/dannhill/.local/bin NO_DEFAULT_PATH)
if(NOT FLATC_EXECUTABLE)
    find_program(FLATC_EXECUTABLE flatc REQUIRED)
endif()

message(STATUS "Found flatc: ${FLATC_EXECUTABLE}")

set(FBS_SRC ${CMAKE_CURRENT_SOURCE_DIR}/cwm.fbs)
set(GENERATED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include/cwm)
set(GENERATED_HEADER ${GENERATED_DIR}/cwm_generated.h)

add_custom_command(
    OUTPUT ${GENERATED_HEADER}
    COMMAND ${FLATC_EXECUTABLE} --cpp --gen-mutable --scoped-enums -o ${GENERATED_DIR} ${FBS_SRC}
    DEPENDS ${FBS_SRC}
    COMMENT "Generating C++ headers from cwm.fbs"
)

add_custom_target(generate_cwm_headers ALL DEPENDS ${GENERATED_HEADER})

add_library(cwm_protocol INTERFACE)
target_include_directories(cwm_protocol INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include/cwm
    ${CWM_FLATBUFFERS_INCLUDE_DIR}
)
add_dependencies(cwm_protocol generate_cwm_headers)

# These tests use assert for checks and setup; keep them effective in Release.
if(MSVC)
    add_compile_options(/UNDEBUG)
else()
    add_compile_options(-UNDEBUG)
endif()

# Tests
enable_testing()

add_executable(test_serialization tests/test_serialization.cpp)
target_link_libraries(test_serialization PRIVATE cwm_protocol)
add_test(NAME test_serialization COMMAND test_serialization)

if(WIN32)
    target_link_libraries(cwm_protocol INTERFACE advapi32)
    add_executable(test_windows_pipe tests/test_windows_pipe.cpp)
    target_link_libraries(test_windows_pipe PRIVATE cwm_protocol)
    add_test(NAME test_windows_pipe COMMAND test_windows_pipe)
else()
    add_executable(test_ipc tests/test_ipc.cpp)
    target_link_libraries(test_ipc PRIVATE cwm_protocol)
    add_test(NAME test_ipc COMMAND test_ipc)

    add_executable(test_transport_limits tests/test_transport_limits.cpp)
    target_link_libraries(test_transport_limits PRIVATE cwm_protocol)
    add_test(NAME test_transport_limits COMMAND test_transport_limits)
endif()

add_executable(test_session tests/test_session.cpp)
target_link_libraries(test_session PRIVATE cwm_protocol)
add_test(NAME test_session COMMAND test_session)

add_executable(test_clock tests/test_clock.cpp)
target_link_libraries(test_clock PRIVATE cwm_protocol)
add_test(NAME test_clock COMMAND test_clock)

add_executable(test_inventory tests/test_inventory.cpp)
target_link_libraries(test_inventory PRIVATE cwm_protocol)
add_test(NAME test_inventory COMMAND test_inventory)

add_executable(test_crafting tests/test_crafting.cpp)
target_link_libraries(test_crafting PRIVATE cwm_protocol)
add_test(NAME test_crafting COMMAND test_crafting)

add_executable(test_ranged tests/test_ranged.cpp)
target_link_libraries(test_ranged PRIVATE cwm_protocol)
add_test(NAME test_ranged COMMAND test_ranged)

add_executable(test_transfer tests/test_transfer.cpp)
target_link_libraries(test_transfer PRIVATE cwm_protocol)
add_test(NAME test_transfer COMMAND test_transfer)

add_executable(test_quickbar tests/test_quickbar.cpp)
target_link_libraries(test_quickbar PRIVATE cwm_protocol)
add_test(NAME test_quickbar COMMAND test_quickbar)

add_executable(test_decision tests/test_decision.cpp)
target_link_libraries(test_decision PRIVATE cwm_protocol)
add_test(NAME test_decision COMMAND test_decision)

add_executable(test_presentation tests/test_presentation.cpp)
target_link_libraries(test_presentation PRIVATE cwm_protocol)
add_test(NAME test_presentation COMMAND test_presentation)

add_executable(test_reading tests/test_reading.cpp)
target_link_libraries(test_reading PRIVATE cwm_protocol)
add_test(NAME test_reading COMMAND test_reading)
