import socket
import json
from settings import settings
import cryptograph
import sender

class file_sender:
    SETTING = settings()

    def __init__(self, soc, file_location):
        self.file_location = file_location
        self.soc = soc
        print('File Sender created.')

    def send_file(self):
        print('Sending file')

        # TODO: DELETE BEFORE UPLOAD DEBUG TEST CODE
        if (self.file_location == 'a'):
            self.file_location = 'quattro.jpg'

        file = open(self.file_location, 'rb')

        identifier = cryptograph.generateIdentifier()
        print(identifier)

        self.send_initial_fragment(self.soc, identifier, file)

        self.send_fragments(self.soc, identifier, file)

        file.close()

    def send_initial_fragment(self, soc, identifier, file):
        payCheck = cryptograph.calculatePayCheck(file.name)
        completeMessage = sender.build_and_send(soc, identifier, 'FIL', 0, payCheck, file.name)

        while not (self.waitForConfirmation(soc, identifier)):
            soc.sendto(completeMessage, (self.SETTING.get_ipAddress(), self.SETTING.get_target_port()))

    def send_fragments(self, soc, identifier, file):
        lastByte = 0
        max_payload = self.SETTING.get_maxFragSize() - self.SETTING.get_header_size()
        message = ' '
        fragmentNumber = 1

        while message:
            message = b'' + file.read(max_payload)
            lastByte += message.__sizeof__() - 25

            if (message == b''):
                flag = 'FIE'
            else:
                flag = 'FIL'

            payCheck = cryptograph.calculatePayCheck(message)

            # TODO: IMPLEMENT ERROR IN PAYCHECK BETTER
            # if (fragmentNumber == 3):
            #     payCheck = 6

            # print('fragment send: ', fragmentNumber)
            completeMessage = sender.build_and_send(soc, identifier, flag, fragmentNumber, payCheck, message)

            while (self.waitForConfirmation(soc, identifier)):
                payCheck = cryptograph.calculatePayCheck(message)
                completeMessage = sender.build_and_send(soc, identifier, flag, fragmentNumber, payCheck, message)
            # a = 2
            # while True:
            #     a += a
            fragmentNumber += 1

    def waitForConfirmation(self, soc, identifier) -> bool:
        data, addr = soc.recvfrom(1024)
        data = cryptograph.decode(cryptograph, data)

        packetIdentifier = data.get('identifier')
        if not (identifier == packetIdentifier):
            print('ERROR: NOT MATCHING IDENTIFIERS (identifier: ', identifier, ') !!! !!! !!!')

        flag = data.get('flag')
        if (flag == 'OKE'):
            return False
        elif (flag == 'MSF'):
            return True
        else:
            print('ERROR: CONFIRMATION PACKET CONTAINS UNKNOWN FLAG: ', flag, " !!! !!! !!!")


        return True