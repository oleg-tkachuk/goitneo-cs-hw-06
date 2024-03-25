import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
modules_subdir_path = os.path.join(current_dir, 'modules')
sys.path.append(modules_subdir_path)

try:
    from pathlib import Path
    from modules.cli import cli
    from dotenv import load_dotenv
    from http.server import HTTPServer
    from multiprocessing import Process
    from modules.http_server import run_http_server
    from modules.http_server import DemoHTTPRequestHandler
    from modules.socket_server import run_socket_server
except ModuleNotFoundError as e:
    print(f"Import error in the main module: {e}")
    exit(1)


# HTTP server base directory
BASE_DIR = Path(__file__).parent


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
        'handler_dst_port': int(os.getenv('SOCKET_BIND_PORT')),
        'handler_directory': BASE_DIR
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

    # Creating processes
    http_prcess = Process(target=run_http_server, kwargs=http_server_params,
                          name='HTTP Server Process')
    socket_process = Process(target=run_socket_server,
                             args=(socket_server_params, mongo_client_params),
                             name='Socket Server Process')

    # Launching processes
    http_prcess.start()
    socket_process.start()

    # Waiting for processes to be completed
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
