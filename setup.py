from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='DeSW-Dash',
    version='0.0.1',
    py_modules=['desw_dash'],
    url='https://bitbucket.org/deginner/desw-dash',
    license='MIT',
    classifiers=classifiers,
    author='deginner',
    author_email='support@deginner.com',
    description='Bitcoin plugin for the desw wallet platform.',
    setup_requires=['pytest-runner'],
    package_data={'desw': ['static/swagger.json']},
    install_requires=[
        'sqlalchemy>=1.0.9',
        'desw>=0.0.2',
        'python-bitcoinrpc>=0.3',
        'pycoin>=0.62'
    ],
    tests_require=['pytest', 'pytest-cov'],
    extras_require={"build": ["flask-swagger"]}
)
