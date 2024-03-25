try:
    import socket
    import mimetypes
    from urllib.parse import urlparse
    from modules.logger import logger_http, logger_socket
    from multiprocessing import current_process
    from http.server import BaseHTTPRequestHandler
except ModuleNotFoundError as e:
    print(f"Import error in the http_server module: {e}")
    exit(1)


class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, socket_host, socket_port, base_directory, **kwargs):
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.directory = base_directory
        super().__init__(*args, **kwargs)

    def do_GET(self):
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
        logger_http.info(f'Received data from {self.client_address[0]}:{self.client_address[1]}')

        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size)).decode()

        logger_http.info(f'Open connection to socket://{self.socket_host}:{self.socket_port}')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        logger_http.info(f'Send data to socket://{self.socket_host}:{self.socket_port}')
        client_socket.sendto(data.encode(), (self.socket_host, self.socket_port))

        logger_http.info(f'Close connection to socket://{self.socket_host}:{self.socket_port}')
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
    handler_directory = kwargs.get('handler_directory')

    httpd = server_class((server_bind_host, server_bind_port),
                         lambda *args, **kwargs:
                         handler_class(*args,
                                       socket_host=handler_dst_host,
                                       socket_port=handler_dst_port,
                                       base_directory=handler_directory,
                                       **kwargs))

    try:
        logger_http.info(
            f'Server running on {server_bind_host}:{server_bind_port}')
        httpd.serve_forever()
    except Exception as e:
        logger_http.error(f'Server error: {e}')
    finally:
        logger_http.info(f'Server stopped')
        httpd.server_close()
