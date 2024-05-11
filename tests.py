import requests
import time


def main():

    url = 'http://localhost:8080/new_captain'
    url2 = 'http://localhost:8080/status'
    start_time = time.time()
    counter = 0
    request_start_time = time.time()
    response = requests.post(url)
    counter += 1
    request_end_time = time.time()
    rtt = (request_end_time - request_start_time) * 1000
    print(f'Response Code: {response.status_code}')
    print(f'Round Trip Time: {rtt} ms')
    end_time = time.time()

    print(f'Total Sent Request: {counter}')


if __name__ == "__main__":
    main()


    # while time.time() - start_time < duration:
    # data = {"counter": counter}
    # url2 = 'http://localhost:8080/status'
    # total_duration = end_time - start_time

    # print(f'Total Test Duration: {total_duration} seconds')