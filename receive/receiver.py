import socket
import cryptograph
import sender
import settings
from receive import file_receiver

class receiver():
    sock: socket
    MAX_PAYCHECK: int

    def __init__(self):
        pass

    def get_file_data(file_data):
        result = b''

        for onePart in file_data:
            result += onePart

        return result


    def confirmPacket(self, addr, identifier, fragmentNumber):
        sender.build_and_send(self.sock, identifier, 'OKE', fragmentNumber, 0, '', addr)

    def requestFragment(self, addr, identifier, fragmentNumber):
        sender.build_and_send(self.sock, identifier, 'MSF', fragmentNumber, 0, '', addr)

    def calculatePaycheck(self, message):
        paycheckCalculated = 0

        if (isinstance(message[0], int)):
            for byte in message:
                paycheckCalculated += byte * byte
        else:
            for byte in message:
                paycheckCalculated += ord(byte) * ord(byte)

        return paycheckCalculated % self.MAX_PAYCHECK

    def validPaycheck(self, data) -> bool:
        paycheckPacket = data.get('paycheck')
        message = data.get('data')
        paycheckCalculated = 0

        if (message != b''):
            paycheckCalculated = self.calculatePaycheck(message)
        else:
            paycheckCalculated = 0

        if (paycheckCalculated == paycheckPacket):
            return True
        else:
            return False

    def receive_file(self, addr, data):
        print('Reeiving file ... ')

        file_data = []
        expectedFragment = 0;
        fragmentNumber = data.get('fragmented')
        packet_flag = data.get('flag')
        identifier = data.get('identifier')

        if not (self.validPaycheck(data)):
            print('ERROR: INVALID PAYCHECK')
            print("Trying to request missing fragment ", fragmentNumber)
            self.requestFragment(addr, identifier, fragmentNumber)

        if not (fragmentNumber == expectedFragment):
            # TODO: REQUEST MISSING FRAGMENT
            print("Trying to request missing fragment ", fragmentNumber)
        else:
            expectedFragment += 1

        self.confirmPacket(addr, identifier, fragmentNumber)

        file_name = data.get('data')
        file = open(file_name, "wb+")

        while packet_flag != 'FIE':  # FILE END
            data, addr = self.sock.recvfrom(1024)
            data = cryptograph.decode(cryptograph, data)

            fragmentNumber = data.get('fragmented')

            if not (self.validPaycheck(data)):
                print('ERROR: INVALID PAYCHECK')
                print("Trying to request missing fragment ", fragmentNumber)
                self.requestFragment(addr, identifier, fragmentNumber)
                continue

            if (fragmentNumber != expectedFragment):
                # TODO: REQUEST MISSING FRAGMENT
                print("Trying to request missing fragment ", fragmentNumber)
                self.requestFragment(addr, identifier, fragmentNumber)
                continue
            else:
                identifier = data.get('identifier')
                expectedFragment += 1

            self.confirmPacket(addr, identifier, fragmentNumber)

            packet_flag = data.get('flag')
            file_data.insert(fragmentNumber, data.get('data'))
            # file_data += data.get('data')

        print('FIE received')

        file_data.insert(fragmentNumber, data.get('data'))

        file.write(self.get_file_data(file_data))
        file.close()

    def get_list_index(self, list, packet_identifier):
        if (list == []):
            return -1
        else:
            for index, fileReceiver in enumerate(list):
                if (packet_identifier == list[index].get_indentifier()):
                    return index

            return -1

    def start_receiving(self):
        fileReceivers = []
        buffer_message = []

        self.sock = socket.socket(socket.AF_INET,  # this specifies address family - IPv4 in this case
                                  socket.SOCK_DGRAM)  # UDP

        print('myport: ', settings.my_port)
        self.sock.bind(('', settings.my_port))

        while True:
            data, addr = self.sock.recvfrom(1480)
            data = cryptograph.decode(cryptograph, data)

            packet_identifier = data.get('identifier')
            packet_flag = data.get('flag')
            if (packet_flag == 'FIL' or packet_flag == 'FIE' or packet_flag == 'MSF'):
                file_receiver_index = self.get_list_index(fileReceivers, packet_identifier)

                if (file_receiver_index == -1):
                    fileReceivers.append(file_receiver.FileReceiver())
                    file_receiver_index = len(fileReceivers) - 1

                fileReceivers[file_receiver_index].receive_file_packet(self.sock, addr, data)

                if (packet_flag == 'FIE'):
                    fileReceivers.remove(fileReceivers[file_receiver_index])

            elif (packet_flag == 'KIA'):
                sender.build_and_send(self.sock, packet_identifier, 'KIA', 1, 0, '', addr)

            elif (packet_flag == 'FGM'):
                identifier = data.get('identifier')
                fragmentNumber = data.get('fragmented')
                buffer_message.append(data.get('data'))
                self.confirmPacket(addr, identifier, fragmentNumber)

            elif (packet_flag == 'FGE'):
                identifier = data.get('identifier')
                fragmentNumber = data.get('fragmented')
                buffer_message.append(data.get('data'))
                for fragment in buffer_message:
                    print(fragment, end="")
                buffer_message.clear()
                self.confirmPacket(addr, identifier, fragmentNumber)

            else:
                identifier = data.get('identifier')
                fragmentNumber = data.get('fragmented')
                self.confirmPacket(addr, identifier, fragmentNumber)

                print('Received data: ', data.get('data'))

    def get_indentifier(self):
        return self.identifier