from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class Bioinformatics(BundlePackage):
    """ARC bioinformatics collection module."""

    homepage = "https://arc.umich.edu"
    version("1.0")

    modules_root = join_path("/sw", "pkgs", "arc", "staging", "biospack", "biomodules")

    @property
    def module_arch(self):
        return "{0}-{1}-{2}".format(
            self.spec.platform,
            self.spec.os,
            self.spec.target.family,
        )

    def setup_run_environment(self, env):
        env.prepend_path(
            "MODULEPATH", join_path(self.modules_root, self.module_arch, "Core")
        )
