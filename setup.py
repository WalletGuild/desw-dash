from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='DeSW-Dash',
    version='0.0.2',
    py_modules=['desw_dash'],
    url='https://github.com/WalletGuild/desw-dash',
    license='MIT',
    classifiers=classifiers,
    author='WalletGuild',
    author_email='support@gitguild.com',
    description='Bitcoin plugin for the desw wallet platform.',
    setup_requires=['pytest-runner'],
    install_requires=[
        'sqlalchemy>=1.0.9',
        'sqlalchemy-models>=0.0.6',
        'desw>=0.0.3',
        'python-bitcoinrpc>=0.3',
        'pycoin>=0.62'
    ],
    tests_require=['pytest', 'pytest-cov'],
    extras_require={"build": ["flask-swagger"]}
)
