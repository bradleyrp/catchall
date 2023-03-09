# Catchall

## Installation

This software depends on the GCC compilers, MPI, and HDF5. If you want to skip MPI, we can demonstrate serial writes to a single file, but not parallel writes. You can install these packages with your operating system package manager, or use [Spack](https://spack.io) to compile them locally.

### Requirements on HPC

On a typical HPC platform, you should load the MPI and HDF5 modules. For example, on *Sol*:

~~~
ml intel/2021.3.0 mvapich2/2.3.4 hdf5/1.10.7 python/3.8.6
~~~

### Compile requirements

In development, you might want to compile your own software stack. The catchall uses [Spack](https://spack.io) to compile HDF5 to demonstrate parallel writes. This requires MPI. The author demonstrated this method first on a MacOS system.

~~~
# via https://spack.readthedocs.io/en/latest/
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
. spack/share/spack/setup-env.sh
# bootstrap is less than 1min
spack bootstrap now
# install GCC on your machine, then tell Spack to look for it
spack compiler find
spack compilers
# make an environment
spack env create catchall
spack env activate catchall
# review compilers and select a home-brew install GCC
spack compiler find
# use one of the GCC versions you installed and found above
# make the spack environment
cat > $SPACK_ENV/spack.yaml <<EOF
spack:
  specs:
  - python@3.10.8
  - py-setuptools ^python@3.10.8
  - py-pip ^python@3.10.8
  - openmpi%gcc@12.2.0
  - hdf5+mpi+shared ^openmpi%gcc@12.2.0
  - py-numpy ^python@3.10.8 ^intel-oneapi-mkl 
  - py-h5py ^python@3.10.8 ^openmpi %gcc@12.2.0
  view: true
  concretizer:
    unify: when_possible
EOF
# install
spack concretize -f 
time spack install -j 8
~~~

Note that the installation is costly, taking more than an hour on an M1 MacBook. We install our own Python to keep the toolchain uniform because [HomeBrew](https://brew.sh) provides Python compiled via `clang` and we want to use GCC compilers on both our development machine and our target HPC platform.

In the above example we have included `py-h5py +mpi` which builds the parallel version of HDF5. This is one of the most reliable ways to provide this package. It might be possible to [use pip to install parallel `h5py`](https://docs.h5py.org/en/stable/mpi.html#building-against-parallel-hdf5) however the author finds Spack to be more reliable. 

If you compile your own parallel `py-h5py` with Spack and then load it with `spack load`, any later use of `pip install -U -e .` to install a custom package that includes the standard `h5py` in the `install_requires` list in `setup.cfg` will notice your custom copy, saying, for example:

~~~
Requirement already satisfied: h5py in ./spack/opt/spack/darwin-ventura-m1/apple-clang-14.0.0/py-h5py-3.7.0-jtkro2t3trdc3g73tmtfepn4fwjl76bv/lib/python3.10/site-packages (from catchall==0.1.dev1+g680bb81.d20230307) (3.7.0)
~~~

Since existing software is not overwritten by `pip`, you can load all of your Spack requirements before using `source go.sh` or `make install` to work inside of the virtual environment.

### Compile

Once you have access to `gcc` and `mpicc` and HDF5, you can can install this directly. If you used a Spack environment named `catchall` in the method above, continue in the same shell or load it with `source spack/share/spack/setup-env.sh && spack env activate catchall`.

~~~
make install
~~~

You can use `source path/to/catchall/go.sh` to activate this environment from anywhere.
