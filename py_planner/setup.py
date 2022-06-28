from setuptools import setup

package_name = 'py_planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='drone',
    maintainer_email='manuel.righele@studenti.unitn.it',
    description='Planner POPF service for specific project',
    license='GNU',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'service = py_planner.planner_service:main',
            'client = py_planner.planner_client:main',
        ],
    },
)
