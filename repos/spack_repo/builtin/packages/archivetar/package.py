import os

from spack_repo.builtin.build_systems.generic import Package

from spack.package import *


class Archivetar(Package):
    """ARC archivetar tool bundled with its mpiFileUtils stack."""

    homepage = "https://github.com/brockpalen/archivetar"
    git = "https://github.com/brockpalen/archivetar.git"

    license("MIT")

    version("0.18.2", tag="v0.18.2", commit="13af5a1591c36548c00ff6519e8b9f2f73da8a23")

    resource(
        name="libcircle",
        url="https://github.com/hpc/libcircle/releases/download/v0.3/libcircle-0.3.0.tar.gz",
        sha256="5ce38eb5b3c2b394bca1316310758f276c893dd3f4c15d7bc14ea05d3110ce58",
        destination="deps",
        placement="libcircle-0.3.0",
    )
    resource(
        name="lwgrp",
        url="https://github.com/llnl/lwgrp/releases/download/v1.0.2/lwgrp-1.0.2.tar.gz",
        sha256="c9d4233946e40f01efd0b4644fd9224becec51b9b5f8cbf45f5bac3129b5b536",
        destination="deps",
        placement="lwgrp-1.0.2",
    )
    resource(
        name="dtcmp",
        url="https://github.com/llnl/dtcmp/releases/download/v1.1.0/dtcmp-1.1.0.tar.gz",
        sha256="fd2c4485eee560a029f62c8f227df4acdb1edc9340907f4ae2dbee59f05f057d",
        destination="deps",
        placement="dtcmp-1.1.0",
    )
    resource(
        name="mpifileutils",
        git="https://github.com/brockpalen/mpifileutils.git",
        branch="master",
    )

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("mpi")
    depends_on("cmake@3.22:", type="build")
    depends_on("gmake", type="build")
    depends_on("pkgconfig", type="build")
    depends_on("python@3.10:3.10", type=("build", "run"))

    # mpiFileUtils still finds these through CMake; keeping them as ordinary
    # dependencies makes the bundled build less dependent on host OS headers.
    depends_on("bzip2")
    depends_on("libarchive")
    depends_on("libcap", when="platform=linux")
    depends_on("openssl")

    app_source_entries = (
        "GlobusTransfer",
        "SuperTar",
        "archivetar",
        "bin",
        "mpiFileUtils",
        "LICENSE",
        "README.md",
        "USAGE.md",
        "INSTALL.md",
        "Pipfile",
        "Pipfile.lock",
        "pyproject.toml",
        "setup.py",
    )

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        spec = self.spec
        env.set("CC", spec["mpi"].mpicc)
        env.set("CXX", spec["mpi"].mpicxx)
        env.set("MPICC", spec["mpi"].mpicc)
        env.set("MPICXX", spec["mpi"].mpicxx)
        env.set("PIP_DISABLE_PIP_VERSION_CHECK", "1")
        env.set("PIP_NO_CACHE_DIR", "1")
        env.set("PIPENV_NOSPIN", "1")

    def install(self, spec, prefix):
        mkdirp(prefix.install)
        self._install_application_source(prefix)
        self._install_bundled_autotools(prefix)
        self._install_bundled_mpifileutils(spec, prefix)
        self._install_frozen_python_tools(spec, prefix)
        self._link_commands(prefix)

    def _install_bundled_autotools(self, prefix):
        deps = join_path(self.stage.source_path, "deps")
        self._configure_make_install(join_path(deps, "libcircle-0.3.0"), prefix)
        self._configure_make_install(join_path(deps, "lwgrp-1.0.2"), prefix)
        self._configure_make_install(
            join_path(deps, "dtcmp-1.1.0"),
            prefix,
            "--with-lwgrp={0}".format(prefix.install),
        )

    def _configure_make_install(self, source_dir, prefix, *extra_args):
        with working_dir(source_dir):
            configure = Executable("./configure")
            configure("--prefix={0}".format(prefix.install), *extra_args)
            make()
            make("install")

    def _install_bundled_mpifileutils(self, spec, prefix):
        source_dir = join_path(self.stage.source_path, "mpifileutils")
        with working_dir("spack-build-mpifileutils", create=True):
            cmake(
                source_dir,
                "-DCMAKE_INSTALL_PREFIX={0}".format(prefix.install),
                "-DCMAKE_C_COMPILER={0}".format(spec["mpi"].mpicc),
                "-DCMAKE_CXX_COMPILER={0}".format(spec["mpi"].mpicxx),
                "-DWITH_DTCMP_PREFIX={0}".format(prefix.install),
                "-DWITH_LibCircle_PREFIX={0}".format(prefix.install),
            )
            make()
            make("install")

    def _install_frozen_python_tools(self, spec, prefix):
        venv = join_path(self.stage.path, "archivetar-pyinstaller-venv")
        spec["python"].command("-m", "venv", venv)

        python = Executable(join_path(venv, "bin", "python"))
        pipenv = Executable(join_path(venv, "bin", "pipenv"))
        pyinstaller = Executable(join_path(venv, "bin", "pyinstaller"))

        python("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
        python("-m", "pip", "install", "pipenv")

        with working_dir(self.stage.source_path):
            try:
                pipenv("install", "--dev", "--system", "--deploy")
            except ProcessError:
                tty.warn("pipenv locked install failed; falling back to direct pip install")
                python(
                    "-m",
                    "pip",
                    "install",
                    "pyinstaller",
                    "humanfriendly",
                    "python-dotenv",
                    "natsort",
                    "globus-sdk",
                    "environs",
                    ".",
                )

            mkdirp(prefix.archivetar.dist)
            for command in sorted(os.listdir("bin")):
                script = join_path("bin", command)
                if not os.path.isfile(script):
                    continue

                pyinstaller(
                    "--collect-all",
                    "globus_sdk",
                    "--onefile",
                    "-p",
                    self.stage.source_path,
                    "--distpath",
                    prefix.archivetar.dist,
                    "--workpath",
                    join_path(self.stage.path, "pyinstaller-work", command),
                    "--specpath",
                    join_path(self.stage.path, "pyinstaller-specs"),
                    script,
                )

    def _install_application_source(self, prefix):
        mkdirp(prefix.archivetar.src)
        for entry in self.app_source_entries:
            src = join_path(self.stage.source_path, entry)
            if os.path.isdir(src):
                install_tree(src, join_path(prefix.archivetar.src, entry))
            elif os.path.isfile(src):
                install(src, prefix.archivetar.src)

    def _link_commands(self, prefix):
        mkdirp(prefix.bin)
        for command in os.listdir(prefix.archivetar.dist):
            src = join_path(prefix.archivetar.dist, command)
            dst = join_path(prefix.bin, command)
            if os.path.isfile(src) and not os.path.exists(dst):
                symlink(src, dst)

    def setup_run_environment(self, env: EnvironmentModifications) -> None:
        env.set("AT_MPIFILEUTILS", self.prefix.install)
        env.set("AT_MPIRUN", self.spec["mpi"].prefix.bin.mpirun)
        env.prepend_path("PATH", self.prefix.archivetar.dist)
