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
    depends_on("netcdf-c@4.7.4:", when="@4.5.3:")  # nc_def_var_szip required
    depends_on("doxygen", when="+doc", type="build")

    # We need to use MPI wrappers when building against static MPI-enabled NetCDF and/or HDF5:
    with when("^netcdf-c~shared"):
        depends_on("mpi", when="^netcdf-c+mpi")
        depends_on("mpi", when="^netcdf-c+parallel-netcdf")
        depends_on("mpi", when="^hdf5+mpi~shared")

    # Enable 'make check' for NAG, which is too strict.
    patch("nag_testing.patch", when="@4.4.5%nag")

    # File fortran/nf_logging.F90 is compiled without -DLOGGING, which leads
    # to missing symbols in the library. Additionally, the patch enables
    # building with NAG, which refuses to compile empty source files (see also
    # comments in the patch):
    patch("logging.patch", when="@:4.4.5")

    # Prevent excessive linking to system libraries. Without this patch the
    # library might get linked to the system installation of libcurl. See
    # https://github.com/Unidata/netcdf-fortran/commit/0a11f580faebbc1c4dce68bf5135709d1c7c7cc1#diff-67e997bcfdac55191033d57a16d1408a
    patch("excessive_linking.patch", when="@4.4.5")

    # Parallel builds do not work in the fortran directory. This patch is
    # derived from https://github.com/Unidata/netcdf-fortran/pull/211
    patch("no_parallel_build.patch", when="@4.5.2")

    filter_compiler_wrappers("nf-config", relative_root="bin")

    def flag_handler(self, name, flags):
        if name == "cflags":
            if "+pic" in self.spec:
                flags.append(self["c"].pic_flag)
        elif name == "fflags":
            if "+pic" in self.spec:
                flags.append(self["fortran"].pic_flag)
            if self.spec.satisfies("@:4.5.2"):
                if self.spec.satisfies("%fortran=gcc@10:"):
                    # https://github.com/Unidata/netcdf-fortran/issues/212
                    flags.append("-fallow-argument-mismatch")
                elif self.spec.satisfies("%fortran=nag"):
                    # https://github.com/Unidata/netcdf-fortran/issues/218
                    flags.append("-mismatch_all")
            if self.spec.satisfies("%fortran=cce"):
                # Cray compiler generates module files with uppercase names by
                # default, which is not handled by the makefiles of
                # NetCDF-Fortran:
                # https://github.com/Unidata/netcdf-fortran/pull/221.
                # The following flag forces the compiler to produce module
                # files with lowercase names.
                flags.append("-ef")
            elif self.spec.satisfies("%fortran=nag platform=darwin"):
                # The MacOS file system is case-insensitive. NAG therefore treats .F90
                # files as .f90 files, and so doesn't run them through its
                # preprocessor. So add -fpp to force NAG to run the preprocessor on
                # all Fortran files.
                flags.append("-fpp")

        # Note that cflags and fflags should be added by the compiler wrapper
        # and not on the command line to avoid overriding the default
        # compilation flags set by the configure script:
        return flags, None, None

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
