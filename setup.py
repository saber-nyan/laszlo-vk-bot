# -*- coding: utf-8 -*-
"""
Наш кривой скрипт установки.
"""
from distutils.core import setup

from setuptools import find_packages

with open('README.md', mode='r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='laszlo-vk-bot',
    version='1.0.0.0',
    description='НИКТО НЕ УЙДЕТ ОБИЖЕННЫМ',
    long_description=readme,
    author='saber-nyan',
    author_email='saber-nyan@ya.ru',
    url='https://github.com/saber-nyan/laszlo-vk-bot',
    license='WTFPL',
    install_requires=[
        'vk_api',
        'cson',
    ],
    packages=find_packages(),
    include_package_data=True
)
