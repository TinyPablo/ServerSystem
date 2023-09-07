import socket as s


class Client:
    def __init__(self, client_socket: s.socket, client_address: tuple):
        self.socket = client_socket
        self.address = client_address

        self.name = str(self.address)
        self.old_name = None

        self.lobby_name = None

    def set_name(self, name: str):
        self.old_name = self.name
        self.name = name

    def close_socket(self):
        self.socket.close()

    def is_in_lobby(self):
        if self.lobby_name is None:
            return False
        return True

