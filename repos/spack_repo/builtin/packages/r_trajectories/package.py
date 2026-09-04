# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RPackage

from spack.package import *


class RTrajectories(RPackage):
    """Classes and methods for trajectory data, with support for nesting individual Track objects in track sets (Tracks)
    and track sets for different entities in collections of Tracks.
    Methods include selection, generalization, aggregation, intersection, simulation, and plotting."""

    cran = "trajectories"

    license("GPL-2.0-or-later", checked_by="theAeon")

    version("0.2-10", sha256="221cafd2e2be68fc8cfeb571ec32829a5b7c425479314483cc01cd26ad5ac1ff")
    version("0.2-9", sha256="f70f88c653d087610f8f3f078102fa83acac4e5ce46189f405605c6ed29f93f3")
    version("0.2-8", sha256="8dd0dbc142d3b792a8bcf30e95bb98ac2002bd52e4ee7948df7e252e24954467")
    version("0.2-7", sha256="c883893c925cb3cc5dba79cba5768001c9514bbd99c069e58ea4e02098371f27")
    version("0.2-6", sha256="e72f7d607d3482aecfe3d6c5372d0f67e9011eef704e1537eca3535adcf03bfc")
    version("0.2-5", sha256="943dd624df71e02d7bfcbd50bed6164a9d6ceda72e066f3e050a7020cdd63272")
    version("0.2-4", sha256="5428d1281496512968b5cf284a52bf07a05d6779dd10ebf579127d8a7f190786")
    version("0.2-3", sha256="f3f4ee82bdb8cb3c96f53e7a72e54fec643cf7d8eb2eb3cb1cb1a667bdf42ecc")
    version("0.2-2", sha256="19cfe1042546cd3ffe89c5cfb64f8a451170c7ce0fc555409ec857b4d1f49018")
    version("0.2-1", sha256="557067c7e29031c6c989bee53510f1f7dd5a5752bdd487263ba2895f397b816b")
    version("0.2-0", sha256="2c35a9127c7b121abd74ba9f836dfebc6d4dbb4ec78e666055ca30774f51a27d")
    version("0.1-4", sha256="dd72c89525c9e2eb744ee4ded8edf4749b948d268d32b479d78a7ba44b5f8e6f")
    version("0.1-3", sha256="78a7bfa9e73c2991bb202dca9d951795cbb9314d9235b2608ba823a75daf62d2")
    version("0.1-2", sha256="4620625ec2cb215e31d7f8b778abdc81fc8083e90572b05e153209dfcbaa47b4")
    version("0.1-1", sha256="430f9aa5eb606a6d707048b38bacb77f916567a049d586ad2e18af93d867c16d")
    version("0.1-0", sha256="7b2bb86bb59a8e8c0922f5d29e91c3870a68517bd44fb5d3b21cb0fb5b2f14e1")

    with default_args(type=("build", "run")):
        depends_on("r-lattice")
        depends_on("r-sp")
        depends_on("r-spacetime")
        depends_on("r-zoo")

