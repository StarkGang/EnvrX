# Copyright (C) 2023-present by StarkGang@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/StarkGang/Envrx > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/StarkGang/Envrx/blob/main/LICENSE >
#
# All rights reserved.

from setuptools import setup, find_packages
import os
import re

def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

def get_version():
    with open(os.path.join('envrx', '__init__.py'), 'r', encoding='utf-8') as f:
        if version_match := re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE
        ):
            return version_match.group(1)
    raise RuntimeError("Version not found.")

setup(
    name='envrx',
    version=get_version(),
    description='A package to manage environment variables with database and custom env file support.',    
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='WarnerStark',
    author_email='starktechfriday@gmail.com',
    url='https://github.com/Starkgang/envrx',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=['envrx', 'env', 'environment', 'variables', 'database', 'mongodb', 'sql', 'redis'],
    include_package_data=True,
)
