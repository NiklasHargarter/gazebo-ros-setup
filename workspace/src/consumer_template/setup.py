from setuptools import find_packages, setup

package_name = 'consumer_template'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Niklas Hargarter',
    maintainer_email='niklashargarter@gmail.com',
    description='Minimal consumer-side examples: subscribe to camera, drive the base.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'echo_camera = consumer_template.echo_camera:main',
            'drive_square = consumer_template.drive_square:main',
        ],
    },
)
