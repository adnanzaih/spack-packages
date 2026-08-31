from spack_repo.builtin.build_systems.python import PythonCollectivePackage

from spack.package import *


class Arcpy(PythonCollectivePackage):
    """ARC centrally supported Python software stack."""

    homepage = "https://arc.umich.edu"
    has_code = False
    metalist = {
    "3.14": [('python', '3.14.7'), ("py-scipy", "1.17"), ("py-numpy", "2.4"), ("py-pandas", "3.0"), ("py-scikit-learn", "1.8")],
    "3.13": [('python', '3.13.13'), ("py-scipy", "1.16"), ("py-numpy", "2.3"), ("py-pandas", "2.3"), ("py-scikit-learn", "1.7")]}
    for key in metalist.keys():
        version(key)
        for pairing in metalist[key]:
             depends_on(f"{pairing[0]}@{pairing[1]}", when=f"@{key}", type="run")
