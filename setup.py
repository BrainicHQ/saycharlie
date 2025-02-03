#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#  #
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  #
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#  #
#  Created on 6/16/24, 5:07 PM
#  #
#  Author: Silviu Stroe

from setuptools import setup, find_packages

setup(
    name='saycharlie',
    version='0.1.0',
    author='Silviu Stroe',
    author_email='your.email@example.com',
    description='A dashboard for managing and synchronizing links across various platforms.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BrainicHQ/saycharlie/',  # Project home page or repository URL
    license='MIT',
    packages=find_packages(),  # Automatically find all packages and subpackages
    include_package_data=True,
    install_requires=[
        'Flask==3.0.3',
        'Flask-SocketIO==5.3.6',
        'numpy==1.26.4',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'requests==2.32.2',
        'watchdog==4.0.1',
        'Werkzeug==3.0.6',
        'zeroconf==0.132.2'
    ],
    python_requires='>=3.6, <4',  # Specify which Python versions are supported
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'saycharlie=app:main',  # Change 'app:main' to your package's main callable
        ],
    },
)
