"""A wrapper for wit.ai's Duckling.

See:
https://github.com/wit-ai/duckling
"""

from setuptools import setup


setup(
    name='duckling',
    version='1.8.0',
    description='A wrapper for wit.ai\'s Duckling',
    url='https://github.com/FraBle/python-duckling',
    author='Frank Blechschmidt',
    author_email='frank.blechschmidt@sap.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='duckling witai datetime parser parsing nlp',
    packages=['duckling'],
    install_requires=[
        'JPype1',
        'python-dateutil',
        'six'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    package_data={
        'duckling': [
            'jars/clj-time-0.8.0.jar',
            'jars/clojure-1.8.0.jar',
            'jars/duckling-0.4.23.jar',
            'jars/joda-time-2.3.jar',
            'jars/lazymap-3.1.0.jar',
            'jars/plumbing-0.5.3.jar',
            'jars/schema-1.0.1.jar',
            'jars/tools.logging-0.2.6.jar',
        ],
    },
    package_dir={'duckling': 'duckling'},
    include_package_data=True,
    zip_safe=False
)
