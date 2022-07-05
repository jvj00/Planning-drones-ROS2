import sys

from planner_interface.srv import MsgJson
import rclpy
from rclpy.node import Node

## PATH VARIABLE ##
path_extern="/home/drone/dev_ws/src/py_planner/extern"
path_json_go=path_extern+"/demo/demo_go.json"
path_json_ret=path_extern+"/demo/demo_ret.json"
path_client_result=path_extern+"/demo/client_result.json"

class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(MsgJson, 'plan')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = MsgJson.Request()

    def send_request(self, string):
        self.req.in_json = string
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)
    if(sys.argv[1] is not None and sys.argv[1]=="return"):
        f = open(path_json_ret, "r")
    else:
        f = open(path_json_go, "r")
    json=f.read()
    f.close()
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(json)
    minimal_client.get_logger().info(response.out_json)
    f = open(path_client_result, "w")
    f.write(response.out_json)

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()