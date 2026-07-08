# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage

from spack.package import *


class NetcdfC(AutotoolsPackage):
    """NetCDF (network Common Data Form) is a set of software libraries and
    machine-independent data formats that support the creation, access, and
    sharing of array-oriented scientific data. This is the C distribution."""

    homepage = "https://www.unidata.ucar.edu/software/netcdf"
    git = "https://github.com/Unidata/netcdf-c.git"
    url = "https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.8.1.tar.gz"

    maintainers("skosukhin", "WardF")

    license("BSD-3-Clause")

    version("main", branch="main")
    version("4.10.0", sha256="ce160f9c1483b32d1ba8b7633d7984510259e4e439c48a218b95a023dc02fd4c")
    version("4.9.3", sha256="990f46d49525d6ab5dc4249f8684c6deeaf54de6fec63a187e9fb382cc0ffdff")
    version("4.9.2", sha256="bc104d101278c68b303359b3dc4192f81592ae8640f1aee486921138f7f88cb7")
    version("4.9.0", sha256="9f4cb864f3ab54adb75409984c6202323d2fc66c003e5308f3cdf224ed41c0a6")
    version("4.8.1", sha256="bc018cc30d5da402622bf76462480664c6668b55eb16ba205a0dfb8647161dd0")
    version("4.8.0", sha256="aff58f02b1c3e91dc68f989746f652fe51ff39e6270764e484920cb8db5ad092")
    version("4.7.4", sha256="99930ad7b3c4c1a8e8831fb061cb02b2170fc8e5ccaeda733bd99c3b9d31666b")
    version("4.7.3", sha256="05d064a2d55147b83feff3747bea13deb77bef390cb562df4f9f9f1ce147840d")
    version("4.7.2", sha256="7648db7bd75fdd198f7be64625af7b276067de48a49dcdfd160f1c2ddff8189c")
    version("4.7.1", sha256="583e6b89c57037293fc3878c9181bb89151da8c6015ecea404dd426fea219b2c")
    version("4.7.0", sha256="26d03164074363b3911ed79b7cddd045c22adf5ebaf978943db11a1d9f15e9d3")

    depends_on("c", type="build")
    depends_on("hdf5")
    depends_on("szip")
    #depends_on("libxml2")

    def patch(self):
        # Needed due to the patch applied to fix CVE-2025-14933.
        # A `#include <stdint.h>` is introduced in version 4.8.1.
        # Refer to https://github.com/spack/spack-packages/issues/5524
        if self.spec.satisfies("@:4.8.0"):
            filter_file(
                "#define NCCONFIGURE_H 1",
                "#define NCCONFIGURE_H 1\n\n#ifdef HAVE_STDINT_H\n#include <stdint.h>\n#endif",
                "include/ncconfigure.h",
                string=True,
            )

    @property
    def libs(self):
        return find_libraries("libnetcdf", root=self.prefix, recursive=True)

    def configure_args(self):
        hdf5 = self.spec["hdf5"]
        szip = self.spec["szip"]

        cppflags = " ".join(
            [
                hdf5.headers.cpp_flags,
                szip.headers.cpp_flags,
            ]
        )

        lib_dirs = dedupe(hdf5.libs.directories + szip.libs.directories)
        ldflags = " ".join("-L{0}".format(d) for d in lib_dirs)

        return [
            "--disable-dap-remote-tests",
            "CPPFLAGS={0}".format(cppflags),
            "CFLAGS={0}".format(cppflags),
            "LDFLAGS={0}".format(ldflags),
            "LIBS=-lhdf5 -lsz -lz",
        ]
