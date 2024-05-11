from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import RobotController
import os
import time
import paho.mqtt.client as mqtt
from collections import deque
import threading
import paho.mqtt.client as mqtt

class RobotClient:
    def __init__(self, host, port, mqtt_broker, mqtt_port):
        # Initialize Thrift connection
        self.transport = TSocket.TSocket(host, port)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = RobotController.Client(self.protocol)
        self.robot_id = os.environ.get("ROBOT_ID")
        # Initialize MQTT connection
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(mqtt_broker, mqtt_port)
        self.mqtt_client.subscribe("leader_election")
        self.participated = False

    def open_connections(self):
        self.transport.open()

    def close_connections(self):
        self.transport.close()

    def open_mqtt(self):
        self.mqtt_client.loop_forever()

    def close_mqtt(self):
        self.mqtt_client.disconnect()

    def next_robot(self, robot_id):
        return str((int(robot_id) % 4) + 1)

    def initiate_leader_election(self):
        self.mqtt_client.publish("leader_election", f"INITIATE:{self.robot_id}")

    def on_mqtt_message(self, client, userdata, msg):
        current_robot_id = int(self.robot_id)
        nextRobot = int(self.next_robot(self.robot_id))
        payload = msg.payload.decode()
        if payload.startswith("INITIATE:"):
            initiating_robot = int(payload.split(":")[1])
            if initiating_robot == nextRobot:
                # Forward the initiation message
                self.mqtt_client.publish("leader_election", f"INITIATE:{self.next_robot(self.robot_id)}")
            elif nextRobot < current_robot_id:
                # I am the leader
                self.notify_leader_election(self.robot_id)
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

    def get_robot_status(self, robot_id):
        try:
            return self.client.getRobotStatus(robot_id)
        except Thrift.TException as e:
            print(f"Thrift error: {e}")
            return None

    def update_robot_status(self, robot_id, new_status):
        self.client.updateRobotStatus(robot_id, new_status)
        time.sleep(10)
def register_robot_thread():
    rpc_host = "controller"
    rpc_port = 9090
    mqtt_broker = "broker"
    mqtt_port = 1883
    robot_id = os.environ.get("ROBOT_ID")
    robot_client = RobotClient(rpc_host, rpc_port, mqtt_broker, mqtt_port)
    robot_info = RobotController.RobotInfo(robot_id=robot_id, status=True)
    print(f"I'm a Robot with ID: {robot_id}")
    try:
        robot_client.open_connections()
        registered_robot = robot_client.register_robot(robot_info)
        robot_client.open_mqtt()
        robot_client.initiate_leader_election()
        time.sleep(15)

    finally:
        # robot_client.close_mqtt()
        robot_client.close_connections()

    # Thread function for robot registration

def thread2():
    time.sleep(1000)

def run_threads():
    # Start threads for registration and leader election
    registration_thread = threading.Thread(target=register_robot_thread)
    thread_2 = threading.Thread(target=thread2)
    registration_thread.start()
    thread_2.start()
    # Wait for both threads to finish
    registration_thread.join()
    thread_2.join()


if __name__ == "__main__":

    run_threads()


