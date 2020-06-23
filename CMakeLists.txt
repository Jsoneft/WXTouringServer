cmake_minimum_required(VERSION 3.16)
project(socketServerCplus)
IF(NOT CMAKE_BUILD_TYPE)
    SET(CMAKE_BUILD_TYPE Release)
ENDIF()
set(CMAKE_CXX_STANDARD 11)

find_package(PythonLibs REQUIRED)
#include_directories("/usr/include/python2.7")
#target_link_libraries("/usr/lib/python2.7/config-x86_64-linux-gnu/")
include_directories(${PYTHON_INCLUDE_DIRS})
add_executable(c_to_python main.cpp util.h util.cpp cmake-build-debug/test.cpp cmake-build-debug/threadpool.h cmake-build-debug/threadpool.cpp)
#target_link_libraries(c_to_python "/usr/lib/python2.7/site-packages/")
#target_link_libraries(c_to_python "/usr/lib/python2.7/config-x86_64-linux-gnu")
target_link_libraries(c_to_python ${PYTHON_LIBRARIES})

#include_directories(/usr/include/python3.4)#添加头文件目录，相当于g++ -I参数
#link_directories(/usr/lib/python3.4)#动态链接库或静态链接库的搜索路径，相当于gcc的-L参数
#add_executable(python python.cc)#生成可执行文件
#target_link_libraries(python python3.4m)#添加链接库,相同于指定gcc -l参数