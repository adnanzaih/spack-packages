# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.r import RPackage

from spack.package import *


class RTmaptools(RPackage):
    """Set of tools for reading and processing spatial data.
    The aim is to supply the workflow to create thematic maps.
    This package also facilitates 'tmap', the package for visualizing thematic maps."""

    cran = "tmaptools"

    license("GPL-3.0-only", checked_by="theAeon")

    version("3.3", sha256="cadb9918a463ca7e4f4d13f964f9fde25436958a56dd9ec6a2be5f609c804c56")
    version("3.2", sha256="ca77f8c9f9380fed4aad9f1c4163600ecfe7b47471bccdf735e6db01989d50ba")
    version("3.1-1", sha256="fd89cb0d7fb44e0a5dd5311fa3e75a729746bf2e8e158d5ec423e5963f1b542d")
    version("3.1", sha256="403aab1754adb6eb966027286e7e624e6aab689e0c44a2bea5f208cfe26bac43")
    version("3.0", sha256="1195bb72e75213b8048b10360fa3bc3bb8521efe2a15d17116a39623d2ce6634")
    version("2.0-2", sha256="04850dcd778a9c5ea79b2b78e458549eba8a5d461cba2e32bac0c483072315d9")
    version("2.0-1", sha256="9febf4dc5128ddc977bdecfb0c3dd32e99f280b0aec5787f3fab76720716d27d")
    version("2.0", sha256="82274a3e317f2a049a4bb6d1a0e6b1b94f8e1deba38e5e2982eb9b09751b53e7")
    version("1.2-4", sha256="a8eb65c04c0af907f2297c66dc4ef9f5a94565848f1e7376f1f36638ecb3d5b7")
    version("1.2-3", sha256="5932c5eb0a29cdd560ed343991fbba9f53550a589ac1719d38aa9d59726ca822")
    version("1.2-2", sha256="79a4c8111bf3033dcdc3b4ba95a92607a52be7a6ce1686383569e6b16168e44e")
    version("1.2-1", sha256="769a6093d27f1a14ed0fce208122cd6125dc8b525a5862508e0d4c50b9f13b66")
    version("1.2", sha256="178b1797a3004c871aa6750a3929bce4a3466e3a9eab526e675850f9a5ca58d2")
    version("1.0", sha256="7dbfcebb8f672518e625e11a63cb9cefdedeef3998cb618cb993dcfc94288ce1")

    with default_args(type=("build", "run")):
        depends_on("r-sf")
        depends_on("r-lwgeom")
        depends_on("r-stars")
        depends_on("r-units")
        depends_on("r-xml")
