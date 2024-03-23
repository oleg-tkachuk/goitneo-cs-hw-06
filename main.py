import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
utils_subdir_path = os.path.join(current_dir, 'modules')
sys.path.append(utils_subdir_path)

try:
    import socket
    import mimetypes
    from pathlib import Path
    from threading import Thread
    from dotenv import load_dotenv
    from urllib.parse import urlparse
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from modules.cli import cli
    from modules.mongo import insert_data_into_mongo
    from modules.logger import logger_http, logger_socket
except ModuleNotFoundError as e:
    print(f"Import error in the main module: {e}")
    exit(1)


# MongoDB settings
MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_SERVER_API_VERSION = '1'
MONGO_DATABASE_NAME = 'cs-homework-06'
MONGO_COLLECTION_NAME = 'posts'

# HTTP server settings
HTTP_HOST = 'localhost'
HTTP_PORT = 3000
# HTTP server base directory
BASE_DIR = Path(__file__).parent

# Socket server settings
SOCKET_HOST = 'localhost'
SOCKET_PORT = 5000
SOCKET_BUFFER_SIZE = 1024

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

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data.encode(), (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()

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


def run_http_server(**kwargs):
    server_class = kwargs.get('server_class', HTTPServer)
    handler_class = kwargs.get('handler_class', DemoHTTPRequestHandler)
    server_address = kwargs.get('server_address', ('localhost', 3000))

    httpd = server_class(server_address, handler_class)
    try:
        logger_http.info(f'Server running on {server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    except Exception as e:
        logger_http.error(f'Server error: {e}')
    finally:
        logger_http.info('Server stopped')
        httpd.server_close()


def run_socket_server(**kwargs):
    socket_host = kwargs.get('socket_host', 'localhost')
    socket_port = kwargs.get('socket_port', 5000)
    socket_buffer_size = kwargs.get('socket_buffer_size', 1024)

    logger_socket.info(f'Server running on socket://{socket_host}:{socket_port}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((socket_host, socket_port))
        try:
            while True:
                data, addr = sock.recvfrom(socket_buffer_size)
                logger_socket.info(f'Received from {addr}: {data.decode()}')
                insert_data_into_mongo(data)
        except Exception as e:
            logger_socket.error(f'Server error: {e}')
        finally:
            logger_socket.info('Server stopped')
            sock.close()


def main():
    args = cli()

    load_dotenv(dotenv_path=args.dotenv)

    # HTTP server settings
    http_server_params = {
        'server_class': HTTPServer,
        'handler_class': DemoHTTPRequestHandler,
        'server_address': (os.getenv('HTTP_HOST', 'localhost'),
                           int(os.getenv('HTTP_PORT', 3000)))
    }

    # Socket server settings
    socket_server_params = {
        'socket_host': os.getenv('SOCKET_HOST', 'localhost'),
        'socket_port': int(os.getenv('SOCKET_PORT', 5000)),
        'socket_buffer_size': int(os.getenv('SOCKET_BUFFER_SIZE', 1024))
    }

    # Mongo client settings
    mongo_client_params = {
        'username': os.getenv('MONGO_INITDB_ROOT_USERNAME', 'root'),
        'password': os.getenv('MONGO_INITDB_ROOT_PASSWORD'),
        'hostname': os.getenv('MONGO_HOST', 'localhost'),
        'port': os.getenv('MONGO_PORT', 27017),
        'auth_source': os.getenv('MONGO_AUTH_SOURCE', 'admin'),
        'db_name': os.getenv('MONGO_DATABASE_NAME'),
        'collection_name': os.getenv('MONGO_COLLECTION_NAME'),
        'server_api_version': os.getenv('MONGO_SERVER_API_VERSION', '1')
    }
    #uri = f"mongodb://{username}:{password}@{hostname}:{port}/?authSource={auth_source}"

    # Run HTTP server thread
    http_thread = Thread(target=run_http_server, kwargs=http_server_params, name='http server')
    http_thread.start()

    # Run Socket server thread
    socket_thread = Thread(target=run_socket_server, kwargs=socket_server_params, name='socket server')
    socket_thread.start()


if __name__ == '__main__':
    main()


