import threading
from ServerCommunication import *
from Lobby import Lobby
import time


class Server:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.server_socket = None

        self.clients: list[Client] = []
        self.lobbies: list[Lobby] = []

        self.last_unique_name_id = 0

    def run(self):
        self.server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))

        self.server_socket.listen()

        while True:
            client = Client(*self.server_socket.accept())
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client: Client):
        print('connection from: ' + str(client.address))
        self.add_client(client)
        client.name = self.get_unique_name()

        while True:
            try:
                message = receive_dict(client.socket)
            except:
                break
            action = message.get('action')

            if action == 'create_lobby':
                self.action_create_lobby(message, client)

            elif action == 'join_lobby':
                self.action_join_lobby(message, client)

            elif action == 'set_name':
                self.action_set_name(message, client)

            elif action == 'leave_lobby':
                self.leave_lobby(client)

            elif action == 'lobby_list':
                self.action_lobby_list(client)

            elif action == 'exit':
                self.action_exit(client)

            try:
                data = client.socket.recv(1024)
                if not data:
                    break
            except ConnectionResetError:
                break

        self.disconnect_client(client)

    def action_create_lobby(self, message, client: Client):
        lobby_name = message.get('name')
        if self.lobby_exists(lobby_name):
            send_dict({'action': 'display_message', 'message': 'this lobby already exists'}, client.socket)
        else:
            self.lobbies.append(Lobby(lobby_name))
            send_dict({'action': 'display_message', 'message': 'lobby created'}, client.socket)
            threading.Thread(target=self.lobby_countdown, args=(self.get_lobby_by_name(lobby_name),)).start()

    def action_join_lobby(self, message, client: Client):
        lobby_name = message.get('lobby_name')
        if not self.lobby_exists(lobby_name):
            send_dict({'action': 'display_message', 'message': 'this lobby does not exist'}, client.socket)
        else:
            lobby = self.get_lobby_by_name(lobby_name)
            lobby.join(client)
            client.lobby_name = lobby.name
            send_dict({'action': 'set_lobby', 'lobby_name': lobby.name}, client.socket)
            broadcast_lobby_excluded({'action': 'display_message', 'message': client.name + ' joined lobby'}, lobby,
                                     client)
            send_dict({'action': 'display_message', 'message': 'joined lobby'}, client.socket)

    def action_set_name(self, message, client: Client):
        name = message.get('name')
        if name in [c.name for c in self.clients]:
            send_dict({'action': 'display_message', 'message': 'name is already in use'}, client.socket)
        else:
            client.set_name(name)
            send_dict({'action': 'set_name', 'name': name}, client.socket)
            send_dict({'action': 'display_message', 'message': f'your name is now {name}'}, client.socket)
            if client.is_in_lobby():
                lobby = self.get_client_lobby(client)
                broadcast_lobby_excluded(
                    {'action': 'display_message', 'message': client.old_name + ' changed name to ' + client.name},
                    lobby, client)

    def action_lobby_list(self, client):
        send_dict({'action': 'display_message', 'message': str([l.name for l in self.lobbies])}, client.socket)

    @staticmethod
    def action_exit(client: Client):
        send_dict({'action': 'exit'}, client.socket)

    def disconnect_client(self, client: Client):
        print('disconnected: ' + str(client.address))
        if client.is_in_lobby():
            self.leave_lobby(client)
        self.remove_client(client)
        client.close_socket()

    def add_client(self, client: Client):
        self.clients.append(client)

    def remove_client(self, client: Client):
        self.clients.remove(client)

    def get_lobby_by_name(self, lobby_name: str):
        for lobby in self.lobbies:
            if lobby.name == lobby_name:
                return lobby

    def get_client_lobby(self, client: Client):
        return self.get_lobby_by_name(client.lobby_name)

    def leave_lobby(self, client: Client):
        if client.is_in_lobby():
            lobby = self.get_client_lobby(client)
            broadcast_lobby_excluded({'action': 'display_message', 'message': client.name + ' left lobby'}, lobby,
                                     client)
            try:
                send_dict({'action': 'display_message', 'message': 'you left lobby'}, client.socket)
                send_dict({'action': 'set_lobby', 'lobby_name': None}, client.socket)
            except:
                pass
            lobby.leave(client)
            client.lobby_name = None
        else:
            send_dict({'action': 'display_message', 'message': 'you are not in a lobby'}, client.socket)

    def lobby_countdown(self, lobby: Lobby):
        while True:
            if len(lobby.clients) < 1:
                lobby.inactivity_time += 1
            else:
                lobby.inactivity_time = 0
            if lobby.inactivity_time > 300:
                break
            time.sleep(1)
        self.lobbies.remove(lobby)
        print('lobby ' + lobby.name + ' has been terminated because of inactivity')

    def greeting(self, client: Client):
        clients_online = len(self.clients)
        send_dict({'action': 'display_message', 'message': 'there are ' + str(clients_online) + ' clients online'},
                  client.socket)

    def get_unique_name(self):
        while True:
            self.last_unique_name_id += 1
            name = 'user' + str(self.last_unique_name_id)
            if name not in [c.name for c in self.clients]:
                return name

    def lobby_exists(self, lobby_name):
        return lobby_name in [l.name for l in self.lobbies]


if __name__ == '__main__':
    server = Server('192.168.1.106', 33003)

    server.run()
