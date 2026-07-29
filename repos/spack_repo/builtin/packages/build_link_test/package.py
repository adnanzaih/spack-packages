# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack_repo.builtin.build_systems.cmake import CMakePackage

class BuildLinkTest(CMakePackage):
    """A small C program that links and exercises MPI, HDF5, NetCDF-C,
    FlexiBLAS, FreeType, libpng, and libjpeg via CMake."""

    homepage = "https://github.com/adnanzaih/build-link-test"
    git = "https://github.com/adnanzaih/build-link-test.git"

    maintainers("adnanzaih")

    version("main", branch="main")

    # ── Build-system ──────────────────────────────────────────────────────────
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("pkgconfig", type="build")

    # ── Runtime dependencies ──────────────────────────────────────────────────
    depends_on("mpi")                  # find_package(MPI REQUIRED COMPONENTS C)
    depends_on("hdf5")                # find_package(HDF5 REQUIRED COMPONENTS C)
    depends_on("netcdf-c")            # pkg_check_modules(NETCDF …)
    depends_on("flexiblas")           # pkg_check_modules(FLEXIBLAS …)
    depends_on("freetype")            # find_package(Freetype REQUIRED)
    depends_on("libpng")              # find_package(PNG REQUIRED)
    depends_on("libjpeg-turbo")       # find_package(JPEG REQUIRED)

    def cmake_args(self):
        args = [
            self.define("BUILD_TESTING", self.run_tests),
        ]
        return args

    def check(self):
        # The CTest suite runs the binary under mpiexec with 1 rank.
        with working_dir(self.build_directory):
            ctest("--output-on-failure", "-j1")