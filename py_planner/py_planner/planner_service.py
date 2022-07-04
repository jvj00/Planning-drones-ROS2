from select import EPOLL_CLOEXEC
from planner_interface.srv import MsgJson

import rclpy
from rclpy.node import Node
import json
import os
from subprocess import Popen, PIPE
import time
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

## INPUT FIXED VARIABLE ##
LEVELS = 3
DISTANCE_LEVELS = 30
LOWEST_LEVEL = 30

## PATH VARIABLE ## 
path_extern="/home/drone/dev_ws/src/py_planner/extern"
path_map_tool=path_extern+"/map_tool"
path_problem=path_extern+"/map_files/problem.pddl"
path_domain=path_extern+"/map_files/domain.pddl"
path_json=path_extern+"/map_files/points.json"
path_links=path_extern+"/map_files/links.json"
path_plan=path_extern+"/plan"
path_popf=path_extern+"/popf/popf2/popf3-clp"
path_solutions=path_extern+"/solutions"

def min_distance(targets, point):
        dist_min=99999999
        min_target=None
        for target in targets:
            dist=math.sqrt(math.pow(target["x"]-point["x"],2)+math.pow(target["y"]-point["y"],2)+math.pow(target["z"]-point["z"],2))
            if dist<dist_min:
                dist_min=dist
                min_target=target
        return min_target

def construct_map(actions, pos_agv_x, pos_agv_y):
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
    ax.set_xlabel("length x (m)")
    ax.set_ylabel("width y (m)")
    ax.set_zlabel("height z (m)")
    ax.grid(False)
    ax.scatter(x_drones,y_drones,z_drones)
    ax.scatter(x_agv,y_agv,z_agv,c="green")
    for i in range(len(link_start_x_agv)):
        ax.plot([link_start_x_agv[i],link_end_x_agv[i]],[link_start_y_agv[i],link_end_y_agv[i]],zs=[link_start_z_agv[i],link_end_z_agv[i]], color='green', linewidth=0.3, linestyle='dotted')
    
    prev_pos_agv_x=pos_agv_x
    prev_pos_agv_y=pos_agv_y
    dist_min=99999999999
    for p in points["points"]:
        if "agv" in p["name"]:
            dist=math.sqrt(math.pow(p["x"]-pos_agv_x,2)+math.pow(p["y"]-pos_agv_y,2))
            if dist < dist_min:
                dist_min=dist
                prev_pos_agv_z=p["z"]
    prev_pos_d1_x=prev_pos_agv_x
    prev_pos_d1_y=prev_pos_agv_y
    prev_pos_d1_z=prev_pos_agv_z
    prev_pos_d2_x=prev_pos_agv_x
    prev_pos_d2_y=prev_pos_agv_y
    prev_pos_d2_z=prev_pos_agv_z
    d1_agv=True
    d2_agv=True
    
    for a in actions:
        if a["drone"]=="d1":
            ax.plot([prev_pos_d1_x,a["x"]],[prev_pos_d1_y,a["y"]],zs=[prev_pos_d1_z,a["z"]], color="blue", linewidth=2)
            if a["action"]==5:
                ax.scatter(a["x"],a["y"],a["z"],c="blue",marker="x",s=60)
            prev_pos_d1_x=a["x"]
            prev_pos_d1_y=a["y"]
            prev_pos_d1_z=a["z"]
            if a["action"]==3:
                d1_agv=False
            if a["action"]==4:
                d1_agv=True
        elif a["drone"]=="d2":
            ax.plot([prev_pos_d2_x,a["x"]],[prev_pos_d2_y,a["y"]],zs=[prev_pos_d2_z,a["z"]], color="red", linewidth=2)
            if a["action"]==5:
                ax.scatter(a["x"],a["y"],a["z"],c="red",marker="x",s=60)
            prev_pos_d2_x=a["x"]
            prev_pos_d2_y=a["y"]
            prev_pos_d2_z=a["z"]
            if a["action"]==3:
                d2_agv=False
            if a["action"]==4:
                d2_agv=True
        else:
            ax.plot([prev_pos_agv_x,a["x"]],[prev_pos_agv_y,a["y"]],zs=[prev_pos_agv_z,a["z"]], color="brown", linewidth=2)
            prev_pos_agv_x=a["x"]
            prev_pos_agv_y=a["y"]
            prev_pos_agv_z=a["z"]
            if d1_agv:
                prev_pos_d1_x=a["x"]
                prev_pos_d1_y=a["y"]
                prev_pos_d1_z=a["z"]
            if d2_agv:
                prev_pos_d2_x=a["x"]
                prev_pos_d2_y=a["y"]
                prev_pos_d2_z=a["z"]
        
    plt.show()

