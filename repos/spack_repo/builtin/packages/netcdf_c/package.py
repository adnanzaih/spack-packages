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

        config_args += self.enable_or_disable("utilities")
        config_args += self.enable_or_disable("test", variant="tests")
        config_args += self.enable_or_disable("examples")

        if self.spec.satisfies("@4.8.0:"):
            config_args.append("--enable-hdf5")
        else:
            config_args.append("--enable-netcdf-4")

        # NCZarr was added in version 4.8.0 as an experimental feature and became a supported one
        # in version 4.8.1:
        if self.spec.satisfies("@4.8.1:"):
            config_args.append("--enable-nczarr")
        elif self.spec.satisfies("@4.8.0"):
            config_args.append("--disable-nczarr")

        if self.spec.satisfies("@4.9.0:+shared"):
            # The plugins are not built when the shared libraries are disabled:
            config_args.extend(
                ["--enable-plugins", "--with-plugin-dir={0}".format(self.prefix.plugins)]
            )

        # The option was introduced in version 4.3.1 and does nothing starting version 4.6.1:
        if self.spec.satisfies("@4.3.1:4.6.0"):
            config_args.append("--enable-dynamic-loading")

        if self.spec.satisfies("@4.4:"):
            config_args += self.enable_or_disable("parallel4", variant="mpi")

        config_args += self.enable_or_disable("pnetcdf", variant="parallel-netcdf")

        config_args += self.enable_or_disable("hdf4")

        config_args += self.enable_or_disable("shared")

        config_args += self.enable_or_disable("dap")
        if self.spec.satisfies("@4.9.0:"):
            # Prevent linking to system libxml2:
            config_args += self.enable_or_disable("libxml2", variant="dap")

        if "+byterange" in self.spec:
            config_args.append("--enable-byterange")
        elif self.spec.satisfies("@4.7.0:"):
            config_args.append("--disable-byterange")

        if self.spec.satisfies("@4.3.2:4.9.2"):
            config_args += self.enable_or_disable("jna")

        config_args += self.enable_or_disable("fsync")

        config_args += self.enable_or_disable("logging")

        if any(self.spec.satisfies(s) for s in ["+mpi", "+parallel-netcdf", "^hdf5+mpi~shared"]):
            config_args.append("CC={0}".format(self.spec["mpi"].mpicc))

        # In general, we rely on the compiler wrapper to inject the required CPPFLAGS and LDFLAGS.
        # However, the injected LDFLAGS are invisible for the configure script and are added
        # neither to the pkg-config nor to the nc-config files. Therefore, we generate LDFLAGS
        # based on the contents of the following list and pass them to the configure script:
        lib_search_dirs = []

        # In general, we rely on the configure script to generate the required linker flags in the
        # right order. However, the configure script does not know and does not check for several
        # possible transitive dependencies and we have to pass them as the LIBS argument. The list
        # is generated based on the contents of the following list:
        extra_libs = []

        if "+parallel-netcdf" in self.spec:
            lib_search_dirs.extend(self.spec["parallel-netcdf"].libs.directories)

        if "+hdf4" in self.spec:
            hdf = self.spec["hdf"]
            lib_search_dirs.extend(hdf.libs.directories)
            # The configure script triggers unavoidable overlinking to jpeg:
            lib_search_dirs.extend(hdf["jpeg"].libs.directories)
            if "~shared" in hdf:
                # We do not use self.spec["hdf:transitive"].libs to avoid even more duplicates
                # introduced by the configure script:
                if "+szip" in hdf:
                    extra_libs.append(hdf["szip"].libs)
                if "+external-xdr ^libtirpc" in hdf:
                    extra_libs.append(hdf["rpc"].libs)
                extra_libs.append(hdf["zlib-api"].libs)

        hdf5 = self.spec["hdf5:hl"]
        lib_search_dirs.extend(hdf5.libs.directories)
        if "~shared" in hdf5:
            if "+szip" in hdf5:
                extra_libs.append(hdf5["szip"].libs)
            extra_libs.append(hdf5["zlib-api"].libs)

        if self.spec.satisfies("@4.9.0:+shared"):
            lib_search_dirs.extend(self.spec["zlib-api"].libs.directories)
        else:
            # Prevent overlinking to zlib:
            config_args.append("ac_cv_search_deflate=")

        if "+nczarr_zip" in self.spec:
            lib_search_dirs.extend(self.spec["libzip"].libs.directories)
        elif self.spec.satisfies("@4.9.2:"):
            # Prevent linking to libzip to disable the feature:
            config_args.append("ac_cv_search_zip_open=no")
        elif self.spec.satisfies("@4.8.0:"):
            # Prevent linking to libzip to disable the feature:
            config_args.append("ac_cv_lib_zip_zip_open=no")

        if "+szip" in self.spec:
            lib_search_dirs.extend(self.spec["szip"].libs.directories)
        elif self.spec.satisfies("@4.9.0:"):
            # Prevent linking to szip to disable the plugin:
            config_args.append("ac_cv_lib_sz_SZ_BufftoBuffCompress=no")

        if self.spec.satisfies("@4.9.3:"):
            # If the plugin is built (i.e. when +shared), we want to ensure that the configure
            # scripts checks for -lbz2 delivered by the bzip2 package. If the plugin is not built,
            # we ensure that the configure script does not pick up system bzip2 (see below), but we
            # also want to skip the checks for -lbzip2. Therefore, we pass the following option in
            # both cases:
            config_args.append("--enable-filter-bz2")
        if self.spec.satisfies("@4.9.0:"):
            if "+shared" in self.spec:
                lib_search_dirs.extend(self.spec["bzip2"].libs.directories)
            else:
                # Prevent redundant entries mentioning system bzip2 in nc-config and pkg-config
                # files:
                config_args.append("ac_cv_lib_bz2_BZ2_bzCompress=no")

        if "+zstd" in self.spec:
            if self.spec.satisfies("@4.9.3:"):
                config_args.append("--enable-filter-zstd")
            lib_search_dirs.extend(self.spec["zstd"].libs.directories)
        elif self.spec.satisfies("@4.9.3:"):
            config_args.append("--disable-filter-zstd")
        elif self.spec.satisfies("@4.9.0:"):
            # Prevent linking to system zstd:
            config_args.append("ac_cv_lib_zstd_ZSTD_compress=no")

        if "+blosc" in self.spec:
            if self.spec.satisfies("@4.9.3:"):
                config_args.append("--enable-filter-blosc")
            lib_search_dirs.extend(self.spec["c-blosc"].libs.directories)
        elif self.spec.satisfies("@4.9.3:"):
            config_args.append("--disable-filter-blosc")
        elif self.spec.satisfies("@4.9.0:"):
            # Prevent linking to system c-blosc:
            config_args.append("ac_cv_lib_blosc_blosc_init=no")

        if not self.spec.satisfies("@:4.4,main"):
            # Suppress the redundant check for m4:
            config_args.append("ac_cv_prog_NC_M4=false")

        lib_search_dirs.extend(d for libs in extra_libs for d in libs.directories)
        # Remove duplicates and system prefixes:
        lib_search_dirs = filter_system_paths(dedupe(lib_search_dirs))
        config_args.append(
            "LDFLAGS={0}".format(" ".join("-L{0}".format(d) for d in lib_search_dirs))
        )

        extra_lib_names = [n for libs in extra_libs for n in libs.names]
        # Remove duplicates in the reversed order:
        extra_lib_names = reversed(list(dedupe(reversed(extra_lib_names))))
        config_args.append("LIBS={0}".format(" ".join("-l{0}".format(n) for n in extra_lib_names)))

        return config_args

    def check(self):
        # Build all tests in parallel:
        make("check", "TESTS=", parallel=True)
        # Run the tests serially if needed. Also, run with the the --keep-going (-k) flag to run
        # all tests even if a test in a subdirectory fails:
        make(
            "check",
            "-k",
            # The h5_test fails when run in parallel (it looks like the issues with running the
            # tests in parallel were fixed around version 4.6.0,
            # see https://github.com/Unidata/netcdf-c/commit/812c2fd4d108cca927582c0d84049c0f271bb9e0):
            parallel=self.spec.satisfies("@4.6.0:"),
        )
