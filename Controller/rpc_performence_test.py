from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from rpc_controller import RobotControllerHandler  # Replace with the actual file name
import time
import queue
import RobotController


def measure_round_trip_time():
    shared_queue = queue.Queue()  # Create a queue object
    robot_client = RobotControllerHandler(shared_queue)  # Instantiate your RPC controller handler
    robot_id = "123"
    status = True
    duration = 1 # Dauer des Tests in Sekunden
    interval = 0  # Intervall zwischen den Requests in Sekunden

    start_time = time.time()
    counter = 0
    while time.time() - start_time < duration:
        response_start_time = time.time()
        robot_info = RobotController.RobotInfo(robot_id='1ad874', status=True)
        response = robot_client.registerRobot(robot_info)
        counter += 1
        response_end_time = time.time()
        rtt = response_end_time - response_start_time
        print(f'Round Trip Time: {rtt} seconds')
        end_time = time.time()
        total_duration = end_time - start_time
        print(f'Total Test Duration: {total_duration} ms')
        print(f'Total Response: {counter}')


if __name__ == "__main__":
 measure_round_trip_time()

#
# import time
# import threading
#
# from thrift import Thrift
# from thrift.transport import TSocket
# from thrift.transport import TTransport
# from thrift.protocol import TBinaryProtocol
# import RobotController
# import unittest
# class RobotControllerTester(unittest.TestCase):
#
#     def setUp(self):
#         # Initialize the Thrift client
#         self.transport = TSocket.TSocket(host="localhost", port=9090)
#         self.transport = TTransport.TBufferedTransport(self.transport)
#         self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
#         self.client = RobotController.Client(self.protocol)
#         self.transport.open()
#
#     def tearDown(self):
#         self.transport.close()
#
#     def test_register_robot(self):
#         robot_info = RobotController.RobotInfo(robot_id="test-robot", status=True)
#         registered_robot = self.client.registerRobot(robot_info)
#         self.assertTrue(registered_robot)

# def test_update_robot_status(self):
#     robot_id = "test-robot"
#     new_status = True
#
#     # Update the robot status
#     self.client.updateRobotStatus(robot_id, new_status)
#
#     # Get the updated robot status
#     robot_status = self.client.getRobotStatus(robot_id)
#     self.assertEqual(robot_status.status, new_status)
#
# def test_notify_leader_election(self):
#     leader_robot_id = "leader-robot"
#
#     # Notify the leader election
#     self.client.notifyLeaderElection(leader_robot_id)
#
#     # Check if the leader information is updated
#     leader_robot = self.client.getRobotStatus(leader_robot_id)
#     self.assertEqual(leader_robot.status, False)
