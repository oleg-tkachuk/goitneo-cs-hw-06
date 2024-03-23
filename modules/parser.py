try:
    from urllib.parse import unquote_plus
    from modules.logger import logger_socket
except ModuleNotFoundError as e:
    print(f"Import error in the parser module: {e}")
    exit(1)

def parse_data(data):
    try:
        decode_data = unquote_plus(data.decode())
        result = {key: value for key, value in
                      [item.split('=') for item in decode_data.split('&')]}
    except ValueError as e:
        logger_socket.error(f'Parse error: {e}')
    return result