class Service(Node):

    def __init__(self):
        super().__init__('service')
        self.srv = self.create_service(MsgJson, 'plan', self.callback)

    def callback(self, request, response):

        ## Load JSON
        input = json.loads(request.in_json)
        
        ## Generate map_tool command & Call map_tool
        map_tool_request = "--pddl "+path_problem+" --json "+path_json+" "+" --links "+path_links+" "
        map_tool_request+= str(int(input["sizes"]["height"]/input["sensibility"]))+" "+str(int(input["sizes"]["width"]/input["sensibility"]))+" "+str(LEVELS)+" "
        map_tool_request+= str(input["sensibility"])+" "+str(DISTANCE_LEVELS)+" "+str(LOWEST_LEVEL)+" "
        map_tool_request+= str(input["pos_agv"]["x"])+" "+str(input["pos_agv"]["y"])+" "
        map_tool_request+= str(input["coordinates"]["lat"])+" "+str(input["coordinates"]["lon"])
        for target in input["targets"]:
            map_tool_request+=" "+str(target["x"])+" "+str(target["y"])+" "+str(target["z"])
        ret = os.system(path_map_tool+" "+map_tool_request)
        if(ret!=0):
            response.out_json = "None"
            return response

        ## Generate popf command & Call popf
        process = Popen(path_plan+' '+path_popf+' '+path_domain+' '+path_problem+' '+path_solutions+'/sol', shell=True)

        start = time.time()
        files=0
        while time.time()-start < 10 or files==0: #10s after every solution
            if files!=len(os.listdir(path_solutions)):
                start = time.time()
            files=len(os.listdir(path_solutions))
            time.sleep(1)
        process.kill()

        ## Read output popf & format output with json
        actions={"actions": []}
        f_sol = open(path_solutions+'/'+os.listdir(path_solutions)[len(os.listdir(path_solutions))-1], "r")
        f_points = open(path_json)
        points = json.loads(f_points.read())
        for line in f_sol:
            if line.startswith(";"):
                continue
            words=line[line.find("(")+1:line.find(")")].split()
            dict={
                "action": 0,
                "drone": "",
                "x": 0,
                "y": 0,
                "z": 0
            }
            if(words[0]=="move_drone"):
                dict["action"]=1
                dict["drone"]=words[1]
                element_point=[point for point in points["points"] if point['name']==words[3]][0]
                dict["x"]=element_point["x"]
                dict["y"]=element_point["y"]
                dict["z"]=element_point["z"]
            if(words[0]=="move_agv"):
                dict["action"]=2
                element_point=[point for point in points["points"] if point['name']==words[2]][0]
                dict["x"]=element_point["x"]
                dict["y"]=element_point["y"]
                dict["z"]=element_point["z"]
            if(words[0]=="takeoff"):
                dict["action"]=3
                dict["drone"]=words[1]
                element_point=[point for point in points["points"] if point['name']==words[3]][0]
                dict["x"]=element_point["x"]
                dict["y"]=element_point["y"]
                dict["z"]=element_point["z"]
            if(words[0]=="landing"):
                dict["action"]=4
                dict["drone"]=words[1]
                element_point=[point for point in points["points"] if point['name']==words[3]][0]
                dict["x"]=element_point["x"]
                dict["y"]=element_point["y"]
                dict["z"]=element_point["z"]
            if(words[0]=="take_picture"):
                #with reposition in right place
                dict["action"]=5
                dict["drone"]=words[1]
                element_point=[point for point in points["points"] if point['name']==words[2]][0]
                dict["x"]=element_point["x"]
                dict["y"]=element_point["y"]
                dict["z"]=element_point["z"]
                ret=min_distance(input["targets"], dict)
                dict["x"]=ret["x"]
                dict["y"]=ret["y"]
                dict["z"]=ret["z"]
            
            actions["actions"].append(dict)

        f_sol.close()
        f_points.close()

        ## Produce a response
        response.out_json = json.dumps(actions)

        ## If GUI, construct and show map
        if input["gui"]=="true":
            construct_map(actions["actions"], input["pos_agv"]["x"], input["pos_agv"]["y"])

        ## Remove files & return response
        os.remove(path_problem)
        os.remove(path_json)
        os.remove(path_links)
        for file in os.listdir(path_solutions):
            os.remove(path_solutions+'/'+file)

        return response


def main(args=None):
    rclpy.init(args=args)
    service = Service()
    rclpy.spin(service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()