import socket
import time
import settings
import sender

KA_IDENTIFIER = 'KEEPALIVE'

class KeepAlive:
    confirmed = False
    sock: socket

    def __init__(self, sock):
        # self.target_ip_address = ip_address
        self.sock = sock
        pass

    def keep_it_alive(self):
        time.sleep(settings.settings.get_timeOutKeepAlive())

        sender.build_and_send(self.sock, KA_IDENTIFIER, 'KIA', 0, 0, b'')

        time.sleep(settings.settings.get_timeOutKeepAlive())

        if not (self.confirmed):
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()


    def confirm_keepAlive(self):
        self.confirmed = True
