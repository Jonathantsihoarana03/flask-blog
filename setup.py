from setuptools import setup, find_packages

setup(
    name='flask-tutorial',  # remplacez par le nom de votre projet
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',  # et autres dépendances nécessaires
    ],
    entry_points={
        'console_scripts': [
            'flask_tutorial=flask_tutorial.flaskr:main',  # remplacez par le module et la fonction principale de votre projet
        ],
    },
)