# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RPackage

from spack.package import *


class RSfnetworks(RPackage):
    """Provides a tidy approach to spatial network analysis,in the form of classes and functions
    that enable a seamless interaction between the network analysis package 'tidygraph'
    and the spatial analysis package 'sf'."""

    cran = "sfnetworks"

    license("Apache-2.0", checked_by="theAeon")

    version("0.6.6", sha256="a4868f4ece9637e6460e4155bf0eb526f900a6cc782d5b723b26111ecbb891f9")
    version("0.6.5", sha256="eb1e1c5941e21e0c2e74b438eb256202b38b784abc3ba2e9f495ce401d19ef10")
    version("0.6.4", sha256="3f424f6132fd9044daba526b3f558857d3b4e120f80ef2c8b77c3eea499cc460")
    version("0.6.3", sha256="63a8d61929ae2abd405f1aa5673842159852d9339ab7331170e8953a1bc35831")
    version("0.6.2", sha256="29753dfad492c3be133cc29b519c7b1218bd4c264a840061ddd71640d4c783bd")
    version("0.6.1", sha256="f84916950cec218df8d42b874f2b04b47ee181e9832387aa5ada1b9cc8d58ece")
    version("0.6.0", sha256="bece2251d478c11480417c6078e7ae6476c90fcfe100dce39b0f317532e3d025")
    version("0.5.5", sha256="0e7bc09b526721901919bd420e7e1cd5c63dfd469aa04eaf36db04dd9040929e")
    version("0.5.4", sha256="91687d774afba0cb4f748d46a3f25e70bf42832a5487950db58a7f611eb75d97")
    version("0.5.3", sha256="0a0e619aa39d66ccb1416ff24bb0ef938c40d20c3a9298e438fa4266c0f97fb8")
    version("0.5.2", sha256="a82aacd306c6c999ad25710c40c1861b7bd8871acc8a0b97c68b27f641badc4f")
    version("0.5.1", sha256="aa9285869573ba3b3c8e6ee315f513eb6cf3336d6e3402c80586ae675a95c2e4")
    version("0.5.0", sha256="6de55e37bc2f7fa2a8ef933aeff691f41b49c89b8ecdfbc42b09b206aa321cb6")

    with default_args(type=("build", "run")):
        depends_on("r-crayon")
        depends_on("r-dplyr")
        depends_on("r-igraph")
        depends_on("r-lwgeom")
        depends_on("r-rlang")
        depends_on("r-sf")
        depends_on("r-sfheaders")
        depends_on("r-tibble")
        depends_on("r-tidygraph")
        depends_on("r-units")
