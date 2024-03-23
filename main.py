import json
import socket
import logging
import mimetypes
from pathlib import Path
from threading import Thread
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from urllib.parse import urlparse, unquote_plus
from http.server import HTTPServer, BaseHTTPRequestHandler


# MongoDB settings
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE_NAME = 'messages'

# HTTP server settings
HTTP_HOST = 'localhost'
HTTP_PORT = 3000
# HTTP server base directory
BASE_DIR = Path(__file__).parent

# Socket server settings
SOCKET_HOST = 'localhost'
SOCKET_PORT = 5000
BUFFER_SIZE = 1024

class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.directory = BASE_DIR

        router = urlparse(self.path).path
        match router:
            case '/':
                self.send_html(self.directory.joinpath('index.html'))
            case '/message.html':
                self.send_html(self.directory.joinpath('message.html'))
            case _:
                file = self.directory.joinpath(router[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html(
                        self.directory.joinpath('error.html'), status=404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size)).decode()

        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data.encode(), (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        #print(unquote_plus(data))

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html(self, file_path, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, file_path, status=200):
        self.send_response(status)
        mt = mimetypes.guess_type(file_path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())


def save_data_to_mongo(data):
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client.get_database(MONGO_DATABASE_NAME)
    posts = db.posts
    posts.insert_one(json.loads(data))


def run_http_server(server_class=HTTPServer,
               handler_class=DemoHTTPRequestHandler,
               server_address=(HTTP_HOST, HTTP_PORT)):

    httpd = server_class(server_address, handler_class)
    try:
        print(f'HTTP server running on {server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    except Exception as e:
        logging.error(f'Server error: {e}')
    finally:
        logging.info('Server stopped')
        httpd.server_close()


def run_socket_server():
    print(f'Socket server running on {SOCKET_HOST}:{SOCKET_PORT}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SOCKET_HOST, SOCKET_PORT))
        sock.listen()
        try:
            while True:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                logging.info(f'Received from {addr}: {data.decode()}')
                save_data_to_mongo()
        except Exception as e:
            logging.error(f'Server error: {e}')
        finally:
            logging.info('Server stopped')
            sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    http_thread = Thread(target=run_http_server, name='http server')
    http_thread.start()

    socket_thread = Thread(target=run_socket_server, name='socket server')
    socket_thread.start()

