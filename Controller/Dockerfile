FROM python:3
COPY __init__.py .
# Install Thrift
RUN apt-get update && \
    apt-get install -y thrift-compiler && \
    pip install thrift


RUN pip install paho-mqtt
COPY constants.py .
COPY app.py .
COPY http_server.py .
COPY rpc_controller.py .
COPY RobotController.py .
COPY RobotController-remote .
COPY ttypes.py .
CMD ["python3","-u","app.py"]