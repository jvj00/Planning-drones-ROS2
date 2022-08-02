# Planning-drones-ROS2
## Description
A service for ROS2 to generate real discrete map, plan a path for 2 drones to take pictures in targets and return to agv, visualize it and translate into 5 simple actions.
* <b>Message request:</b><br>A json file with parameters to generate a map: geocoordinates of points (0,0) bottom left, height & width of the map in meters, sensibility in meters, agv position from origin in meters, drones or target positions from origin in meters (see demo files for more)
* <b>Message response:</b><br>A json file with actions, x, y ,z in this format:
  * action 1: move drone in position x y z
  * action 2: move agv in position x y z
  * action 3: takeoff in position x y z
  * action 4: landing in position x y z
  * action 5: take picture in position x y z
 ## Requirements
 * Ubuntu Linux OS
 * [ROS 2 Foxy](https://docs.ros.org/en/foxy/index.html)
 * [CbC](https://github.com/coin-or/Cbc) : installation integrated in setup.sh
 ## Installation
 1. Make a workspace directory in home directory as `~/dev_ws`
 2. Clone this project in the directory just created with command 
 ```
 git clone https://github.com/jvj00/Planning-drones-ROS2.git
 ```
 3. Enter the directory just downloaded and execute command 
 ```
 sudo bash setup.sh
 ```
 ## Running
 1. Build from your workspace (e.g. `~/dev_ws`) using 
 ```
 colcon build
 ```
 2. Execute command 
 ```
 source install/setup.bash
 ```
 3. Run the service typing
 ```
 ros2 run py_planner service
 ```
 and if you want you can test it with demo client 
 ```
 ros2 run py_planner client
 ```
 or, for the 'return to agv' service,
 ```
 ros2 run py_planner client return
 ```
 ## Contributors
 [jvj00](https://github.com/jvj00)
