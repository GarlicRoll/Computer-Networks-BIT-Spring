import socket
import threading
import os
import mimetypes
import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Server configuration
HOST = 'localhost'
PORT = 8888
WEB_ROOT = 'webroot'
CGI_BIN = os.path.join(WEB_ROOT, 'cgi-bin')
LOG_FILE = os.path.join(WEB_ROOT, 'log', 'server.log')
MAX_CONNECTIONS = 10
THREAD_POOL_SIZE = 20

# Ensure the directories exist
os.makedirs(CGI_BIN, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# List to keep track of active connections
active_connections = []
connections_lock = threading.Lock()


# Logging function
def log_request(client_ip, method, path, status_code, content_length, referrer=''):
    with open(LOG_FILE, 'a') as log:
        log.write(
            f"{client_ip} - - [{datetime.datetime.now()}] \"{method} {path} HTTP/1.1\" {status_code} {content_length} \"{referrer}\"\n")


# Function to handle each client connection
def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode()
        if not request:
            return

        headers = request.split('\n')
        method, path, _ = headers[0].split()
        referrer = ''

        for header in headers:
            if header.startswith('Referer:'):
                referrer = header.split(': ')[1].strip()
                break

        if method == 'GET':
            handle_get(client_socket, client_address, path, referrer)
        elif method == 'POST':
            handle_post(client_socket, client_address, headers, request, referrer)
        elif method == 'HEAD':
            handle_head(client_socket, client_address, path, referrer)
        else:
            send_response(client_socket, 'HTTP/1.1 400 Bad Request\r\n', '<html><body>Bad Request</body></html>',
                          'text/html')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        with connections_lock:
            active_connections.remove((client_socket, threading.current_thread()))
        client_socket.close()
        print(f"Connection from {client_address} closed.")


# Function to handle GET requests
def handle_get(client_socket, client_address, path, referrer):
    if path == '/':
        path = '/index.html'
    file_path = WEB_ROOT + path

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            content = file.read()
            mime_type, _ = mimetypes.guess_type(file_path)
            send_response(client_socket, 'HTTP/1.1 200 OK\r\n', content, mime_type)
            log_request(client_address[0], 'GET', path, 200, len(content), referrer)
    else:
        with open(os.path.join(WEB_ROOT, '404.html'), 'rb') as file:
            content = file.read()
            send_response(client_socket, 'HTTP/1.1 404 Not Found\r\n', content, 'text/html')
            log_request(client_address[0], 'GET', path, 404, len(content), referrer)


# Function to handle HEAD requests
def handle_head(client_socket, client_address, path, referrer):
    if path == '/':
        path = '/index.html'
    file_path = WEB_ROOT + path

    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        send_response(client_socket, 'HTTP/1.1 200 OK\r\n', b'', mime_type)
        log_request(client_address[0], 'HEAD', path, 200, 0, referrer)
    else:
        send_response(client_socket, 'HTTP/1.1 404 Not Found\r\n', b'', 'text/html')
        log_request(client_address[0], 'HEAD', path, 404, 0, referrer)


# Function to handle POST requests
def handle_post(client_socket, client_address, headers, request, referrer):
    content_length = 0
    for header in headers:
        if header.startswith('Content-Length'):
            content_length = int(header.split(': ')[1])
            break

    body = request.split('\r\n\r\n')[1][:content_length]
    path = headers[0].split()[1]

    # Handling CGI
    if path.startswith('/cgi-bin/'):
        cgi_path = CGI_BIN + path[8:]
        if os.path.exists(cgi_path):
            env = os.environ.copy()
            env['CONTENT_LENGTH'] = str(content_length)
            # Explicitly invoke Python
            with open("python-path.txt", 'r') as file:
                python_path = file.read()
            process = subprocess.Popen([python_path, cgi_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, env=env)

            output, error = process.communicate(input=body.encode())
            if process.returncode == 0:
                send_response(client_socket, 'HTTP/1.1 200 OK\r\n', output, 'text/html')
                log_request(client_address[0], 'POST', path, 200, len(output), referrer)
            else:
                send_response(client_socket, 'HTTP/1.1 500 Internal Server Error\r\n', error.decode(), 'text/plain')
                log_request(client_address[0], 'POST', path, 500, len(error.decode()), referrer)
                print(process)
                print(python_path)
                print("(Check python-path.txt and make sure that it says the correct path to the python interpreter)")
        else:
            with open(os.path.join(WEB_ROOT, '404.html'), 'rb') as file:
                content = file.read()
                send_response(client_socket, 'HTTP/1.1 404 Not Found\r\n', content, 'text/html')
                log_request(client_address[0], 'POST', path, 404, len(content), referrer)
    else:
        send_response(client_socket, 'HTTP/1.1 200 OK\r\n', '<html><body>POST received</body></html>', 'text/html')
        log_request(client_address[0], 'POST', path, 200, len(body), referrer)


# Function to send HTTP response
def send_response(client_socket, header, content, content_type):
    client_socket.sendall(
        header.encode() + f"Content-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n".encode() + content if isinstance(
            content, bytes) else content.encode())


# Function to start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"Server started at http://{HOST}:{PORT}")

    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            with connections_lock:
                if len(active_connections) >= MAX_CONNECTIONS:
                    # Close the oldest connection
                    oldest_socket, oldest_thread = active_connections.pop(0)
                    print(f"Closing oldest connection from {oldest_socket.getpeername()}")
                    oldest_socket.close()
                    oldest_thread.join()
                thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                active_connections.append((client_socket, thread))
                executor.submit(thread.start)


if __name__ == "__main__":
    start_server()
