# Distributed-Systems

It's a distributed system consisting of a controller and four robots. The controller functions as an HTTP and RPC server concurrently, utilizing multithreading and is connecting to the robots via RPC (client/server connection). The robots establish connections with each other using MQTT. Upon receiving an HTTP request, the controller initiates an election process where the four robots select a new leader using the bully algorithm. Additionally, Kubernetes is employed to automatically deploy a new controller or robots in case of failure.

<img src="https://github.com/yassinemh3/Distributed-Systems/assets/108351375/7aaa8f22-5c69-4918-b835-f8668e554435" width="300">

