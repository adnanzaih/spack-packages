# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from typing import List, Optional, Tuple

from spack.package import ClassProperty, classproperty, depends_on, extends, mkdirp

from .generic import GenericBuilder, Package


class RBuilder(GenericBuilder):
    """The R builder provides a single phase that can be overridden:

        1. :py:meth:`~.RBuilder.install`

    It has sensible defaults, and for many packages the only thing
    necessary will be to add dependencies.
    """

    #: Names associated with package methods in the old build-system format
    package_methods: Tuple[str, ...] = (
        "configure_args",
        "configure_vars",
    ) + GenericBuilder.package_methods

    def configure_args(self):
        """Arguments to pass to install via ``--configure-args``."""
        return []

    def configure_vars(self):
        """Arguments to pass to install via ``--configure-vars``."""
        return []

    def install(self, pkg, spec, prefix):
        """Installs an R package."""
        mkdirp(pkg.module.r_lib_dir)

        config_args = self.configure_args()
        config_vars = self.configure_vars()

        args = ["--vanilla", "CMD", "INSTALL"]

        if config_args:
            args.append(f"--configure-args={' '.join(config_args)}")

        if config_vars:
            args.append(f"--configure-vars={' '.join(config_vars)}")

        args.extend([f"--library={pkg.module.r_lib_dir}", self.stage.source_path])

        pkg.module.R(*args)


def _homepage(cls: "RPackage") -> Optional[str]:
    if cls.cran:
        return f"https://cloud.r-project.org/package={cls.cran}"
    elif cls.bioc:
        return f"https://bioconductor.org/packages/{cls.bioc}"
    return None


def _urls(cls: "RPackage") -> List[str]:
    if cls.cran:
        return [
            f"https://cran.r-project.org/src/contrib/{cls.cran}_{str(list(cls.versions)[0])}.tar.gz",
            f"https://cran.r-project.org/src/contrib/Archive/{cls.cran}/{cls.cran}_{str(list(cls.versions)[0])}.tar.gz",
        ]
    return []


def _list_url(cls: "RPackage") -> Optional[str]:
    if cls.cran:
        return f"https://cran.r-project.org/src/contrib/Archive/{cls.cran}/"
    return None


def _git(cls: "RPackage") -> Optional[str]:
    if cls.bioc:
        return f"https://git.bioconductor.org/packages/{cls.bioc}"
    return None


class RPackage(Package):
    """Specialized class for packages that are built using R.

    For more information on the R build system, see:
    https://stat.ethz.ch/R-manual/R-devel/library/utils/html/INSTALL.html
    """

    # package attributes that can be expanded to set the homepage, url,
    # list_url, and git values
    # For CRAN packages
    cran: Optional[str] = None

    # For Bioconductor packages
    bioc: Optional[str] = None

    GenericBuilder = RBuilder

    #: This attribute is used in UI queries that need to know the build
    #: system base class
    build_system_class = "RPackage"

    extends("r")

    # needed for packages that need compiling
    depends_on("gmake", type="build", when="%c")
    depends_on("gmake", type="build", when="%cxx")
    depends_on("gmake", type="build", when="%fortran")

    homepage: ClassProperty[Optional[str]] = classproperty(_homepage)
    urls: ClassProperty[List[str]] = classproperty(_urls)
    list_url: ClassProperty[Optional[str]] = classproperty(_list_url)
    git: ClassProperty[Optional[str]] = classproperty(_git)


class RCollectiveBuilder(RBuilder):
    """Builder for RCollectivePackage.

    Installs the primary CRAN package and all packages listed in
    ``cran_packages`` via ``install.packages()`` from the configured mirror.
    Using ``install.packages()`` (rather than ``R CMD INSTALL``) lets CRAN
    resolve and fetch R-level dependencies automatically, which is necessary
    when those dependencies are not individually packaged in Spack.

    Each ``install.packages()`` invocation inherits Spack's normal dependency
    build environment, so pkg-config, CMake, R extension paths, and dependency
    executables are resolved the same way they are for regular RPackage
    builds.  After each install the package is verified with
    ``requireNamespace()``; a failed install causes an explicit ``stop()`` so
    Spack receives a non-zero exit code.
    """

    def _r_string(self, value):
        """Return a quoted R string literal."""
        import json

        return json.dumps(str(value))

    def install(self, pkg, spec, prefix):
        mkdirp(pkg.module.r_lib_dir)

        r = pkg.module.R
        r_lib_dir = pkg.module.r_lib_dir

        all_packages = ([pkg.cran] if pkg.cran else []) + list(pkg.cran_packages)

        for cran_pkg in all_packages:
            cran_pkg_expr = self._r_string(cran_pkg)
            r_lib_dir_expr = self._r_string(r_lib_dir)
            cran_mirror_expr = self._r_string(pkg.cran_mirror)
            failed_msg_expr = self._r_string(
                "install.packages failed for {0}".format(cran_pkg)
            )

            r(
                "--vanilla",
                "-e",
                (
                    "install.packages({0}, lib={1}, repos={2}, dependencies=TRUE); ".format(
                        cran_pkg_expr, r_lib_dir_expr, cran_mirror_expr
                    )
                    + "if (!requireNamespace({0}, lib.loc={1}, quietly=TRUE)) ".format(
                        cran_pkg_expr, r_lib_dir_expr
                    )
                    + "stop({0})".format(failed_msg_expr)
                ),
                extra_env={"R_LIBS_USER": ""},
            )


class RCollectivePackage(RPackage):
    """Specialized class for a primary R package that also installs a
    collection of additional CRAN packages into the same R library prefix.

    Subclasses must set :attr:`cran` (the primary package) and may populate
    :attr:`cran_packages` with the names of extra CRAN packages to install.

    Example::

        class Rtidyverse(RCollectivePackage):
            cran = "tidyverse"
            cran_packages = ["Rcpp"]
    """

    #: Additional CRAN package names to install alongside the primary package.
    cran_packages: List[str] = []

    #: CRAN mirror used for the additional ``install.packages()`` calls.
    cran_mirror: str = "https://cloud.r-project.org"

    GenericBuilder = RCollectiveBuilder
    build_system_class = "RCollectivePackage"
