import sys
import socket
import select
# from _typeshed import FileDescriptorLike
from collections.abc import Callable, Iterable

SIZE = 1024
MINUTE = 60
NUM_LISTEN = 5


class Reactor(object):
    def __init__(self):
        self.handler = select.poll()
        self.fd_to_action: dict[int: (Callable, Iterable)] = {}

    def register(self, file_obj: socket.socket, event_mask: int, func: Callable, args: Iterable = ()):
        self.handler.register(file_obj, event_mask)
        self.fd_to_action[file_obj.fileno()] = (func, args)

    def unregister(self, file_obj: socket.socket):
        self.handler.unregister(file_obj)

    def handle_events(self):
        while True:
            events = self.handler.poll()
            for key, mask in events:
                callback, args = self.fd_to_action[key]
                callback(*args)


class EchoServer(object):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reactor = Reactor()

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(NUM_LISTEN)
        self.sock.setblocking(False)
        self.reactor.register(self.sock, select.POLLIN, self.accept_client)
        self.reactor.handle_events()

    def accept_client(self):
        client, addr = self.sock.accept()
        print(f'Connected to {addr[0]} : {addr[1]}')
        client.setblocking(False)
        self.reactor.register(client, select.POLLIN, self.handle_client, (client,))

    def handle_client(self, client: socket.socket):
        data = client.recv(SIZE)
        if data:
            client.send(data)
        else:
            print(f'Closing connection')
            self.reactor.unregister(client)
            client.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: echo_server.py [host] [ip]")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        server = EchoServer(host, port)
        server.start()
