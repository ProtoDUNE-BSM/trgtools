

# This is a skeleton CMakeLists.txt file, auto-generated on
# Fri Dec 1 20:19:30 CET 2023.  The developer(s) of this package should delete
# this comment as well as adding dependent targets, packages,
# etc. specific to the package. For details on how to write a package,
# please see
# https://dune-daq-sw.readthedocs.io/en/latest/packages/daq-cmake/

cmake_minimum_required(VERSION 3.12)
project(trgtools VERSION 2.0.0)

find_package(daq-cmake REQUIRED)
find_package(CLI11 REQUIRED)
find_package(fmt REQUIRED)

find_package(nlohmann_json REQUIRED)
find_package(hdf5libs REQUIRED)
find_package(trgdataformats REQUIRED)
find_package(triggeralgs REQUIRED)
find_package(detchannelmaps REQUIRED)


daq_setup_environment()


find_package(Boost COMPONENTS unit_test_framework REQUIRED)

##############################################################################


# See https://dune-daq-sw.readthedocs.io/en/latest/packages/daq-cmake/#daq_add_library

daq_add_library( LINK_LIBRARIES hdf5libs::hdf5libs trgdataformats::trgdataformats triggeralgs::triggeralgs detchannelmaps::detchannelmaps) # Any source files and/or dependent libraries to link in not yet determined

##############################################################################

daq_install()
