from spack_repo.builtin.build_systems.python import PythonCollectivePackage

from spack.package import *


class Arcpy(PythonCollectivePackage):
    """ARC centrally supported Python software stack."""

    homepage = "https://arc.umich.edu"
    has_code = False
    metalist = {
    "3.14t": [('python+optimizations+freethreading', '3.14.7'), ("py-scipy", "1.18"), ("py-numpy", "2.3"), ("py-pandas", "3.0+parquet+excel+performance"), ("py-scikit-learn", "1.8")],
    "3.14ut": [('python+optimizations', '3.14.7'), ("py-scipy", "1.17"), ("py-numpy", "2.3"), ("py-pandas", "3.0+parquet+excel+performance"), ("py-scikit-learn", "1.8")],
    "3.13": [('python+optimizations', '3.13.15'), ("py-scipy", "1.16"), ("py-numpy", "2.3"), ("py-pandas", "2.3+parquet+excel+performance"), ("py-scikit-learn", "1.7")],
    "3.12": [('python+optimizations', '3.12.14'), ("py-scipy", "1.16"), ("py-numpy", "2.2"), ("py-pandas", "2.2+parquet+excel+performance"), ("py-scikit-learn", "1.6")],
    "3.11": [('python+optimizations', '3.11.16'), ("py-scipy", "1.16"), ("py-numpy", "1.25"), ("py-pandas", "2.1.4+parquet+excel+performance"), ("py-scikit-learn", "1.5")],
    "3.10": [('python+optimizations', '3.10.21'), ("py-scipy", "1.12"), ("py-numpy", "1.25"), ("py-pandas", "1.5.3+excel+performance"), ("py-scikit-learn", "1.5")]
    }

    for key in metalist.keys():
        version(key)
        for pairing in metalist[key]:
             depends_on(f"{pairing[0]}@{pairing[1]}", when=f"@{key}", type="run")
