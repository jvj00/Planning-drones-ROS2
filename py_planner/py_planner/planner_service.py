from planner_interface.srv import MsgJson

import rclpy
from rclpy.node import Node
import json
import os
from subprocess import Popen, PIPE
import time

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
path_plan=path_extern+"/plan"
path_popf=path_extern+"/popf/popf2/popf3-clp"
path_solutions=path_extern+"/solutions"

class Service(Node):

    def __init__(self):
        super().__init__('service')
        self.srv = self.create_service(MsgJson, 'plan', self.callback)

    def callback(self, request, response):
        ## Load JSON
        input = json.loads(request.in_json)
        
        ## Generate map_tool command & Call map_tool
        map_tool_request = "--pddl "+path_problem+" --json "+path_json+" "
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

        ## Read output popf


        ## Format output with json & produce a response


        ## Remove files & return response
        os.remove(path_problem)
        os.remove(path_json)
        for file in os.listdir(path_solutions):
            os.remove(path_solutions+'/'+file)

        response.out_json = "None"
        return response


def main(args=None):
    rclpy.init(args=args)
    service = Service()
    rclpy.spin(service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()