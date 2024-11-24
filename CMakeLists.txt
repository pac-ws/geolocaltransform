cmake_minimum_required(VERSION 3.16)
if(NOT DEFINED SKBUILD_PROJECT_NAME)
	set(PROJECT_NAME "geolocaltransform")
else()
	set(PROJECT_NAME ${SKBUILD_PROJECT_NAME})
endif()
project(${PROJECT_NAME} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_COLOR_DIAGNOSTICS True)

if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()

include(FetchContent)

find_package(Python COMPONENTS Interpreter Development)
if(NOT ${SKBUILD_STATE} STREQUAL "sdist"
		AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/third_party/pybind11/CMakeLists.txt")
	message(STATUS "Using integrated pybind11")
	add_subdirectory(third_party/pybind11)
else()
	message(STATUS "Using pybind11 via FetchContent")
	FetchContent_Declare(
		pybind11
		GIT_REPOSITORY https://github.com/pybind/pybind11.git
		GIT_TAG v2.12.0
	)
	FetchContent_MakeAvailable(pybind11)
endif()

set(PYBIND11_NEWPYTHON True)
# find_package(pybind11 CONFIG REQUIRED)
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
set(CMAKE_INSTALL_RPATH "$ORIGIN;$ORIGIN/lib")

###########################
#### Eigen3 dependency ####
###########################
find_package(Eigen3 3.4 QUIET)
if(NOT Eigen3_FOUND OR Eigen3_VERSION VERSION_LESS 3.4)
  message(STATUS "Eigen3 3.4 not found, fetching it")
  include(FetchContent)
  FetchContent_Declare(Eigen3
    URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
  )
  set(FETCHCONTENT_QUIET FALSE) # show progress dialog
  FetchContent_Populate(Eigen3)   # finish fetching and unpacking before continuing
  add_subdirectory(${FETCHCONTENT_BASE_DIR}/eigen3-src ${CMAKE_CURRENT_BINARY_DIR}/eigen3)
endif()

find_package(GeographicLib REQUIRED)

pybind11_add_module(${PROJECT_NAME} MODULE transform_pybinds.cpp)
set(dependencies_list Eigen3::Eigen ${GeographicLib_LIBRARIES})
target_link_libraries(${PROJECT_NAME} PUBLIC ${dependencies_list})

install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION ${PROJECT_NAME})
