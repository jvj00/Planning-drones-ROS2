#!/bin/sh
echo "Give exec permissions..."
sudo chmod 777 -R py_planner/extern
echo "Done!"
echo "Set absolute path..."
change_from="path_extern=\"/home/drone/dev_ws/src/py_planner/extern\""
change_to="path_extern=\"$(pwd)/py_planner/extern\""
echo $change_to
sed -i "s+$change_from+$change_to+" py_planner/py_planner/planner_service.py
sed -i "s+$change_from+$change_to+" py_planner/py_planner/planner_client.py
echo "Done!"