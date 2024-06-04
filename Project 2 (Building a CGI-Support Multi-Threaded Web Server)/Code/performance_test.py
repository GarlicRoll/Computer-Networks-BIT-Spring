
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Server configuration
SERVER_URL = 'http://localhost:8888'

# Number of requests
NUM_REQUESTS = 10
CONCURRENCY_LEVEL = 10


# Function to perform a GET request
def get_request(path):
    url = SERVER_URL + path
    response = requests.get(url)
    return response.status_code, len(response.content)


# Function to perform a POST request
def post_request(path, data):
    url = SERVER_URL + path
    response = requests.post(url, data=data)
    return response.status_code, len(response.content)


# Function to measure performance
def measure_performance(request_type, path, data=None):
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
        futures = []
        for _ in range(NUM_REQUESTS):
            if request_type == 'GET':
                futures.append(executor.submit(get_request, path))
            elif request_type == 'POST':
                futures.append(executor.submit(post_request, path, data))

        results = [future.result() for future in futures]

    end_time = time.time()
    duration = end_time - start_time
    success_count = sum(1 for status, _ in results if status == 200)
    fail_count = NUM_REQUESTS - success_count

    print(f"Test completed in {duration:.2f} seconds")
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {fail_count}")
    print(f"Requests per second: {NUM_REQUESTS / duration:.2f}")


# Test cases
def main():
    print("Testing static content...")
    measure_performance('GET', '/index.html')

    print("\nTesting CGI calculator...")
    measure_performance('POST', '/cgi-bin/calculator.py', data={'num1': '10', 'num2': '20', 'operation': 'add'})

    print("\nTesting CGI data query...")
    measure_performance('POST', '/cgi-bin/data_query.py', data={'name': 'Alice'})


if __name__ == "__main__":
    main()
