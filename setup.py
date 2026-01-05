import os
import sys
import subprocess
from setuptools import setup, Extension, find_packages
import numpy as np
from Cython.Build import cythonize
from distutils.sysconfig import get_python_lib
from site import getusersitepackages

def locate_gsl():
    """
    Function to find GSL in 4 possible places that depend on how it was installed 
    and whether pkg-config is installed. 
    """
    # Check if GSL installed via conda and use that path
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        inc = os.path.join(conda_prefix, "include")
        lib = os.path.join(conda_prefix, "lib")
        header = os.path.join(inc, "gsl", "gsl_math.h")
        if os.path.exists(header):
            return inc, lib

    # Try using pkg-config (if installed) to find path to GSL
    try:
        cflags = subprocess.check_output(["pkg-config", "--cflags", "gsl"],
                                         stderr=subprocess.DEVNULL).decode().strip().split()
        libs = subprocess.check_output(["pkg-config", "--libs", "gsl"],
                                       stderr=subprocess.DEVNULL).decode().strip().split()
        inc = None
        lib = None
        for tok in cflags:
            if tok.startswith("-I"):
                inc = tok[2:]
        for tok in libs:
            if tok.startswith("-L"):
                lib = tok[2:]
        if inc and lib:
            return inc, lib
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Use default paths in macOS as installed via HomeBrew
    if sys.platform == "darwin":
        for prefix in ("/usr/local", "/opt/homebrew"):
            inc = os.path.join(prefix, "include")
            lib = os.path.join(prefix, "lib")
            header = os.path.join(inc, "gsl", "gsl_math.h")
            if os.path.exists(header):
                return inc, lib

    # Standard unix paths
    for prefix in ("/usr/local", "/usr"):
        inc = os.path.join(prefix, "include")
        lib = os.path.join(prefix, "lib")
        header = os.path.join(inc, "gsl", "gsl_math.h")
        if os.path.exists(header):
            return inc, lib

    return None, None

gsl_inc, gsl_lib = locate_gsl()

# Throw error if cannot find GSL
if gsl_inc is None or gsl_lib is None:
    msg = (
        "Could not find GSL in the predicted places. "
        "If you have not installed it, we recommend installing it via conda/mamba. "
        "If you have installed it and it is in an unusual path, we recommend installing pkg-config to find it automatically."
    )
    raise RuntimeError(msg)

# Try 3 different paths to the file ee2_bindata.dat, so that you are sure to find it
pathtopythonlib1=get_python_lib()
data_dir_1 = os.path.join(pathtopythonlib1, "euclidemu2", "ee2_bindata.dat")
pathtopythonlib2=getusersitepackages()
data_dir_2 = os.path.join(pathtopythonlib2, "euclidemu2", "ee2_bindata.dat")
package_dir = os.path.dirname(os.path.abspath(__file__))
data_dir_3 = os.path.join(package_dir, "ee2_bindata.dat")

ext_modules = [
    Extension(
        "euclidemu2",
        sources=[
            "src/euclidemu2.pyx","src/cosmo.cxx","src/emulator.cxx"
        ],
        include_dirs=["src", gsl_inc, np.get_include()],
        library_dirs=[gsl_lib],
        libraries=["gsl", "gslcblas"],
        language="c++",
        extra_compile_args=["-std=c++11"],
        define_macros=[
        ("PRINT_FLAG", "0"),
        ("PATH_TO_EE2_DATA_FILE1", f"\"{data_dir_1}\""),
        ("PATH_TO_EE2_DATA_FILE2", f"\"{data_dir_2}\""),
        ("PATH_TO_EE2_DATA_FILE3", f"\"{data_dir_3}\""),
        ]
    )
]

setup(
    name="euclidemu2",
    version="1.4.1",
    author="Pedro Carrilho,  Mischa Knabenhans",
    description="Python wrapper for EuclidEmulator2",
    author_email="pedromgcarrilho@gmail.com",
    packages=['euclidemu2'],
    package_dir={'euclidemu2': 'src'},
    ext_modules=cythonize(ext_modules),
    install_requires=[
        "numpy",
        "scipy"
    ],
    package_data={'euclidemu2': ["ee2_bindata.dat"]},
    include_package_data=True,
    zip_safe=False,
)
