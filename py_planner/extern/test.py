import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

path_extern="/home/drone/dev_ws/src/py_planner/extern"
path_json=path_extern+"/map_files/points.json"
path_links=path_extern+"/map_files/links.json"
f_points = open(path_json)
f_links = open(path_links)
points = json.loads(f_points.read())
links = json.loads(f_links.read())

x_drones=[]
y_drones=[]
z_drones=[]
x_agv=[]
y_agv=[]
z_agv=[]
link_start_x_agv=[]
link_start_y_agv=[]
link_start_z_agv=[]
link_end_x_agv=[]
link_end_y_agv=[]
link_end_z_agv=[]
for point in points["points"]:
    if "agv" in point["name"]:
        x_agv.append(point["x"])
        y_agv.append(point["y"])
        z_agv.append(point["z"])
    else:
        x_drones.append(point["x"])
        y_drones.append(point["y"])
        z_drones.append(point["z"])
for link in links["links"]:
    if link["type"] == "agv":
        link_start_x_agv.append(link["from"]["x"])
        link_start_y_agv.append(link["from"]["y"])
        link_start_z_agv.append(link["from"]["z"])
        link_end_x_agv.append(link["to"]["x"])
        link_end_y_agv.append(link["to"]["y"])
        link_end_z_agv.append(link["to"]["z"])

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel("length (m)")
ax.set_ylabel("width (m)")
ax.set_zlabel("height (m)")
ax.grid(False)
ax.scatter(x_drones,y_drones,z_drones)
ax.scatter(x_agv,y_agv,z_agv,c="green")
for i in range(len(link_start_x_agv)):
    ax.plot([link_start_x_agv[i],link_end_x_agv[i]],[link_start_y_agv[i],link_end_y_agv[i]],zs=[link_start_z_agv[i],link_end_z_agv[i]], color='green', linewidth=0.3, linestyle='dotted')
plt.show()