try:
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
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    exit(1)


# MongoDB settings
MONGO_URI = 'mongodb://localhost:27017'
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


def insert_data_into_mongo(data, mongo_uri=MONGO_URI,
                           mongo_server_api_version=MONGO_SERVER_API_VERSION,
                           mongo_db_name=MONGO_DATABASE_NAME,
                           mongo_collection_name=MONGO_COLLECTION_NAME):

    client = MongoClient(mongo_uri, server_api=ServerApi(mongo_server_api_version))
    db = client.get_database(mongo_db_name)
    collection = db.get_collection(mongo_collection_name)

    parse_data = unquote_plus(data)

    try:
        parse_data = {key: value for key, value in
                      [item.split('=') for item in parse_data.split('&')]}
        logger_mongo.error(parse_data)
        if isinstance(parse_data, list):
            result = collection.insert_many(parse_data)
        else:
            result = collection.insert_one(json.loads(parse_data))
        return result
    except ValueError as e:
        logger_mongo.error(f'Parse error: {e}')
    except Exception as e:
        logger_mongo.error(f'Failed to insert: {e}')
    finally:
        client.close()


def run_http_server(server_class=HTTPServer,
               handler_class=DemoHTTPRequestHandler,
               server_address=(HTTP_HOST, HTTP_PORT)):

    httpd = server_class(server_address, handler_class)
    try:
        logger_http.info(f'Server running on {server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    except Exception as e:
        logger_http.error(f'Server error: {e}')
    finally:
        logger_http.info('Server stopped')
        httpd.server_close()


def run_socket_server():
    logger_socket.info(f'Server running on socket://{SOCKET_HOST}:{SOCKET_PORT}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SOCKET_HOST, SOCKET_PORT))
        try:
            while True:
                data, addr = sock.recvfrom(SOCKET_BUFFER_SIZE)
                logger_socket.info(f'Received from {addr}: {data.decode()}')
                insert_data_into_mongo(data.decode())
        except Exception as e:
            logger_socket.error(f'Server error: {e}')
        finally:
            logger_socket.info('Server stopped')
            sock.close()


if __name__ == '__main__':
    # Logging settings
    common_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Logger for Socket server
    logger_socket = logging.getLogger('socket server')
    logger_socket.setLevel(logging.INFO)
    handler_socket = logging.StreamHandler()
    handler_socket.setFormatter(common_formatter)
    logger_socket.addHandler(handler_socket)

    # Logger for HTTP server
    logger_http = logging.getLogger('http server')
    logger_http.setLevel(logging.INFO)
    handler_http = logging.StreamHandler()
    handler_http.setFormatter(common_formatter)
    logger_http.addHandler(handler_http)

    # Logger for MongoDB client
    logger_mongo = logging.getLogger('mongodb client')
    logger_mongo.setLevel(logging.INFO)
    handler_mongo = logging.StreamHandler()
    handler_mongo.setFormatter(common_formatter)
    logger_mongo.addHandler(handler_mongo)

    # Run HTTP server thread
    http_thread = Thread(target=run_http_server, name='http server')
    http_thread.start()

    # Run Socket server thread
    socket_thread = Thread(target=run_socket_server, name='socket server')
    socket_thread.start()

