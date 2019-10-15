import socket
import time
import settings
import sender
import cryptograph

class KeepAlive:
    confirmed = False
    sock: socket
    ka_identifier = ''

    def __init__(self, sock):
        # self.target_ip_address = ip_address
        self.sock = sock
        pass

    def keep_it_alive(self):
        print ('keepin it alive')
        setting = settings
        time.sleep(settings.settings.timeOutKeepAlive)

        self.ka_identifier = cryptograph.generateIdentifier()

        sender.build_and_send(self.sock, self.ka_identifier, 'KIA', 0, 0, b'')

        time.sleep(settings.settings.timeOutKeepAlive)

        if not (self.confirmed):
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

    def answer_request(self):
        sender.build_and_send(self.sock, self.ka_identifier, 'KIA', 1, 0, b'')

    def get_indentifier(self):
        return self.ka_identifier

    def confirm_keepAlive(self):
        self.confirmed = True
