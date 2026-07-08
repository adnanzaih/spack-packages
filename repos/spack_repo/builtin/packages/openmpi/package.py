# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os
import re
import sys

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

from spack.package import *


def slingshot_network():
    return os.path.exists("/opt/cray/pe") and (
        os.path.exists("/lib64/libcxi.so") or os.path.exists("/usr/lib64/libcxi.so")
    )


@memoized
def is_CrayEX():
    # Credit to upcxx and chapel packages for this hpe-cray-ex detection function
    if host_platform().name == "linux":
        target = os.environ.get("CRAYPE_NETWORK_TARGET")
        if target in ["ofi", "ucx"]:  # normal case
            return True
        elif target is None:  # but some systems lack Cray PrgEnv
            fi_info = which("fi_info")
            if (
                fi_info
                and fi_info("-l", output=str, error=str, fail_on_error=False).find("cxi") >= 0
            ):
                return True
    return False


def check_FI_HMEM_ROCR():
    if host_platform().name == "linux":
        fi_info = which("fi_info")
        if fi_info:
            output = fi_info("--caps", "FI_HMEM_ROCR", output=str, error=str, fail_on_error=False)
            # Check if there is any output indicating at least one provider
            if output.strip():
                return True
    return False


class Openmpi(AutotoolsPackage, CudaPackage, ROCmPackage):
    """An open source Message Passing Interface implementation.

    The Open MPI Project is an open source Message Passing Interface
    implementation that is developed and maintained by a consortium
    of academic, research, and industry partners. Open MPI is
    therefore able to combine the expertise, technologies, and
    resources from all across the High Performance Computing
    community in order to build the best MPI library available.
    Open MPI offers advantages for system and software vendors,
    application developers and computer science researchers.
    """

    homepage = "https://www.open-mpi.org"
    url = "https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.0.tar.bz2"
    list_url = "https://www.open-mpi.org/software/ompi/"
    git = "https://github.com/open-mpi/ompi.git"
    cxxname = "mpic++"

    maintainers("hppritcha", "naughtont3")

    executables = ["^ompi_info$"]

    tags = ["e4s"]

    license("custom")

    version("main", branch="main", submodules=True)

    # Current
    version(
        "5.0.10", sha256="0acecc4fc218e5debdbcb8a41d182c6b0f1d29393015ed763b2a91d5d7374cc6"
    )  # libmpi.so.40.40.7
    version(
        "5.0.9", sha256="dfb72762531170847af3e4a0f21d77d7b23cf36f67ce7ce9033659273677d80b"
    )  # libmpi.so.40.40.7
    version(
        "5.0.8", sha256="53131e1a57e7270f645707f8b0b65ba56048f5b5ac3f68faabed3eb0d710e449"
    )  # libmpi.so.40.40.7
    version(
        "5.0.7", sha256="119f2009936a403334d0df3c0d74d5595a32d99497f9b1d41e90019fee2fc2dd"
    )  # libmpi.so.40.40.7
    version(
        "5.0.6", sha256="bd4183fcbc43477c254799b429df1a6e576c042e74a2d2f8b37d537b2ff98157"
    )  # libmpi.so.40.40.6
    version(
        "5.0.5", sha256="6588d57c0a4bd299a24103f4e196051b29e8b55fbda49e11d5b3d32030a32776"
    )  # libmpi.so.40.40.5
    version(
        "5.0.4", sha256="64526852cdd88b2d30e022087c16ab3e03806c451b10cd691d5c1ac887d8ef9d"
    )  # libmpi.so.40.40.4
    version(
        "5.0.3", sha256="990582f206b3ab32e938aa31bbf07c639368e4405dca196fabe7f0f76eeda90b"
    )  # libmpi.so.40.40.3
    version(
        "5.0.2", sha256="ee46ad8eeee2c3ff70772160bff877cbf38c330a0bc3b3ddc811648b3396698f"
    )  # libmpi.so.40.40.2
    version(
        "5.0.1", sha256="e357043e65fd1b956a47d0dae6156a90cf0e378df759364936c1781f1a25ef80"
    )  # libmpi.so.40.40.1
    version(
        "5.0.0", sha256="9d845ca94bc1aeb445f83d98d238cd08f6ec7ad0f73b0f79ec1668dbfdacd613"
    )  # libmpi.so.40.40.0

    # Still supported
    version(
        "4.1.8", sha256="466f68e3132a1dc02710cc2011fafced8336d98359fa2dae4dddcfd5719f12a9"
    )  # libmpi.so.40.30.8
    version(
        "4.1.7", sha256="54a33cb7ad81ff0976f15a6cc8003c3922f0f3d8ceed14e1813ef3603f22cd34"
    )  # libmpi.so.40.30.7
    version(
        "4.1.6", sha256="f740994485516deb63b5311af122c265179f5328a0d857a567b85db00b11e415"
    )  # libmpi.so.40.30.6
    version(
        "4.1.5", sha256="a640986bc257389dd379886fdae6264c8cfa56bc98b71ce3ae3dfbd8ce61dbe3"
    )  # libmpi.so.40.30.5
    version(
        "4.1.4", sha256="92912e175fd1234368c8730c03f4996fe5942e7479bb1d10059405e7f2b3930d"
    )  # libmpi.so.40.30.4
    version(
        "4.1.3", sha256="3d81d04c54efb55d3871a465ffb098d8d72c1f48ff1cbaf2580eb058567c0a3b"
    )  # libmpi.so.40.30.3
    version(
        "4.1.2", sha256="9b78c7cf7fc32131c5cf43dd2ab9740149d9d87cadb2e2189f02685749a6b527"
    )  # libmpi.so.40.30.2
    version(
        "4.1.1", sha256="e24f7a778bd11a71ad0c14587a7f5b00e68a71aa5623e2157bafee3d44c07cda"
    )  # libmpi.so.40.30.1
    version(
        "4.1.0", sha256="73866fb77090819b6a8c85cb8539638d37d6877455825b74e289d647a39fd5b5"
    )  # libmpi.so.40.30.0

    
    patch("ad_lustre_rwcontig_open_source.patch", when="@1.6.5")
    patch("llnl-platforms.patch", when="@1.6.5")
    patch("configure.patch", when="@1.10.1")
    patch("fix_multidef_pmi_class.patch", when="@2.0.0:2.0.1")
    patch("fix-ucx-1.7.0-api-instability.patch", when="@4.0.0:4.0.2")
    # see issue with gpfs #13313 on https://github.com/open-mpi/ompi and
    # commit https://github.com/open-mpi/ompi/commit/556014c
    patch("fix_fs_gpfs_file_set_info.patch", when="@4.1 +gpfs")

    # Vader Bug: https://github.com/open-mpi/ompi/issues/5375
    # Haven't release fix for 2.1.x
    patch("btl_vader.patch", when="@2.1.3:2.1.5")

    # Fixed in 3.0.3 and 3.1.3
    patch("btl_vader.patch", when="@3.0.1:3.0.2")
    patch("btl_vader.patch", when="@3.1.0:3.1.2")

    # Fix MPI_Sizeof() in the "mpi" Fortran module for compilers that do not
    # support "IGNORE TKR" functionality (e.g. NAG).
    # The issue has been resolved upstream in two steps:
    #   1) https://github.com/open-mpi/ompi/pull/2294
    #   2) https://github.com/open-mpi/ompi/pull/5099
    # The first one was applied starting version v3.0.0 and backported to
    # v1.10. A subset with relevant modifications is applicable starting
    # version 1.8.4.
    patch("use_mpi_tkr_sizeof/step_1.patch", when="@1.8.4:1.10.6,2.0:2")
    # The second patch was applied starting version v4.0.0 and backported to
    # v2.x, v3.0.x, and v3.1.x.
    patch("use_mpi_tkr_sizeof/step_2.patch", when="@1.8.4:2.1.3,3:3.0.1")
    # To fix performance regressions introduced while fixing a bug in older
    # gcc versions on x86_64, Refs. open-mpi/ompi#8603
    patch("opal_assembly_arch.patch", when="@4.0.0:4.0.5,4.1.0")
    # Fix reduce operations for unsigned long integers
    # See https://github.com/open-mpi/ompi/issues/10648
    patch(
        "https://github.com/open-mpi/ompi/commit/8e6d9ba8058a0c128438dbc0cd6476f1abb1d4f1.patch?full_index=1",
        sha256="12f3aabbcdb02f28138e250273c2f62591db4b1f9f8aa3dcc3ef9ed551f4f587",
        when="@4.0.7,4.1.2:4.1.4",
    )
    # To fix an error in Open MPI configury related to findng dl lib.
    # This is specific to the 5.0.0 release.
    patch("fix-for-dlopen-missing-symbol-problem.patch", when="@5.0.0")
    # Patches to accelerator CUDA component to link in libcuda
    # when in non-standard location
    patch("accelerator-cuda-fix-bug-in-makefile.patch", when="@5.0.0")
    patch("btlsmcuda-fix-problem-with-makefile.patch", when="@5.0.0")
    patch("accelerator-build-components-as-dso-s-by-default.patch", when="@5.0.0:5.0.1")

    # OpenMPI 5.0.0-5.0.3 needs to change PMIX version check to compile w/ PMIX > 4.2.5
    # https://github.com/open-mpi/ompi/issues/12537#issuecomment-2103350910
    # https://github.com/openpmix/prrte/pull/1957
    patch("pmix_getline_pmix_version.patch", when="@5.0.0:5.0.3")
    patch("pmix_getline_pmix_version-prte.patch", when="@5.0.3")

    # OpenMPI 5.0.7 specific patch - see https://github.com/open-mpi/ompi/pull/13106
    patch(
        "https://github.com/open-mpi/ompi/commit/d10e9765bdd28e62621395aef6bbb7710bae2e82.patch?full_index=1",
        sha256="38529b557df029d6a987fa7e337db40b0ac1c1bb921776b95aacaa40e945cd21",
        when="@4.1.8,5.0.7",
    )

    # Add missing header for memcpy
    # https://github.com/open-mpi/ompi/commit/aa5577441ff1ab7f97f8b63e442b37457c7bd997
    patch("add_string.patch", when="@5.0.1:5.0.8 +rocm")

    # GCC 16: drop __opal_attribute_always_inline__ from mca_part_persist_start
    # to fix "inlining failed in call to always_inline: recursive inlining" error
    # https://github.com/open-mpi/ompi/issues/13721
    patch(
        "https://github.com/open-mpi/ompi/commit/aa024ac73d624611cfe3af6f541b5d28dedf07bb.patch?full_index=1",
        sha256="646eb1a7382d628eb821715ca69fc5467a9a25aaddfe8290dbce008536dbfaa0",
        when="@5.0.0:",
    )

    # GCC 16: fix excessive brace initialization in memheap_base_frame.c
    # https://github.com/open-mpi/ompi/issues/13757
    patch(
        "https://github.com/open-mpi/ompi/commit/b878c7d974dae767246ad20ef9124a331d0f59a4.patch?full_index=1",
        sha256="1dcebafdb310203f3b62456a5ba67e1a21ad3a88aaf40326734885d7b0d776f9",
        when="@5.0.0: +openshmem",
    )

    FABRICS = (
        "psm",
        "psm2",
        "verbs",
        "mxm",
        "ucx",
        "ofi",
        "fca",
        "hcoll",
        "ucc",
        "xpmem",
        "cma",
        "knem",
    )

    variant(
        "fabrics",
        values=disjoint_sets(("auto",), FABRICS).with_non_feature_values(
            "auto", "none"
        ),  # shared memory transports
        description="List of fabrics that are enabled; 'auto' lets openmpi determine",
    )

    SCHEDULERS = ("alps", "lsf", "tm", "slurm", "sge", "loadleveler")

    variant(
        "schedulers",
        values=disjoint_sets(("auto",), SCHEDULERS).with_non_feature_values("auto", "none"),
        description="List of schedulers for which support is enabled; "
        "'auto' lets openmpi determine",
    )

    # Additional support options
    variant("atomics", default=True, description="Enable built-in atomics")
    variant("java", default=False, when="@1.7.4:", description="Build Java support")
    variant("static", default=False, description="Build static libraries")
    variant("sqlite3", default=False, when="@1.7.3:1", description="Build SQLite3 support")
    variant("vt", default=True, description="Build VampirTrace support")
    variant(
        "thread_multiple",
        default=False,
        when="@1.5.4:2",
        description="Enable MPI_THREAD_MULTIPLE support",
    )
    variant(
        "pmi", default=False, when="@1.5.5:4 schedulers=slurm", description="Enable PMI support"
    )
    variant(
        "wrapper-rpath",
        default=True,
        when="@1.7.4:",
        description="Enable rpath support in the wrappers",
    )
    variant("cxx", default=False, when="@:4", description="Enable deprecated C++ MPI bindings")
    variant(
        "cxx_exceptions",
        default=False,
        when="@:4",
        description="Enable deprecated C++ exception support",
    )
    variant("fortran", default=True, description="Enable Fortran support")
    variant("gpfs", default=False, description="Enable GPFS support")
    variant("lustre", default=False, description="Lustre filesystem library support")
    variant("romio", default=True, when="@:5", description="Enable ROMIO support")
    variant("romio", default=False, when="@5:", description="Enable ROMIO support")
    variant(
        "romio-filesystem",
        description="Add the filesystem to romio",
        values=disjoint_sets(
            (
                "daos",
                "nfs",
                "ufs",
                "pvfs2",
                "testfs",
                "xfs",
                "panfs",
                "lustre",
                "gpfs",
                "ime",
                "quobytefs",
            )
        ).with_non_feature_values("none"),
    )

    variant("rsh", default=True, description="Enable rsh (openssh) process lifecycle management")
    variant(
        "orterunprefix",
        default=False,
        when="@1.3:4",
        description="Prefix Open MPI to PATH and LD_LIBRARY_PATH on local and remote hosts",
    )
    variant("ipv6", default=False, when="@4:", description="Enable IPv6 support")
    # Adding support to build a debug version of OpenMPI that activates
    # Memchecker, as described here:
    #
    # https://www.open-mpi.org/faq/?category=debugging#memchecker_what
    #
    # This option degrades run-time support, and thus is disabled by default
    variant(
        "memchecker",
        default=False,
        description="Memchecker support for debugging [degrades performance]",
        sticky=True,
    )

    variant(
        "legacylaunchers",
        default=False,
        when="@1.6:4 schedulers=slurm",
        description="Do not remove mpirun/mpiexec when building with slurm",
    )

    variant("debug", default=False, description="Make debug build", when="build_system=autotools")

    variant(
        "two_level_namespace",
        default=False,
        description="""Build shared libraries and programs
built with the mpicc/mpifort/etc. compiler wrappers
with '-Wl,-commons,use_dylibs' and without
'-Wl,-flat_namespace'.""",
    )

    variant(
        "cray-xpmem",
        default=False,
        when="fabrics=xpmem",
        description="use cray-xpmem instead of xpmem configure flag",
    )

    # Patch to allow two-level namespace on a MacOS platform when building
    # openmpi. Unfortuntately, the openmpi configure command has flat namespace
    # hardwired in. In spack, this only works for openmpi up to versions 4,
    # because for versions 5+ autoreconf is triggered (see below) and this
    # patch needs to be applied (again) AFTER autoreconf ran.
    @when("+two_level_namespace platform=darwin")
    def patch(self):
        filter_file(r"-flat_namespace", "-commons,use_dylibs", "configure")

    provides("mpi@:2.0", when="@:1.2")
    provides("mpi@:2.1", when="@1.3:1.7.2")
    provides("mpi@:2.2", when="@1.7.3:1.7.4")
    provides("mpi@:3.0", when="@1.7.5:1.10.7")
    provides("mpi@:3.1", when="@2.0.0:")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build", when="+fortran")
    depends_on("autoconf @2.69:", type="build", when="@5.0.0:,main")
    depends_on("automake @1.13.4:", type="build", when="@5.0.0:,main")
    depends_on("sqlite", when="+sqlite3")

    with when("fabrics=ucx"):
        depends_on("ucx")
        depends_on("ucx +cuda", when="+cuda")
        depends_on("ucx +thread_multiple", when="+thread_multiple")
        depends_on("ucx +thread_multiple", when="@3.0.0:")
        depends_on("ucx@1.9.0:", when="@4.0.6:4.0")
        depends_on("ucx@1.9.0:", when="@4.1.1:4.1")
        depends_on("ucx@1.9.0:", when="@5.0.0:")
    depends_on("libfabric", when="fabrics=ofi")
    depends_on("libfabric@1", when="@:4.0 fabrics=ofi")
    depends_on("fca", when="fabrics=fca")
    depends_on("hcoll", when="fabrics=hcoll")
    depends_on("ucc", when="fabrics=ucc")
    depends_on("ucc +rocm", when="fabrics=ucc +rocm")
    depends_on("xpmem", when="fabrics=xpmem")
    depends_on("knem", when="fabrics=knem")

    depends_on("lsf", when="schedulers=lsf")
    depends_on("pbs", when="schedulers=tm")
    depends_on("slurm", when="schedulers=slurm")

    with when("+rocm"):
        libfabric_requirement = ""
        if is_CrayEX() or check_FI_HMEM_ROCR() or slingshot_network():
            libfabric_requirement = "fabrics=cxi"
        requires("fabrics=ucx ^ucx +rocm", f"^libfabric {libfabric_requirement}", policy="one_of")

    depends_on("cuda", type=("build", "link", "run"), when="@5: +cuda")
    depends_on("hip", type=("build", "link", "run"), when="@5: +rocm")

    conflicts("+cxx_exceptions", when="%nvhpc", msg="nvc does not ignore -fexceptions, but errors")

    # CUDA support was added in 1.7, and since the variant is part of the
    # parent package we must express as a conflict rather than a conditional
    # variant.
    conflicts("+cuda", when="@:1.6")
    # Same goes with ROCm support added in 5.0
    conflicts("+rocm", when="@:4")
    # PSM2 support was added in 1.10.0
    conflicts("fabrics=psm2", when="@:1.8")
    # MXM support was added in 1.5.4
    conflicts("fabrics=mxm", when="@:1.5.3")
    # libfabric (OFI) support was added in 1.10.0
    conflicts("fabrics=ofi", when="@:1.8")
    # fca support was added in 1.5.0 and removed in 5.0.0
    conflicts("fabrics=fca", when="@:1.4,5:")
    # hcoll support was added in 1.7.3:
    conflicts("fabrics=hcoll", when="@:1.7.2")
    # ucc support was added in 4.1.4:
    conflicts("fabrics=ucc", when="@:4.1.3")
    # xpmem support was added in 1.7
    conflicts("fabrics=xpmem", when="@:1.6")
    # cma support was added in 1.7
    conflicts("fabrics=cma", when="@:1.6")
    # knem support was added in 1.5
    conflicts("fabrics=knem", when="@:1.4")

    # According to this comment on github:
    #
    # https://github.com/open-mpi/ompi/issues/4338#issuecomment-383982008
    #
    # adding --enable-static silently disables slurm support via pmi/pmi2
    # for versions older than 3.0.3,3.1.3,4.0.0
    # Presumably future versions after 11/2018 should support slurm+static
    conflicts("+static", when="schedulers=slurm @:3.0.2,3.1:3.1.2,4.0.0")

    # May be able to get working for LLVM 18/19 using FC=flang-new
    conflicts("%fortran=clang %llvm@:19")

    filter_compiler_wrappers("openmpi/*-wrapper-data*", relative_root="share")

    extra_install_tests = "examples"

    @classmethod
    def determine_version(cls, exe):
        output = Executable(exe)(output=str, error=str)
        match = re.search(r"Open MPI: (\S+)", output)
        return Version(match.group(1)) if match else None

    @classmethod
    def determine_variants(cls, exes, version):
        results = []
        for exe in exes:
            variants = []
            output = Executable(exe)("-a", output=str, error=str)
            # Some of these options we have to find by hoping the
            # configure string is in the ompi_info output. While this
            # is usually true, it's not guaranteed.  For anything that
            # begins with --, we want to use the defaults as provided
            # by the openmpi package in the absense of any other info.

            # atomics
            if re.search(r"--enable-builtin-atomics", output):
                variants.append("+atomics")

            # java
            if version in ver("1.7.4:"):
                match = re.search(r"\bJava bindings: (\S+)", output)
                if match and is_enabled(match.group(1)):
                    variants.append("+java")
                else:
                    variants.append("~java")

            # static
            if re.search(r"--enable-static", output):
                variants.append("+static")
            elif re.search(r"--disable-static", output):
                variants.append("~static")
            elif re.search(r"\bMCA (?:coll|oca|pml): monitoring", output):
                # Built multiple variants of openmpi and ran diff.
                # This seems to be the distinguishing feature.
                variants.append("~static")

            # sqlite
            if version in ver("1.7.3:1"):
                if re.search(r"\bMCA db: sqlite", output):
                    variants.append("+sqlite3")
                else:
                    variants.append("~sqlite3")

            # vt
            if re.search(r"--enable-contrib-no-build=vt", output):
                variants.append("+vt")

            # thread_multiple
            if version in ver("1.5.4:2"):
                match = re.search(r"MPI_THREAD_MULTIPLE: (\S+?),?", output)
                if match and is_enabled(match.group(1)):
                    variants.append("+thread_multiple")
                else:
                    variants.append("~thread_multiple")

            # cuda
            match = re.search(
                r'parameter "mpi_built_with_cuda_support" ' + r'\(current value: "(\S+)"', output
            )
            if match and is_enabled(match.group(1)):
                variants.append("+cuda")
            else:
                variants.append("~cuda")

            # rocm
            match = re.search(
                r'parameter "mpi_built_with_rocm_support" ' + r'\(current value: "(\S+)"', output
            )
            if match and is_enabled(match.group(1)):
                variants.append("+rocm")
            else:
                variants.append("~rocm")

            # wrapper-rpath
            if version in ver("1.7.4:"):
                match = re.search(r"\bWrapper compiler rpath: (\S+)", output)
                if match and is_enabled(match.group(1)):
                    variants.append("+wrapper-rpath")
                else:
                    variants.append("~wrapper-rpath")

            # cxx
            if version in ver(":4"):
                match = re.search(r"\bC\+\+ bindings: (\S+)", output)
                if match and match.group(1) == "yes":
                    variants.append("+cxx")
                else:
                    variants.append("~cxx")

            # cxx_exceptions
            if version in ver(":4"):
                match = re.search(r"\bC\+\+ exceptions: (\S+)", output)
                if match and match.group(1) == "yes":
                    variants.append("+cxx_exceptions")
                else:
                    variants.append("~cxx_exceptions")

            # lustre
            if re.search(r"--with-lustre", output):
                variants.append("+lustre")

            # memchecker
            match = re.search(r"Memory debugging support: (\S+)", output)
            if match and is_enabled(match.group(1)):
                variants.append("+memchecker")
            else:
                variants.append("~memchecker")

            # pmi
            if version in ver("1.5.5:4"):
                if re.search(r"\bMCA (?:ess|prrte): pmi", output):
                    variants.append("+pmi")
                else:
                    variants.append("~pmi")

            # fabrics
            used_fabrics = []
            for fabric in cls.FABRICS:
                match = re.search(r"\bMCA (?:mtl|btl|pml): %s\b" % fabric, output)
                if match:
                    used_fabrics.append(fabric)
            if used_fabrics:
                variants.append("fabrics=" + ",".join(used_fabrics))
            else:
                variants.append("fabrics=none")

            # schedulers
            used_schedulers = []
            for scheduler in cls.SCHEDULERS:
                match = re.search(r"\bMCA (?:prrte|ras): %s\b" % scheduler, output)
                if match:
                    used_schedulers.append(scheduler)
            if used_schedulers:
                variants.append("schedulers=" + ",".join(used_schedulers))
            else:
                variants.append("schedulers=none")

            # Get the appropriate compiler
            match = re.search(r"\bC compiler absolute: (\S+)", output)
            if match:
                compiler = match.group(1)
                compiler_spec = get_spack_compiler_spec(compiler)
                if compiler_spec:
                    variants.append("%" + str(compiler_spec))
            results.append(" ".join(variants))
        return results

    def url_for_version(self, version):
        url = "https://download.open-mpi.org/release/open-mpi/v{0}/openmpi-{1}.tar.bz2"
        return url.format(version.up_to(2), version)

    @property
    def headers(self):
        hdrs = HeaderList(find(self.prefix.include, "mpi.h", recursive=False))
        if not hdrs:
            hdrs = HeaderList(find(self.prefix, "mpi.h", recursive=True))
        return hdrs or None

    @property
    def libs(self):
        query_parameters = self.spec.last_query.extra_parameters
        libraries = ["libmpi"]

        if "cxx" in query_parameters:
            libraries = ["libmpi_cxx"] + libraries

        return find_libraries(libraries, root=self.prefix, shared=True, recursive=True)

    def setup_run_environment(self, env: EnvironmentModifications) -> None:
        # Because MPI is both a runtime and a compiler, we have to setup the
        # compiler components as part of the run environment.
        env.set("MPICC", join_path(self.prefix.bin, "mpicc"))
        env.set("MPICXX", join_path(self.prefix.bin, self.cxxname))
        env.set("MPIF77", join_path(self.prefix.bin, "mpif77"))
        env.set("MPIF90", join_path(self.prefix.bin, "mpif90"))
        # Open MPI also has had mpifort since v1.7, so we can set MPIFC to that
        # Note: that mpif77 and mpif90 are deprecated since v1.7, but careful
        # testing would be needed to change the MPIF77 and MPIF90 above. For now
        # we just *add* functionality
        if self.spec.satisfies("@1.7:"):
            env.set("MPIFC", join_path(self.prefix.bin, "mpifort"))

    def setup_dependent_build_environment(
        self, env: EnvironmentModifications, dependent_spec: Spec
    ) -> None:
        # Use the spack compiler wrappers under MPI
        dependent_module = dependent_spec.package.module
        for var_name, attr_name in (
            ("OMPI_CC", "spack_cc"),
            ("OMPI_CXX", "spack_cxx"),
            ("OMPI_FC", "spack_fc"),
            ("OMPI_F77", "spack_f77"),
        ):
            if hasattr(dependent_module, attr_name):
                env.set(var_name, getattr(dependent_module, attr_name))

        # See https://www.open-mpi.org/faq/?category=building#installdirs
        for suffix in [
            "PREFIX",
            "EXEC_PREFIX",
            "BINDIR",
            "SBINDIR",
            "LIBEXECDIR",
            "DATAROOTDIR",
            "DATADIR",
            "SYSCONFDIR",
            "SHAREDSTATEDIR",
            "LOCALSTATEDIR",
            "LIBDIR",
            "INCLUDEDIR",
            "INFODIR",
            "MANDIR",
            "PKGDATADIR",
            "PKGLIBDIR",
            "PKGINCLUDEDIR",
        ]:
            env.unset(f"OPAL_{suffix}")

    def setup_dependent_package(self, module, dependent_spec):
        self.spec.mpicc = join_path(self.prefix.bin, "mpicc")
        self.spec.mpicxx = join_path(self.prefix.bin, self.cxxname)
        # Some derived packages define the "fortran" variant, most don't. Checking on the
        # presence of ~fortran makes us default to add fortran wrappers if the variant is
        # not declared.
        if self.spec.satisfies("~fortran"):
            return
        self.spec.mpifc = join_path(self.prefix.bin, "mpif90")
        self.spec.mpif77 = join_path(self.prefix.bin, "mpif77")

    # Most of the following with_or_without methods might seem redundant
    # because Spack compiler wrapper adds the required -I and -L flags, which
    # is enough for the configure script to find them. However, we also need
    # the flags in Libtool (lib/*.la) and pkg-config (lib/pkgconfig/*.pc).
    # Therefore, we pass the prefixes explicitly.

    def with_or_without_psm2(self, activated):
        if not activated:
            return "--without-psm2"
        return "--with-psm2={0}".format(self.spec["opa-psm2"].prefix)

    def with_or_without_verbs(self, activated):
        # Up through version 1.6, this option was named --with-openib.
        # In version 1.7, it was renamed to be --with-verbs.
        opt = "verbs" if self.spec.satisfies("@1.7:") else "openib"
        if not activated:
            return "--without-{0}".format(opt)
        return "--with-{0}={1}".format(opt, self.spec["rdma-core"].prefix)

    def with_or_without_mxm(self, activated):
        if not activated:
            return "--without-mxm"
        return "--with-mxm={0}".format(self.spec["mxm"].prefix)

    def with_or_without_ucx(self, activated):
        if not activated:
            return "--without-ucx"
        return "--with-ucx={0}".format(self.spec["ucx"].prefix)

    def with_or_without_ofi(self, activated):
        # Up through version 3.0.3 this option was name --with-libfabric.
        # In version 3.0.4, the old name was deprecated in favor of --with-ofi.
        opt = "ofi" if self.spec.satisfies("@3.0.4:") else "libfabric"
        if not activated:
            return "--without-{0}".format(opt)
        return "--with-{0}={1}".format(opt, self.spec["libfabric"].prefix)

    def with_or_without_fca(self, activated):
        if not activated:
            return "--without-fca"
        return f"--with-fca={self.spec['fca'].prefix}"

    def with_or_without_hcoll(self, activated):
        if not activated:
            return "--without-hcoll"
        return f"--with-hcoll={self.spec['hcoll'].prefix}"

    def with_or_without_ucc(self, activated):
        if not activated:
            return "--without-ucc"
        return f"--with-ucc={self.spec['ucc'].prefix}"

    def with_or_without_xpmem(self, activated):
        s1 = "xpmem"
        if self.spec.satisfies("+cray-xpmem"):
            s1 = "cray-xpmem"
        if not activated:
            return f"--without-{s1}"
        return f"--with-{s1}={self.spec['xpmem'].prefix}"

    def with_or_without_knem(self, activated):
        if not activated:
            return "--without-knem"
        return f"--with-knem={self.spec['knem'].prefix}"

    def with_or_without_lsf(self, activated):
        if not activated:
            return "--without-lsf"
        return f"--with-lsf={self.spec['lsf'].prefix}"

    def with_or_without_tm(self, activated):
        if not activated:
            return "--without-tm"
        return f"--with-tm={self.spec['pbs'].prefix}"

    def configure_args(self):
        spec = self.spec
        config_args = [
            "--enable-shared",
            "--disable-silent-rules",
            "--disable-sphinx",
            "--disable-dependency-tracking",
        ]

        # Work around incompatibility with new apple-clang linker
        # https://github.com/open-mpi/ompi/issues/12427
        if spec.satisfies("@:4.1.6,5.0.0:5.0.3 %apple-clang@15:"):
            config_args.append("--with-wrapper-fcflags=-Wl,-ld_classic")

        config_args.extend(self.enable_or_disable("builtin-atomics", variant="atomics"))

        if spec.satisfies("+pmi"):
            config_args.append(f"--with-pmi={spec['slurm'].prefix}")
        else:
            config_args.extend(self.with_or_without("pmi"))

        config_args.extend(self.enable_or_disable("static"))

        if spec.satisfies("@4.0.0:4.0.2"):
            # uct btl doesn't work with some UCX versions so just disable
            config_args.append("--enable-mca-no-build=btl-uct")

        # Remove ssh/rsh pml
        if spec.satisfies("~rsh"):
            config_args.append("--enable-mca-no-build=plm-rsh")

        # Useful for ssh-based environments
        # For v4 and lower
        if spec.satisfies("+orterunprefix"):
            config_args.append("--enable-orterun-prefix-by-default")

        # Enable IPv6 support
        if spec.satisfies("+ipv6"):
            config_args.append("--enable-ipv6")

        # some scientific packages ignore deprecated/remove symbols. Re-enable
        # them for now, for discussion see
        # https://github.com/open-mpi/ompi/issues/6114#issuecomment-446279495
        if spec.satisfies("@4.0.1:"):
            config_args.append("--enable-mpi1-compatibility")

        # Fabrics
        if "fabrics=auto" not in spec:
            config_args.extend(self.with_or_without("fabrics"))

        if spec.satisfies("@2.0.0:"):
            config_args.append(self.with_or_without_xpmem("fabrics=xpmem" in spec))

        # Schedulers
        if "schedulers=auto" not in spec:
            config_args.extend(self.with_or_without("schedulers"))

        if spec.satisfies("schedulers=lsf"):
            config_args.append(f"--with-lsf-libdir={spec['lsf'].libs.directories[0]}")

        config_args.extend(self.enable_or_disable("memchecker"))
        if spec.satisfies("+memchecker"):
            config_args.extend(["--enable-debug"])

        # Package dependencies
        for dep in ["lustre", "valgrind"]:
            if spec.satisfies(f"%{dep}"):
                config_args.append(f"--with-{dep}={spec[dep].prefix}")

        if "+gpfs" in spec:
            config_args.append("--with-gpfs")
        else:
            config_args.append("--with-gpfs=no")

        # SQLite3 support
        config_args.extend(self.with_or_without("sqlite3"))

        # VampirTrace support
        if spec.satisfies("@1.3:1"):
            if "~vt" in spec:
                config_args.append("--enable-contrib-no-build=vt")

        # Multithreading support
        config_args.extend(
            self.enable_or_disable("mpi-thread-multiple", variant="thread_multiple")
        )

        # CUDA support
        # See https://www.open-mpi.org/faq/?category=buildcuda
        if "+cuda" in spec:
            # OpenMPI dynamically loads libcuda.so, requires dlopen
            config_args.append("--enable-dlopen")
            # Searches for header files in DIR/include
            config_args.append("--with-cuda={0}".format(spec["cuda"].prefix))
            if spec.satisfies("@1.7:1.7.2"):
                # This option was removed from later versions
                config_args.append(
                    "--with-cuda-libdir={0}".format(spec["cuda"].libs.directories[0])
                )
            if spec.satisfies("@5.0:"):
                # And then it returned
                config_args.append(
                    "--with-cuda-libdir={0}".format(spec["cuda"].libs.directories[0] + "/stubs")
                )
            if spec.satisfies("@1.7.2"):
                # There was a bug in 1.7.2 when --enable-static is used
                config_args.append("--enable-mca-no-build=pml-bfo")
        elif spec.satisfies("@1.7:"):
            config_args.append("--without-cuda")

        # ROCm support
        # See https://docs.open-mpi.org/en/v5.0.x/tuning-apps/networking/rocm.html
        if "+rocm" in spec:
            config_args.append("--with-rocm={0}".format(spec["hip"].prefix))
        elif spec.satisfies("@5:"):
            config_args.append("--without-rocm")

        if spec.satisfies("%nvhpc@:20.11"):
            # Workaround compiler issues
            config_args.append("CFLAGS=-O1")

        if "+openshmem" in spec:
            config_args.append("--enable-oshmem")

        if "+wrapper-rpath" in spec:
            config_args.append("--enable-wrapper-rpath")

            # Disable new dynamic tags in the wrapper (--disable-new-dtags)
            # In the newer versions this can be done with a configure option
            # (for older versions, we rely on filter_compiler_wrappers() and
            # filter_pc_files()):
            if spec.satisfies("@3.0.5:"):
                config_args.append("--disable-wrapper-runpath")
        else:
            config_args.append("--disable-wrapper-rpath")
            config_args.append("--disable-wrapper-runpath")

        config_args.extend(self.enable_or_disable("mpi-cxx", variant="cxx"))
        config_args.extend(self.enable_or_disable("cxx-exceptions", variant="cxx_exceptions"))

        config_args.extend(self.enable_or_disable("mpi-fortran", variant="fortran"))

        #
        # the Spack path padding feature causes issues with Open MPI's lex based parsing system
        # used by the compiler wrappers.  Crank up lex buffer to 1MB to handle this.
        # see https://spack.readthedocs.io/en/latest/binary_caches.html#relocation
        #

        if spec.satisfies("@5.0.0:"):
            config_args.append("CFLAGS=-DYY_BUF_SIZE=1048576")

        #
        # disable romio for 5.0.0 or newer if using Intel OneAPI owing to a problem
        # building ZE related components of the romio packaged with this release
        #

        #       if spec.satisfies("@5.0.0:") and spec.satisfies("%oneapi"):
        #           config_args.append("--disable-io-romio")

        # https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-c-compiler-release-notes.html:
        # Key Features in Intel C++ Compiler Classic 2021.7
        #
        # The Intel C++ Classic Compiler is deprecated and an additional
        # diagnostic message will be output with each invocation. This
        # diagnostic may impact expected output during compilation. For
        # example, using the compiler to produce preprocessed information
        # (icpc -E) will produce the additional deprecation diagnostic,
        # interfering with the expected preprocessed output.
        #
        # This output can be disabled by using -diag-disable=10441 on
        # Linux/macOS or /Qdiag-disable:10441 on Windows. You can add this
        # option on the command line, configuration file or option setting
        # environment variables.
        if spec.satisfies("%intel@2021.7.0:"):
            config_args.append("CPPFLAGS=-diag-disable=10441")

        config_args += self.enable_or_disable("debug")

        return config_args

    # For v4 and lower
    @run_after("install")
    def delete_mpirun_mpiexec(self):
        # The preferred way to run an application when Slurm is the
        # scheduler is to let Slurm manage process spawning via PMI.
        #
        # Deleting the links to orterun avoids users running their
        # applications via mpirun or mpiexec, and leaves srun as the
        # only sensible choice (orterun is still present, but normal
        # users don't know about that).
        if self.spec.satisfies("~legacylaunchers schedulers=slurm"):
            exe_list = [
                self.prefix.bin.mpirun,
                self.prefix.bin.mpiexec,
                self.prefix.bin.shmemrun,
                self.prefix.bin.oshrun,
            ]
            script_stub = join_path(os.path.dirname(__file__), "nolegacylaunchers.sh")
            for exe in exe_list:
                try:
                    os.remove(exe)
                except OSError:
                    tty.debug("File not present: " + exe)
                else:
                    copy(script_stub, exe)

    @run_after("install")
    def setup_install_tests(self):
        """
        Copy the example files after the package is installed to an
        install test subdirectory for use during `spack test run`.
        """
        cache_extra_test_sources(self, self.extra_install_tests)

    def run_installed_binary(self, bin, options, expected):
        """run and check outputs for the installed binary"""
        exe_path = join_path(self.prefix.bin, bin)
        if not os.path.exists(exe_path):
            raise SkipTest(f"{bin} is not installed")

        exe = which(exe_path, required=True)
        out = exe(*options, output=str.split, error=str.split)
        check_outputs(expected, out)

    def test_mpirun(self):
        """test installed mpirun"""
        options = ["-n", "1", "ls", ".."]
        self.run_installed_binary("mpirun", options, [f"openmpi-{self.spec.version}"])

    def test_opmpi_info(self):
        """test installed ompi_info"""
        self.run_installed_binary("ompi_info", [], [f"Ident string: {self.spec.version}", "MCA"])

    def test_version(self):
        """check versions of installed software"""
        comp_vers = str(self.spec.compiler.version)
        spec_vers = str(self.spec.version)
        checks = {
            # Binaries available in at least versions 2.0.0 through 4.0.3
            "mpiCC": comp_vers,
            "mpic++": comp_vers,
            "mpicc": comp_vers,
            "mpicxx": comp_vers,
            "mpiexec": spec_vers,
            "mpif77": comp_vers,
            "mpif90": comp_vers,
            "mpifort": comp_vers,
            "mpirun": spec_vers,
            "ompi_info": spec_vers,
            "ortecc": comp_vers,
            "orterun": spec_vers,
        }

        for bin in checks:
            expected = checks[bin]
            with test_part(
                self, f"test_version_{bin}", purpose=f"ensure version of {bin} is {expected}"
            ):
                self.run_installed_binary(bin, ["--version"], [expected])

    @property
    def _cached_tests_work_dir(self):
        """The working directory for cached test sources."""
        return join_path(self.test_suite.current_test_cache_dir, self.extra_install_tests)

    def test_example(self):
        """Run test examples copied from source at build-time."""
        # Build the copied, cached test examples
        with test_part(
            self,
            "test_example_make",
            purpose="test: building cached test examples",
            work_dir=self._cached_tests_work_dir,
        ):
            make("all")

        # Run basic examples with known, simple-to-verify results
        hello_world = ["Hello, world", "I am", "0 of", "1"]
        ring_out = ["1 processes in ring", "0 exiting"]

        checks = {
            "hello_c": hello_world,
            "hello_cxx": hello_world,
            "hello_mpifh": hello_world,
            "hello_usempi": hello_world,
            "hello_usempif08": hello_world,
            "ring_c": ring_out,
            "ring_cxx": ring_out,
            "ring_mpifh": ring_out,
            "ring_usempi": ring_out,
            "ring_usempif08": ring_out,
        }

        for binary in checks:
            expected = checks[binary]
            with test_part(
                self,
                f"test_example_{binary}",
                purpose="run and check output",
                work_dir=self._cached_tests_work_dir,
            ):
                exe = which(binary)
                if not exe:
                    raise SkipTest(f"{binary} is missing")

                out = exe(output=str.split, error=str.split)
                check_outputs(expected, out)


def get_spack_compiler_spec(compiler):
    spack_compilers = find_compilers([os.path.dirname(compiler)])
    actual_compiler = None
    # check if the compiler actually matches the one we want
    for spack_compiler in spack_compilers:
        if spack_compiler.cc and spack_compiler.cc == compiler:
            actual_compiler = spack_compiler
            break
    return actual_compiler.spec if actual_compiler else None


def is_enabled(text):
    if text in set(["t", "true", "enabled", "yes", "1"]):
        return True
    return False
