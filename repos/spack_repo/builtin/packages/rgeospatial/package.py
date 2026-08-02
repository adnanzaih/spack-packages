# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RCollectivePackage

from spack.package import *


class Rgeospatial(RCollectivePackage):
    """Easily Install and Load Geospatial Packages in R.

    This package provides an easy way to install and load multiple geospatial
    packages in R, ensuring that all necessary dependencies are correctly
    configured."""

    cran = "geosphere"
    cran_packages = ["chromote", "leafem", "leaflet", "satellite", "s2", "terra", "sf", "foreign", "stars", "raster", "spatstat", "mapproj", "gdalUtilities", "mapview", "OpenStreetMap", "tigris", "igraph", "tidygraph", "sfnetworks"]
    #cran_mirror = "https://repo.miserver.it.umich.edu/cran/"

    license("MIT")

    version("1.5-18", sha256="99ff6ff050cc8c2d565b6bb1488607fc7950a6d448930f8d9642eccefbc6dac0")


    depends_on("c", type="build")
    depends_on("cxx", type="build")


    depends_on("r@3.3:", type=("build", "run"))
    #depends_on("r-rcpp", type=("build", "run"))
    depends_on("rtidyverse")
    depends_on("gdal")
    depends_on("proj")
    depends_on("geos")
    #depends_on("pkgconfig", type="build")
    depends_on('netcdf-fortran')
    depends_on('hdf5+hl+cxx+fortran')
    depends_on("java", type=("build", "run"))
