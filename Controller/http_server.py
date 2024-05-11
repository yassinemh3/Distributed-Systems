
import socket
import queue
from rpc_controller import election_event
# Datenstruktur zur Speicherung von Dummy-Daten
# dummy_data = []
def count_data_by_robot_id(shared_queue):
    robot_ids = set()
    while True:
        try:
            data = shared_queue.get()
            robot_id = data.get("robot_id")
            robot_ids.add(robot_id)
        except queue.Empty:
            break
    return len(robot_ids)
# Funktion zur Verarbeitung einer HTTP-Anfrage
def handle_http_request(client_socket, shared_data):
    request = client_socket.recv(1024).decode()
    if request:
        lines = request.split('\n')
        first_line = lines[0].strip()
        method, path, _ = first_line.split(' ')

        if method == 'GET':
            if path == '/status':
                num_registered_robots = sum(1 for item in shared_data.queue if item.get("status"))
                response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nAnzahl der aktiven Roboter: {num_registered_robots}'
            elif path == '/captain':
                if shared_data.qsize() == 0:
                    response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nkein Aktueller Kapitän'
                else:
                    # Convert the queue to a list to access the last added item
                    leader_info_list = list(shared_data.queue)

                    # Get the last added leader
                    if leader_info_list:
                        last_leader_info = leader_info_list[-1]
                        leader_robot_id = last_leader_info.get("leader_robot_id")
                        response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nAktuellen Kapitäns: robot {leader_robot_id}'
                    else:
                        response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nkein Aktueller Kapitän'
            elif path == '/health':
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nController-Status: OK'
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nNot Found'
        elif method == 'POST':
            if path == '/data':
                # Dummy-Daten speichern
                data = request.split('\r\n\r\n', 1)[1]
                print(f"received data: {data}")
                shared_data.put(data)
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nDaten erfolgreich gespeichert'
            elif path == '/new_captain':
                election_event.set()
                # Neue Kapitänsauswahl
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nNeue Kapitänsauswahl gestartet'

            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nNot Found'
        else:
            response = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\n\nBad Request: Nur GET und POST werden unterstützt'

        client_socket.send(response.encode())
    client_socket.close()


# Hauptfunktion
def run_http_server(shared_data):

    host = '0.0.0.0'  # Server-IP-Adresse
    port = 8080  # Server-Port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"HTTP-Controller gestartet auf {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Verbindung von {addr[0]}:{addr[1]} hergestellt.")
        handle_http_request(client_socket, shared_data)


# if __name__ == "__main__":
#     run_http_server()
