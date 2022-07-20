#!/bin/sh
echo "Giving exec permissions..."
sudo chmod 777 -R py_planner/extern

echo "Setting absolute path..."
change_from="path_extern=\"/home/drone/dev_ws/src/py_planner/extern\""
change_to="path_extern=\"$(pwd)/py_planner/extern\""
echo $change_to
sed -i "s+$change_from+$change_to+" py_planner/py_planner/planner_service.py
sed -i "s+$change_from+$change_to+" py_planner/py_planner/planner_client.py

echo "Installing dependecies..."
pip install setuptools==58.2.0
sudo apt-get -y install coinor-cbc coinor-libcbc-dev

echo "Making directories..."
mkdir py_planner/extern/solutions

echo "Done!"