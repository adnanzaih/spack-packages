# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage

from spack.package import *


class NetcdfCxx4(AutotoolsPackage):
    """NetCDF (network Common Data Form) is a set of software libraries and
    machine-independent data formats that support the creation, access, and
    sharing of array-oriented scientific data. This is the C++ distribution."""

    homepage = "https://www.unidata.ucar.edu/software/netcdf"
    url = "https://downloads.unidata.ucar.edu/netcdf-cxx/4.3.1/netcdf-cxx4-4.3.1.tar.gz"

    maintainers("WardF")

    license("Apache-2.0")

    version("4.3.1", sha256="6a1189a181eed043b5859e15d5c080c30d0e107406fbb212c8fb9814e90f3445")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("hdf5")
    depends_on("netcdf-c")

    filter_compiler_wrappers("ncxx4-config", relative_root="bin")

    @property
    def libs(self):
        return find_libraries("libnetcdf_c++4", root=self.prefix, recursive=True)

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        env.set("CPATH", self._include_flags)

    @property
    def _include_flags(self):
        hdf5 = self.spec["hdf5"]
        netcdf_c = self.spec["netcdf-c"]

        return " ".join(
            [
                "-I{0}".format(hdf5.prefix.include),
                "-I{0}".format(netcdf_c.prefix.include),
            ]
        )

    @property
    def _ldflags(self):
        hdf5 = self.spec["hdf5"]
        netcdf_c = self.spec["netcdf-c"]

        lib_dirs = dedupe(hdf5.libs.directories + netcdf_c.libs.directories)
        return " ".join("-L{0}".format(d) for d in lib_dirs)

    def configure_args(self):
        cppflags = self._include_flags
        ldflags = self._ldflags
        cflags = "{0} {1} -lhdf5 -lz -lnetcdf".format(cppflags, ldflags)

        return [
            "--disable-filter-testing",
            "CPPFLAGS={0}".format(cppflags),
            "CFLAGS={0}".format(cflags),
            "CXXFLAGS={0}".format(cflags),
            "LDFLAGS={0}".format(ldflags),
        ]
