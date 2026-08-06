# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.build_systems.generic import Package

from spack.package import *


class Qupath(Package):
    """Open-source bioimage analysis software for digital pathology and
    whole-slide image analysis."""

    homepage = "https://qupath.github.io/"
    url = "https://github.com/qupath/qupath/archive/refs/tags/v0.7.0.tar.gz"
    git = "https://github.com/qupath/qupath.git"

    license("GPL-3.0-only")

    version("main", branch="main")
    version(
        "0.7.0",
        sha256="5cd23875aa49a90d652726ddca0d06338c67084a005e453c39f0d7125623448e",
    )

    djl_extension_versions = {"0.7.0": "0.4.2"}
    pytorch_flavors = {"0.7.0": "cu128"}

    variant("djl", default=True, description="Bundle the QuPath Deep Java Library extension")
    variant("fiji", default=False, description="Build QuPath with Fiji dependencies")
    variant("javadocs", default=False, description="Build and package bundled Javadocs")
    variant("pytorch", default=True, description="Bundle DJL PyTorch GPU runtime support")
    variant(
        "torch_version",
        default="2.7.1",
        values=str,
        multi=False,
        when="+pytorch",
        description="PyTorch wheel version to bundle with +pytorch",
    )

    patch(
        "extensions-expose.patch",
        sha256="072a6ed94bae33ddfb512ce330c5d50303a45d0f04913ec67dfc87fca7e9aa77",
    )

    depends_on("java@21:", type="build")
    depends_on("python@3.13+ssl", type=("build", "run"), when="+pytorch")
    depends_on("py-pip", type="build", when="+pytorch")

    conflicts("+pytorch", when="~djl", msg="+pytorch requires +djl")
    conflicts("platform=darwin", msg="This recipe currently installs the Linux jpackage image")
    conflicts("platform=windows", msg="This recipe currently installs the Linux jpackage image")

    executables = ["^QuPath$"]
    sanity_check_is_file = [join_path("bin", "QuPath")]

    def setup_build_environment(self, env):
        java_home = self.spec["java"].package.home

        env.set("JAVA_HOME", java_home)
        env.prepend_path("PATH", join_path(java_home, "bin"))

        env.set("GRADLE_USER_HOME", join_path(self.stage.path, "gradle"))
        env.set("GRADLE_OPTS", "-Dorg.gradle.daemon=false")
        env.set("PYTHONNOUSERSITE", "1")

    def url_for_version(self, version):
        return "https://github.com/qupath/qupath/archive/refs/tags/v{0}.tar.gz".format(version)

    def install(self, spec, prefix):
        java_home = spec["java"].package.home
        gradlew = Executable("./gradlew")

        self.configure_djl_extension()

        args = [
            "--no-daemon",
            "clean",
            "jpackage",
            "-Ppackage=image",
            "-Dorg.gradle.java.home={0}".format(java_home),
            "-Dbadass.runtime.java.home={0}".format(java_home),
            "-Dbadass.runtime.jpackage.home={0}".format(java_home),
        ]

        if "+fiji" in spec:
            args.append("-Pfiji")
        args.extend(self.djl_args())
        if "~javadocs" in spec:
            args.extend(["-x", "javadoc"])

        gradlew(*args)

        app_image = join_path("build", "dist", "QuPath")
        if not os.path.isdir(app_image):
            raise InstallError("Expected jpackage image was not created: {0}".format(app_image))

        install_tree(app_image, prefix)
        self.install_pytorch_runtime(prefix)
        self.install_pytorch_launcher(prefix)

    def configure_djl_extension(self):
        if "~djl" in self.spec:
            return

        extension_version = self.djl_extension_versions.get(str(self.version))
        if extension_version is None:
            raise InstallError(
                "No QuPath DJL extension version is known for {0}".format(self.version)
            )

        with open("include-extra.properties", "w") as include_extra:
            include_extra.write("[dependencies]\n")
            dependency = "io.github.qupath:qupath-extension-djl:{0}\n".format(extension_version)
            include_extra.write(dependency)

    def djl_args(self):
        if "~djl" in self.spec:
            return ["-Pdjl.engines=none", "-Pdjl.zoos=none"]

        engines = []
        zoos = []
        if "+pytorch" in self.spec:
            engines.append("pytorch")
            zoos.append("pytorch")

        if engines:
            return [
                "-Pdjl.engines={0}".format(",".join(engines)),
                "-Pdjl.zoos={0}".format(",".join(zoos)),
            ]

        return ["-Pdjl.api=true", "-Pdjl.engines=none", "-Pdjl.zoos=none"]

    def install_pytorch_launcher(self, prefix):
        if "~pytorch" in self.spec:
            return

        pytorch_version = self.spec.variants["torch_version"].value
        pytorch_flavor = self.pytorch_flavors.get(str(self.version))
        if pytorch_flavor is None:
            raise InstallError(
                "No PyTorch GPU runtime mapping is known for {0}".format(self.version)
            )

        torch_lib = self.torch_lib_dir(prefix)
        dependency_libs = self.pytorch_dependency_lib_dirs(prefix)
        path_entries = self.pytorch_path_entries(prefix, torch_lib, dependency_libs)
        jna_path = os.pathsep.join(path_entries)
        library_path = os.pathsep.join([torch_lib] + dependency_libs)
        python_path = os.pathsep.join(self.python_site_packages(prefix))
        executable = join_path(prefix.bin, "QuPath")
        launcher = join_path(prefix.bin, "qupath-pytorch")

        mkdirp(prefix.bin)
        with open(launcher, "w") as script:
            script.write("#!/usr/bin/env bash\n\n")
            script.write("export PYTORCH_VERSION={0}\n".format(pytorch_version))
            script.write("export PYTORCH_FLAVOR={0}\n".format(pytorch_flavor))
            script.write("export PYTORCH_LIBRARY_PATH={0}\n".format(torch_lib))
            script.write('export PYTHONPATH="{0}:${{PYTHONPATH}}"\n'.format(python_path))
            script.write('export LD_LIBRARY_PATH="{0}:${{LD_LIBRARY_PATH}}"\n'.format(library_path))
            script.write('export PATH="{0}:$PATH"\n\n'.format(self.pytorch_bin_path(prefix)))
            script.write('exec "{0}" -Djna.library.path="{1}" "$@"\n'.format(executable, jna_path))
        set_executable(launcher)

    def install_pytorch_runtime(self, prefix):
        if "~pytorch" in self.spec:
            return

        pytorch_flavor = self.pytorch_flavors.get(str(self.version))
        if pytorch_flavor is None:
            raise InstallError(
                "No PyTorch GPU runtime mapping is known for {0}".format(self.version)
            )

        torch_version = self.spec.variants["torch_version"].value
        pip(
            "--no-input",
            "--no-cache-dir",
            "--disable-pip-version-check",
            "install",
            "--ignore-installed",
            "--no-warn-script-location",
            "--only-binary=:all:",
            "--prefix={0}".format(prefix),
            "--index-url",
            "https://download.pytorch.org/whl/{0}".format(pytorch_flavor),
            "torch=={0}".format(torch_version),
        )

    def torch_lib_dir(self, prefix):
        candidates = [
            join_path(site_packages, "torch", "lib")
            for site_packages in self.python_site_packages(prefix)
        ]
        for directory in candidates:
            if os.path.isdir(directory):
                return directory
        return candidates[0]

    def python_site_packages(self, prefix):
        python = self.spec["python"].package
        return self.unique_paths(
            [
                join_path(prefix, python.platlib),
                join_path(prefix, python.purelib),
            ]
        )

    def pytorch_dependency_lib_dirs(self, prefix):
        candidates = []
        for site_packages in self.python_site_packages(prefix):
            nvidia_root = join_path(site_packages, "nvidia")
            if not os.path.isdir(nvidia_root):
                continue
            for root, dirs, files in os.walk(nvidia_root):
                dirs.sort()
                if os.path.basename(root) in ("lib", "lib64") and any(
                    name.endswith(".so") or ".so." in name for name in files
                ):
                    candidates.append(root)
        return self.unique_paths(candidates)

    def unique_paths(self, paths):
        unique = []
        seen = set()
        for path in paths:
            path = str(path)
            if path in seen:
                continue
            seen.add(path)
            unique.append(path)
        return unique

    def pytorch_bin_path(self, prefix):
        return os.pathsep.join(
            self.unique_paths([str(prefix.bin), str(self.spec["python"].prefix.bin)])
        )

    def pytorch_path_entries(self, prefix, torch_lib, dependency_libs):
        python_prefix = self.spec["python"].prefix
        return self.unique_paths(
            [
                str(prefix),
                str(prefix.bin),
                str(prefix.lib),
                str(python_prefix),
                str(python_prefix.bin),
                str(python_prefix.lib),
            ]
            + self.python_site_packages(prefix)
            + [torch_lib]
            + dependency_libs
        )
