import os, re, sys

__all__ = ["get_cereal_include_dir"]

def get_cereal_include_dir():
    ### will try to see if this file exists
    append_path = os.path.join("include", "cereal", "archives", "binary.hpp")

    ## if installing with pip or setuptools, will be here (this is the ideal case)
    if os.path.exists(os.path.join(  re.sub(r"__init__\.py$", "", __file__), append_path )):
        return os.path.join( re.sub(r"__init__\.py$", "", __file__), "include" )

    elif os.path.exists(os.path.join(  re.sub(r"cycereal[/\\]+__init__\.py$", "", __file__), append_path )):
        return os.path.join( re.sub(r"cycereal[/\\]+__init__\.py$", "", __file__), "include" )

    ## if installing with distutils, will be placed here (this should ideally not happen)
    elif os.path.exists(os.path.join(sys.prefix, append_path)):
        return os.path.join(sys.prefix, "include")

    ## if the header file doesn't exist, shall raise en error
    else:
        raise ValueError("Could not find header files from 'cycereal' - please try reinstalling with 'pip install --force cycereal'")
