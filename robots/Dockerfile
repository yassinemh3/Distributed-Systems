FROM python:3
# Set the working directory
WORKDIR /app

# Install Thrift
RUN apt-get update && \
    apt-get install -y thrift-compiler && \
    pip install thrift
RUN pip install paho-mqtt

COPY __init__.py .
COPY constants.py .
COPY robot.py .
COPY RobotController.py .
COPY RobotController-remote .
COPY ttypes.py .
COPY election.py .
ENTRYPOINT ["python3", "election.py"]