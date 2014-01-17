import os
from distutils.sysconfig import get_python_lib

from orchestra.utils.system import run


def get_existing_pip_installation():
    """ returns current pip installation path """
    if run("pip freeze|grep django-orchestra", err_codes=[0,1]).return_code == 0:
        for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
            existing_path = os.path.abspath(os.path.join(lib_path, "orchestra"))
            if os.path.exists(existing_path):
                return existing_path
    return None
