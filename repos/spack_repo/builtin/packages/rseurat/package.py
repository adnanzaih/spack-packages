# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RCollectivePackage

from spack.package import *


class Rseurat(RCollectivePackage):
    cran = "Seurat"
    #cran_mirror = "https://repo.miserver.it.umich.edu/cran/"

    license("MIT")

    version("5.1.0", sha256="adcfb43d7a8cc55eaa7a0954a082ac95e14059a82901913379bfec115e224d59")


    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("r@3.3:", type=("build", "run"))
