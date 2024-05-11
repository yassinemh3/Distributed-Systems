import unittest
import time
import threading
import paho.mqtt.client as mqtt
from election import RobotClient # Import your RobotClient class

class TestMQTTCommunication(unittest.TestCase):

    def setUp(self):
        # Set up your MQTT client and RobotClient instance
        self.mqtt_client = mqtt.Client()
        self.robot_client = RobotClient("localhost", 9090)  # Update with your RPC host and port
        self.robot_id = "1"  # Update with a valid robot ID
        self.mqtt_topic = "test_topic"

    def tearDown(self):
        # Clean up resources after each test
        self.mqtt_client.disconnect()
        self.robot_client.close_connections()

    def test_publish_subscribe(self):
        # Test basic publish and subscribe functionality
        received_messages = []

        def on_message(client, userdata, msg):
            received_messages.append(msg.payload.decode())

        self.mqtt_client.on_message = on_message

        # Connect to MQTT broker
        self.mqtt_client.connect("mqtt.eclipseprojects.io", 1883, 60)
        self.mqtt_client.subscribe([(self.mqtt_topic, 0)])

        # Open RPC connections
        self.robot_client.open_connections()

        # Start the MQTT loop in a separate thread
        mqtt_thread = threading.Thread(target=self.mqtt_client.loop_forever)
        mqtt_thread.start()

        # Wait for the MQTT client to be connected
        time.sleep(2)

        # Publish a message from a robot
        test_message = "Hello, world!"
        self.mqtt_client.publish(self.mqtt_topic, test_message)

        # Wait for the message to be received
        time.sleep(2)

        # Assert that the message was received
        self.assertIn(test_message, received_messages)

        # Close connections and stop the MQTT loop
        self.robot_client.close_connections()
        self.mqtt_client.disconnect()
        mqtt_thread.join()

if __name__ == "__main__":
    unittest.main()
