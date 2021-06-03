from setuptools import setup

install_requires = [
    'pandas==1.1.4',
    'requests==2.24.0',
    'simplejson==3.16.0',
]

extra_require = {
    'test': ['pytest'],
    'doc': ['sphinx', 'pydata_sphinx_theme'],
}

setup(
        name='pyspectcl',
        version='0.0.2',
        description='Python interface to SpecTcl server',
        author='Tong Zhang',
        author_email='zhangt@frib.msu.edu',
        packages=['spectcl.data',
                  'spectcl.client',
                  'spectcl'],
        package_dir={
            'spectcl.data' : 'main/data',
            'spectcl.client': 'main/client',
            'spectcl': 'main'
        },
        install_requires=install_requires,
        extra_require=extra_require,
)
