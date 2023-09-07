import pickle
import socket as s
from Lobby import Lobby
from Client import Client


def send_message(message: bytes, socket: s.socket, header_length=10):
    def convert_to_header(header: bytes, header_length: int) -> bytes:  # noqa
        return bytes(f'{len(header):<{header_length}}', "utf-8") + header
    message = convert_to_header(message, header_length)
    socket.send(message)


def receive_message(socket: s.socket, sending_size=1024 * 1024, header_size=10):
    full_message = b''
    new_message = True
    while True:
        server_message = socket.recv(sending_size)
        if new_message:
            message_length = int(server_message[:header_size])
            new_message = False

        full_message += server_message

        if len(full_message) - header_size == message_length:  # noqa
            return full_message[header_size:]


def send_dict(d: dict, socket: s.socket, header_length=10):
    send_message(pickle.dumps(d), socket, header_length)


def receive_dict(socket: s.socket, sending_size=1024 * 1024, header_size=10):
    return pickle.loads(receive_message(socket, sending_size, header_size))


def broadcast_message(d: dict, sockets: list[s.socket], header_length=10):
    for socket in sockets:
        send_dict(d, socket, header_length)


def broadcast_lobby_excluded(d: dict, lobby: Lobby, excluded_client: Client):
    clients = lobby.clients.copy()
    clients.remove(excluded_client)
    broadcast_message(d, [c.socket for c in clients])


def broadcast_lobby(d: dict, lobby: Lobby):
    broadcast_message(d, [c.socket for c in lobby.clients])
