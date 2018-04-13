cmake_minimum_required(VERSION 3.4)
project(ncs C)

set(CMAKE_C_STANDARD 99)


add_library(mvnc SHARED
        api/src/mvnc_api.c
        api/src/usb_boot.c
        api/src/usb_link_vsc.c)

target_include_directories(mvnc PRIVATE api/include)

add_library(usb1.0 SHARED IMPORTED)
message("os is " ${CMAKE_SYSTEM_NAME})

if (ANDROID)
    set_target_properties(mvnc
            PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_BINARY_DIR}/${ANDROID_ABI}")
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${ANDROID_ABI}/libusb1.0.so DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${ANDROID_ABI})
    set_target_properties(usb1.0 PROPERTIES IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${ANDROID_ABI}/libusb1.0.so)
else ()
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${CMAKE_SYSTEM_NAME}/libusb-1.0.0${CMAKE_SHARED_LIBRARY_SUFFIX} DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/)
    set_target_properties(usb1.0 PROPERTIES IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/api/libs/${CMAKE_SYSTEM_NAME}/libusb-1.0.0${CMAKE_SHARED_LIBRARY_SUFFIX})
endif ()

target_link_libraries(mvnc usb1.0)
if (UNIX AND NOT APPLE) # Linux system
    set_property(TARGET mvnc PROPERTY LINK_FLAGS "-Wl,--no-as-needed -ldl")
endif ()

add_executable(ncs_demo ncs_demo.c fp16.c)

add_custom_command(
        TARGET ncs_demo POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/api/src/mvnc ${CMAKE_CURRENT_BINARY_DIR}/mvnc
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/keyboard.jpg ${CMAKE_CURRENT_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/mobilenet_v1.graph ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Copying resource-file mvnc/MvNCAPI.mvcmd"
)

if (NOT ANDROID)
    add_custom_command(
            TARGET ncs_demo POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/api/mvncapi.py ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/ncs_demo.py ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/test_resources/labels.txt ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Copying data and python demo to output directory"
    )
endif ()

target_include_directories(ncs_demo PRIVATE api/include)
target_link_libraries(ncs_demo mvnc m)