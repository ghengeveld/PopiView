from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='popiview',
    version='1.0b',
    description=('Real-time website analytics'),
    long_description=open(join(
        dirname(__file__),
        'src', 'popiview', 'README.txt'
    )).read(),
    author='Gert Hengeveld',
    author_email='info@infrae.com',
    url='',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    entry_points={
    'paste.app_factory': [
        'main=popiview.server:app_factory'
      ],
    'console_scripts': ['cleanup=popiview.dbcleanup:cleanup']
    },
    install_requires=[
      'setuptools',
      'PasteScript',
      'PasteDeploy',
      'WebOb',
      'WSGIUtils',
      'MySQL-python',
    ],
    test_suite='popiview',
)
