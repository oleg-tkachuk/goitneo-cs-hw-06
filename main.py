import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
modules_subdir_path = os.path.join(current_dir, 'modules')
sys.path.append(modules_subdir_path)

try:
    import socket
    import mimetypes
    from pathlib import Path
    from dotenv import load_dotenv
    from urllib.parse import urlparse
    from multiprocessing import Process, current_process
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from modules.logger import logger_http, logger_socket
    from modules.mongo import insert_data_into_mongo
    from modules.parser import parse_data
    from modules.cli import cli
except ModuleNotFoundError as e:
    print(f"Import error in the main module: {e}")
    exit(1)


# HTTP server base directory
BASE_DIR = Path(__file__).parent


class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, socket_host, socket_port, **kwargs):
        self.socket_host = socket_host
        self.socket_port = socket_port
        super().__init__(*args, **kwargs)

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
        client_socket.sendto(data.encode(), (self.socket_host, self.socket_port))
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
    server_class = kwargs.get('server_class')
    server_bind_host = kwargs.get('server_bind_host')
    server_bind_port = kwargs.get('server_bind_port')

    handler_class = kwargs.get('handler_class')
    handler_dst_host = kwargs.get('handler_dst_host')
    handler_dst_port = kwargs.get('handler_dst_port')

    httpd = server_class((server_bind_host, server_bind_port),
            lambda *args, **kwargs:
            handler_class(*args, socket_host=handler_dst_host, socket_port=handler_dst_port, **kwargs))

    try:
        logger_http.info(
            f'{current_process().name} running on {server_bind_host}:{server_bind_port}')
        httpd.serve_forever()
    except Exception as e:
        logger_http.error(f'Server error: {e}')
    finally:
        logger_http.info(f'{current_process().name} stopped')
        httpd.server_close()


def run_socket_server(socket_server_params, mongo_client_params):
    socket_bind_host = socket_server_params.get('socket_bind_host')
    socket_bind_port = socket_server_params.get('socket_bind_port')
    socket_buffer_size = socket_server_params.get('socket_buffer_size')

    logger_socket.info(
        f'{current_process().name} running on socket://{socket_bind_host}:{socket_bind_port}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((socket_bind_host, socket_bind_port))
        try:
            while True:
                data, addr = sock.recvfrom(socket_buffer_size)
                logger_socket.info(f'Received data from {addr[0]}:{addr[1]}')
                insert_data_into_mongo(parse_data(data), mongo_client_params)
        except Exception as e:
            logger_socket.error(f'Server error: {e}')
        finally:
            logger_socket.info(f'{current_process().name} stopped')


def main():
    args = cli(BASE_DIR)
    load_dotenv(dotenv_path=args.dotenv)

    # HTTP server settings
    http_server_params = {
        'server_class':     HTTPServer,
        'server_bind_host': os.getenv('HTTP_BIND_HOST'),
        'server_bind_port': int(os.getenv('HTTP_BIND_PORT')),
        'handler_class':    DemoHTTPRequestHandler,
        'handler_dst_host': os.getenv('SOCKET_BIND_HOST'),
        'handler_dst_port': int(os.getenv('SOCKET_BIND_PORT'))
    }

    # Socket server settings
    socket_server_params = {
        'socket_bind_host':   os.getenv('SOCKET_BIND_HOST'),
        'socket_bind_port':   int(os.getenv('SOCKET_BIND_PORT')),
        'socket_buffer_size': int(os.getenv('SOCKET_BUFFER_SIZE', 1024))
    }

    # Mongo client settings
    mongo_client_params = {
        'username':           os.getenv('MONGO_INITDB_ROOT_USERNAME'),
        'password':           os.getenv('MONGO_INITDB_ROOT_PASSWORD'),
        'hostname':           os.getenv('MONGO_HOSTNAME'),
        'port':               os.getenv('MONGO_BIND_PORT'),
        'auth_source':        os.getenv('MONGO_AUTH_SOURCE'),
        'db_name':            os.getenv('MONGO_DATABASE_NAME'),
        'collection_name':    os.getenv('MONGO_COLLECTION_NAME'),
        'server_api_version': os.getenv('MONGO_SERVER_API_VERSION', '1')
    }

    http_prcess = Process(target=run_http_server, kwargs=http_server_params,
                          name='HTTP Server Process')
    socket_process = Process(target=run_socket_server,
                             args=(socket_server_params, mongo_client_params),
                             name='Socket Server Process')

    http_prcess.start()
    socket_process.start()

    http_prcess.join()
    socket_process.join()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\nGood bye!")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
