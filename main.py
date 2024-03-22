import mimetypes
from pathlib import Path
from urllib.parse import urlparse, unquote_plus
from http.server import HTTPServer, BaseHTTPRequestHandler


BASE_DIR = Path(__file__).parent


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

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, World!')

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


def run_server(server_class=HTTPServer,
               handler_class=DemoHTTPRequestHandler,
               server_address=('localhost', 3000)):

    httpd = server_class(server_address, handler_class)
    try:
        print(f'Server running on {server_address[0]}:{server_address[1]}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server stopped')


if __name__ == '__main__':
    run_server()
