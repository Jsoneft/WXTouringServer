# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /Applications/CLion.app/Contents/bin/cmake/mac/bin/cmake

# The command to remove a file.
RM = /Applications/CLion.app/Contents/bin/cmake/mac/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/flysky/CLionProjects/socketServerCplus

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug

# Include any dependencies generated for this target.
include CMakeFiles/socketServerCplus.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/socketServerCplus.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/socketServerCplus.dir/flags.make

CMakeFiles/socketServerCplus.dir/main.cpp.o: CMakeFiles/socketServerCplus.dir/flags.make
CMakeFiles/socketServerCplus.dir/main.cpp.o: ../main.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/socketServerCplus.dir/main.cpp.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/socketServerCplus.dir/main.cpp.o -c /Users/flysky/CLionProjects/socketServerCplus/main.cpp

CMakeFiles/socketServerCplus.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/socketServerCplus.dir/main.cpp.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/flysky/CLionProjects/socketServerCplus/main.cpp > CMakeFiles/socketServerCplus.dir/main.cpp.i

CMakeFiles/socketServerCplus.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/socketServerCplus.dir/main.cpp.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/flysky/CLionProjects/socketServerCplus/main.cpp -o CMakeFiles/socketServerCplus.dir/main.cpp.s

# Object files for target socketServerCplus
socketServerCplus_OBJECTS = \
"CMakeFiles/socketServerCplus.dir/main.cpp.o"

# External object files for target socketServerCplus
socketServerCplus_EXTERNAL_OBJECTS =

socketServerCplus: CMakeFiles/socketServerCplus.dir/main.cpp.o
socketServerCplus: CMakeFiles/socketServerCplus.dir/build.make
socketServerCplus: CMakeFiles/socketServerCplus.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable socketServerCplus"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/socketServerCplus.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/socketServerCplus.dir/build: socketServerCplus

.PHONY : CMakeFiles/socketServerCplus.dir/build

CMakeFiles/socketServerCplus.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/socketServerCplus.dir/cmake_clean.cmake
.PHONY : CMakeFiles/socketServerCplus.dir/clean

CMakeFiles/socketServerCplus.dir/depend:
	cd /Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/flysky/CLionProjects/socketServerCplus /Users/flysky/CLionProjects/socketServerCplus /Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug /Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug /Users/flysky/CLionProjects/socketServerCplus/cmake-build-debug/CMakeFiles/socketServerCplus.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/socketServerCplus.dir/depend

