# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import (
    CMakeBuilder as SpackCMakeBuilder,
    CMakePackage,
    generator,
)

from spack.package import *


class Gdal(CMakePackage):
    """GDAL: Geospatial Data Abstraction Library."""

    homepage = "https://www.gdal.org/"
    url = "https://download.osgeo.org/gdal/3.13.1/gdal-3.13.1.tar.xz"
    list_url = "https://download.osgeo.org/gdal/"
    list_depth = 1

    license("MIT")
    maintainers("adamjstewart")

    version("3.13.1", sha256="7398fb132753140740fac4f099f0dbe49d1ad074c4162290c308e067c46b7f92")
    version("3.13.0", sha256="1c537dd2f4d66f05534ae419bc2af495c2204ce13bb266c8cbd867dd6705f0c7")
    version("3.12.4", sha256="813094498c17522ac42821a5ea1ea783d8326c0adf286cce86a949038bd09198")
    version("3.12.3", sha256="398a5a32ee6e75040598a7f8e895126a8225118317f272d715867c844f932848")
    version("3.12.2", sha256="21c5e0f91974383b4c5692b7103650f176f2f54f1b0d449787f444b89881e9b4")
    version("3.12.1", sha256="2a4fd3170ff81def93db60f7f61f2842a2ae7ad0335e4ed4ba305252f05835de")
    version("3.12.0", sha256="428c19fff818bbb4136766cfee86fae2eebd3620806aa40af21844f4f0b2dbcf")
    version("3.11.5", sha256="79f66756f1c843b5ee52c8482d4f6bd2a8b7706d6161cc11f0b27c83d638796a")
    version("3.11.4", sha256="6401eba2bb63f5ef7a08d2157f240194f06d508d096898a705637aeea9d3bbe8")
    version("3.11.3", sha256="ba0807729fa681eed55bb6d5588bb9e4bde2b691c46e8d6d375ff5eaf789b16a")
    version("3.11.2", sha256="bda41b7cf12f05995a00106ae0db1b784d9c307953d81c76d351c7dbeb121aeb")
    version("3.11.1", sha256="21341b39a960295bd3194bcc5f119f773229b4701cd752499fbd850f3cc160fd")
    version("3.11.0", sha256="ba1a17a74428bfd5c789ce293f59b6a3d8bfabab747431c33331ac0ac579ea71")

    patch("gdal-3.12-gcc8-complete-rat.patch", when="@3.12: %gcc@:8")
    
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.16:", type="build")
    depends_on("geos")
    depends_on("hdf5")
    depends_on("proj")
    depends_on("netcdf-c")
    depends_on("libtiff")
    depends_on("sqlite")

    executables = ["^gdal-config$"]

    @classmethod
    def determine_version(cls, exe):
        return Executable(exe)("--version", output=str, error=str).rstrip()


class CMakeBuilder(SpackCMakeBuilder):
    def _library(self, spec_name, lib_name, shared=True):
        dep = self.spec[spec_name]
        libs = find_libraries(lib_name, root=dep.prefix, shared=shared, recursive=True)
        if libs:
            return libs[0]

        msg = "Unable to locate {0} library for {1} in {2}"
        raise NoLibrariesError(msg.format(lib_name, dep.name, dep.prefix))

    def cmake_args(self):
        geos = self.spec["geos"]
        hdf5 = self.spec["hdf5"]
        proj = self.spec["proj"]
        netcdf_c = self.spec["netcdf-c"]
        libtiff = self.spec["libtiff"]
        sqlite = self.spec["sqlite"]

        prefix_path = ":".join(
            [
                str(libtiff.prefix),
                str(geos.prefix),
                str(hdf5.prefix),
                str(proj.prefix),
                str(netcdf_c.prefix),
            ]
        )

        return [
            self.define("CMAKE_INSTALL_PREFIX", self.prefix),
            self.define("CMAKE_BUILD_TYPE", "Release"),
            self.define("BUILD_SHARED_LIBS", True),
            self.define("GDAL_USE_ARCHIVE", False),
            self.define("CMAKE_PREFIX_PATH", prefix_path),
            self.define("GEOS_INCLUDE_DIR", geos.prefix.include),
            self.define("GEOS_LIBRARY", self._library("geos", "libgeos_c")),
            self.define("HDF5_INCLUDE_DIR", hdf5.prefix.include),
            self.define("PROJ_INCLUDE_DIR", proj.prefix.include),
            self.define("PROJ_LIBRARY_RELEASE", self._library("proj", "libproj")),
            self.define("NETCDF_INCLUDE_DIR", netcdf_c.prefix.include),
            self.define("NETCDF_LIBRARY", self._library("netcdf-c", "libnetcdf")),
            self.define("TIFF_INCLUDE_DIR", libtiff.prefix.include),
            self.define("TIFF_LIBRARY_RELEASE", self._library("libtiff", "libtiff")),
            self.define("SQLite3_INCLUDE_DIR", sqlite.prefix.include),
            self.define("SQLite3_LIBRARY", self._library("sqlite", "libsqlite3", shared=False)),
            self.define("GDAL_USE_TIFF_INTERNAL", False),
            self.define("GDAL_USE_GEOS", True),
            self.define("GDAL_USE_HDF5", True),
            self.define("GDAL_USE_NETCDF", True),
            self.define("GDAL_USE_POPPLER", False),
        ]
