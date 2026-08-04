# Copyright Spack Project Developers.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
import os


class Fiji(Package):
    """Fiji is an ImageJ distribution containing many useful plugins
    for scientific image analysis.
    """

    homepage = "https://imagej.net/software/fiji/"
    url = "https://downloads.imagej.net/fiji/stable/fiji-stable-linux64-jdk.zip"

    maintainers("adnanzaih")

    # The stable archive is mutable. Replace the placeholder with the current
    # SHA-256 checksum before installing.
    version(
        "2026.03.07",
        sha256="35d85770a0a2c6b59adffff63e845bcb63866211b80411af1f6a2d6644764ff8",
        url="https://downloads.imagej.net/fiji/stable/fiji-stable-linux64-jdk.zip",
        preferred=True,
    )

    conflicts("platform=darwin", msg="This recipe installs the Linux x86-64 binary.")
    conflicts("target=aarch64:", msg="This archive contains x86-64 Linux binaries.")

    def install(self, spec, prefix):
        # self.stage.source_path is already the extracted Fiji.app directory.
        install_tree(self.stage.source_path, prefix.fiji)

        mkdirp(prefix.bin)

        launcher = join_path(prefix.fiji, "ImageJ-linux64")

        if not os.path.isfile(launcher):
            raise InstallError(
                "Could not find the Fiji launcher at {0}".format(launcher)
            )

        set_executable(launcher)

        relative_launcher = os.path.relpath(launcher, start=prefix.bin)

        symlink(relative_launcher, prefix.bin.Fiji)
        symlink(relative_launcher, prefix.bin.fiji)