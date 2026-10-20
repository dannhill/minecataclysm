cmake_minimum_required(VERSION 3.20)
project(cwm_launcher CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(WIN32)
    enable_language(RC)
    add_executable(Minecataclysm WIN32 src/windows_launcher.cpp src/windows_launcher.rc)
    target_include_directories(Minecataclysm PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../protocol/include)
    target_link_libraries(Minecataclysm PRIVATE user32 gdi32 shell32 ole32 ws2_32)
    if(MINGW)
        target_link_options(Minecataclysm PRIVATE -municode)
    endif()
else()
add_executable(cwm-launcher src/launcher_main.cpp)
set(CWM_PROJECT_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." CACHE PATH "Integration supervisor checkout")
target_compile_definitions(cwm-launcher PRIVATE CWM_PROJECT_ROOT="${CWM_PROJECT_ROOT}")
add_custom_command(TARGET cwm-launcher POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink cwm-launcher cwm-coordinator
)

endif()
