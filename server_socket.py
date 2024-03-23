import socket

def main(port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        host = socket.gethostbyname(socket.gethostname())
        sock.bind((host, port))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024).decode()
                    print(f'Received: {data!r}')
                    if not data:
                        break
                    conn.send(data.encode())
                    #conn.sendall(data.encode())

if __name__ == '__main__':
    main()
