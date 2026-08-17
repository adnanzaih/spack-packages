# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RCollectivePackage

from spack.package import *


class Rdeseq2(RCollectivePackage):
    """Estimate variance-mean dependence in count data from high-throughput
    sequencing assays and test for differential expression based on a model
    using the negative binomial distribution.
    """

    bioc = "DESeq2"
    bioc_version = "3.23"
    url = "https://bioconductor.org/packages/3.23/bioc/src/contrib/DESeq2_1.52.0.tar.gz"

    license("LGPL-3.0-or-later")

    version("1.52.0", sha256="8c91699286336350e66eec132ce6fdf5bb4af78e2a4d015a5a61224f62a95984")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("r@4.6:", type=("build", "run"))
