from setuptools import setup, find_packages

packages = find_packages()
print(packages)

setup(name = 'bnl_chip_analysis', version = '0.1', packages = packages,
      entry_points = {
          'console_scripts': [
              'build = build.main:main',
              'bnl_test = build.tester:main',
          ],
      },
)



