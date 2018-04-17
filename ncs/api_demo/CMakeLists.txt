cmake_minimum_required(VERSION 3.4)
project(ncs C)

set(CMAKE_C_STANDARD 99)

add_library(mvnc SHARED
        ${CMAKE_CURRENT_SOURCE_DIR}/api/src/mvnc_api.c
        ${CMAKE_CURRENT_SOURCE_DIR}/api/src/usb_boot.c
        ${CMAKE_CURRENT_SOURCE_DIR}/api/src/usb_link_vsc.c)

target_include_directories(mvnc PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/api/include)

message("os is " ${CMAKE_SYSTEM_NAME})

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/api/src/mvnc DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/keyboard.jpg DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/mobilenet_v1.graph DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

if (ANDROID)
    set_target_properties(mvnc
            PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_BINARY_DIR}/${ANDROID_ABI}")
    add_library(usb1.0 SHARED IMPORTED)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${ANDROID_ABI}/libusb1.0.so DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${ANDROID_ABI})
    set_target_properties(usb1.0 PROPERTIES IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${ANDROID_ABI}/libusb1.0.so)

    target_link_libraries(mvnc usb1.0 log)
else ()
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/api/mvncapi.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/ncs_demo.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/labels.txt DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
    target_link_libraries(mvnc usb-1.0)
endif ()


if (UNIX AND NOT APPLE) # Linux system
    set_property(TARGET mvnc PROPERTY LINK_FLAGS "-Wl,--no-as-needed -ldl")
endif ()

add_executable(ncs_demo ${CMAKE_CURRENT_SOURCE_DIR}/ncs_demo.c)

target_include_directories(ncs_demo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/api/include)
target_link_libraries(ncs_demo mvnc m)
