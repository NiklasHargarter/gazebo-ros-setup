from setuptools import find_packages, setup

package_name = 'consumer_camera'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@example.com',
    description='Example consumer: TB4 camera -> cmd_vel based on mean brightness.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'brightness_driver = consumer_camera.brightness_driver:main',
        ],
    },
)
