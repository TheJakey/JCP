from _socket import *
import settings
import cryptograph
import sender

class file_sender:

    def __init__(self, soc, file_location):
        self.file_location = file_location
        self.soc = soc
        self.missing_fragments = []
        self.identifier_for_sender = cryptograph.generateIdentifier()
        self.kill_thread = False

        print('File Sender created. ', self.identifier_for_sender)

    def send_file(self):
        print('Sending file')

        if (self.file_location == 'a'):
            self.file_location = 'quattro.jpg'

        identifier = self.identifier_for_sender

        file = open(self.file_location, 'rb')

        self.send_fragments(self.soc,  identifier, file)

        file.close()

        return

    def send_initial_fragment(self, soc, identifier, file):
        payCheck = cryptograph.calculatePayCheck(file.name)
        completeMessage = sender.build_and_send(soc, identifier, 'FIL', 0, payCheck, file.name)

        while (self.waitForConfirmation(soc, identifier)):
            continue

    def send_fragments(self, soc, identifier, file):
        lastByte = 0
        max_payload = settings.maxFragSize - settings.MY_HEADER
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

                payCheck = cryptograph.calculatePayCheck(message)

                if (fragmentNumber == 10 and settings.sent_faulty):
                    payCheck = 0

                completeMessage = sender.build_and_send(soc, identifier, flag, fragmentNumber, payCheck, message)

                messages_list.append(completeMessage)

                if (flag == 'FIE'):
                    sending = False
                    break;
                else:
                    fragmentNumber += 1

            while (self.waitForConfirmation(soc, identifier)):
                print('Re-sending fragment')
                for miss_fragment in self.missing_fragments:
                    completeMessage = messages_list.__getitem__(int(miss_fragment))
                    sender.send_message(soc, completeMessage)

            if (self.kill_thread):
                return

    def waitForConfirmation(self, soc, identifier) -> bool:
        self.soc.settimeout(settings.timeOutKeepAlive)
        kia = 0
        while True:
            try:
                data, addr = soc.recvfrom(1024)
                data = cryptograph.decode(cryptograph, data)
                packet_flag = data.get('flag')

                if (packet_flag == 'KIA'):
                    kia = 0
                    continue

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
                sender.build_and_send(soc, identifier, 'KIA', 0, 0, '')

                if (kia < 3):
                    kia += 1
                    print('KeepAlive send')
                    continue
                else:
                    print('Connection was lost')
                    self.kill_thread = True
                    return False

                continue
            except ConnectionResetError:
                print('Connection was lost')
                self.kill_thread = True
                return False

