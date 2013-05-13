from setuptools import setup

setup(
    name='django-static-filtered-images',
    version='0.1.1',
    author='Gabriel Grant',
    packages=['static_filtered_images',],
    license='LGPL',
    long_description=open('README').read(),
    install_requires=['PIL',],
)

