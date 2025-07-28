import sys
import socket
import threading

# HOST = "127.0.0.1"
# PORT = 6666

SIZE = 1024
MINUTE = 60
NUM_LISTEN = 5


class EchoServer(object):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.bind((self.host, self.port))  # It might be better to put that in "start" but not really important
        self.sock.listen(NUM_LISTEN)  # Magic
        while True:
            client, addr = self.sock.accept()  # What is c (bad naming)
            print(f'Connected to: {addr[0]} : {addr[1]}')  # Use f-string
            client.settimeout(MINUTE)  # Magic
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client: socket.socket):  # I would probably prefer it as a method of EchoServer if possible # Type anotations
        while True:
            data = client.recv(SIZE)
            if not data:  # I prefer data == "" but not very important
                print('Closing Connection')
                break
            client.send(data)
        client.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: echo_server.py [host] [ip]")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        server = EchoServer(host, port)
        server.start()
