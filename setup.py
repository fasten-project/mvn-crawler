"""
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
"""

from setuptools import setup
from os import path
from mvncrawler import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mvncrawler',
    version=__version__,
    description='A crawler for extracting Maven coordinates',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fasten-project/mvn-crawler',
    author='FASTEN project - Amir M. Mir',
    author_email='mir-am@hotmail.com',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development',
    ],
    keywords='crawler maven coordinates fasten',
    packages=['mvncrawler'],
    python_requries='>=3.5',
    install_requires=['requests', 'beautifulsoup4', 'kafka-python'],
    entry_points={
        'console_scripts': [
            'mvncrawler = mvncrawler.crawler:main',
        ],
    }
)
