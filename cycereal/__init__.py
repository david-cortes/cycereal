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

    ## in PEP518 environments, files will be under a temporary folder
    else:
        candidate_paths = [sys.prefix]
        try:
            candidate_paths.append(os.environ['PYTHONPATH'])
        except:
            pass
        if sys.platform[:3] == "win":
            candidate_paths += os.environ['PATH'].split(";")
        else:
            candidate_paths += os.environ['PATH'].split(":")

        for path in candidate_paths:
            if bool(re.search(r"[Oo]verlay", path)):
                clean_path = re.sub(r"^(.*[Oo]verlay).*$", r"\1", path)
                if os.path.exists( os.path.join(clean_path, append_path) ):
                    return os.path.join(clean_path, "include")

        ## if still not found, try to get it from pip itself
        import pip
        import io
        from contextlib import redirect_stdout
        pip_outp = io.StringIO()
        with redirect_stdout(pip_outp):
            pip.main(['show', '-f', 'cycereal'])
        pip_outp = pip_outp.getvalue()
        pip_outp = pip_outp.split("\n")
        for ln in pip_outp:
            if bool(re.search(r"^Location", ln)):
                files_root = re.sub(r"^Location:\s+", "", ln)
                break
        for ln in pip_outp:
            if bool(re.search(r"\.hpp$", ln)):
                files_root = os.path.join(files_root, re.sub(r"^\s*(.*include)[/\\]+cereal.*\.hpp$", r"\1", ln))
                return files_root

        ## if the header file doesn't exist, shall raise en error
        else:
            raise ValueError("Could not find header files from 'cycereal' - please try reinstalling with 'pip install --force cycereal'")
