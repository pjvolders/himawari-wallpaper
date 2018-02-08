from setuptools import setup, find_packages
setup(
    name='himawari',
    version='1.0',
    author='Pieter-Jan Volders',
    author_email='webmaster@pjvolders.be',
    url='https://github.com/pjvolders/himawari-wallpaper',
    packages=find_packages(),
    install_requires=[
        'Pillow>=5.0.0'
    ]
)
