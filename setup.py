from setuptools import setup, find_packages

setup(name='facebookinsights',
    description='A wrapper and command-line interface for the Facebook Insights API.',
    #long_description=open('README.rst').read(),
    author='Stijn Debrouwere',
    author_email='stijn@debrouwere.org',
    #url='http://stdbrouw.github.com/facebook-insights/',
    download_url='http://www.github.com/debrouwere/facebook-insights/tarball/master',
    version='0.3.1',
    license='ISC',
    packages=find_packages(),
    keywords='data analytics api wrapper facebook insights',
    entry_points = {
          'console_scripts': [
                'insights = insights.commands:main', 
          ],
    }, 
    install_requires=[
        'click', 
        'requests', 
        'rauth', 
        'facepy', 
        'python-dateutil', 
        'pytz', 
        'addressable', 
        'flask', 
        'keyring', 
    ], 
    # test_suite='facebookinsights.tests', 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        ],
    )