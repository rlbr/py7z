#Argomirr is the original author but project was dead; see fork
from setuptools import setup
setup(name='py7z',
      version='2.2.1',
      description='Python wrapper around 7-zip',
      url='https://github.com/rlbr/py7z',
      author='Raphael Roberts',
      author_email='raphael.roberts48@gmail.com',
      package_data={'': ['config.ini']},
      include_package_data=True,
      license='GPLv2',
      packages=['py7z'],
      install_requires=[
        'python-dateutil'
      ],
      zip_safe=False)