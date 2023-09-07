from ClientCommunication import *
import threading


class Client:
    def __init__(self, host_ip: str, host_port: int):
        self.host_ip = host_ip
        self.host_port = host_port

        self.name = None
        self.socket = None
        self.lobby_name = None

    def run(self):
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.socket.connect((self.host_ip, self.host_port))

        try:
            threading.Thread(target=self.handle_server).start()
        except ConnectionResetError:
            self.print('server crashed')

        while True:
            self.print('1. Create Lobby\n2. Join Lobby\n3. Set Name\n4. Leave Lobby\n5. Lobbies List\n6. Exit')

            choice = None
            try:
                choice = int(self.input('> '))
            except Exception as exc:
                self.print('incorrect value' + str(exc))

            if choice == 1:
                self.create_lobby()

            elif choice == 2:
                self.join_lobby()

            elif choice == 3:
                self.set_name()

            elif choice == 4:
                self.leave_lobby()

            elif choice == 5:
                self.lobby_list()

            elif choice == 6:
                self.exit()

    def handle_server(self):
        while True:
            server_message = receive_dict(self.socket)

            action = server_message.get('action')

            if action == 'display_message':
                self.action_display_message(server_message)
            elif action == 'set_lobby':
                self.action_set_lobby(server_message)
            elif action == 'exit':
                exit()
            elif action == 'set_name':
                self.action_set_name(server_message)

    def action_display_message(self, server_message):
        message = server_message.get('message')
        self.print(message)

    def action_set_lobby(self, server_message):
        self.lobby_name = server_message.get('lobby_name')

    def create_lobby(self):

        lobby_name = self.input('enter name > ')
        if lobby_name == '':
            self.print('incorrect lobby name')
        elif len(lobby_name) > 24:
            self.print('too long name (MAX: 24)')
        else:
            send_dict({'action': 'create_lobby', 'name': lobby_name}, self.socket)

    def join_lobby(self):
        if self.is_in_lobby():
            self.print('you are currently in lobby')
        else:
            lobby_name = self.input('lobby name > ')
            self.print(lobby_name)
            if lobby_name == '':
                self.print('incorrect lobby name')
            else:
                send_dict({'action': 'join_lobby', 'lobby_name': lobby_name}, self.socket)

    def set_name(self):
        name = self.input('enter name > ')
        if name == '':
            self.print('incorrect name')
        elif len(name) > 24:
            self.print('too long name (MAX: 24)')
        else:
            send_dict({'action': 'set_name', 'name': name}, self.socket)

    def leave_lobby(self):
        if self.is_in_lobby():
            send_dict({'action': 'leave_lobby'}, self.socket)
        else:
            self.print('you are not in a lobby')

    def lobby_list(self):
        send_dict({'action': 'lobby_list'}, self.socket)

    def exit(self):
        send_dict({'action': 'exit'}, self.socket)
        exit()

    def action_set_name(self, server_message):
        self.name = server_message.get('name')

    def is_in_lobby(self):
        return self.lobby_name is not None

    @staticmethod
    def input(msg: str):
        return input(msg)

    @staticmethod
    def print(*args, **kwargs):
        print(*args, **kwargs)


if __name__ == '__main__':
    client = None
    try:
        client = Client('178.235.194.75', 33003)
        client.run()
    except Exception as e:
        print('an error occurred: ' + str(e))
        input()
