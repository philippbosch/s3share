from setuptools import setup, find_packages


setup(
    name='s3share',
    version='0.2',
    packages=find_packages(),
    install_requires=['boto'],
    author='Philipp Bosch',
    author_email='hello@pb.io',
    license='MIT',
    url='https://github.com/philippbosch/s3share',
    scripts=['s3share.py'],
    entry_points={
        'console_scripts': [
            's3share = s3share:main'
        ]
    },
)
