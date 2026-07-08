# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage

from spack.package import *


class NetcdfFortran(AutotoolsPackage):
    """NetCDF (network Common Data Form) is a set of software libraries and
    machine-independent data formats that support the creation, access, and
    sharing of array-oriented scientific data. This is the Fortran
    distribution."""

    homepage = "https://www.unidata.ucar.edu/software/netcdf"
    url = "https://downloads.unidata.ucar.edu/netcdf-fortran/4.5.4/netcdf-fortran-4.5.4.tar.gz"

    maintainers("skosukhin", "WardF")

    tags = ["e4s"]

    license("Apache-2.0")

    version("4.6.2", sha256="df26b99d9003c93a8bc287b58172bf1c279676f8c10d6dd0daf8bc7204877096")
    version("4.6.1", sha256="b50b0c72b8b16b140201a020936aa8aeda5c79cf265c55160986cd637807a37a")
    version("4.6.0", sha256="198bff6534cc85a121adc9e12f1c4bc53406c403bda331775a1291509e7b2f23")
    version("4.5.4", sha256="0a19b26a2b6e29fab5d29d7d7e08c24e87712d09a5cafeea90e16e0a2ab86b81")
    version("4.5.3", sha256="123a5c6184336891e62cf2936b9f2d1c54e8dee299cfd9d2c1a1eb05dd668a74")
    version("4.5.2", sha256="b959937d7d9045184e9d2040a915d94a7f4d0185f4a9dceb8f08c94b0c3304aa")
    version("4.4.5", sha256="2467536ce29daea348c736476aa8e684c075d2f6cab12f3361885cb6905717b8")
    version("4.4.4", sha256="b2d395175f8d283e68c8be516e231a96b191ade67ad0caafaf7fa01b1e6b5d75")
    version("4.4.3", sha256="330373aa163d5931e475b5e83da5c1ad041e855185f24e6a8b85d73b48d6cda9")

    depends_on("c", type="build")
    depends_on("fortran", type="build")
    depends_on("netcdf-c")

    @property
    def libs(self):
        return find_libraries("libnetcdff", root=self.prefix, recursive=True)

    def configure_args(self):
        netcdf_c = self.spec["netcdf-c"]
        cppflags = "-I{0}".format(netcdf_c.prefix.include)
        ldflags = "-L{0}".format(netcdf_c.prefix.lib)
        fflags = "-w -fallow-argument-mismatch"

        return [
            "CPPFLAGS={0}".format(cppflags),
            "LDFLAGS={0}".format(ldflags),
            "FC={0}".format(self.compiler.fc),
            "F77={0}".format(self.compiler.f77),
            #"FCFLAGS={0}".format(fflags),
            #"FFLAGS={0}".format(fflags),
        ]
