import threading
import time
from multiprocessing import Process, Queue
from http_server import run_http_server
from rpc_controller import run_rpc_controller, rpc_client_thread
import queue


if __name__ == "__main__":
    # Create a shared queue for inter-thread communication
    shared_queue = queue.Queue()
    # # Create threads for HTTP server and RPC controller
    http_server = threading.Thread(target=run_http_server, args=(shared_queue,))
    rpc_server = threading.Thread(target=run_rpc_controller, args=(shared_queue,))
    http_server.start()
    rpc_server.start()
    thread3 = threading.Thread(target=rpc_client_thread)
    thread3.start()
    thread3.join()
    http_server.join()
    rpc_server.join()





