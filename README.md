# Cereal headers for Cython

This is a Python package which installs the [Cereal](https://uscilab.github.io/cereal/) C++ header-only library as a Python package and provides a function to get the path in which these headers are to be found, so that they can be included in Cython projects in a similar way as with the [Rcereal](https://cran.r-project.org/web/packages/Rcereal/index.html) library for Rcpp.

Cereal is a library for serialization/pickling of arbitrary C++ objects into raw bytes using C++ ostreams and which can then be de-serialized using the same library from istreams, similarly to how it is done in the Boost library, so as to save objects between sessions or export them as files of raw bytes - for more information see the cereal webpage.

The intended use of this package is to have Cython extensions for Python which are able to export C++ objects to then use them in another language, such as C++ or R+Rcpp. Note that Cython itself provides its own auto-pickle functionality which can be used for passing Cython cdef'd classes between Python sessions using pickle, and that is a better option if you are only looking at sharing objects within Python.

# Installation

Package is available in PyPI - can be installed with
```
pip install cycereal
```

Note: the current cereal files in this package were taken from the cereal GitHub master branch as they were on 2020-06-19.

# Sample usage

Example C++ file defining an arbitrary struct with serialization and de-serialzation (`cpp_file.cpp`):
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cereal/archives/binary.hpp>
#include <cereal/types/vector.hpp>

typedef struct MyObj {
    std::vector<int> vec;
    double dbl;

    template<class Archive>
    void serialize(Archive &archive)
    {
        archive(this->vec, this->dbl);
    }
} MyObj;

MyObj produce_obj()
{
    MyObj outp;
    outp.dbl = 100.;
    outp.vec.resize(10);
    for (int i = 0; i < 10; i++)
        outp.vec[i] = i * i;
    return outp;
}

void print_obj(MyObj &my_obj)
{
    std::cout << "attr double: " << my_obj.dbl << "\n";
    std::cout << "attr vector: [ ";
    for (double v : my_obj.vec)
        std::cout << v << " ";
    std::cout << "]" << std::endl;
}

std::string serialize_obj(MyObj &my_obj)
{
    std::stringstream ss;
    {
        cereal::BinaryOutputArchive oarchive(ss);
        oarchive(my_obj);
    }
    return ss.str();
}

MyObj deserialize_obj(std::string &obj_bytes)
{
    MyObj outp;
    std::stringstream ss;
    ss.str(std::move(obj_bytes));

    {
        cereal::BinaryInputArchive iarchive(ss);
        iarchive(outp);
    }

    return outp;
} 

```

Examply Cython file wrapping the functions and adding functionality for saving and loading the objects into raw files (`cy_file.pyx`):
```python
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector

cdef extern from "cpp_file.cpp":
    ctypedef struct MyObj:
        vector[int] vec
        double dbl
    MyObj produce_obj()
    void print_obj(MyObj &my_obj)
    cpp_string serialize_obj(MyObj &my_obj)
    MyObj deserialize_obj(cpp_string &obj_bytes)

cdef class obj_holder:
    cdef MyObj my_obj
    def create_obj(self):
        self.my_obj = produce_obj()
    def inspect_obj(self):
        print_obj(self.my_obj)
    def serialize_obj(self, fpath):
        cdef cpp_string obj_bytes = serialize_obj(self.my_obj)
        with open(fpath, "wb") as of:
            of.write(obj_bytes)
    def deserialize_obj(self, fpath):
        with open(fpath, "rb") as ff:
            model_bytes_py = ff.read()
        cdef size_t n_bytes = len(model_bytes_py)
        cdef char *ptr_to_bytes = model_bytes_py
        cdef cpp_string obj_bytes = cpp_string(ptr_to_bytes, n_bytes)
        self.my_obj = deserialize_obj(obj_bytes)

```

Example `setup.py` file for making this an extension:
```python
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup
    from distutils.extension import Extension
import cycereal
from Cython.Distutils import build_ext

setup(
    name  = "cereal_example",
    packages = ["cereal_example"],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("cereal_example",
                             language="c++",
                             sources=["cy_file.pyx"],
                             include_dirs=[cycereal.get_cereal_include_dir()])]
    )

```

Trying it then in Python (e.g. compile with `python setup.py build_ext --inplace --force`, then launch a Python session in the same folder):
```python
from cereal_example import obj_holder

obj1 = obj_holder()
obj2 = obj_holder()

obj1.create_obj()
obj1.inspect_obj()
obj1.serialize_obj("temp.raw")

obj2.deserialize_obj("temp.raw")
obj2.inspect_obj()

```
