from Client import Client


class Lobby:
    def __init__(self, name: str):
        self.name = name
        print('lobby ' + name + ' has been created')

        self.clients: list[Client] = []

        self.inactivity_time = 0

    def join(self, client: Client):
        self.add_client(client)

    def leave(self, client: Client):
        self.remove_client(client)

    def add_client(self, client: Client):
        self.clients.append(client)

    def remove_client(self, client: Client):
        self.clients.remove(client)
