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

    Installs CRAN packages via ``install.packages()`` and Bioconductor packages
    via ``BiocManager::install()``.  Installing from the repositories (rather
    than using ``R CMD INSTALL``) lets R resolve and fetch R-level dependencies
    automatically, which is necessary when those dependencies are not
    individually packaged in Spack.

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

    def _verify(self, package, r_lib_dir, expected_version=None):
        package_expr = self._r_string(package)
        library_expr = self._r_string(r_lib_dir)
        failed_expr = self._r_string("installation failed for {0}".format(package))
        expression = (
            "if (!requireNamespace({0}, lib.loc={1}, quietly=TRUE)) stop({2})".format(
                package_expr, library_expr, failed_expr
            )
        )
        if expected_version is not None:
            version_expr = self._r_string(expected_version)
            mismatch_expr = self._r_string(
                "installed {0} version does not match Spack version {1}".format(
                    package, expected_version
                )
            )
            expression += (
                "; if (as.character(packageVersion({0}, lib.loc={1})) != {2}) "
                "stop({3})"
            ).format(package_expr, library_expr, version_expr, mismatch_expr)
        return expression

    def install(self, pkg, spec, prefix):
        mkdirp(pkg.module.r_lib_dir)

        r = pkg.module.R
        r_lib_dir = pkg.module.r_lib_dir

        all_cran_packages = ([pkg.cran] if pkg.cran else []) + list(pkg.cran_packages)
        all_bioc_packages = ([pkg.bioc] if pkg.bioc else []) + list(pkg.bioc_packages)

        for cran_pkg in all_cran_packages:
            cran_pkg_expr = self._r_string(cran_pkg)
            r_lib_dir_expr = self._r_string(r_lib_dir)
            cran_mirror_expr = self._r_string(pkg.cran_mirror)
            expected_version = str(pkg.version) if cran_pkg == pkg.cran else None

            r(
                "--vanilla",
                "-e",
                (
                    "install.packages({0}, lib={1}, repos={2}, dependencies=TRUE); ".format(
                        cran_pkg_expr, r_lib_dir_expr, cran_mirror_expr
                    )
                    + self._verify(cran_pkg, r_lib_dir, expected_version)
                ),
                extra_env={"R_LIBS_USER": ""},
            )

        if all_bioc_packages:
            r_lib_dir_expr = self._r_string(r_lib_dir)
            cran_mirror_expr = self._r_string(pkg.cran_mirror)
            r(
                "--vanilla",
                "-e",
                (
                    ".libPaths(c({0}, .libPaths())); ".format(r_lib_dir_expr)
                    + "if (!requireNamespace(\"BiocManager\", quietly=TRUE)) "
                    + "install.packages(\"BiocManager\", lib={0}, repos={1})".format(
                        r_lib_dir_expr, cran_mirror_expr
                    )
                ),
                extra_env={"R_LIBS_USER": ""},
            )

        for bioc_pkg in all_bioc_packages:
            bioc_pkg_expr = self._r_string(bioc_pkg)
            r_lib_dir_expr = self._r_string(r_lib_dir)
            expected_version = str(pkg.version) if bioc_pkg == pkg.bioc else None
            version_arg = (
                ", version={0}".format(self._r_string(pkg.bioc_version))
                if pkg.bioc_version
                else ""
            )
            r(
                "--vanilla",
                "-e",
                (
                    ".libPaths(c({0}, .libPaths())); ".format(r_lib_dir_expr)
                    + "BiocManager::install({0}, lib={1}, dependencies=TRUE, "
                    "ask=FALSE, update=FALSE{2}); ".format(
                        bioc_pkg_expr, r_lib_dir_expr, version_arg
                    )
                    + self._verify(bioc_pkg, r_lib_dir, expected_version)
                ),
                extra_env={"R_LIBS_USER": ""},
            )


class RCollectivePackage(RPackage):
    """Specialized class for a primary R package that also installs a
    collection of additional R packages into the same R library prefix.

    Subclasses set either :attr:`cran` or :attr:`bioc` for the primary package
    and may populate :attr:`cran_packages` and :attr:`bioc_packages` with
    additional packages to install.

    Example::

        class Rtidyverse(RCollectivePackage):
            cran = "tidyverse"
            cran_packages = ["Rcpp"]
    """

    #: Additional CRAN package names to install alongside the primary package.
    cran_packages: List[str] = []

    #: Additional Bioconductor package names to install alongside the primary package.
    bioc_packages: List[str] = []

    #: CRAN mirror used for the additional ``install.packages()`` calls.
    cran_mirror: str = "https://cloud.r-project.org"

    #: Optional Bioconductor release passed to ``BiocManager::install``.
    bioc_version: Optional[str] = None

    GenericBuilder = RCollectiveBuilder
    build_system_class = "RCollectivePackage"
