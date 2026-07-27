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

    license("GPL-3.0-only")

    version(
        "0.7.0",
        sha256="5cd23875aa49a90d652726ddca0d06338c67084a005e453c39f0d7125623448e",
    )

    djl_extension_versions = {"0.7.0": "0.4.2"}
    pytorch_versions = {"0.7.0": "2.7.1"}
    pytorch_flavors = {"0.7.0": "cu128"}

    variant("djl", default=True, description="Bundle the QuPath Deep Java Library extension")
    variant("fiji", default=False, description="Build QuPath with Fiji dependencies")
    variant("javadocs", default=False, description="Build and package bundled Javadocs")
    variant("pytorch", default=True, description="Bundle DJL PyTorch GPU runtime support")

    depends_on("java@25:", type="build")
    depends_on("cuda@12.8.1", type=("build", "run"), when="@0.7.0+pytorch")
    depends_on("cudnn@8.5:9.0", type=("build", "run"), when="@0.7.0+pytorch")
    depends_on("python@3.13", type=("build", "run"), when="@0.7.0+pytorch")
    depends_on(
        "py-torch@2.7.1",
        type=("build", "run"),
        when="@0.7.0+pytorch",
    )

    conflicts("+pytorch", when="~djl", msg="+pytorch requires +djl")
    conflicts("platform=darwin", msg="This recipe currently installs the Linux jpackage image")
    conflicts("platform=windows", msg="This recipe currently installs the Linux jpackage image")

    executables = ["^QuPath$"]
    sanity_check_is_file = [join_path("bin", "QuPath")]

    def setup_build_environment(self, env):
        env.set("GRADLE_USER_HOME", join_path(self.stage.path, "gradle"))
        env.set("GRADLE_OPTS", "-Dorg.gradle.daemon=false")

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

        pytorch_version = self.pytorch_versions.get(str(self.version))
        pytorch_flavor = self.pytorch_flavors.get(str(self.version))
        if pytorch_version is None or pytorch_flavor is None:
            raise InstallError(
                "No PyTorch GPU runtime mapping is known for {0}".format(self.version)
            )

        torch_lib = self.torch_lib_dir()
        path_entries = self.pytorch_path_entries(torch_lib)
        jna_path = os.pathsep.join(path_entries)
        library_path = os.pathsep.join(
            [
                torch_lib,
                str(self.spec["cudnn"].prefix.lib),
                str(self.spec["cuda"].prefix.lib64),
                str(self.spec["cuda"].prefix.lib),
            ]
        )
        executable = join_path(prefix.bin, "QuPath")
        launcher = join_path(prefix.bin, "qupath-pytorch")

        mkdirp(prefix.bin)
        with open(launcher, "w") as script:
            script.write("#!/usr/bin/env bash\n\n")
            script.write("export PYTORCH_VERSION={0}\n".format(pytorch_version))
            script.write("export PYTORCH_FLAVOR={0}\n".format(pytorch_flavor))
            script.write("export PYTORCH_LIBRARY_PATH={0}\n".format(torch_lib))
            script.write("export LD_LIBRARY_PATH={0}:${{LD_LIBRARY_PATH}}\n".format(library_path))
            script.write("export PATH={0}:$PATH\n\n".format(self.pytorch_bin_path()))
            script.write('exec "{0}" -Djna.library.path="{1}" "$@"\n'.format(executable, jna_path))
        set_executable(launcher)

    def torch_lib_dir(self):
        torch_prefix = self.spec["py-torch"].prefix
        python = self.spec["python"].package
        candidates = [
            join_path(torch_prefix, python.platlib, "torch", "lib"),
            join_path(torch_prefix, python.purelib, "torch", "lib"),
        ]
        for directory in candidates:
            if os.path.isdir(directory):
                return directory
        return candidates[0]

    def pytorch_bin_path(self):
        return os.pathsep.join(
            [str(self.spec["python"].prefix.bin), str(self.spec["cuda"].prefix.bin)]
        )

    def pytorch_path_entries(self, torch_lib):
        python_prefix = self.spec["python"].prefix
        return [
            str(python_prefix),
            str(python_prefix.bin),
            str(python_prefix.lib),
            torch_lib,
            str(self.spec["cuda"].prefix.lib64),
            str(self.spec["cuda"].prefix.lib),
            str(self.spec["cudnn"].prefix.lib),
        ]
