import unittest
import time
import threading
import paho.mqtt.client as mqtt


class TestMQTTPerformance(unittest.TestCase):

    def setUp(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_topic = "performance_test_topic"
        self.message_count = 10000  # Adjust the number of messages for your test

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_mqtt_performance(self):
        received_messages = []
        message_payload = "Test message payload"*5  # Adjust payload size if needed

        def on_message(client, userdata, msg):
            received_messages.append(msg.payload.decode())

        self.mqtt_client.on_message = on_message

        # Connect to MQTT broker
        self.mqtt_client.connect("mqtt.eclipseprojects.io", 1883, 60)
        self.mqtt_client.subscribe([(self.mqtt_topic, 0)])

        # Start the MQTT loop in a separate thread
        mqtt_thread = threading.Thread(target=self.mqtt_client.loop_forever)
        mqtt_thread.start()

        # Wait for the MQTT client to be connected
        time.sleep(2)

        # Measure publish throughput
        start_time = time.time()
        for i in range(self.message_count):
            self.mqtt_client.publish(self.mqtt_topic, message_payload)
        end_time = time.time()
        publish_throughput = self.message_count / (end_time - start_time)

        # Wait for the messages to be received
        time.sleep(5)  # Adjust the wait time based on your scenario

        # Assert that the messages were received
        self.assertEqual(len(received_messages), self.message_count)

        # Measure subscribe throughput
        start_time = time.time()
        for i in range(self.message_count):
            self.mqtt_client.subscribe(self.mqtt_topic)
        end_time = time.time()
        subscribe_throughput = self.message_count / (end_time - start_time)

        # Print results
        print(f"Publish Throughput: {publish_throughput} messages per second")
        print(f"Subscribe Throughput: {subscribe_throughput} messages per second")

        # Stop the MQTT loop and clean up
        self.mqtt_client.disconnect()
        mqtt_thread.join()

if __name__ == "__main__":
    unittest.main()
