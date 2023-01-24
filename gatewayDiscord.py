import socket
import ssl
import threading
import time
from sys import platform

import certifi
from discord_gateway import DiscordConnection

class DiscordSocket:
    TOKEN = 'YOUR_VERY.WELL.HIDDEN_TOKEN'
    RECV_SIZE = 65536
    SERVER_NAME = 'gateway.discord.gg'

    #class constructor
    def __init__(self, token, serverName):
        self.TOKEN = token
        self.SERVER_NAME = serverName
        pass

    def heartbeat(self,conn, sock):
        while True:
            sock.send(conn.heartbeat())
            time.sleep(conn.heartbeat_interval)


    def recv_event(self,conn, sock):
        while True:
            for event in conn.events():
                return event

            for to_send in conn.receive(sock.recv(self.RECV_SIZE)):
                sock.send(to_send)


    def main(self):
        # Setup the socket and SSL for the WebSocket Secure connection.
        conn = DiscordConnection(self.SERVER_NAME, encoding='json')
        ctx = ssl.create_default_context(cafile=certifi.where())
        sock = socket.create_connection(conn.destination)
        sock = ctx.wrap_socket(sock, server_hostname=self.SERVER_NAME)

        sock.send(conn.connect())  # Convert to a WebSocket

        # Receive the very first HELLO event.
        hello = self.recv_event(conn, sock)

        # Send RESUME or IDENTIFY depending on state (will always be False
        # when initially connecting, but may be different when reconnecting).
        if conn.should_resume:
            sock.send(conn.resume(self.TOKEN))
        else:
            sock.send(conn.identify(
                token=self.TOKEN,
                intents=65535,
                properties={
                    '$os': platform,
                    '$browser': 'discord-gateway',
                    '$device': 'discord-gateway'
                },
            ))

        heartbeater = threading.Thread(target=self.heartbeat, args=(conn,sock))
        heartbeater.start()

        try:
            while True:
                event = self.recv_event(conn, sock)
                print('Received:', event)
        finally:
            sock.shutdown(socket.SHUT_WR)
            sock.close()

