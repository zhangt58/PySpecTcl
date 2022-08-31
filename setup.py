from setuptools import setup

install_requires = [
    'pandas==1.3.5', # Python 3.7
    'requests==2.28.1',
    'simplejson==3.17.6',
    'matplotlib==3.5.3',
    'toml==0.10.2'
]

extra_require = {
    'test': ['pytest'],
    'doc': ['sphinx', 'sphinx_rtd_theme'],
}


def readme():
    with open('README.md', 'r') as f:
        return f.read()


def set_entry_points():
    r = {}
#    r['console_scripts'] = [
#        'fetch_mach_state=phantasy_apps.msviz.tools:main',
#    ]

    r['gui_scripts'] = [
        'spectcl_viz=spectcl.apps.viz:run',
    ]
    return r

setup(
    name='pyspectcl',
    version='0.4.0',
    description='Python interface to SpecTcl server',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/archman/PySpecTcl',
    author='Tong Zhang',
    author_email='zhangt@frib.msu.edu',
    packages=[
        'spectcl.apps',
        'spectcl.apps.viz',
        'spectcl.apps.viz.ui',
        'spectcl.contrib',
        'spectcl.data',
        'spectcl.client',
        'spectcl'],
    package_dir={
        'spectcl.apps': 'main/apps',
        'spectcl.apps.viz': 'main/apps/viz',
        'spectcl.apps.viz.ui': 'main/apps/viz/ui',
        'spectcl.contrib': 'main/contrib',
        'spectcl.data' : 'main/data',
        'spectcl.client': 'main/client',
        'spectcl': 'main'
    },
    include_package_data=True,
    install_requires=install_requires,
    extra_require=extra_require,
    entry_points=set_entry_points(),
    license='GPL3+',
    keywords='SpecTcl REST',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Physics'],
)
