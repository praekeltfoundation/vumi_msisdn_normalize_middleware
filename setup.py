from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


version = '0.1.4'

install_requires = [
    'vumi',
]


setup(
    name='vumi_msisdn_normalize_middleware',
    version=version,
    description="Middleware to normalize msisdns",
    long_description=README,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='Praekelt.org',
    author_email='',
    url='',
    license='',
    packages=[
        'vumi_msisdn_normalize_middleware',
    ],
    package_dir={'vumi_msisdn_normalize_middleware':
                 'vumi_msisdn_normalize_middleware'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['vumi_msisdn_normalize_middleware=vumi_msisdn_normalize_middleware:main']
    }
)
