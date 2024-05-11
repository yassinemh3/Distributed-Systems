from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import RobotController
from ttypes import RobotInfo, RobotStatus
import time
import threading

# Create an event to signal the start of the election
election_event = threading.Event()


class RobotControllerHandler:
    def __init__(self, shared_queue):
        self.robot_status = {}
        self.shared_queue = shared_queue
    def registerRobot(self, robot_info):
        robot_id = robot_info.robot_id
        status = robot_info.status

        print(f"Robot {robot_id} registered.")
        if status:
            self.robot_status[robot_id] = True
            print(f"Status: is healthy")
        else:
            self.robot_status[robot_id] = False
            print(f"Status: is not healthy")

        self.shared_queue.put({"robot_id": robot_id, "status": status})

        return True

    def getRobotStatus(self, robot_id):
        return RobotStatus(status=self.robot_status.get(robot_id, False))

    def updateRobotStatus(self, robot_id, new_status):
        try:
            self.robot_status[robot_id] = new_status
            if new_status:
                print(f"robot {robot_id} new Status: Healthy")
            else:
                print(f"robot {robot_id} new Status: not Healthy")
        except Exception as e:
            print(f"Error updating robot status: {e}")

    def notifyLeaderElection(self, leader_robot_id):
        # print("Election Started...")
        global leader_id
        leader_id = leader_robot_id
        time.sleep(5)
        print(f"Robot {leader_robot_id} is the new leader!")
        self.shared_queue.put({"leader_robot_id": leader_robot_id})

    def startElection(self):
        try:
            print("Election started...")
        except Exception as e:
            print(f"Error updating robot status: {e}")


def run_rpc_controller(shared_queue):

    handler = RobotControllerHandler(shared_queue)
    processor = RobotController.Processor(handler)
    transport = TSocket.TServerSocket(host="0.0.0.0", port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

    try:
        print("RobotController Server started on Port 9090...")
        server.serve()

    except Thrift.TException as e:
        print(f"Error: {e}")


class ControllerClient:
    def __init__(self, host, port):
        self.transport = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = RobotController.Client(self.protocol)

    def startElection(self):
        self.client.startElection()

    def open_connections(self):
        self.transport.open()

    def close_connections(self):
        self.transport.close()


def rpc_client_thread():
    while True:
        election_event.wait()
        host = "robot"+str(leader_id)
        port = 9090+int(leader_id)
        robot_client = ControllerClient(host, port)
        robot_client.open_connections()
        robot_client.startElection()
        election_event.clear()




