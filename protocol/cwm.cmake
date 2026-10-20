# Header-only CWM SDK is explicitly selectable for native and cross builds.
if(NOT CWM_FLATBUFFERS_INCLUDE_DIR)
    find_path(CWM_FLATBUFFERS_INCLUDE_DIR flatbuffers/flatbuffers.h
        HINTS "$ENV{HOME}/.local/include" NO_CMAKE_FIND_ROOT_PATH REQUIRED)
endif()
