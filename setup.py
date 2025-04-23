import os
import shutil
from setuptools import setup, find_packages
from ahorros import PACKAGE_NAME, __email__, __author__

dir_path = os.path.dirname(os.path.realpath(__file__))


def parse_dependencies(requirements_file):
    """
    Given a requirements file path, parse all dependencies into a list.

    Parameters
    ----------
    requirements_file : str or path
        Requirements file path.

    Returns
    -------
    list
        List with dependency and version.
    """
    dependencies = []
    for _line in requirements_file:
        if not (_line.startswith('#') or _line.startswith('--') or _line.startswith('-')):
            dependencies.append(_line)
    return dependencies


with open('VERSION.txt') as version_file:
    version = version_file.read().strip()


with open("requirements.txt") as _file:
    requirements = parse_dependencies(_file)


with open("requirements_dev.txt") as _file:
    requirements_dev = parse_dependencies(_file)


setup(
    author=__author__,
    author_email=__email__,
    name=PACKAGE_NAME,
    version=version,
    description='Project description',
    install_requires=requirements,
    setup_requires=requirements_dev,
    packages=find_packages(include=[PACKAGE_NAME, f"{PACKAGE_NAME}.*"])
)


# remove temporary files generates in wheel file build
shutil.rmtree(os.path.join(dir_path, "build"))
shutil.rmtree(os.path.join(dir_path, f"{PACKAGE_NAME}.egg-info"))
