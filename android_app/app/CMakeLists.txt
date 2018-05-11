cmake_minimum_required(VERSION 3.4)


set(api_build_DIR ${PROJECT_BINARY_DIR}/ncs_api_outputs)
file(MAKE_DIRECTORY ${api_build_DIR})

set(api_SRC "${CMAKE_CURRENT_SOURCE_DIR}/../../ncs/api_demo/")
add_subdirectory(${api_SRC} ${api_build_DIR})
add_library(libmvnc SHARED IMPORTED)
set_target_properties(libmvnc PROPERTIES IMPORTED_LOCATION ${api_build_DIR}/${ANDROID_ABI}/libmvnc.so)

add_library(ncs_jni SHARED ${CMAKE_CURRENT_SOURCE_DIR}/src/main/cpp/ncs_jni.c)
target_link_libraries(ncs_jni libmvnc log)

add_library(acc SHARED ${CMAKE_CURRENT_SOURCE_DIR}/src/main/cpp/snpe_jni.cpp)
target_include_directories(acc PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/main/cpp/include/zdl)
target_link_libraries(acc ncs_jni)
