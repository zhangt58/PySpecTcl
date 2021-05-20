from setuptools import setup

install_requires = [
    'pandas==1.1.4',
#    'tzlocal==2.1',
    'requests==2.24.0',
    'simplejson==3.16.0',
#    'tqdm==4.47.0',
]

extra_require = {
    'test': ['pytest'],
    'doc': ['sphinx', 'pydata_sphinx_theme'],
}

def set_entry_points():
    r = {}
    r['console_scripts'] = [
        'pyarchappl-get=archappl.scripts.get:main',
    ]
    return r


setup(
        name='pyspectcl',
        version='0.0.1',
        description='Python interface to SpecTcl server',
        author='Tong Zhang',
        author_email='zhangt@frib.msu.edu',
        packages=[#'archappl.admin',
                  'spectcl.data',
                  'spectcl.client',
                  #'archappl.contrib',
                  #'archappl.scripts',
                  'spectcl'],
        package_dir={
            #'archappl.admin': 'main/mgmt',
            'spectcl.data' : 'main/data',
            'spectcl.client': 'main/client',
            #'archappl.contrib': 'main/contrib',
            #'archappl.scripts': 'main/scripts',
            'spectcl': 'main'
        },
        # entry_points=set_entry_points(),
        install_requires=install_requires,
        extra_require=extra_require,
)
