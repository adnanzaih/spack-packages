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

    version("3.13.3", sha256="a3348c2102dd91962290007d7c293b467bb1b0cd89f086f24bb97b9b653a9804")
    version("3.13.2", sha256="0200b7878d837a7f475ff4070121d0e601f8ef801c2fd83a64294c544f609211")
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
    version("3.6.3", sha256="3cccbed883b1fb99b913966aa3a650ad930e7c3afc714f5823f9754176ee49ea")
    version("3.5.3", sha256="d32223ddf145aafbbaec5ccfa5dbc164147fb3348a3413057f9b1600bb5b3890")

    conflicts("@3.11:", when="%gcc@:9", msg="version 3.11+ requires GCC > 10")

    patch("gdal-3.12-gcc8-complete-rat.patch", when="@3.12: %gcc@:8")
    patch("gdal-3.5.3-netcdf-fillvalue.patch", when="@3.5.3")
    patch("gdal-3.5.3-hdf5-1.14-vfl.patch", when="@3.5.3 ^hdf5@1.14:")

    variant(
        "armadillo",
        default=False,
        description="Speed up computations related to the Thin Plate Spline transformer",
    )
    # cmake configure fails if arrow~filesystem is found when variant ~arrow
    # https://github.com/OSGeo/gdal/issues/12327
    variant(
        "arrow", default=True, when="build_system=cmake", description="Required for Arrow driver"
    )
    variant("avif", default=True, when="@3.10:", description="Required for AVIF driver")
    variant("blosc", default=True, description="Required for Zarr driver")
    variant("curl", default=True, description="Required for network access")
    variant("deflate", default=True, description="Required for Deflate compression")
    variant("freexl", default=True, description="Required for XLS driver")
    variant("geos", default=True, description="Required for geometry processing operations in OGR")
    variant("gif", default=True, description="Required for GIF driver")
    variant("heif", default=True, description="Required for HEIF driver")
    variant("hdf5", default=True, description="Required for HDF5, BAG, and KEA drivers")
    variant("jpeg", default=True, description="Required for JPEG driver")
    variant("jxl", default=True, description="Required for JPEGXL driver")
    variant("libkml", default=True, description="Required for LIBKML driver")
    variant("liblzma", default=True, description="Required for Zarr driver")
    variant(
        "libxml2", default=True, description="Required for XML validation in many OGR drivers"
    )
    variant("lz4", default=True, description="Required for Zarr driver")
    variant(
        "muparser",
        default=True,
        when="@3.11:",
        description="Required for nominal C++ VRT expressions",
    )
    variant("mysql", default=True, description="Required for MySQL driver")
    variant("netcdf", default=True, description="Required for NetCDF driver")
    variant("odbc", default=True, description="Required for many OGR drivers")
    variant(
        "opencl",
        default=True,
        description="Required to accelerate warping computations",
    )
    variant("openjpeg", default=True, description="Required for JP2OpenJPEG driver")
    variant("oracle", default=False, description="Required for OCI and GeoRaster drivers")
    variant(
        "parquet",
        default=True,
        when="build_system=cmake",
        description="Required for Parquet driver",
    )
    variant(
        "pcre2", default=True, description="Required for REGEXP operator in drivers using SQLite3"
    )
    variant("png", default=True, description="Required for PNG driver")
    variant("poppler", default=True, description="Possible backend for PDF driver")
    variant(
        "postgresql",
        default=False,
        description="Required for PostgreSQL and PostGISRaster drivers",
    )
    variant(
        "qhull",
        default=True,
        description="Used for linear interpolation of gdal_grid",
    )
    variant("sfcgal", default=True, description="Provides 3D geometry operations")
    variant("spatialite", default=True, description="Required for SQLite and GPKG drivers")
    variant("sqlite3", default=True, description="Required for SQLite and GPKG drivers")
    variant("tiledb", default=False, description="Required for TileDB driver")
    variant("webp", default=True, description="Required for WEBP driver")
    variant("zstd", default=True, description="Required for Zarr driver")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.16:", type="build")
    depends_on("proj@6:")
    depends_on("libtiff@4.1:")
    depends_on("libgeotiff@1.5:")
    depends_on("json-c")

    # Optional dependencies
    depends_on("armadillo", when="+armadillo")
    depends_on("blas", when="+armadillo")
    depends_on("lapack", when="+armadillo")
    depends_on("arrow+filesystem", when="+arrow")
    depends_on("libavif", when="+avif")
    depends_on("c-blosc", when="+blosc")
    depends_on("curl@7.68:")
    depends_on('freexl', when='+freexl')
    depends_on("geos")
    depends_on("giflib", when="+gif")
    depends_on("libheif@1.1:", when="+heif")
    depends_on("hdf", when="+hdf4")
    depends_on("hdf5", when="+hdf5")
    depends_on("jpeg", when="+jpeg")
    depends_on("libjxl", when="+jxl")
    depends_on("libdeflate", when="+deflate")
    depends_on("libkml@1.3:", when="+libkml")
    depends_on("libxml2", when="+libxml2")
    depends_on("lz4", when="+lz4")
    depends_on("muparser", when="+muparser")
    depends_on("netcdf-c", when="+netcdf")
    depends_on("unixodbc", when="+odbc")
    depends_on("opencl", when="+opencl")
    depends_on("openjpeg@2.3.1:", when="+openjpeg")
    depends_on("arrow+parquet+filesystem", when="+parquet")
    depends_on("pcre2", when="+pcre2")
    depends_on("pcre", when="+pcre2")
    depends_on("libpng@1.6:", when="@3.9:+png")
    with when("+poppler"):
        depends_on("poppler@0.24:")
        depends_on("poppler@:26.05", when="@:3.13.0")
        depends_on("poppler@:26.04", when="@:3.12.4")
        depends_on("poppler@:26.03", when="@:3.12.3")
        depends_on("poppler@:26.01", when="@:3.12.2")
        depends_on("poppler@:26.00", when="@:3.12.1")
        depends_on("poppler@:25.09", when="@:3.11.4")
    depends_on("postgresql", when="+postgresql")
    depends_on("qhull@2015:", when="@3.5:+qhull")
    depends_on("sfcgal", when="+sfcgal")
    depends_on("libspatialite@4.1.2:", when="+spatialite")
    depends_on("sqlite@3.31:", when="+sqlite3")
    depends_on("libwebp", when="+webp")
    depends_on("xz", when="+liblzma")
    depends_on("zstd", when="+zstd")


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

        args = [
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
            self.define("GDAL_USE_INTERNAL_LIBS", False),
            self.define("GDAL_USE_GEOS", True),
            self.define("GDAL_USE_HDF5", True),
            self.define("GDAL_USE_NETCDF", True),
            # Required dependencies
            self.define("GDAL_USE_GEOTIFF", True),
            self.define("GDAL_USE_JSONC", True),
            self.define("GDAL_USE_TIFF", True),
            self.define("GDAL_USE_ZLIB", True),
            self.define("GDAL_USE_ICONV", True),
            # zlib-ng + deflate64 doesn't compile (heavily relies on zlib)
            # but since zlib-ng is faster than zlib, it deflate shouldn't
            # be necessary.
            self.define("ENABLE_DEFLATE64", "zlib-ng" not in self.spec),
            # Optional dependencies
            self.define_from_variant("GDAL_USE_ARMADILLO", "armadillo"),
            self.define_from_variant("GDAL_USE_ARROW", "arrow"),
            self.define_from_variant("GDAL_USE_AVIF", "avif"),
            self.define_from_variant("GDAL_USE_BLOSC", "blosc"),
            self.define_from_variant("GDAL_USE_CURL", "curl"),
            self.define_from_variant("GDAL_USE_DEFLATE", "deflate"),
            self.define_from_variant("GDAL_USE_FREEXL", "freexl"),
            self.define_from_variant("GDAL_USE_GEOS", "geos"),
            self.define_from_variant("GDAL_USE_GIF", "gif"),
            self.define_from_variant("GDAL_USE_HEIF", "heif"),
            self.define_from_variant("GDAL_USE_HDF4", "hdf4"),
            self.define_from_variant("GDAL_USE_HDF5", "hdf5"),
            self.define_from_variant("GDAL_USE_JPEG", "jpeg"),
            self.define_from_variant("GDAL_USE_JXL", "jxl"),
            self.define_from_variant("GDAL_USE_LIBKML", "libkml"),
            self.define_from_variant("GDAL_USE_LIBLZMA", "liblzma"),
            self.define_from_variant("GDAL_USE_LIBXML2", "libxml2"),
            self.define_from_variant("GDAL_USE_LZ4", "lz4"),
            self.define_from_variant("GDAL_USE_MUPARSER", "muparser"),
            self.define_from_variant("GDAL_USE_MYSQL", "mysql"),
            self.define_from_variant("GDAL_USE_NETCDF", "netcdf"),
            self.define_from_variant("GDAL_USE_ODBC", "odbc"),
            self.define_from_variant("GDAL_USE_OPENCL", "opencl"),
            self.define_from_variant("GDAL_USE_OPENJPEG", "openjpeg"),
            self.define_from_variant("GDAL_USE_PARQUET", "parquet"),
            self.define_from_variant("GDAL_USE_PCRE2", "pcre2"),
            self.define_from_variant("GDAL_USE_PNG", "png"),
            self.define_from_variant("GDAL_USE_POPPLER", "poppler"),
            self.define_from_variant("GDAL_USE_POSTGRESQL", "postgresql"),
            self.define_from_variant("GDAL_USE_QHULL", "qhull"),
            self.define_from_variant("GDAL_USE_RDB", "rdb"),
            self.define_from_variant("GDAL_USE_SFCGAL", "sfcgal"),
            self.define_from_variant("GDAL_USE_SPATIALITE", "spatialite"),
            self.define_from_variant("GDAL_USE_SQLITE3", "sqlite3"),
            self.define_from_variant("GDAL_USE_WEBP", "webp"),
            self.define_from_variant("GDAL_USE_ZSTD", "zstd"),
        ]

        if self.spec.satisfies("%clang") or self.spec.satisfies("%apple-clang"):
            args.append(self.define("CMAKE_CXX_STANDARD", 17))

        return args
