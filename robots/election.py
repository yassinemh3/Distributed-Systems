import paho.mqtt.client as mqtt
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import RobotController
import os
import time
import threading
from thrift.server import TServer
import atexit
import logging


def registerRobots():
    # robot_client.open_connections()
    robot_info = RobotController.RobotInfo(robot_id=robot_client.robot_id, status=True)
    robot_client.register_robot(robot_info)


def run_server():
    handler = RobotControllerHandler
    processor = RobotController.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=9091)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    print('Starting the Controller...')
    server.serve()


class RobotClient:
    def __init__(self, host, port):
        self.transport = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = RobotController.Client(self.protocol)
        self.robot_id = os.environ.get("ROBOT_ID")
        self.init = os.environ.get("INIT")

        self.participated = False
        self.port = os.environ.get("PORT")
        self.rpc_host = "0.0.0.0"
        self.rpc_port = 9091
        # Initialize variables
        self.leader_id = "1"
        self.in_election = False
        self.LEADER_TOPIC = "leader"
        self.ELECTION_TOPIC = "election"
        self.ACK_TOPIC = "OK"
        self.ACK = False
        # Logging configuration
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"Robot{self.robot_id}")

        # ACK timeout parameters
        self.ack_timeout = 5  # seconds
        self.ack_received = threading.Event()

    def open_connections(self):
        self.transport.open()

    def close_connections(self):
        self.transport.close()

    def start_election(self):
        ROBOT_ID = int(self.robot_id)
        self.logger.info("Starts election")

        higher_robots = [str(i) for i in range(ROBOT_ID + 1, 5)]
        self.in_election = False
        self.ACK = False

        # Initiate the election by sending requests
        self.send_election_requests(higher_robots)

        # Wait for ACKs with timeout
        ack_timeout_expired = not self.wait_for_acknowledgments()

        if ack_timeout_expired:
            self.logger.warning("Timeout: No ACK received. Election may have failed.")
            self.retry_election()

    def send_election_requests(self, higher_robots):
        for higher_robot in higher_robots:
            self.logger.info(f" sent election request to Robot {higher_robot}")
            mqtt_client.publish(self.ELECTION_TOPIC, f"{self.robot_id}{higher_robot}")

    def wait_for_acknowledgments(self):
        # Wait for ACKs with timeout
        ack_timeout_expired = not self.ack_received.wait(timeout=self.ack_timeout)
        return not ack_timeout_expired

    def retry_election(self):
        # Logic to handle retrying the election if no ACK is received
        self.logger.info("Retrying election...")
        self.retry_election()

    def start_election(self):
        ROBOT_ID = int(self.robot_id)
        self.logger.info(f"Starts election")

        higher_robots = [i for i in range(ROBOT_ID + 1, 5)]
        self.in_election = False
        self.ACK = False

        for higher_robot in higher_robots:
            self.logger.info(f" sent election request to Robot {higher_robot}")
            mqtt_client.publish(self.ELECTION_TOPIC, self.robot_id+str(higher_robot))

        #  Wait for ACKs with timeout
        ack_timeout_expired = not self.ack_received.wait(timeout=self.ack_timeout)

        if ack_timeout_expired:
            self.logger.warning("Timeout: No ACK received. Election may have failed.")
            self.retry_election()

    def on_mqtt_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        if msg.topic == self.LEADER_TOPIC:
            self.leader_id = payload[-1]
            self.logger.info(f" received leader: {self.leader_id}")
            time.sleep(2)
            self.ACK = False
            self.in_election = False

        elif msg.topic == self.ELECTION_TOPIC and not self.in_election and payload[-1] == self.robot_id:
            init_robot = payload[-2]
            self.logger.info(f" send OK to Robot {init_robot}")
            time.sleep(2)
            mqtt_client.publish(self.ACK_TOPIC, init_robot+self.robot_id)
            self.in_election = True

        elif msg.topic == self.ACK_TOPIC and self.robot_id == payload[-2] and not self.ACK:
            init_robot = payload[-2]
            self.logger.info(f" Received ACK from Robot {payload[-1]}")
            time.sleep(2)
            mqtt_client.publish(self.LEADER_TOPIC, payload[-1])
            self.ACK = True
            self.ack_received.set()
            if robot_client:
                robot_client.notify_leader_election(payload[-1])
            if robot_client2:
                robot_client2.notify_leader_election(payload[-1])


    def retry_election(self):
        # Add your logic for handling election retry here
        self.logger.info(f"Retrying election...{self.leader_id}")
        if self.robot_id == self.leader_id:
            self.start_election()

    def register_robot(self, robot_info):
        try:
            return self.client.registerRobot(robot_info)
        except Thrift.TException as e:
            print(f"Thrift error: {e}")
            return None

    def notify_leader_election(self, leader_robot_id):
        try:
            self.client.notifyLeaderElection(leader_robot_id)
        except Thrift.TException as e:
            print(f"Thrift error: {e}")

    def update_robot_status(self, robot_id, new_status):
        time.sleep(15)
        while True:
            try:
                self.client.updateRobotStatus(robot_id, new_status)
                time.sleep(15)
            except Thrift.TException as e:
                time.sleep(20)
                self.logger.info(f"Failed to update robot status. Retrying to connect to Controller ...")
                connect_to_newController(robot_id)

    def thread_rpc_server(self):

        handler = RobotControllerHandler()
        processor = RobotController.Processor(handler)
        transport = TSocket.TServerSocket(host="0.0.0.0", port=self.port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        try:
            print(f"Robot Server started on Port {self.port}...")
            server.serve()

        except Thrift.TException as e:
            print(f"Error: {e}")


rpc_host2 = "controller"
rpc_port2 = 9090
robot_client2 = RobotClient(rpc_host2, rpc_port2)


def connect_to_newController(robot_id):
    robot_client2.open_connections()
    robot_info2 = RobotController.RobotInfo(robot_id=robot_id, status=True)
    robot_client2.register_robot(robot_info2)
    if robot_client2.leader_id == robot_client2.robot_id:
        robot_client2.notify_leader_election(robot_id)
    time.sleep(100000)


class RobotControllerHandler:

    def startElection(self):
        if robot_client.robot_id == robot_client.leader_id:
            robot_client.start_election()


if __name__ == "__main__":
    init = os.environ.get("INIT")
    robot_id = os.environ.get("ROBOT_ID")

    rpc_host = "controller"
    rpc_port = 9090
    robot_client = RobotClient(rpc_host, rpc_port)

    mqtt_client = mqtt.Client()
    mqtt_client.on_message = robot_client.on_mqtt_message
    mqtt_client.connect("mqtt.eclipseprojects.io", 1883, 60)
    mqtt_client.subscribe([(robot_client.LEADER_TOPIC, 0), (robot_client.ELECTION_TOPIC, 0), (robot_client.ACK_TOPIC, 0)])

    thread1 = threading.Thread(target=robot_client.thread_rpc_server)
    thread1.start()
    robot_client.open_connections()
    robot_info = RobotController.RobotInfo(robot_id=robot_client.robot_id, status=True)
    robot_client.register_robot(robot_info)
    threading.Thread(target=robot_client.update_robot_status, args=(robot_id, "True")).start()
    # # Thread function for RPC client
    if init == "1":
        robot_client.notify_leader_election(robot_id)
    print(f"im a Robot with ID: {robot_id}")
    time.sleep(3)
    mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
    mqtt_thread.start()

    def cleanup():
        # This function will be called on program exit
        mqtt_thread.join()
        thread1.join()
        #     thread2.join()
    # # Register the cleanup function
    atexit.register(cleanup)





