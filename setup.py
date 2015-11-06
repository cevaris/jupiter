import juptiter
version = juptiter.__version__
readme = open('README.md').read()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='juptiter',
    version=version,
    description="""TODO""",
    long_description="""TODO""",
    author='Adam Cardenas',
    author_email='cevaris@gmail.com',
    url='https://github.com/cevaris/juptiter',
    packages=['juptiter',],
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords='juptiter',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        ],

)
