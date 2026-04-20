from setuptools import find_packages, setup

package_name = 'camera_subscriber'

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
    description='Subscribes to a bridged Gazebo camera and logs frame stats.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'image_consumer = camera_subscriber.image_consumer:main',
        ],
    },
)
