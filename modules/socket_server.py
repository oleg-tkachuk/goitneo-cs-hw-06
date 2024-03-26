try:
    import socket
    from modules.parser import parse_data
    from modules.logger import logger_socket
    from modules.mongo_client import insert_data_into_mongo
    from multiprocessing import current_process
except ModuleNotFoundError as e:
    print(f"Import error in the socket_server module: {e}")
    exit(1)


def run_socket_server(socket_server_params, mongo_client_params):
    socket_bind_host = socket_server_params.get('socket_bind_host')
    socket_bind_port = socket_server_params.get('socket_bind_port')
    socket_buffer_size = socket_server_params.get('socket_buffer_size')

    logger_socket.info(
        f'Server running on socket://{socket_bind_host}:{socket_bind_port}')
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
            logger_socket.info(f'Server stopped')
