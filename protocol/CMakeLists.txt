cmake_minimum_required(VERSION 3.20)
project(cwm_protocol CXX)

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
    /home/dannhill/.local/include
)
add_dependencies(cwm_protocol generate_cwm_headers)

# Tests
enable_testing()

add_executable(test_serialization tests/test_serialization.cpp)
target_link_libraries(test_serialization PRIVATE cwm_protocol)
add_test(NAME test_serialization COMMAND test_serialization)

add_executable(test_ipc tests/test_ipc.cpp)
target_link_libraries(test_ipc PRIVATE cwm_protocol)
add_test(NAME test_ipc COMMAND test_ipc)

add_executable(test_transport_limits tests/test_transport_limits.cpp)
target_link_libraries(test_transport_limits PRIVATE cwm_protocol)
add_test(NAME test_transport_limits COMMAND test_transport_limits)

add_executable(test_session tests/test_session.cpp)
target_link_libraries(test_session PRIVATE cwm_protocol)
add_test(NAME test_session COMMAND test_session)

add_executable(test_clock tests/test_clock.cpp)
target_link_libraries(test_clock PRIVATE cwm_protocol)
add_test(NAME test_clock COMMAND test_clock)
