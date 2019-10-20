from _socket import *
import json
from settings import settings
import cryptograph
import sender

class file_sender:
    SETTING = settings()

    def __init__(self, soc, file_location):
        self.file_location = file_location
        self.soc = soc
        self.missing_fragments = []
        print('File Sender created.')

    def send_file(self):
        print('Sending file')

        # TODO: DELETE BEFORE UPLOAD DEBUG TEST CODE
        if (self.file_location == 'a'):
            self.file_location = 'quattro.jpg'

        file = open(self.file_location, 'rb')

        identifier = cryptograph.generateIdentifier()
        print(identifier)

        self.send_fragments(self.soc, identifier, file)

        file.close()

    def send_initial_fragment(self, soc, identifier, file):
        payCheck = cryptograph.calculatePayCheck(file.name)
        completeMessage = sender.build_and_send(soc, identifier, 'FIL', 0, payCheck, file.name)

        while (self.waitForConfirmation(soc, identifier)):
            soc.sendto(completeMessage, (self.SETTING.get_ipAddress(), self.SETTING.get_target_port()))

    def send_fragments(self, soc, identifier, file):
        lastByte = 0
        max_payload = self.SETTING.get_maxFragSize() - self.SETTING.get_header_size()
        message = ' '
        messages_list = []
        fragmentNumber = 1
        sending = True
        initial_fragment_send = False

        while sending:
            for i in range(0, 50):
                if not (initial_fragment_send):
                    self.send_initial_fragment(self.soc, identifier, file)
                    initial_fragment_send = True
                    continue

                message = b'' + file.read(max_payload)
                lastByte += message.__sizeof__() - 25

                if (message == b''):
                    flag = 'FIE'
                else:
                    flag = 'FIL'

                # print("sending: ", fragmentNumber)

                payCheck = cryptograph.calculatePayCheck(message)

                # TODO: IMPLEMENT ERROR IN PAYCHECK BETTER
                # if (fragmentNumber == 3):
                #     payCheck = 6

                # print('fragment send: ', fragmentNumber)
                completeMessage = sender.build_and_send(soc, identifier, flag, fragmentNumber, payCheck, message)

                messages_list.append(completeMessage)

                # a = 2
                # while True:
                #     a += a
                if (flag == 'FIE'):
                    sending = False
                    break;
                else:
                    fragmentNumber += 1

            while (self.waitForConfirmation(soc, identifier)):
                print('verify')
                for miss_fragment in self.missing_fragments:
                    completeMessage = messages_list.__getitem__(miss_fragment)
                    sender.send_message(soc, completeMessage)

                # TODO: IMPLEMENT CHECKING HERE
                # payCheck = cryptograph.calculatePayCheck(message)
                # completeMessage = sender.build_and_send(soc, identifier, flag, fragmentNumber, payCheck, message)
            fragmentNumber = 0

    def waitForConfirmation(self, soc, identifier) -> bool:
        self.soc.settimeout(10)
        while True:
            try:
                data, addr = soc.recvfrom(1024)
                data = cryptograph.decode(cryptograph, data)

                packetIdentifier = data.get('identifier')
                if not (identifier == packetIdentifier):
                    print('ERROR: NOT MATCHING IDENTIFIERS (identifier: ', identifier, ') !!! !!! !!!')

                flag = data.get('flag')
                if (flag == 'OKE'):
                    return False
                elif (flag == 'MSF'):
                    self.missing_fragments = data.get('data').split('-')
                    return True
                else:
                    print('ERROR: CONFIRMATION PACKET CONTAINS UNKNOWN FLAG: ', flag, " !!! !!! !!!")

                return True
            except timeout:
                print('Timeout')
                # sender.build_and_send(soc, identifier, 'MSF', 0, 0, b'')
                continue

