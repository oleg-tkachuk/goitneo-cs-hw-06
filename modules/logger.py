try:
    import logging
except ModuleNotFoundError as e:
    print(f"Import error in the logger module: {e}")
    exit(1)

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