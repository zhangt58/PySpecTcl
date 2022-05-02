from setuptools import setup

install_requires = [
    'pandas==1.1.4',
    'requests==2.24.0',
    'simplejson==3.16.0',
]

extra_require = {
    'test': ['pytest'],
    'doc': ['sphinx', 'sphinx_rtd_theme'],
}

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
    version='0.3.2',
    description='Python interface to SpecTcl server',
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Physics'],
)
