try:
    from setuptools import setup
except:
    from distutils.core import setup
import os, re

def get_all_files_in_folder():
    all_files = []
    root_path = "./include"
    for path, subdirs, files in os.walk(root_path):
        for name in files:
            all_files.append( (path, name) )

    for i in range(len(all_files)):
        all_files[i] = re.sub(r"^.*(include[/\\]+cereal.*)$", r"\1", all_files[i][0]), all_files[i][1]

    all_files_dct = dict()
    for path, file in all_files:
        if path in all_files_dct.keys():
            all_files_dct[path].append(file)
        else:
            all_files_dct[path] = [file]

    all_files_tuples = []
    for k, v in all_files_dct.items():
        all_files_tuples.append((k, [os.path.join(k, f) for f in v]))
    return all_files_tuples

setup(
  name = 'cycereal',
  packages = ['cycereal'],
  version = '0.1.4',
  author = 'David Cortes',
  author_email = 'david.cortes.rivera@gmail.com',
  url = 'https://github.com/david-cortes/cycereal',
  data_files = get_all_files_in_folder(),
  include_package_data = True
)
