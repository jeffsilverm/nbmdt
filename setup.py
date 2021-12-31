# Expose all of the functions in nmbdt.py to the world
from setuptools import setup, find_packages

setup(
    name='nbmdt',
    packages=find_packages(where='src'),
    package_dir={'': 'src'}		# A dictionary with package names for keys and directories for values
)

"""
Some thoughts on file organization and the usage of this file

There should be "top level" project directory and all of the files in that project go under that directory
In this case, the project directory is either nbmdt (the "real" project) or nbmdt_proj (the "blue sky" experimental
version).

This organization follows "Python Testing with Pytest" by Brian Okken, page 170.


jeffs@jeffs-desktop:~/python/nbmdt$ tree .
.
├── setup.py (this file)
├── src
│   └── nbmdt_d
│       ├── __init__.py
│       └── nbmdt_src.py
└── test
    ├── __pycache__
    │   └── test_nbmdt.cpython-38-PYTEST.pyc
    ├── test_nbmdt.py
    └── test_network.py

4 directories, 5 files
jeffs@jeffs-desktop:~/python/nbmdt_proj$ 

However, in version ? there was a change and now the prefered method of installing packages is to use
setup.cfg, which is static, rather than setup.py, which is dynamic.


Remember the period at the end of the line!

jeffs@jeffs-desktop:~/python/nbmdt_proj$ python3 -m pip install .
Processing /home/jeffs/python/nbmdt_proj
Building wheels for collected packages: nbmdt-proj
  Building wheel for nbmdt-proj (setup.py) ... done
  Created wheel for nbmdt-proj: filename=nbmdt_proj-0.0.0-py3-none-any.whl size=1483 sha256=66956aaf21e2ac1fa514c8c5572be0f4abb000c463428b10f77e56db869ff648
  Stored in directory: /tmp/pip-ephem-wheel-cache-l30ct_g3/wheels/fc/22/73/ce835b1e615f33409536d1122bc3f7c02c7639f33fa86f3f3d
Successfully built nbmdt-proj
Installing collected packages: nbmdt-proj
  Attempting uninstall: nbmdt-proj
    Found existing installation: nbmdt-proj 0.0.0
    Uninstalling nbmdt-proj-0.0.0:
      Successfully uninstalled nbmdt-proj-0.0.0
Successfully installed nbmdt-proj-0.0.0

To test that the installation was done correctly.

jeffs@jeffs-desktop:~/python/nbmdt_proj$ python3 -c "import nbmdt_d.nbmdt_src as nbmdt_src; print( dir(nbmdt_src)); assert nbmdt_src.nbmdt_func()==74"
['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__']
jeffs@jeffs-desktop:~/python/nbmdt_proj$ 
python3 -c "import nbmdt_d.nbmdt_src as nbmdt_src; assert nbmdt_src.nbmdt_func()==74; print('success') "




(BTW: the VT-100 graphic characters I found at http://fileformats.archiveteam.org/wiki/DEC_Special_Graphics_Character_Set)
"""

