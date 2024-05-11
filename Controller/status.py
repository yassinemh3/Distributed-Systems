import RobotController
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def get_robot_status(robot_id):
    transport = TSocket.TSocket("localhost", 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = RobotController.Client(protocol)

    try:
        transport.open()

        # Call getRobotStatus
        robot_status = client.getRobotStatus(robot_id)

        # Process the result
        print(f"Robot ID: {robot_id}")
        print(f"Is Healthy: {robot_status}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        transport.close()


# Example usage
get_robot_status('12131')  # Replace with the actual robot ID you want to query
