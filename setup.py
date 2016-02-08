from setuptools import setup, find_packages

setup(
    name='samza-prometheus-exporter',
    version='0.1.1',
    description='Samza metrics Prometheus exporter',
    url='https://github.com/movio/samza-prometheus-exporter',
    author='Nicolas Maquet',
    author_email='nicolas@movio.co',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='monitoring prometheus exporter apache samza',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'kafka-python',
        'prometheus-client>=0.0.13'
    ],
    entry_points={
        'console_scripts': [
            'samza-prometheus-exporter=exporter:main',
        ],
    },
)
