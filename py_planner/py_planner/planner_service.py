from planner_interface.srv import MsgJson

import rclpy
from rclpy.node import Node
import json

#self.get_logger().info(targets)

class Service(Node):

    def __init__(self):
        super().__init__('service')
        self.srv = self.create_service(MsgJson, 'plan', self.callback)

    def callback(self, request, response):
        input = json.loads(request.in_json)
        
        targets=input["targets"]
        print(targets)

        response.out_json = "None"
        return response


def main(args=None):
    rclpy.init(args=args)
    service = Service()
    rclpy.spin(service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()