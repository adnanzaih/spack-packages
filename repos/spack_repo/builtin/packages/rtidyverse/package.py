# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RCollectivePackage

from spack.package import *


class Rtidyverse(RCollectivePackage):
    """Easily Install and Load the Tidyverse.

    The tidyverse is a set of packages that work in harmony because they share
    common data representations and API design. This package is designed to
    make it easy to install and load multiple tidyverse packages in a single
    step."""

    cran = "tidyverse"
    cran_packages = ["ggplot2", "tibble", "tidyr", "readr", "purrr", "dplyr", "stringr", "forcats"]
    cran_mirror = "https://repo.miserver.it.umich.edu/cran/"

    license("MIT")

    version("2.0.0", sha256="3d3c2d135056333247d309d1c2cc98cc0d87e2c781f4c6fbceab28d28c0728e5")

    depends_on("c", type="build")
    depends_on("cxx", type="build")


    depends_on("r@3.3:", type=("build", "run"))
    #depends_on("libpng", type=("build", "link", "run"))
    #depends_on("libtiff", type=("build", "link", "run"))
    #depends_on("jpeg", type=("build", "link", "run"))
    depends_on("pkgconfig", type="build")

    #def setup_build_environment(self, env: EnvironmentModifications) -> None:
    #    for name in ("libpng", "libtiff", "jpeg"):
    #        for directory in reversed(self.spec[name].libs.directories):
   #             env.prepend_path("LD_LIBRARY_PATH", directory)

