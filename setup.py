from setuptools import setup
import os
import glob

install_requires = ['numpy', 'uncertainties', 'pint', 'netCDF4', 'boto3', 'matplotlib', 'scipy']

extras_require = {'hdc': ['pyhdc'],
                  'imas': ['imas'],
                  'ual': ['pyual'],
                  'build_structures': ['xmltodict','bs4'],
                  'build_documentation': ['Sphinx','sphinx-bootstrap-theme','sphinx-gallery','Pillow']}

# Add .json IMAS structure files to the package
here = os.path.abspath(os.path.split(__file__)[0]) + os.sep

# Automatically generate requirement.txt file if this is the OMAS repo and requirements.txt is missing
if os.path.exists(here + '.git') and not os.path.exists(here + 'requirements.txt'):
    print('Generating new requirements.txt')
    with open(here + 'requirements.txt', 'w') as f:
        f.write('# Do not edit this file by hand, operate on setup.py instead\n#\n')
        f.write('# usage: pip install -r requirements.txt\n\n')
        for item in install_requires:
            f.write(item.ljust(25) + '# required\n')
        for requirement in extras_require:
            for item in extras_require[requirement]:
                if requirement in ['imas','hdc','ual','build_structures']:
                    item='#'+item
                f.write(item.ljust(25) + '# %s\n' % requirement)


packages = ['omas','omas.tests']
package_data = {'omas': ['*.py', 'version'],'omas.tests':['*.py']}
for item in glob.glob(os.sep.join([here, 'omas', 'imas_structures', '*'])):
    print(item)
    packages.append('omas.imas_structures.' + os.path.split(item)[1])
    package_data['omas.imas_structures.' + os.path.split(item)[1]] = ['*.json']


setup(
    name='omas',
    version=open('omas/version', 'r').read().strip(),
    description='Ordered Multidimensional Array Structure',
    url='https://gafusion.github.io/omas',
    author='Orso Meneghini',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='integrated modeling OMFIT IMAS ITER',
    packages=packages,
    package_data=package_data,
    install_requires=install_requires,
    extras_require=extras_require)
